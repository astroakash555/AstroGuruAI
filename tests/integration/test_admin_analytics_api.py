"""Integration tests for admin analytics API."""

from __future__ import annotations

from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from backend.app.api.deps import get_analytics_service
from backend.app.services.analytics.analytics_service import AnalyticsService
from backend.app.services.analytics.models import (
    AIMetrics,
    ChatMetrics,
    DashboardOverview,
    ReportMetrics,
    RevenueMetrics,
    SystemMetrics,
    UserMetrics,
)
from backend.app.services.analytics.serializers import (
    ai_metrics_to_dict,
    chat_metrics_to_dict,
    dashboard_overview_to_dict,
    report_metrics_to_dict,
    revenue_metrics_to_dict,
    system_metrics_to_dict,
    user_metrics_to_dict,
)
from tests.helpers import override_current_user, override_usage_service


def _timestamp() -> datetime:
    return datetime(2026, 6, 15, 12, 0, tzinfo=UTC)


def _period_start() -> date:
    return date(2026, 6, 1)


def _placeholder_overview(**overrides: int) -> DashboardOverview:
    values = {
        "total_users": 1,
        "active_users": 1,
        "verified_users": 1,
        "total_clients": 1,
        "active_clients": 1,
        "total_reports": 1,
        "total_chat_queries": 1,
        "total_revenue_paise": 1,
        "active_subscriptions": 1,
        "captured_payments": 1,
        "generated_at": _timestamp(),
    }
    values.update(overrides)
    return DashboardOverview(**values)


def _placeholder_revenue_metrics(**overrides: int | float) -> RevenueMetrics:
    values = {
        "total_revenue_paise": 99900,
        "revenue_this_period_paise": 49900,
        "captured_payments": 2,
        "failed_payments": 0,
        "pending_payments": 0,
        "refunded_payments": 0,
        "total_orders": 2,
        "paid_orders": 2,
        "failed_orders": 0,
        "pending_orders": 0,
        "conversion_rate": 1.0,
        "average_order_value_paise": 49950,
        "revenue_by_plan": (("pro", 99900),),
        "subscriptions_by_plan": (("pro", 2),),
        "period_start": _period_start(),
        "generated_at": _timestamp(),
    }
    values.update(overrides)
    return RevenueMetrics(**values)


def _placeholder_user_metrics(**overrides: int | float) -> UserMetrics:
    values = {
        "total_users": 10,
        "active_users": 8,
        "verified_users": 7,
        "inactive_users": 2,
        "unverified_users": 3,
        "new_users_this_period": 1,
        "users_by_role": (("user", 9), ("admin", 1)),
        "active_subscriptions_by_plan": (("free", 8),),
        "total_clients": 20,
        "average_clients_per_user": 2.0,
        "quota_usage_by_metric": (("reports", 5),),
        "period_start": _period_start(),
        "generated_at": _timestamp(),
    }
    values.update(overrides)
    return UserMetrics(**values)


def _placeholder_report_metrics(**overrides: int | float) -> ReportMetrics:
    values = {
        "total_reports": 5,
        "reports_this_period": 2,
        "reports_with_pdf": 3,
        "distinct_clients_with_reports": 4,
        "distinct_owners": 2,
        "average_reports_per_owner": 2.5,
        "reports_by_version": (("1.0", 5),),
        "pdf_by_status": (("completed", 3),),
        "period_start": _period_start(),
        "generated_at": _timestamp(),
    }
    values.update(overrides)
    return ReportMetrics(**values)


def _placeholder_chat_metrics(**overrides: int | float) -> ChatMetrics:
    values = {
        "total_queries": 30,
        "queries_this_period": 10,
        "answered_queries": 25,
        "failed_queries": 3,
        "processing_queries": 2,
        "queries_by_type": (("kundali", 30),),
        "queries_by_status": (("answered", 25),),
        "total_prompt_tokens": 100,
        "total_completion_tokens": 200,
        "total_tokens": 300,
        "average_tokens_per_query": 12.0,
        "queries_by_model": (("gemini", 20),),
        "quota_consumed_this_period": 10,
        "period_start": _period_start(),
        "generated_at": _timestamp(),
    }
    values.update(overrides)
    return ChatMetrics(**values)


def _placeholder_system_metrics(**overrides: int | float) -> SystemMetrics:
    values = {
        "active_sessions": 5,
        "failed_orders": 1,
        "expired_orders": 0,
        "failed_pdf_generations": 2,
        "inactive_users": 2,
        "unverified_users": 3,
        "chat_error_rate": 0.1,
        "generated_at": _timestamp(),
    }
    values.update(overrides)
    return SystemMetrics(**values)


