"""Tests for BillingService."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.billing.usage import next_period_end
from backend.app.core.exceptions import ValidationError
from backend.app.models.enums import OrderStatus, SubscriptionPlan, SubscriptionStatus
from backend.app.models.order import Order
from backend.app.models.subscription import Subscription


@pytest.mark.asyncio
async def test_list_plans(billing_service):
    plans = billing_service.list_plans()
    assert len(plans) == 3
    assert plans[0]["plan"] == "free"


@pytest.mark.asyncio
async def test_create_checkout_order(billing_service, sample_user, mock_orders, mock_session):
    result = await billing_service.create_checkout_order(sample_user, SubscriptionPlan.PRO)
    assert result["plan"] == "pro"
    mock_orders.create.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_checkout_order_rejects_free_plan(billing_service, sample_user):
    with pytest.raises(ValidationError):
        await billing_service.create_checkout_order(sample_user, SubscriptionPlan.FREE)


@pytest.mark.asyncio
async def test_verify_payment_success(billing_service, sample_user, mock_orders, mock_payments, mock_subscriptions, mock_session):
    order = Order(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        plan=SubscriptionPlan.PRO,
        amount_paise=99900,
        currency="INR",
        status=OrderStatus.CREATED,
        razorpay_order_id="order_abc",
        receipt="rcpt",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_orders.get_by_razorpay_order_id.return_value = order
    mock_payments.get_by_razorpay_payment_id.return_value = None

    async def _create_subscription(**kwargs):
        return Subscription(
            id=uuid.uuid4(),
            user_id=kwargs["user_id"],
            plan=kwargs["plan"],
            status=SubscriptionStatus.ACTIVE,
            current_period_start=kwargs["current_period_start"],
            current_period_end=kwargs["current_period_end"],
            razorpay_subscription_id=None,
            cancelled_at=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    mock_subscriptions.get_active_for_user.return_value = None
    mock_subscriptions.create.side_effect = _create_subscription
    mock_payments.create.return_value = MagicMock(id=uuid.uuid4())

    result = await billing_service.verify_payment(
        user=sample_user,
        razorpay_order_id="order_abc",
        razorpay_payment_id="pay_abc",
        razorpay_signature="valid_signature",
    )
    assert result["status"] == "success"
    mock_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_verify_payment_invalid_signature(billing_service, sample_user):
    with pytest.raises(ValidationError):
        await billing_service.verify_payment(
            user=sample_user,
            razorpay_order_id="order_abc",
            razorpay_payment_id="pay_abc",
            razorpay_signature="bad",
        )


@pytest.mark.asyncio
async def test_admin_activate_subscription(billing_service, mock_subscriptions, mock_session):
    mock_subscriptions.get_active_for_user.return_value = None

    async def _create(**kwargs):
        return Subscription(
            id=uuid.uuid4(),
            user_id=kwargs["user_id"],
            plan=kwargs["plan"],
            status=SubscriptionStatus.ACTIVE,
            current_period_start=kwargs["current_period_start"],
            current_period_end=kwargs["current_period_end"],
            razorpay_subscription_id=None,
            cancelled_at=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    mock_subscriptions.create.side_effect = _create
    result = await billing_service.admin_activate_subscription(
        user_id=uuid.uuid4(),
        plan=SubscriptionPlan.PREMIUM,
    )
    assert result["plan"] == "premium"


@pytest.mark.asyncio
async def test_handle_webhook_captures_payment(billing_service, mock_orders, mock_payments, mock_subscriptions, mock_session):
    order = Order(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        plan=SubscriptionPlan.PRO,
        amount_paise=99900,
        currency="INR",
        status=OrderStatus.CREATED,
        razorpay_order_id="order_webhook",
        receipt="rcpt",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_orders.get_by_razorpay_order_id.return_value = order
    mock_payments.get_by_razorpay_payment_id.return_value = None
    mock_subscriptions.get_active_for_user.return_value = None
    mock_subscriptions.create.return_value = Subscription(
        id=uuid.uuid4(),
        user_id=order.user_id,
        plan=SubscriptionPlan.PRO,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.now(UTC),
        current_period_end=next_period_end(),
        razorpay_subscription_id=None,
        cancelled_at=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    payload = b'{"event":"payment.captured","payload":{"payment":{"entity":{"id":"pay_hook","order_id":"order_webhook","method":"upi"}}}}'
    result = await billing_service.handle_webhook(payload, "valid_webhook_signature")
    assert result["status"] == "ok"
    mock_session.commit.assert_awaited()
