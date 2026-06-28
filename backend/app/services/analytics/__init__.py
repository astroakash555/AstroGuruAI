"""Platform analytics aggregation layer."""

from backend.app.services.analytics.analytics_service import AnalyticsService
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

__all__ = [
    "AIMetrics",
    "AnalyticsResponse",
    "AnalyticsService",
    "ChatMetrics",
    "DashboardOverview",
    "ReportMetrics",
    "RevenueMetrics",
    "SystemMetrics",
    "UserMetrics",
    "ai_metrics_to_dict",
    "analytics_response_to_dict",
    "chat_metrics_to_dict",
    "dashboard_overview_to_dict",
    "report_metrics_to_dict",
    "revenue_metrics_to_dict",
    "system_metrics_to_dict",
    "user_metrics_to_dict",
]