def _placeholder_ai_metrics(**overrides: int | float) -> AIMetrics:
    values = {
        "total_invocations": 30,
        "successful_invocations": 25,
        "failed_invocations": 3,
        "invocations_this_period": 10,
        "total_prompt_tokens": 100,
        "total_completion_tokens": 200,
        "total_tokens": 300,
        "average_tokens_per_success": 12.0,
        "invocations_by_model": (("gemini", 20),),
        "invocations_by_query_type": (("kundali", 30),),
        "invocations_without_token_data": 5,
        "period_start": _period_start(),
        "generated_at": _timestamp(),
    }
    values.update(overrides)
    return AIMetrics(**values)


ANALYTICS_ENDPOINTS: list[tuple[str, str, set[str]]] = [
    (
        "/api/v1/admin/analytics/overview",
        "overview",
        set(dashboard_overview_to_dict(_placeholder_overview()).keys()),
    ),
    (
        "/api/v1/admin/analytics/users",
        "users",
        set(user_metrics_to_dict(_placeholder_user_metrics()).keys()),
    ),
    (
        "/api/v1/admin/analytics/revenue",
        "revenue",
        set(revenue_metrics_to_dict(_placeholder_revenue_metrics()).keys()),
    ),
    (
        "/api/v1/admin/analytics/reports",
        "reports",
        set(report_metrics_to_dict(_placeholder_report_metrics()).keys()),
    ),
    (
        "/api/v1/admin/analytics/chat",
        "chat",
        set(chat_metrics_to_dict(_placeholder_chat_metrics()).keys()),
    ),
    (
        "/api/v1/admin/analytics/system",
        "system",
        set(system_metrics_to_dict(_placeholder_system_metrics()).keys()),
    ),
    (
        "/api/v1/admin/analytics/ai",
        "ai",
        set(ai_metrics_to_dict(_placeholder_ai_metrics()).keys()),
    ),
]


def _empty_overview() -> DashboardOverview:
    return _placeholder_overview(
        total_users=0,
        active_users=0,
        verified_users=0,
        total_clients=0,
        active_clients=0,
        total_reports=0,
        total_chat_queries=0,
        total_revenue_paise=0,
        active_subscriptions=0,
        captured_payments=0,
    )


@pytest.fixture
def populated_analytics_service() -> AsyncMock:
    service = AsyncMock(spec=AnalyticsService)
    service.get_dashboard_overview.return_value = _placeholder_overview()
    service.get_user_metrics.return_value = _placeholder_user_metrics()
    service.get_revenue_metrics.return_value = _placeholder_revenue_metrics()
    service.get_report_metrics.return_value = _placeholder_report_metrics()
    service.get_chat_metrics.return_value = _placeholder_chat_metrics()
    service.get_system_metrics.return_value = _placeholder_system_metrics()
    service.get_ai_metrics.return_value = _placeholder_ai_metrics()
    return service


@pytest.fixture
def empty_analytics_service() -> AsyncMock:
    service = AsyncMock(spec=AnalyticsService)
    service.get_dashboard_overview.return_value = _empty_overview()
    service.get_user_metrics.return_value = _placeholder_user_metrics(
        total_users=0,
        active_users=0,
        verified_users=0,
        inactive_users=0,
        unverified_users=0,
        new_users_this_period=0,
        users_by_role=(),
        active_subscriptions_by_plan=(),
        total_clients=0,
        average_clients_per_user=0.0,
        quota_usage_by_metric=(),
    )
    service.get_revenue_metrics.return_value = _placeholder_revenue_metrics(
        total_revenue_paise=0,
        revenue_this_period_paise=0,
        captured_payments=0,
        failed_payments=0,
        pending_payments=0,
        refunded_payments=0,
        total_orders=0,
        paid_orders=0,
        failed_orders=0,
        pending_orders=0,
        conversion_rate=0.0,
        average_order_value_paise=0,
        revenue_by_plan=(),
        subscriptions_by_plan=(),
    )
    service.get_report_metrics.return_value = _placeholder_report_metrics(
        total_reports=0,
        reports_this_period=0,
        reports_with_pdf=0,
        distinct_clients_with_reports=0,
        distinct_owners=0,
        average_reports_per_owner=0.0,
        reports_by_version=(),
        pdf_by_status=(),
    )
    service.get_chat_metrics.return_value = _placeholder_chat_metrics(
        total_queries=0,
        queries_this_period=0,
        answered_queries=0,
        failed_queries=0,
        processing_queries=0,
        queries_by_type=(),
        queries_by_status=(),
        total_prompt_tokens=0,
        total_completion_tokens=0,
        total_tokens=0,
        average_tokens_per_query=0.0,
        queries_by_model=(),
        quota_consumed_this_period=0,
    )
    service.get_system_metrics.return_value = _placeholder_system_metrics(
        active_sessions=0,
        failed_orders=0,
        expired_orders=0,
        failed_pdf_generations=0,
        inactive_users=0,
        unverified_users=0,
        chat_error_rate=0.0,
    )
    service.get_ai_metrics.return_value = _placeholder_ai_metrics(
        total_invocations=0,
        successful_invocations=0,
        failed_invocations=0,
        invocations_this_period=0,
        total_prompt_tokens=0,
        total_completion_tokens=0,
        total_tokens=0,
        average_tokens_per_success=0.0,
        invocations_by_model=(),
        invocations_by_query_type=(),
        invocations_without_token_data=0,
    )
    return service


