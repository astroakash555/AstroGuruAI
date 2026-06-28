"""Billing module test fixtures."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from backend.app.billing.razorpay_client import MockRazorpayGateway, RazorpayOrderResult
from backend.app.billing.repositories import OrderRepository, PaymentRepository, SubscriptionRepository, UsageQuotaRepository
from backend.app.billing.service import BillingService
from backend.app.billing.usage import UsageService
from backend.app.core.config import Settings
from backend.app.models.enums import SubscriptionPlan, UserRole
from backend.app.models.user import User


@pytest.fixture
def billing_settings() -> Settings:
    return Settings(
        SECRET_KEY="billing-test-secret",
        RAZORPAY_ENABLED="false",
        RAZORPAY_KEY_ID="rzp_test_key",
        RAZORPAY_KEY_SECRET="test_secret",
        BILLING_FRONTEND_URL="http://localhost:5173",
    )


@pytest.fixture
def razorpay_settings() -> Settings:
    return Settings(
        SECRET_KEY="billing-test-secret",
        RAZORPAY_ENABLED="true",
        RAZORPAY_KEY_ID="rzp_test",
        RAZORPAY_KEY_SECRET="secret_key",
        RAZORPAY_WEBHOOK_SECRET="webhook_secret",
        BILLING_FRONTEND_URL="http://localhost:5173",
    )


@pytest.fixture
def sample_user() -> User:
    now = datetime.now(UTC)
    return User(
        id=uuid.uuid4(),
        email="billing@example.com",
        full_name="Billing User",
        hashed_password="hash",
        role=UserRole.USER,
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def mock_gateway(billing_settings):
    return MockRazorpayGateway(billing_settings)


@pytest.fixture
def mock_subscriptions():
    return AsyncMock(spec=SubscriptionRepository)


@pytest.fixture
def mock_orders():
    repo = AsyncMock(spec=OrderRepository)

    async def _create(**kwargs):
        from backend.app.models.order import Order
        from backend.app.models.enums import OrderStatus

        return Order(
            id=uuid.uuid4(),
            user_id=kwargs["user_id"],
            plan=kwargs["plan"],
            amount_paise=kwargs["amount_paise"],
            currency=kwargs["currency"],
            razorpay_order_id=kwargs["razorpay_order_id"],
            receipt=kwargs["receipt"],
            status=OrderStatus.CREATED,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    repo.create.side_effect = _create
    repo.get_by_razorpay_order_id.return_value = None
    return repo


@pytest.fixture
def mock_payments():
    return AsyncMock(spec=PaymentRepository)


@pytest.fixture
def mock_quotas():
    return AsyncMock(spec=UsageQuotaRepository)


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def usage_service(mock_session, mock_subscriptions, mock_quotas):
    return UsageService(mock_session, subscriptions=mock_subscriptions, quotas=mock_quotas)


@pytest.fixture
def billing_service(
    mock_session,
    billing_settings,
    mock_gateway,
    mock_subscriptions,
    mock_orders,
    mock_payments,
    usage_service,
):
    return BillingService(
        session=mock_session,
        settings=billing_settings,
        gateway=mock_gateway,
        subscriptions=mock_subscriptions,
        orders=mock_orders,
        payments=mock_payments,
        usage=usage_service,
    )
