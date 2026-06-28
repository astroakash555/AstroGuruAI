"""Tests for analytics serializers."""

from __future__ import annotations

from datetime import UTC, date, datetime

from backend.app.services.analytics.models import (
    AIMetrics,
    AnalyticsResponse,
    ChatMetrics,
    DashboardOverview,
    ReportMetrics,
    RevenueMetrics,
    SystemMetrics,
    UserMetrics,
)
from backend.app.services.analytics.serializers import (
    ai_metrics_to_dict,
    analytics_response_to_dict,
    chat_metrics_to_dict,
    dashboard_overview_to_dict,
    report_metrics_to_dict,
    revenue_metrics_to_dict,
    system_metrics_to_dict,
    user_metrics_to_dict,
)


def _timestamp() -> datetime:
    return datetime(2026, 6, 15, 12, 0, tzinfo=UTC)


def test_dashboard_overview_to_dict():
    overview = DashboardOverview(
        total_users=10,
        active_users=8,
        verified_users=7,
        total_clients=20,
        active_clients=18,
        total_reports=5,
        total_chat_queries=30,
        total_revenue_paise=99900,
        active_subscriptions=4,
        captured_payments=2,
        generated_at=_timestamp(),
    )
    payload = dashboard_overview_to_dict(overview)
    assert payload["total_users"] == 10
    assert payload["generated_at"] == _timestamp().isoformat()


def test_revenue_metrics_to_dict():
    metrics = RevenueMetrics(
        total_revenue_paise=99900,
        revenue_this_period_paise=49900,
        captured_payments=2,
        failed_payments=1,
        pending_payments=0,
        refunded_payments=0,
        total_orders=3,
        paid_orders=2,
        failed_orders=1,
        pending_orders=0,
        conversion_rate=0.6666666666666666,
        average_order_value_paise=49950,
        revenue_by_plan=(("pro", 99900),),
        subscriptions_by_plan=(("pro", 2),),
        period_start=date(2026, 6, 1),
        generated_at=_timestamp(),
    )
    payload = revenue_metrics_to_dict(metrics)
    assert payload["revenue_by_plan"] == [{"plan": "pro", "amount_paise": 99900}]
    assert payload["subscriptions_by_plan"] == [{"label": "pro", "count": 2}]


def test_user_metrics_to_dict():
    metrics = UserMetrics(
        total_users=10,
        active_users=8,
        verified_users=7,
        inactive_users=2,
        unverified_users=3,
        new_users_this_period=1,
        users_by_role=(("user", 9), ("admin", 1)),
        active_subscriptions_by_plan=(("free", 8),),
        total_clients=20,
        average_clients_per_user=2.0,
        quota_usage_by_metric=(("reports", 5),),
        period_start=date(2026, 6, 1),
        generated_at=_timestamp(),
    )
    payload = user_metrics_to_dict(metrics)
    assert payload["average_clients_per_user"] == 2.0


def test_report_metrics_to_dict():
    metrics = ReportMetrics(
        total_reports=5,
        reports_this_period=2,
        reports_with_pdf=3,
        distinct_clients_with_reports=4,
        distinct_owners=2,
        average_reports_per_owner=2.5,
        reports_by_version=(("1.0", 5),),
        pdf_by_status=(("completed", 3),),
        period_start=date(2026, 6, 1),
        generated_at=_timestamp(),
    )
    payload = report_metrics_to_dict(metrics)
    assert payload["reports_by_version"] == [{"label": "1.0", "count": 5}]


def test_chat_metrics_to_dict():
    metrics = ChatMetrics(
        total_queries=30,
        queries_this_period=10,
        answered_queries=25,
        failed_queries=3,
        processing_queries=2,
        queries_by_type=(("kundali", 30),),
        queries_by_status=(("answered", 25),),
        total_prompt_tokens=100,
        total_completion_tokens=200,
        total_tokens=300,
        average_tokens_per_query=12.0,
        queries_by_model=(("gemini", 20),),
        quota_consumed_this_period=10,
        period_start=date(2026, 6, 1),
        generated_at=_timestamp(),
    )
    payload = chat_metrics_to_dict(metrics)
    assert payload["total_tokens"] == 300


def test_system_metrics_to_dict():
    metrics = SystemMetrics(
        active_sessions=5,
        failed_orders=1,
        expired_orders=0,
        failed_pdf_generations=2,
        inactive_users=2,
        unverified_users=3,
        chat_error_rate=0.1,
        generated_at=_timestamp(),
    )
    payload = system_metrics_to_dict(metrics)
    assert payload["chat_error_rate"] == 0.1


def test_ai_metrics_to_dict():
    metrics = AIMetrics(
        total_invocations=30,
        successful_invocations=25,
        failed_invocations=3,
        invocations_this_period=10,
        total_prompt_tokens=100,
        total_completion_tokens=200,
        total_tokens=300,
        average_tokens_per_success=12.0,
        invocations_by_model=(("gemini", 20),),
        invocations_by_query_type=(("kundali", 30),),
        invocations_without_token_data=5,
        period_start=date(2026, 6, 1),
        generated_at=_timestamp(),
    )
    payload = ai_metrics_to_dict(metrics)
    assert payload["invocations_without_token_data"] == 5


def test_analytics_response_to_dict():
    timestamp = _timestamp()
    overview = DashboardOverview(
        total_users=1,
        active_users=1,
        verified_users=1,
        total_clients=1,
        active_clients=1,
        total_reports=1,
        total_chat_queries=1,
        total_revenue_paise=0,
        active_subscriptions=1,
        captured_payments=0,
        generated_at=timestamp,
    )
    response = AnalyticsResponse(
        overview=overview,
        revenue=RevenueMetrics(
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
            period_start=date(2026, 6, 1),
            generated_at=timestamp,
        ),
        users=UserMetrics(
            total_users=1,
            active_users=1,
            verified_users=1,
            inactive_users=0,
            unverified_users=0,
            new_users_this_period=0,
            users_by_role=(),
            active_subscriptions_by_plan=(),
            total_clients=1,
            average_clients_per_user=1.0,
            quota_usage_by_metric=(),
            period_start=date(2026, 6, 1),
            generated_at=timestamp,
        ),
        reports=ReportMetrics(
            total_reports=1,
            reports_this_period=0,
            reports_with_pdf=0,
            distinct_clients_with_reports=1,
            distinct_owners=1,
            average_reports_per_owner=1.0,
            reports_by_version=(),
            pdf_by_status=(),
            period_start=date(2026, 6, 1),
            generated_at=timestamp,
        ),
        chat=ChatMetrics(
            total_queries=1,
            queries_this_period=0,
            answered_queries=1,
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
            period_start=date(2026, 6, 1),
            generated_at=timestamp,
        ),
        system=SystemMetrics(
            active_sessions=0,
            failed_orders=0,
            expired_orders=0,
            failed_pdf_generations=0,
            inactive_users=0,
            unverified_users=0,
            chat_error_rate=0.0,
            generated_at=timestamp,
        ),
        ai=AIMetrics(
            total_invocations=1,
            successful_invocations=1,
            failed_invocations=0,
            invocations_this_period=0,
            total_prompt_tokens=0,
            total_completion_tokens=0,
            total_tokens=0,
            average_tokens_per_success=0.0,
            invocations_by_model=(),
            invocations_by_query_type=(),
            invocations_without_token_data=1,
            period_start=date(2026, 6, 1),
            generated_at=timestamp,
        ),
        generated_at=timestamp,
    )
    payload = analytics_response_to_dict(response)
    assert set(payload.keys()) == {"overview", "revenue", "users", "reports", "chat", "system", "ai", "generated_at"}
