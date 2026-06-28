"""Billing and subscription API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status

from backend.app.api.deps import get_billing_service, get_current_user
from backend.app.billing.service import BillingService
from backend.app.core.exceptions import (
    ConflictError,
    NotFoundError,
    QuotaExceededError,
    ValidationError,
    conflict_error,
    not_found_error,
    quota_exceeded_error,
)
from backend.app.models.user import User
from backend.app.schemas.billing import (
    AdminActivateSubscriptionRequest,
    CreateOrderRequest,
    CreateOrderResponse,
    MessageResponse,
    PaginatedPaymentsResponse,
    PaginatedSubscriptionsResponse,
    PlanResponse,
    SubscriptionResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(service: BillingService = Depends(get_billing_service)) -> list[PlanResponse]:
    return [PlanResponse(**plan) for plan in service.list_plans()]


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> SubscriptionResponse:
    try:
        result = await service.get_subscription(current_user.id)
    except NotFoundError as exc:
        raise not_found_error("Subscription", str(current_user.id)) from exc
    return SubscriptionResponse(**result)


@router.post("/orders", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> CreateOrderResponse:
    try:
        result = await service.create_checkout_order(current_user, payload.plan)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    return CreateOrderResponse(**result)


@router.post("/verify-payment", response_model=VerifyPaymentResponse)
async def verify_payment(
    payload: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> VerifyPaymentResponse:
    try:
        result = await service.verify_payment(
            user=current_user,
            razorpay_order_id=payload.razorpay_order_id,
            razorpay_payment_id=payload.razorpay_payment_id,
            razorpay_signature=payload.razorpay_signature,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except NotFoundError as exc:
        raise not_found_error("Order", payload.razorpay_order_id) from exc
    except ConflictError as exc:
        raise conflict_error(exc.message) from exc
    return VerifyPaymentResponse(**result)


@router.get("/payments", response_model=PaginatedPaymentsResponse)
async def list_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> PaginatedPaymentsResponse:
    result = await service.list_payment_history(current_user.id, page=page, page_size=page_size)
    return PaginatedPaymentsResponse(**result)


@router.post("/subscription/cancel", response_model=MessageResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
) -> MessageResponse:
    try:
        await service.cancel_subscription(current_user.id)
    except NotFoundError as exc:
        raise not_found_error("Subscription", str(current_user.id)) from exc
    return MessageResponse(message="Subscription cancelled. You are now on the Free plan.")


@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    service: BillingService = Depends(get_billing_service),
    x_razorpay_signature: str | None = Header(default=None),
) -> dict[str, str]:
    payload = await request.body()
    signature = x_razorpay_signature or ""
    try:
        return await service.handle_webhook(payload, signature)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
