"""Pydantic schemas for billing APIs."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import Field

from backend.app.models.enums import SubscriptionPlan
from backend.app.schemas.common import BaseSchema


class PlanResponse(BaseSchema):
    plan: SubscriptionPlan
    name: str
    description: str
    price_paise: int
    currency: str
    features: list[str]
    limits: dict[str, int | None]


class UsageMetricResponse(BaseSchema):
    metric: str
    used: int
    limit: int | None
    remaining: int | None


class UsageSummaryResponse(BaseSchema):
    plan: SubscriptionPlan
    period_start: str
    metrics: list[UsageMetricResponse]


class SubscriptionResponse(BaseSchema):
    subscription_id: uuid.UUID
    plan: SubscriptionPlan
    status: str
    current_period_start: datetime
    current_period_end: datetime
    usage: UsageSummaryResponse


class CreateOrderRequest(BaseSchema):
    plan: SubscriptionPlan


class CreateOrderResponse(BaseSchema):
    order_id: uuid.UUID
    razorpay_order_id: str
    amount_paise: int
    currency: str
    key_id: str
    plan: SubscriptionPlan
    receipt: str


class VerifyPaymentRequest(BaseSchema):
    razorpay_order_id: str = Field(..., min_length=5)
    razorpay_payment_id: str = Field(..., min_length=5)
    razorpay_signature: str = Field(..., min_length=5)


class VerifyPaymentResponse(BaseSchema):
    status: str
    payment_id: uuid.UUID | None = None
    subscription_id: uuid.UUID | None = None
    plan: SubscriptionPlan | None = None


class PaymentHistoryItem(BaseSchema):
    payment_id: uuid.UUID
    user_id: uuid.UUID
    order_id: uuid.UUID | None
    subscription_id: uuid.UUID | None
    amount_paise: int
    currency: str
    status: str
    razorpay_payment_id: str
    razorpay_order_id: str
    method: str | None
    paid_at: datetime | None
    created_at: datetime


class PaginatedPaymentsResponse(BaseSchema):
    items: list[PaymentHistoryItem]
    total: int
    page: int
    page_size: int
    pages: int


class AdminSubscriptionItem(BaseSchema):
    subscription_id: uuid.UUID
    user_id: uuid.UUID
    plan: SubscriptionPlan
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancelled_at: datetime | None
    created_at: datetime


class PaginatedSubscriptionsResponse(BaseSchema):
    items: list[AdminSubscriptionItem]
    total: int
    page: int
    page_size: int
    pages: int


class AdminActivateSubscriptionRequest(BaseSchema):
    user_id: uuid.UUID
    plan: SubscriptionPlan


class MessageResponse(BaseSchema):
    message: str
