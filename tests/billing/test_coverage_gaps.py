"""Targeted tests for remaining billing coverage gaps."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.billing.repositories import OrderRepository, PaymentRepository, SubscriptionRepository, UsageQuotaRepository
from backend.app.billing.service import BillingService
from backend.app.billing.usage import UsageService, next_period_end
from backend.app.core.exceptions import ConflictError, NotFoundError
from backend.app.models.enums import OrderStatus, PaymentStatus, SubscriptionPlan, SubscriptionStatus, UsageMetric
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.models.subscription import Subscription
from backend.app.models.usage_quota import UsageQuota


@pytest.mark.asyncio
async def test_subscription_repository_create(mock_session):
    repo = SubscriptionRepository(mock_session)
    user_id = uuid.uuid4()
    now = datetime.now(UTC)
    subscription = await repo.create(
        user_id=user_id,
        plan=SubscriptionPlan.FREE,
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()
    assert subscription.plan == SubscriptionPlan.FREE


@pytest.mark.asyncio
async def test_order_repository_mark_paid(mock_session):
    repo = OrderRepository(mock_session)
    order = Order(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        plan=SubscriptionPlan.PRO,
        amount_paise=99900,
        currency="INR",
        status=OrderStatus.CREATED,
        razorpay_order_id="order_1",
        receipt="rcpt",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    await repo.mark_paid(order)
    assert order.status == OrderStatus.PAID
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_payment_repository_list_for_user(mock_session):
    repo = PaymentRepository(mock_session)
    user_id = uuid.uuid4()
    payment = Payment(
        id=uuid.uuid4(),
        user_id=user_id,
        order_id=None,
        subscription_id=None,
        amount_paise=99900,
        currency="INR",
        status=PaymentStatus.CAPTURED,
        razorpay_payment_id="pay_1",
        razorpay_order_id="order_1",
        method="upi",
        paid_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [payment]
    mock_session.execute = AsyncMock(side_effect=[count_result, list_result])

    payments, total = await repo.list_for_user(user_id)
    assert total == 1
    assert payments[0].razorpay_payment_id == "pay_1"


@pytest.mark.asyncio
async def test_usage_quota_get_or_create_returns_existing(mock_session):
    repo = UsageQuotaRepository(mock_session)
    existing = UsageQuota(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        metric=UsageMetric.REPORTS,
        period_start=date(2026, 6, 1),
        used_count=3,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing
    mock_session.execute.return_value = result

    quota = await repo.get_or_create(
        user_id=existing.user_id,
        metric=UsageMetric.REPORTS,
        period_start=date(2026, 6, 1),
    )
    assert quota is existing
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_usage_quota_list_for_user_period(mock_session):
    repo = UsageQuotaRepository(mock_session)
    quota = UsageQuota(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        metric=UsageMetric.CHAT_MESSAGES,
        period_start=date(2026, 6, 1),
        used_count=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    result = MagicMock()
    result.scalars.return_value.all.return_value = [quota]
    mock_session.execute.return_value = result

    items = await repo.list_for_user_period(quota.user_id, date(2026, 6, 1))
    assert len(items) == 1


def test_next_period_end_december():
    moment = datetime(2026, 12, 15, tzinfo=UTC)
    assert next_period_end(moment) == datetime(2027, 1, 1, tzinfo=UTC)


@pytest.mark.asyncio
async def test_get_active_plan_fallback_free(mock_session, mock_subscriptions):
    mock_subscriptions.get_active_for_user.return_value = None
    mock_subscriptions.create = AsyncMock()
    service = UsageService(mock_session, subscriptions=mock_subscriptions, quotas=AsyncMock())
    service.ensure_free_subscription = AsyncMock()
    plan = await service.get_active_plan(uuid.uuid4())
    assert plan == SubscriptionPlan.FREE


@pytest.mark.asyncio
async def test_initialize_new_user(billing_service, mock_session):
    billing_service._usage.ensure_free_subscription = AsyncMock()
    await billing_service.initialize_new_user(uuid.uuid4())
    billing_service._usage.ensure_free_subscription.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_payment_already_processed_order(billing_service, sample_user, mock_orders, mock_payments):
    order = Order(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        plan=SubscriptionPlan.PRO,
        amount_paise=99900,
        currency="INR",
        status=OrderStatus.PAID,
        razorpay_order_id="order_paid",
        receipt="rcpt",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    existing = Payment(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        order_id=order.id,
        subscription_id=uuid.uuid4(),
        amount_paise=99900,
        currency="INR",
        status=PaymentStatus.CAPTURED,
        razorpay_payment_id="pay_existing",
        razorpay_order_id="order_paid",
        method=None,
        paid_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_orders.get_by_razorpay_order_id.return_value = order
    mock_payments.get_by_razorpay_payment_id.return_value = existing

    result = await billing_service.verify_payment(
        user=sample_user,
        razorpay_order_id="order_paid",
        razorpay_payment_id="pay_existing",
        razorpay_signature="valid_signature",
    )
    assert result["status"] == "already_processed"


@pytest.mark.asyncio
async def test_verify_payment_duplicate_conflict(billing_service, sample_user, mock_orders, mock_payments):
    order = Order(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        plan=SubscriptionPlan.PRO,
        amount_paise=99900,
        currency="INR",
        status=OrderStatus.CREATED,
        razorpay_order_id="order_dup",
        receipt="rcpt",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    existing = Payment(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        order_id=order.id,
        subscription_id=uuid.uuid4(),
        amount_paise=99900,
        currency="INR",
        status=PaymentStatus.CAPTURED,
        razorpay_payment_id="pay_dup",
        razorpay_order_id="order_other",
        method=None,
        paid_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_orders.get_by_razorpay_order_id.return_value = order

    async def _lookup(payment_id: str):
        if payment_id == "pay_dup":
            return existing
        return None

    mock_payments.get_by_razorpay_payment_id.side_effect = _lookup

    with pytest.raises(ConflictError):
        await billing_service.verify_payment(
            user=sample_user,
            razorpay_order_id="order_dup",
            razorpay_payment_id="pay_dup",
            razorpay_signature="valid_signature",
        )


@pytest.mark.asyncio
async def test_cancel_subscription_not_found(billing_service, sample_user, mock_subscriptions):
    mock_subscriptions.get_active_for_user.return_value = None
    with pytest.raises(NotFoundError):
        await billing_service.cancel_subscription(sample_user.id)
