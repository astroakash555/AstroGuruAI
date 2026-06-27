"""Tests for auth repositories with mocked SQLAlchemy session."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.auth.repositories import AuthTokenRepository, RefreshTokenRepository, UserRepository
from backend.app.models.enums import AuthTokenType, UserRole


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_user_repository_create_user(mock_session):
    repo = UserRepository(mock_session)
    user = await repo.create_user(
        email="User@Example.com",
        full_name="User",
        hashed_password="hash",
        role=UserRole.USER,
    )
    assert user.email == "user@example.com"
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_repository_getters(mock_session):
    repo = UserRepository(mock_session)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = "user"
    mock_session.execute.return_value = mock_result

    assert await repo.get_by_id(uuid.uuid4()) == "user"
    assert await repo.get_by_email("test@example.com") == "user"


@pytest.mark.asyncio
async def test_refresh_token_repository_create_revoke_and_lookup(mock_session):
    repo = RefreshTokenRepository(mock_session)
    created = await repo.create(
        user_id=uuid.uuid4(),
        token_hash="hash",
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    assert created.token_hash == "hash"

    token = MagicMock()
    await repo.revoke(token)
    assert token.revoked_at is not None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = created
    mock_session.execute.return_value = mock_result
    assert await repo.get_active_by_hash("hash") == created


@pytest.mark.asyncio
async def test_refresh_token_repository_revoke_all_for_user(mock_session):
    repo = RefreshTokenRepository(mock_session)
    token = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [token]
    mock_session.execute.return_value = mock_result

    await repo.revoke_all_for_user(uuid.uuid4())
    assert token.revoked_at is not None


@pytest.mark.asyncio
async def test_auth_token_repository_create_mark_used_and_get_valid(mock_session):
    repo = AuthTokenRepository(mock_session)
    token = await repo.create(
        user_id=uuid.uuid4(),
        token_type=AuthTokenType.PASSWORD_RESET,
        token_hash="hash",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    assert token.token_type == AuthTokenType.PASSWORD_RESET
    mock_session.add.assert_called_once()

    await repo.mark_used(token)
    assert token.used_at is not None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = token
    mock_session.execute.return_value = mock_result
    found = await repo.get_valid(token_hash="hash", token_type=AuthTokenType.PASSWORD_RESET)
    assert found == token
