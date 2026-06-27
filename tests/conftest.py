"""Shared pytest fixtures."""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

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
def app():
    """Create a fresh FastAPI application instance for testing."""
    return create_app()


@pytest.fixture
async def client(app, test_user):
    """Async HTTP client bound to the test application with auth override."""
    override_current_user(app, test_user)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
