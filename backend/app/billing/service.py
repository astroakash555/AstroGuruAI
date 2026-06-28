"""Billing and subscription orchestration."""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.billing.plans import PLAN_DEFINITIONS, get_plan_definition
from backend.app.billing.razorpay_client import PaymentGateway, build_payment_gateway
from backend.app.billing.repositories import OrderRepository, PaymentRepository, SubscriptionRepository
from backend.app.billing.usage import UsageService, next_period_end
from backend.app.core.config import Settings
from backend.app.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.app.models.enums import OrderStatus, PaymentStatus, SubscriptionPlan, SubscriptionStatus
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.models.subscription import Subscription
from backend.app.models.user import User


class BillingService:
    """Manage plans, checkout, payments, and subscriptions."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        settings: Settings,
        gateway: PaymentGateway | None = None,
        subscriptions: SubscriptionRepository | None = None,
        orders: OrderRepository | None = None,
        payments: PaymentRepository | None = None,
        usage: UsageService | None = None,
    ) -> None:
        self._session = session
        self._settings = settings
        self._gateway = gateway or build_payment_gateway(settings)
        self._subscriptions = subscriptions or SubscriptionRepository(session)
        self._orders = orders or OrderRepository(session)
        self._payments = payments or PaymentRepository(session)
        self._usage = usage or UsageService(session, subscriptions=self._subscriptions)

    async def initialize_new_user(self, user_id: uuid.UUID) -> None:
        await self._usage.ensure_free_subscription(user_id)
        await self._session.commit()

    def list_plans(self) -> list[dict[str, Any]]:
        return [
            {
                "plan": plan_def.plan.value,
                "name": plan_def.name,
                "description": plan_def.description,
                "price_paise": plan_def.price_paise,
                "currency": plan_def.currency,
                "features": list(plan_def.features),
                "limits": {
                    metric.value: (None if limit is None else limit)
                    for metric, limit in plan_def.limits.items()
                },
            }
            for plan_def in PLAN_DEFINITIONS.values()
        ]

    async def get_subscription(self, user_id: uuid.UUID) -> dict[str, Any]:
        await self._usage.ensure_free_subscription(user_id)
        subscription = await self._subscriptions.get_active_for_user(user_id)
        if subscription is None:
            raise NotFoundError("Active subscription not found.")
        usage = await self._usage.get_usage_summary(user_id)
        return {
            "subscription_id": str(subscription.id),
            "plan": subscription.plan.value,
            "status": subscription.status.value,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "usage": usage,
        }

    async def create_checkout_order(self, user: User, plan: SubscriptionPlan) -> dict[str, Any]:
        if plan == SubscriptionPlan.FREE:
            raise ValidationError("The Free plan does not require payment.")

        plan_def = get_plan_definition(plan)
        await self._usage.ensure_free_subscription(user.id)

        receipt = f"rcpt_{user.id.hex[:8]}_{plan.value}_{uuid.uuid4().hex[:8]}"
        gateway_order = await self._gateway.create_order(
            amount_paise=plan_def.price_paise,
            currency=plan_def.currency,
            receipt=receipt,
            notes={"user_id": str(user.id), "plan": plan.value},
        )

        order = await self._orders.create(
            user_id=user.id,
            plan=plan,
            amount_paise=gateway_order.amount_paise,
            currency=gateway_order.currency,
            razorpay_order_id=gateway_order.order_id,
            receipt=gateway_order.receipt,
        )
        await self._session.commit()

        return {
            "order_id": str(order.id),
            "razorpay_order_id": gateway_order.order_id,
            "amount_paise": gateway_order.amount_paise,
            "currency": gateway_order.currency,
            "key_id": gateway_order.key_id,
            "plan": plan.value,
            "receipt": gateway_order.receipt,
        }

    async def verify_payment(
        self,
        *,
        user: User,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> dict[str, Any]:
        if not self._gateway.verify_payment_signature(
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
        ):
            raise ValidationError("Invalid payment signature.")

        order = await self._orders.get_by_razorpay_order_id(razorpay_order_id)
        if order is None or order.user_id != user.id:
            raise NotFoundError("Order not found.")
        if order.status == OrderStatus.PAID:
            existing = await self._payments.get_by_razorpay_payment_id(razorpay_payment_id)
            if existing is not None:
                return {"status": "already_processed", "payment_id": str(existing.id)}

        existing_payment = await self._payments.get_by_razorpay_payment_id(razorpay_payment_id)
        if existing_payment is not None:
            raise ConflictError("Payment has already been processed.")

        subscription = await self._activate_plan(user_id=user.id, plan=order.plan)
        paid_at = datetime.now(UTC)
        payment = await self._payments.create(
            user_id=user.id,
            order_id=order.id,
            subscription_id=subscription.id,
            amount_paise=order.amount_paise,
            currency=order.currency,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            status=PaymentStatus.CAPTURED,
            paid_at=paid_at,
        )
        await self._orders.mark_paid(order)
        await self._session.commit()

        return {
            "status": "success",
            "payment_id": str(payment.id),
            "subscription_id": str(subscription.id),
            "plan": subscription.plan.value,
        }

    async def handle_webhook(self, payload: bytes, signature: str) -> dict[str, str]:
        if not self._gateway.verify_webhook_signature(payload, signature):
            raise ValidationError("Invalid webhook signature.")

        import json

        event = json.loads(payload.decode("utf-8"))
        event_type = event.get("event", "")
        entity = event.get("payload", {}).get("payment", {}).get("entity", {})

        if event_type == "payment.captured":
            razorpay_payment_id = entity.get("id")
            razorpay_order_id = entity.get("order_id")
            if razorpay_payment_id and razorpay_order_id:
                order = await self._orders.get_by_razorpay_order_id(razorpay_order_id)
                if order and order.status != OrderStatus.PAID:
                    existing = await self._payments.get_by_razorpay_payment_id(razorpay_payment_id)
                    if existing is None:
                        subscription = await self._activate_plan(user_id=order.user_id, plan=order.plan)
                        await self._payments.create(
                            user_id=order.user_id,
                            order_id=order.id,
                            subscription_id=subscription.id,
                            amount_paise=order.amount_paise,
                            currency=order.currency,
                            razorpay_payment_id=razorpay_payment_id,
                            razorpay_order_id=razorpay_order_id,
                            status=PaymentStatus.CAPTURED,
                            method=entity.get("method"),
                            paid_at=datetime.now(UTC),
                        )
                        await self._orders.mark_paid(order)
                        await self._session.commit()

        return {"status": "ok"}

    async def list_payment_history(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        payments, total = await self._payments.list_for_user(user_id, page=page, page_size=page_size)
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        pages = math.ceil(total / page_size) if total else 0
        return {
            "items": [self._payment_to_dict(payment) for payment in payments],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }

    async def admin_list_subscriptions(self, *, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        subscriptions, total = await self._subscriptions.list_all(page=page, page_size=page_size)
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        pages = math.ceil(total / page_size) if total else 0
        return {
            "items": [self._subscription_to_dict(subscription) for subscription in subscriptions],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }

    async def admin_list_payments(self, *, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        payments, total = await self._payments.list_all(page=page, page_size=page_size)
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        pages = math.ceil(total / page_size) if total else 0
        return {
            "items": [self._payment_to_dict(payment) for payment in payments],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }

    async def admin_activate_subscription(
        self,
        *,
        user_id: uuid.UUID,
        plan: SubscriptionPlan,
    ) -> dict[str, Any]:
        subscription = await self._activate_plan(user_id=user_id, plan=plan)
        await self._session.commit()
        return self._subscription_to_dict(subscription)

    async def cancel_subscription(self, user_id: uuid.UUID) -> dict[str, Any]:
        subscription = await self._subscriptions.get_active_for_user(user_id)
        if subscription is None:
            raise NotFoundError("Active subscription not found.")

        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.now(UTC)
        free_subscription = await self._activate_plan(user_id=user_id, plan=SubscriptionPlan.FREE)
        await self._session.commit()
        return self._subscription_to_dict(free_subscription)

    async def _activate_plan(self, *, user_id: uuid.UUID, plan: SubscriptionPlan) -> Subscription:
        current = await self._subscriptions.get_active_for_user(user_id)
        now = datetime.now(UTC)
        period_end = next_period_end(now)

        if current is not None:
            current.status = SubscriptionStatus.CANCELLED
            current.cancelled_at = now

        subscription = await self._subscriptions.create(
            user_id=user_id,
            plan=plan,
            current_period_start=now,
            current_period_end=period_end,
            status=SubscriptionStatus.ACTIVE,
        )
        await self._usage.reset_monthly_quotas(user_id)
        return subscription

    @staticmethod
    def _payment_to_dict(payment: Payment) -> dict[str, Any]:
        return {
            "payment_id": str(payment.id),
            "user_id": str(payment.user_id),
            "order_id": str(payment.order_id) if payment.order_id else None,
            "subscription_id": str(payment.subscription_id) if payment.subscription_id else None,
            "amount_paise": payment.amount_paise,
            "currency": payment.currency,
            "status": payment.status.value,
            "razorpay_payment_id": payment.razorpay_payment_id,
            "razorpay_order_id": payment.razorpay_order_id,
            "method": payment.method,
            "paid_at": payment.paid_at,
            "created_at": payment.created_at,
        }

    @staticmethod
    def _subscription_to_dict(subscription: Subscription) -> dict[str, Any]:
        return {
            "subscription_id": str(subscription.id),
            "user_id": str(subscription.user_id),
            "plan": subscription.plan.value,
            "status": subscription.status.value,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "cancelled_at": subscription.cancelled_at,
            "created_at": subscription.created_at,
        }
