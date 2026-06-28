"""Billing persistence layer."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import (
    OrderStatus,
    PaymentStatus,
    SubscriptionPlan,
    SubscriptionStatus,
    UsageMetric,
)
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.models.subscription import Subscription
from backend.app.models.usage_quota import UsageQuota


class SubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        plan: SubscriptionPlan,
        current_period_start: datetime,
        current_period_end: datetime,
        status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
        razorpay_subscription_id: str | None = None,
    ) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            status=status,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            razorpay_subscription_id=razorpay_subscription_id,
        )
        self._session.add(subscription)
        await self._session.flush()
        await self._session.refresh(subscription)
        return subscription

    async def get_active_for_user(self, user_id: uuid.UUID) -> Subscription | None:
        result = await self._session.execute(
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
            .order_by(Subscription.created_at.desc())
        )
        return result.scalars().first()

    async def list_all(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Subscription], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size

        total = int((await self._session.execute(select(func.count()).select_from(Subscription))).scalar_one())
        result = await self._session.execute(
            select(Subscription).order_by(Subscription.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        result = await self._session.execute(select(Subscription).where(Subscription.id == subscription_id))
        return result.scalar_one_or_none()


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        plan: SubscriptionPlan,
        amount_paise: int,
        currency: str,
        razorpay_order_id: str,
        receipt: str,
    ) -> Order:
        order = Order(
            user_id=user_id,
            plan=plan,
            amount_paise=amount_paise,
            currency=currency,
            razorpay_order_id=razorpay_order_id,
            receipt=receipt,
            status=OrderStatus.CREATED,
        )
        self._session.add(order)
        await self._session.flush()
        await self._session.refresh(order)
        return order

    async def get_by_razorpay_order_id(self, razorpay_order_id: str) -> Order | None:
        result = await self._session.execute(
            select(Order).where(Order.razorpay_order_id == razorpay_order_id)
        )
        return result.scalar_one_or_none()

    async def mark_paid(self, order: Order) -> None:
        order.status = OrderStatus.PAID
        await self._session.flush()


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        order_id: uuid.UUID | None,
        subscription_id: uuid.UUID | None,
        amount_paise: int,
        currency: str,
        razorpay_payment_id: str,
        razorpay_order_id: str,
        status: PaymentStatus,
        method: str | None = None,
        paid_at: datetime | None = None,
    ) -> Payment:
        payment = Payment(
            user_id=user_id,
            order_id=order_id,
            subscription_id=subscription_id,
            amount_paise=amount_paise,
            currency=currency,
            status=status,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            method=method,
            paid_at=paid_at,
        )
        self._session.add(payment)
        await self._session.flush()
        await self._session.refresh(payment)
        return payment

    async def get_by_razorpay_payment_id(self, razorpay_payment_id: str) -> Payment | None:
        result = await self._session.execute(
            select(Payment).where(Payment.razorpay_payment_id == razorpay_payment_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Payment], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size

        filters = [Payment.user_id == user_id]
        total = int(
            (await self._session.execute(select(func.count()).select_from(Payment).where(*filters))).scalar_one()
        )
        result = await self._session.execute(
            select(Payment)
            .where(*filters)
            .order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def list_all(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Payment], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size

        total = int((await self._session.execute(select(func.count()).select_from(Payment))).scalar_one())
        result = await self._session.execute(
            select(Payment).order_by(Payment.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total


class UsageQuotaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create(
        self,
        *,
        user_id: uuid.UUID,
        metric: UsageMetric,
        period_start: date,
    ) -> UsageQuota:
        result = await self._session.execute(
            select(UsageQuota).where(
                UsageQuota.user_id == user_id,
                UsageQuota.metric == metric,
                UsageQuota.period_start == period_start,
            )
        )
        quota = result.scalar_one_or_none()
        if quota is not None:
            return quota

        quota = UsageQuota(user_id=user_id, metric=metric, period_start=period_start, used_count=0)
        self._session.add(quota)
        await self._session.flush()
        await self._session.refresh(quota)
        return quota

    async def increment(self, quota: UsageQuota, amount: int = 1) -> UsageQuota:
        quota.used_count += amount
        await self._session.flush()
        return quota

    async def list_for_user_period(
        self,
        user_id: uuid.UUID,
        period_start: date,
    ) -> list[UsageQuota]:
        result = await self._session.execute(
            select(UsageQuota).where(
                UsageQuota.user_id == user_id,
                UsageQuota.period_start == period_start,
            )
        )
        return list(result.scalars().all())

    async def reset_period(self, user_id: uuid.UUID, old_period: date, new_period: date) -> None:
        """Lazy monthly reset: create fresh counters for the new period."""
        for metric in UsageMetric:
            await self.get_or_create(user_id=user_id, metric=metric, period_start=new_period)
