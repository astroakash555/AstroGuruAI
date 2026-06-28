"""Billing API endpoint tests."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.deps import get_billing_service
from backend.app.models.enums import SubscriptionPlan, UserRole
from tests.helpers import override_current_user, override_usage_service


@pytest.fixture
def mock_billing_service():
    service = MagicMock()
    service.list_plans.return_value = [
        {
            "plan": "free",
            "name": "Free",
            "description": "Starter",
            "price_paise": 0,
            "currency": "INR",
            "features": ["5 reports"],
            "limits": {"reports": 5, "chat_messages": 20, "clients": 10},
        }
    ]
    service.get_subscription = AsyncMock(return_value={
        "subscription_id": "00000000-0000-4000-8000-000000000099",
        "plan": "free",
        "status": "active",
        "current_period_start": datetime.now(UTC),
        "current_period_end": datetime.now(UTC),
        "usage": {"plan": "free", "period_start": "2026-06-01", "metrics": []},
    })
    service.initialize_new_user = AsyncMock(return_value=None)
    return service


@pytest.fixture
async def billing_client(app, mock_billing_service, test_user):
    app.dependency_overrides[get_billing_service] = lambda: mock_billing_service
    override_current_user(app, test_user)
    override_usage_service(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_plans_public(billing_client, mock_billing_service):
    response = await billing_client.get("/api/v1/billing/plans")
    assert response.status_code == 200
    assert response.json()[0]["plan"] == "free"
    mock_billing_service.list_plans.assert_called_once()


@pytest.mark.asyncio
async def test_get_subscription(billing_client, mock_billing_service):
    response = await billing_client.get("/api/v1/billing/subscription")
    assert response.status_code == 200
    mock_billing_service.get_subscription.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_list_subscriptions_forbidden_for_user(app, test_user, mock_billing_service):
    app.dependency_overrides[get_billing_service] = lambda: mock_billing_service
    override_current_user(app, test_user)
    override_usage_service(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/billing/subscriptions")
    app.dependency_overrides.clear()
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_list_subscriptions(app, admin_user, mock_billing_service):
    mock_billing_service.admin_list_subscriptions = AsyncMock(return_value={
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "pages": 0,
    })
    app.dependency_overrides[get_billing_service] = lambda: mock_billing_service
    override_current_user(app, admin_user)
    override_usage_service(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/billing/subscriptions")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    mock_billing_service.admin_list_subscriptions.assert_awaited_once()
