"""Tests for AnalyticsService."""

from __future__ import annotations

from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.models.enums import SubscriptionPlan, UserRole
from backend.app.models.user import User
from backend.app.services.analytics.analytics_service import AnalyticsService


def _scalar(value: object) -> MagicMock:
    result = MagicMock()
    result.scalar_one.return_value = value
    return result


def _group_rows(rows: list[tuple[object, int]]) -> MagicMock:
    result = MagicMock()
    result.all.return_value = rows
    return result


@pytest.mark.asyncio
async def test_scalar_helpers(analytics_service, mock_session):
    mock_session.execute.return_value = _scalar(12)
    assert await analytics_service._count_rows(User) == 12
    assert await analytics_service._count_distinct(User, User.id) == 12
    assert await analytics_service._sum_column(User, User.id) == 12
    assert await analytics_service._quota_total_for_metric(
        __import__("backend.app.models.enums", fromlist=["UsageMetric"]).UsageMetric.REPORTS,
        date(2026, 6, 1),
    ) == 12


@pytest.mark.asyncio
async def test_group_count_sorts_labels(analytics_service, mock_session):
    mock_session.execute.return_value = _group_rows([(UserRole.ADMIN, 1), (UserRole.USER, 9)])
    rows = await analytics_service._group_count(User.role, User)
    assert rows == (("admin", 1), ("user", 9))


@pytest.mark.asyncio
async def test_revenue_by_plan(analytics_service, mock_session):
    mock_session.execute.return_value = _group_rows([(SubscriptionPlan.PRO, 99900)])
    rows = await analytics_service._revenue_by_plan()
    assert rows == (("pro", 99900),)


@pytest.mark.asyncio
async def test_quota_usage_by_metric(analytics_service, mock_session):
    metric = __import__("backend.app.models.enums", fromlist=["UsageMetric"]).UsageMetric.REPORTS
    mock_session.execute.return_value = _group_rows([(metric, 4)])
    rows = await analytics_service._quota_usage_by_metric(date(2026, 6, 1))
    assert rows == (("reports", 4),)


@pytest.mark.asyncio
async def test_scalar_helpers_with_filters(analytics_service, mock_session):
    mock_session.execute.return_value = _scalar(4)
    assert await analytics_service._count_rows(User, User.is_active.is_(True)) == 4
    assert await analytics_service._count_distinct(User, User.id, User.is_active.is_(True)) == 4
    assert await analytics_service._sum_column(User, User.id, User.is_active.is_(True)) == 4


@pytest.mark.asyncio
async def test_group_count_with_filters(analytics_service, mock_session):
    mock_session.execute.return_value = _group_rows([(UserRole.USER, 2)])
    rows = await analytics_service._group_count(User.role, User, User.is_active.is_(True))
    assert rows == (("user", 2),)


@pytest.mark.asyncio
async def test_get_dashboard_overview(analytics_service):
    analytics_service._sum_column = AsyncMock(return_value=99900)
    analytics_service._count_rows = AsyncMock(
        side_effect=[10, 8, 7, 20, 18, 5, 30, 4, 12]
    )

    overview = await analytics_service.get_dashboard_overview()

    assert overview.total_users == 10
    assert overview.total_revenue_paise == 99900
    assert overview.captured_payments == 12
    assert overview.generated_at.tzinfo == UTC


@pytest.mark.asyncio
async def test_get_revenue_metrics(analytics_service):
    analytics_service._count_rows = AsyncMock(
        side_effect=[2, 2, 3, 1, 0, 0, 1, 0]
    )
    analytics_service._sum_column = AsyncMock(side_effect=[99900, 49900])
    analytics_service._revenue_by_plan = AsyncMock(return_value=(("pro", 99900),))
    analytics_service._group_count = AsyncMock(return_value=(("pro", 2),))

    metrics = await analytics_service.get_revenue_metrics()

    assert metrics.total_revenue_paise == 99900
    assert metrics.revenue_this_period_paise == 49900
    assert metrics.conversion_rate == pytest.approx(2 / 3)
    assert metrics.average_order_value_paise == 49950
    assert metrics.revenue_by_plan == (("pro", 99900),)


