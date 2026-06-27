"""Auth module test fixtures."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from backend.app.auth.email import EmailDeliveryService
from backend.app.auth.repositories import AuthTokenRepository, RefreshTokenRepository, UserRepository
from backend.app.auth.service import AuthService
from backend.app.core.config import Settings
from backend.app.models.enums import UserRole
from backend.app.models.user import User


@pytest.fixture
def auth_settings() -> Settings:
    return Settings(
        secret_key="test-secret-key-for-auth-tests-only",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
        password_reset_expire_minutes=60,
        email_verification_expire_hours=24,
        auth_frontend_url="http://localhost:5173",
    )


@pytest.fixture
def sample_user() -> User:
    now = datetime.now(UTC)
    return User(
        id=uuid.uuid4(),
        email="user@example.com",
        full_name="Sample User",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$test$test",
        role=UserRole.USER,
        is_active=True,
        is_verified=False,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def mock_users(sample_user: User) -> AsyncMock:
    repo = AsyncMock(spec=UserRepository)
    repo.get_by_email.return_value = None
    repo.get_by_id.return_value = sample_user

    async def _create_user(**kwargs):
        sample_user.email = kwargs["email"]
        sample_user.full_name = kwargs["full_name"]
        sample_user.hashed_password = kwargs["hashed_password"]
        return sample_user

    repo.create_user.side_effect = _create_user
    return repo


@pytest.fixture
def mock_refresh_tokens() -> AsyncMock:
    repo = AsyncMock(spec=RefreshTokenRepository)
    repo.get_active_by_hash.return_value = None
    return repo


@pytest.fixture
def mock_auth_tokens() -> AsyncMock:
    repo = AsyncMock(spec=AuthTokenRepository)
    repo.get_valid.return_value = None
    return repo


@pytest.fixture
def mock_email() -> EmailDeliveryService:
    return EmailDeliveryService()


@pytest.fixture
def auth_service(
    auth_settings: Settings,
    mock_users: AsyncMock,
    mock_refresh_tokens: AsyncMock,
    mock_auth_tokens: AsyncMock,
    mock_email: EmailDeliveryService,
) -> AuthService:
    return AuthService(
        settings=auth_settings,
        users=mock_users,
        refresh_tokens=mock_refresh_tokens,
        auth_tokens=mock_auth_tokens,
        email_service=mock_email,
    )
