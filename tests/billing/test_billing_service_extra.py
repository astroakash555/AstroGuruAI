"""Extended billing service and usage coverage tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.billing.usage import UsageService, next_period_end
from backend.app.core.exceptions import NotFoundError, ValidationError
from backend.app.models.enums import OrderStatus, SubscriptionPlan, SubscriptionStatus, UsageMetric
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.models.subscription import Subscription
from backend.app.models.usage_quota import UsageQuota


@pytest.mark.asyncio
async def test_get_subscription(billing_service, mock_subscriptions, usage_service, sample_user):
    subscription = Subscription(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        plan=SubscriptionPlan.PRO,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.now(UTC),
        current_period_end=next_period_end(),
        razorpay_subscription_id=None,
        cancelled_at=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_subscriptions.get_active_for_user.return_value = subscription
    usage_service.get_usage_summary = AsyncMock(return_value={"plan": "pro", "period_start": "2026-06-01", "metrics": []})

    result = await billing_service.get_subscription(sample_user.id)
    assert result["plan"] == "pro"


@pytest.mark.asyncio
async def test_get_subscription_not_found(billing_service, mock_subscriptions, sample_user):
    mock_subscriptions.get_active_for_user.return_value = None
    usage_service = billing_service._usage
    usage_service.ensure_free_subscription = AsyncMock()
    usage_service.get_usage_summary = AsyncMock()
    with pytest.raises(NotFoundError):
        await billing_service.get_subscription(sample_user.id)


@pytest.mark.asyncio
async def test_list_payment_history(billing_service, mock_payments):
    payment = Payment(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        order_id=None,
        subscription_id=None,
        amount_paise=99900,
        currency="INR",
        status=__import__("backend.app.models.enums", fromlist=["PaymentStatus"]).PaymentStatus.CAPTURED,
        razorpay_payment_id="pay_1",
        razorpay_order_id="order_1",
        method="upi",
        paid_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_payments.list_for_user.return_value = ([payment], 1)
    result = await billing_service.list_payment_history(uuid.uuid4())
    assert result["total"] == 1


@pytest.mark.asyncio
async def test_admin_list_subscriptions_and_payments(billing_service, mock_subscriptions, mock_payments):
    mock_subscriptions.list_all.return_value = ([], 0)
    mock_payments.list_all.return_value = ([], 0)
    assert (await billing_service.admin_list_subscriptions())["total"] == 0
    assert (await billing_service.admin_list_payments())["total"] == 0


@pytest.mark.asyncio
async def test_cancel_subscription(billing_service, mock_subscriptions, mock_session, sample_user):
    subscription = Subscription(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        plan=SubscriptionPlan.PRO,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.now(UTC),
        current_period_end=next_period_end(),
        razorpay_subscription_id=None,
        cancelled_at=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_subscriptions.get_active_for_user.return_value = subscription
    mock_subscriptions.create.return_value = Subscription(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        plan=SubscriptionPlan.FREE,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.now(UTC),
        current_period_end=next_period_end(),
        razorpay_subscription_id=None,
        cancelled_at=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    result = await billing_service.cancel_subscription(sample_user.id)
    assert result["plan"] == "free"
    mock_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_verify_payment_order_not_found(billing_service, sample_user, mock_orders):
    mock_orders.get_by_razorpay_order_id.return_value = None
    with pytest.raises(NotFoundError):
        await billing_service.verify_payment(
            user=sample_user,
            razorpay_order_id="missing",
            razorpay_payment_id="pay_1",
            razorpay_signature="valid_signature",
        )


@pytest.mark.asyncio
async def test_handle_webhook_invalid_signature(billing_service):
    with pytest.raises(ValidationError):
        await billing_service.handle_webhook(b'{"event":"test"}', "bad")


@pytest.mark.asyncio
async def test_usage_ensure_free_subscription(mock_session, mock_subscriptions, mock_quotas):
    mock_subscriptions.get_active_for_user.return_value = None

    async def _create(**kwargs):
        return Subscription(
            id=uuid.uuid4(),
            user_id=kwargs["user_id"],
            plan=kwargs["plan"],
            status=kwargs["status"],
            current_period_start=kwargs["current_period_start"],
            current_period_end=kwargs["current_period_end"],
            razorpay_subscription_id=None,
            cancelled_at=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    mock_subscriptions.create.side_effect = _create

    async def _quota(**kwargs):
        return UsageQuota(
            id=uuid.uuid4(),
            user_id=kwargs["user_id"],
            metric=kwargs["metric"],
            period_start=kwargs["period_start"],
            used_count=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    mock_quotas.get_or_create.side_effect = _quota
    service = UsageService(mock_session, subscriptions=mock_subscriptions, quotas=mock_quotas)
    await service.ensure_free_subscription(uuid.uuid4())
    mock_subscriptions.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_usage_get_usage_summary(mock_session, mock_subscriptions, mock_quotas):
    mock_subscriptions.get_active_for_user.return_value = MagicMock(plan=SubscriptionPlan.FREE)
    mock_quotas.list_for_user_period.return_value = [
        UsageQuota(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            metric=UsageMetric.REPORTS,
            period_start=datetime.now(UTC).date().replace(day=1),
            used_count=2,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    ]
    service = UsageService(mock_session, subscriptions=mock_subscriptions, quotas=mock_quotas)
    summary = await service.get_usage_summary(uuid.uuid4())
    assert summary["plan"] == "free"
    assert summary["metrics"][0]["used"] == 2