@pytest.mark.asyncio
async def test_get_user_metrics(analytics_service):
    analytics_service._count_rows = AsyncMock(side_effect=[10, 8, 7, 20, 2, 3, 1])
    analytics_service._group_count = AsyncMock(
        side_effect=[(("user", 9), ("admin", 1)), (("free", 8),)]
    )
    analytics_service._quota_usage_by_metric = AsyncMock(return_value=(("reports", 5),))

    metrics = await analytics_service.get_user_metrics()

    assert metrics.total_users == 10
    assert metrics.average_clients_per_user == 2.0
    assert metrics.quota_usage_by_metric == (("reports", 5),)


@pytest.mark.asyncio
async def test_get_report_metrics(analytics_service):
    analytics_service._count_rows = AsyncMock(side_effect=[5, 2, 3])
    analytics_service._count_distinct = AsyncMock(side_effect=[2, 4])
    analytics_service._group_count = AsyncMock(
        side_effect=[(("1.0", 5),), (("completed", 3),)]
    )

    metrics = await analytics_service.get_report_metrics()

    assert metrics.total_reports == 5
    assert metrics.average_reports_per_owner == 2.5
    assert metrics.distinct_clients_with_reports == 4


@pytest.mark.asyncio
async def test_get_chat_metrics(analytics_service):
    analytics_service._count_rows = AsyncMock(side_effect=[30, 10, 25, 3, 2, 20])
    analytics_service._sum_column = AsyncMock(side_effect=[300, 100, 200])
    analytics_service._group_count = AsyncMock(
        side_effect=[(("kundali", 30),), (("answered", 25),), (("gemini", 20),)]
    )
    analytics_service._quota_total_for_metric = AsyncMock(return_value=10)

    metrics = await analytics_service.get_chat_metrics()

    assert metrics.total_queries == 30
    assert metrics.total_tokens == 300
    assert metrics.average_tokens_per_query == 15.0
    assert metrics.quota_consumed_this_period == 10


@pytest.mark.asyncio
async def test_get_system_metrics(analytics_service):
    analytics_service._count_rows = AsyncMock(side_effect=[30, 3, 5, 1, 0, 2, 2, 3])

    metrics = await analytics_service.get_system_metrics()

    assert metrics.active_sessions == 5
    assert metrics.chat_error_rate == 0.1


@pytest.mark.asyncio
async def test_get_ai_metrics(analytics_service):
    analytics_service._count_rows = AsyncMock(side_effect=[25, 30, 3, 10, 5])
    analytics_service._sum_column = AsyncMock(side_effect=[100, 200, 300])
    analytics_service._group_count = AsyncMock(
        side_effect=[(("gemini", 20),), (("kundali", 30),)]
    )

    metrics = await analytics_service.get_ai_metrics()

    assert metrics.successful_invocations == 25
    assert metrics.total_tokens == 300
    assert metrics.average_tokens_per_success == 12.0
    assert metrics.invocations_without_token_data == 5


@pytest.mark.asyncio
async def test_get_analytics_response(analytics_service):
    timestamp = datetime(2026, 6, 15, tzinfo=UTC)
    analytics_service.get_dashboard_overview = AsyncMock(
        return_value=MagicMock(generated_at=timestamp)
    )
    analytics_service.get_revenue_metrics = AsyncMock(return_value=MagicMock())
    analytics_service.get_user_metrics = AsyncMock(return_value=MagicMock())
    analytics_service.get_report_metrics = AsyncMock(return_value=MagicMock())
    analytics_service.get_chat_metrics = AsyncMock(return_value=MagicMock())
    analytics_service.get_system_metrics = AsyncMock(return_value=MagicMock())
    analytics_service.get_ai_metrics = AsyncMock(return_value=MagicMock())

    response = await analytics_service.get_analytics_response()

    assert response.overview.generated_at == timestamp
    analytics_service.get_dashboard_overview.assert_awaited_once()
    analytics_service.get_ai_metrics.assert_awaited_once()


@pytest.mark.asyncio
async def test_empty_database_defaults_via_execute(analytics_service, mock_session):
    mock_session.execute.return_value = _scalar(0)
    overview = await analytics_service.get_dashboard_overview()
    assert overview.total_users == 0
    assert overview.total_revenue_paise == 0
