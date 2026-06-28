"""Shared helpers for pytest modules."""

from __future__ import annotations

from unittest.mock import AsyncMock

from backend.app.api.deps import get_current_user, get_usage_service
from backend.app.models.enums import SubscriptionPlan
from backend.app.models.user import User


def override_current_user(app, user: User) -> None:
    """Attach a deterministic authenticated user to a test app instance."""

    async def _get_current_user() -> User:
        return user

    app.dependency_overrides[get_current_user] = _get_current_user


def override_usage_service(app, service: AsyncMock | None = None) -> AsyncMock:
    """Bypass quota checks in integration tests."""
    mock = service or AsyncMock()
    mock.check_quota = AsyncMock(return_value=None)
    mock.consume = AsyncMock(return_value=None)
    mock.ensure_free_subscription = AsyncMock(return_value=None)
    mock.get_active_plan = AsyncMock(return_value=SubscriptionPlan.FREE)
    app.dependency_overrides[get_usage_service] = lambda: mock
    return mock
