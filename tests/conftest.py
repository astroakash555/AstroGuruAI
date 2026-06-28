"""Shared pytest fixtures."""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock

from backend.app.main import create_app
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from tests.helpers import override_current_user


@pytest.fixture
def test_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def test_user(test_user_id: uuid.UUID) -> User:
    now = datetime.now(UTC)
    return User(
        id=test_user_id,
        email="test@astroguru.ai",
        full_name="Test User",
        hashed_password="hashed",
        role=UserRole.USER,
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def admin_user(test_user_id: uuid.UUID) -> User:
    now = datetime.now(UTC)
    return User(
        id=test_user_id,
        email="admin@astroguru.ai",
        full_name="Admin User",
        hashed_password="hashed",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def mock_usage_service():
    service = AsyncMock()
    service.check_quota = AsyncMock(return_value=None)
    service.consume = AsyncMock(return_value=None)
    service.ensure_free_subscription = AsyncMock(return_value=None)
    service.get_active_plan = AsyncMock(return_value=__import__(
        "backend.app.models.enums", fromlist=["SubscriptionPlan"]
    ).SubscriptionPlan.FREE)
    return service


@pytest.fixture
def app():
    """Create a fresh FastAPI application instance for testing."""
    return create_app()


@pytest.fixture
async def client(app, test_user, mock_usage_service):
    """Async HTTP client bound to the test application with auth override."""
    from backend.app.api.deps import get_usage_service

    override_current_user(app, test_user)
    app.dependency_overrides[get_usage_service] = lambda: mock_usage_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
