"""JSON serialization helpers for analytics models."""

from __future__ import annotations

from typing import Any

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


def _serialize_breakdown(items: tuple[tuple[str, int], ...]) -> list[dict[str, int | str]]:
    return [{"label": label, "count": count} for label, count in items]


def _serialize_revenue_breakdown(items: tuple[tuple[str, int], ...]) -> list[dict[str, int | str]]:
    return [{"plan": plan, "amount_paise": amount} for plan, amount in items]


def dashboard_overview_to_dict(overview: DashboardOverview) -> dict[str, Any]:
    """Serialize a dashboard overview snapshot."""
    return {
        "total_users": overview.total_users,
        "active_users": overview.active_users,
        "verified_users": overview.verified_users,
        "total_clients": overview.total_clients,
        "active_clients": overview.active_clients,
        "total_reports": overview.total_reports,
        "total_chat_queries": overview.total_chat_queries,
        "total_revenue_paise": overview.total_revenue_paise,
        "active_subscriptions": overview.active_subscriptions,
        "captured_payments": overview.captured_payments,
        "generated_at": overview.generated_at.isoformat(),
    }


def revenue_metrics_to_dict(metrics: RevenueMetrics) -> dict[str, Any]:
    """Serialize revenue metrics."""
    return {
        "total_revenue_paise": metrics.total_revenue_paise,
        "revenue_this_period_paise": metrics.revenue_this_period_paise,
        "captured_payments": metrics.captured_payments,
        "failed_payments": metrics.failed_payments,
        "pending_payments": metrics.pending_payments,
        "refunded_payments": metrics.refunded_payments,
        "total_orders": metrics.total_orders,
        "paid_orders": metrics.paid_orders,
        "failed_orders": metrics.failed_orders,
        "pending_orders": metrics.pending_orders,
        "conversion_rate": metrics.conversion_rate,
        "average_order_value_paise": metrics.average_order_value_paise,
        "revenue_by_plan": _serialize_revenue_breakdown(metrics.revenue_by_plan),
        "subscriptions_by_plan": _serialize_breakdown(metrics.subscriptions_by_plan),
        "period_start": metrics.period_start.isoformat(),
        "generated_at": metrics.generated_at.isoformat(),
    }


def user_metrics_to_dict(metrics: UserMetrics) -> dict[str, Any]:
    """Serialize user metrics."""
    return {
        "total_users": metrics.total_users,
        "active_users": metrics.active_users,
        "verified_users": metrics.verified_users,
        "inactive_users": metrics.inactive_users,
        "unverified_users": metrics.unverified_users,
        "new_users_this_period": metrics.new_users_this_period,
        "users_by_role": _serialize_breakdown(metrics.users_by_role),
        "active_subscriptions_by_plan": _serialize_breakdown(metrics.active_subscriptions_by_plan),
        "total_clients": metrics.total_clients,
        "average_clients_per_user": metrics.average_clients_per_user,
        "quota_usage_by_metric": _serialize_breakdown(metrics.quota_usage_by_metric),
        "period_start": metrics.period_start.isoformat(),
        "generated_at": metrics.generated_at.isoformat(),
    }


def report_metrics_to_dict(metrics: ReportMetrics) -> dict[str, Any]:
    """Serialize report metrics."""
    return {
        "total_reports": metrics.total_reports,
        "reports_this_period": metrics.reports_this_period,
        "reports_with_pdf": metrics.reports_with_pdf,
        "distinct_clients_with_reports": metrics.distinct_clients_with_reports,
        "distinct_owners": metrics.distinct_owners,
        "average_reports_per_owner": metrics.average_reports_per_owner,
        "reports_by_version": _serialize_breakdown(metrics.reports_by_version),
        "pdf_by_status": _serialize_breakdown(metrics.pdf_by_status),
        "period_start": metrics.period_start.isoformat(),
        "generated_at": metrics.generated_at.isoformat(),
    }


def chat_metrics_to_dict(metrics: ChatMetrics) -> dict[str, Any]:
    """Serialize chat metrics."""
    return {
        "total_queries": metrics.total_queries,
        "queries_this_period": metrics.queries_this_period,
        "answered_queries": metrics.answered_queries,
        "failed_queries": metrics.failed_queries,
        "processing_queries": metrics.processing_queries,
        "queries_by_type": _serialize_breakdown(metrics.queries_by_type),
        "queries_by_status": _serialize_breakdown(metrics.queries_by_status),
        "total_prompt_tokens": metrics.total_prompt_tokens,
        "total_completion_tokens": metrics.total_completion_tokens,
        "total_tokens": metrics.total_tokens,
        "average_tokens_per_query": metrics.average_tokens_per_query,
        "queries_by_model": _serialize_breakdown(metrics.queries_by_model),
        "quota_consumed_this_period": metrics.quota_consumed_this_period,
        "period_start": metrics.period_start.isoformat(),
        "generated_at": metrics.generated_at.isoformat(),
    }


def system_metrics_to_dict(metrics: SystemMetrics) -> dict[str, Any]:
    """Serialize system metrics."""
    return {
        "active_sessions": metrics.active_sessions,
        "failed_orders": metrics.failed_orders,
        "expired_orders": metrics.expired_orders,
        "failed_pdf_generations": metrics.failed_pdf_generations,
        "inactive_users": metrics.inactive_users,
        "unverified_users": metrics.unverified_users,
        "chat_error_rate": metrics.chat_error_rate,
        "generated_at": metrics.generated_at.isoformat(),
    }


def ai_metrics_to_dict(metrics: AIMetrics) -> dict[str, Any]:
    """Serialize AI metrics."""
    return {
        "total_invocations": metrics.total_invocations,
        "successful_invocations": metrics.successful_invocations,
        "failed_invocations": metrics.failed_invocations,
        "invocations_this_period": metrics.invocations_this_period,
        "total_prompt_tokens": metrics.total_prompt_tokens,
        "total_completion_tokens": metrics.total_completion_tokens,
        "total_tokens": metrics.total_tokens,
        "average_tokens_per_success": metrics.average_tokens_per_success,
        "invocations_by_model": _serialize_breakdown(metrics.invocations_by_model),
        "invocations_by_query_type": _serialize_breakdown(metrics.invocations_by_query_type),
        "invocations_without_token_data": metrics.invocations_without_token_data,
        "period_start": metrics.period_start.isoformat(),
        "generated_at": metrics.generated_at.isoformat(),
    }


def analytics_response_to_dict(response: AnalyticsResponse) -> dict[str, Any]:
    """Serialize the full analytics response payload."""
    return {
        "overview": dashboard_overview_to_dict(response.overview),
        "revenue": revenue_metrics_to_dict(response.revenue),
        "users": user_metrics_to_dict(response.users),
        "reports": report_metrics_to_dict(response.reports),
        "chat": chat_metrics_to_dict(response.chat),
        "system": system_metrics_to_dict(response.system),
        "ai": ai_metrics_to_dict(response.ai),
        "generated_at": response.generated_at.isoformat(),
    }
