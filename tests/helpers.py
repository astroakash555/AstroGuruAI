"""Shared helpers for pytest modules."""

from __future__ import annotations

from backend.app.api.deps import get_current_user
from backend.app.models.user import User


def override_current_user(app, user: User) -> None:
    """Attach a deterministic authenticated user to a test app instance."""

    async def _get_current_user() -> User:
        return user

    app.dependency_overrides[get_current_user] = _get_current_user
