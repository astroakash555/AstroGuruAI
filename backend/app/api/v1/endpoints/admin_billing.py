"""Admin billing management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.api.deps import get_billing_service, require_roles
from backend.app.billing.service import BillingService
from backend.app.core.exceptions import ValidationError
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.billing import (
    AdminActivateSubscriptionRequest,
    AdminSubscriptionItem,
    PaginatedPaymentsResponse,
    PaginatedSubscriptionsResponse,
    PaymentHistoryItem,
)

router = APIRouter(prefix="/admin/billing", tags=["admin-billing"])


@router.get(
    "/subscriptions",
    response_model=PaginatedSubscriptionsResponse,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_list_subscriptions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: BillingService = Depends(get_billing_service),
) -> PaginatedSubscriptionsResponse:
    result = await service.admin_list_subscriptions(page=page, page_size=page_size)
    return PaginatedSubscriptionsResponse(**result)


@router.get(
    "/payments",
    response_model=PaginatedPaymentsResponse,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_list_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: BillingService = Depends(get_billing_service),
) -> PaginatedPaymentsResponse:
    result = await service.admin_list_payments(page=page, page_size=page_size)
    return PaginatedPaymentsResponse(**result)


@router.post(
    "/subscriptions/activate",
    response_model=AdminSubscriptionItem,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def admin_activate_subscription(
    payload: AdminActivateSubscriptionRequest,
    _admin: User = Depends(require_roles(UserRole.ADMIN)),
    service: BillingService = Depends(get_billing_service),
) -> AdminSubscriptionItem:
    try:
        result = await service.admin_activate_subscription(user_id=payload.user_id, plan=payload.plan)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    return AdminSubscriptionItem(**result)