@pytest.fixture
async def admin_analytics_client(app, admin_user, populated_analytics_service):
    app.dependency_overrides[get_analytics_service] = lambda: populated_analytics_service
    override_current_user(app, admin_user)
    override_usage_service(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_analytics_unauthorized(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/analytics/overview")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("path,_,__", ANALYTICS_ENDPOINTS)
async def test_admin_analytics_forbidden_for_non_admin(app, test_user, populated_analytics_service, path, _, __):
    app.dependency_overrides[get_analytics_service] = lambda: populated_analytics_service
    override_current_user(app, test_user)
    override_usage_service(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(path)
    app.dependency_overrides.clear()
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize("path,_,expected_keys", ANALYTICS_ENDPOINTS)
async def test_admin_analytics_success_for_admin(admin_analytics_client, path, _, expected_keys):
    response = await admin_analytics_client.get(path)
    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == expected_keys


@pytest.mark.asyncio
async def test_admin_analytics_overview_populated_schema(admin_analytics_client):
    response = await admin_analytics_client.get("/api/v1/admin/analytics/overview")
    payload = response.json()
    assert payload["total_users"] == 1
    assert payload["total_revenue_paise"] == 1
    assert payload["generated_at"] == _timestamp().isoformat()


@pytest.mark.asyncio
async def test_admin_analytics_empty_database(app, admin_user, empty_analytics_service):
    app.dependency_overrides[get_analytics_service] = lambda: empty_analytics_service
    override_current_user(app, admin_user)
    override_usage_service(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        overview = await client.get("/api/v1/admin/analytics/overview")
        revenue = await client.get("/api/v1/admin/analytics/revenue")
    app.dependency_overrides.clear()

    assert overview.status_code == 200
    assert overview.json()["total_users"] == 0
    assert revenue.status_code == 200
    assert revenue.json()["total_revenue_paise"] == 0
    assert revenue.json()["revenue_by_plan"] == []


@pytest.mark.asyncio
async def test_admin_analytics_revenue_populated_breakdowns(admin_analytics_client):
    response = await admin_analytics_client.get("/api/v1/admin/analytics/revenue")
    payload = response.json()
    assert payload["revenue_by_plan"] == [{"plan": "pro", "amount_paise": 99900}]
    assert payload["subscriptions_by_plan"] == [{"label": "pro", "count": 2}]


@pytest.mark.asyncio
async def test_admin_analytics_database_error_returns_500(app, admin_user):
    failing_service = AsyncMock(spec=AnalyticsService)
    failing_service.get_dashboard_overview.side_effect = SQLAlchemyError("database unavailable")

    app.dependency_overrides[get_analytics_service] = lambda: failing_service
    override_current_user(app, admin_user)
    override_usage_service(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/analytics/overview")
    app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json()["detail"] == "Unable to load analytics data."


@pytest.mark.asyncio
async def test_admin_analytics_service_methods_invoked(admin_analytics_client, populated_analytics_service):
    await admin_analytics_client.get("/api/v1/admin/analytics/overview")
    await admin_analytics_client.get("/api/v1/admin/analytics/users")
    await admin_analytics_client.get("/api/v1/admin/analytics/revenue")
    await admin_analytics_client.get("/api/v1/admin/analytics/reports")
    await admin_analytics_client.get("/api/v1/admin/analytics/chat")
    await admin_analytics_client.get("/api/v1/admin/analytics/system")
    await admin_analytics_client.get("/api/v1/admin/analytics/ai")

    populated_analytics_service.get_dashboard_overview.assert_awaited_once()
    populated_analytics_service.get_user_metrics.assert_awaited_once()
    populated_analytics_service.get_revenue_metrics.assert_awaited_once()
    populated_analytics_service.get_report_metrics.assert_awaited_once()
    populated_analytics_service.get_chat_metrics.assert_awaited_once()
    populated_analytics_service.get_system_metrics.assert_awaited_once()
    populated_analytics_service.get_ai_metrics.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_analytics_empty_database_via_real_service(app, admin_user):
    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(scalar_one=MagicMock(return_value=0), all=MagicMock(return_value=[]))

    app.dependency_overrides[get_analytics_service] = lambda: AnalyticsService(mock_session)
    override_current_user(app, admin_user)
    override_usage_service(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/analytics/system")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["active_sessions"] == 0
    assert response.json()["chat_error_rate"] == 0.0
