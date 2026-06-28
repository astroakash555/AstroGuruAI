"""Extended repository coverage tests."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.billing.repositories import OrderRepository, PaymentRepository, SubscriptionRepository, UsageQuotaRepository
from backend.app.models.enums import AuthTokenType, OrderStatus, PaymentStatus, SubscriptionPlan, SubscriptionStatus, UsageMetric


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_subscription_get_active_and_by_id(mock_session):
    repo = SubscriptionRepository(mock_session)
    sub = MagicMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = sub
    mock_session.execute.return_value = result
    assert await repo.get_active_for_user(uuid.uuid4()) is sub

    result.scalar_one_or_none.return_value = sub
    assert await repo.get_by_id(uuid.uuid4()) is sub


@pytest.mark.asyncio
async def test_subscription_list_all(mock_session):
    repo = SubscriptionRepository(mock_session)
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [MagicMock()]
    mock_session.execute = AsyncMock(side_effect=[count_result, list_result])
    items, total = await repo.list_all()
    assert total == 1
    assert len(items) == 1


@pytest.mark.asyncio
async def test_order_get_by_razorpay_and_create(mock_session):
    repo = OrderRepository(mock_session)
    result = MagicMock()
    result.scalar_one_or_none.return_value = MagicMock()
    mock_session.execute.return_value = result
    assert await repo.get_by_razorpay_order_id("order_1") is not None

    order = await repo.create(
        user_id=uuid.uuid4(),
        plan=SubscriptionPlan.PRO,
        amount_paise=99900,
        currency="INR",
        razorpay_order_id="order_2",
        receipt="rcpt",
    )
    assert order.razorpay_order_id == "order_2"


@pytest.mark.asyncio
async def test_payment_create_and_get(mock_session):
    repo = PaymentRepository(mock_session)
    payment = await repo.create(
        user_id=uuid.uuid4(),
        order_id=None,
        subscription_id=None,
        amount_paise=99900,
        currency="INR",
        razorpay_payment_id="pay_1",
        razorpay_order_id="order_1",
        status=PaymentStatus.CAPTURED,
    )
    assert payment.razorpay_payment_id == "pay_1"

    result = MagicMock()
    result.scalar_one_or_none.return_value = payment
    mock_session.execute.return_value = result
    assert await repo.get_by_razorpay_payment_id("pay_1") is payment


@pytest.mark.asyncio
async def test_payment_list_all(mock_session):
    repo = PaymentRepository(mock_session)
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(side_effect=[count_result, list_result])
    payments, total = await repo.list_all()
    assert total == 0
    assert payments == []


@pytest.mark.asyncio
async def test_usage_quota_increment_and_reset(mock_session):
    repo = UsageQuotaRepository(mock_session)
    quota = MagicMock(used_count=1)
    await repo.increment(quota, 2)
    assert quota.used_count == 3

    mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
    await repo.reset_period(uuid.uuid4(), date(2026, 5, 1), date(2026, 6, 1))
    assert mock_session.add.called
