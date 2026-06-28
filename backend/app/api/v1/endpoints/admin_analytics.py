"""Admin analytics endpoints."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from backend.app.api.deps import get_analytics_service, require_roles
from backend.app.models.enums import UserRole
from backend.app.services.analytics.analytics_service import AnalyticsService
from backend.app.services.analytics.serializers import (
    ai_metrics_to_dict,
    chat_metrics_to_dict,
    dashboard_overview_to_dict,
    report_metrics_to_dict,
    revenue_metrics_to_dict,
    system_metrics_to_dict,
    user_metrics_to_dict,
)

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])

T = TypeVar("T")


async def _serialize_metrics(
    loader: Callable[[], Awaitable[T]],
    serializer: Callable[[T], dict[str, Any]],
) -> dict[str, Any]:
    """Load analytics metrics and serialize them for JSON responses."""
    try:
        return serializer(await loader())
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load analytics data.",
        ) from exc


@router.get(
    "/overview",
    summary="Get platform analytics overview",
    description="Return high-level counts for users, clients, reports, chat, revenue, and subscriptions.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_analytics_overview(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    return await _serialize_metrics(service.get_dashboard_overview, dashboard_overview_to_dict)


@router.get(
    "/users",
    summary="Get user analytics metrics",
    description="Return user growth, verification, subscription, and quota utilization metrics.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_analytics_users(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    return await _serialize_metrics(service.get_user_metrics, user_metrics_to_dict)


@router.get(
    "/revenue",
    summary="Get revenue analytics metrics",
    description="Return payment, order, and subscription revenue aggregates.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_analytics_revenue(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    return await _serialize_metrics(service.get_revenue_metrics, revenue_metrics_to_dict)


@router.get(
    "/reports",
    summary="Get report analytics metrics",
    description="Return report generation volume, PDF coverage, and version breakdowns.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_analytics_reports(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    return await _serialize_metrics(service.get_report_metrics, report_metrics_to_dict)


@router.get(
    "/chat",
    summary="Get chat analytics metrics",
    description="Return chat query volume, status breakdowns, token usage, and quota consumption.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_analytics_chat(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    return await _serialize_metrics(service.get_chat_metrics, chat_metrics_to_dict)


@router.get(
    "/system",
    summary="Get system analytics metrics",
    description="Return operational health indicators such as active sessions and failure rates.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_analytics_system(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    return await _serialize_metrics(service.get_system_metrics, system_metrics_to_dict)


@router.get(
    "/ai",
    summary="Get AI analytics metrics",
    description="Return AI invocation counts, token consumption, and model/query-type breakdowns.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_analytics_ai(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    return await _serialize_metrics(service.get_ai_metrics, ai_metrics_to_dict)
