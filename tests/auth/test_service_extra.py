"""Additional auth service coverage tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from backend.app.auth.security import create_refresh_token, hash_token
from backend.app.core.exceptions import UnauthorizedError, ValidationError
from backend.app.models.auth_token import AuthToken
from backend.app.models.enums import AuthTokenType
from backend.app.models.refresh_token import RefreshToken


@pytest.mark.asyncio
async def test_refresh_rejects_non_refresh_jwt(auth_service, auth_settings):
    access = jwt.encode(
        {"sub": str(uuid.uuid4()), "role": "user", "type": "access", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        auth_settings.secret_key,
        algorithm=auth_settings.jwt_algorithm,
    )
    with pytest.raises(UnauthorizedError):
        await auth_service.refresh(refresh_token=access)


@pytest.mark.asyncio
async def test_refresh_rejects_inactive_user(auth_service, auth_settings, mock_users, mock_refresh_tokens, sample_user):
    sample_user.is_active = False
    mock_users.get_by_id.return_value = sample_user
    refresh_token, expires_at = create_refresh_token(
        user_id=sample_user.id,
        role=sample_user.role.value,
        settings=auth_settings,
    )
    stored = RefreshToken(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        token_hash=hash_token(refresh_token),
        expires_at=expires_at,
        revoked_at=None,
        created_at=datetime.now(UTC),
    )
    mock_refresh_tokens.get_active_by_hash.return_value = stored

    with pytest.raises(UnauthorizedError):
        await auth_service.refresh(refresh_token=refresh_token)


@pytest.mark.asyncio
async def test_refresh_rejects_expired_stored_token(auth_service, auth_settings, mock_refresh_tokens, sample_user):
    refresh_token, _ = create_refresh_token(
        user_id=sample_user.id,
        role=sample_user.role.value,
        settings=auth_settings,
    )
    stored = RefreshToken(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
        revoked_at=None,
        created_at=datetime.now(UTC),
    )
    mock_refresh_tokens.get_active_by_hash.return_value = stored

    with pytest.raises(UnauthorizedError):
        await auth_service.refresh(refresh_token=refresh_token)


@pytest.mark.asyncio
async def test_refresh_rejects_mismatched_user(auth_service, auth_settings, mock_refresh_tokens, sample_user):
    refresh_token, expires_at = create_refresh_token(
        user_id=sample_user.id,
        role=sample_user.role.value,
        settings=auth_settings,
    )
    stored = RefreshToken(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        token_hash=hash_token(refresh_token),
        expires_at=expires_at,
        revoked_at=None,
        created_at=datetime.now(UTC),
    )
    mock_refresh_tokens.get_active_by_hash.return_value = stored

    with pytest.raises(UnauthorizedError):
        await auth_service.refresh(refresh_token=refresh_token)


@pytest.mark.asyncio
async def test_reset_password_rejects_inactive_user(auth_service, mock_auth_tokens, mock_users, sample_user):
    record = AuthToken(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        token_type=AuthTokenType.PASSWORD_RESET,
        token_hash=hash_token("reset-token"),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        used_at=None,
        created_at=datetime.now(UTC),
    )
    sample_user.is_active = False
    mock_auth_tokens.get_valid.return_value = record
    mock_users.get_by_id.return_value = sample_user

    with pytest.raises(ValidationError):
        await auth_service.reset_password(token="reset-token", new_password="ResetPass123!")


@pytest.mark.asyncio
async def test_verify_email_rejects_expired_token(auth_service, mock_auth_tokens):
    record = AuthToken(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        token_type=AuthTokenType.EMAIL_VERIFICATION,
        token_hash=hash_token("verify-token"),
        expires_at=datetime.now(UTC) - timedelta(hours=1),
        used_at=None,
        created_at=datetime.now(UTC),
    )
    mock_auth_tokens.get_valid.return_value = record

    with pytest.raises(ValidationError):
        await auth_service.verify_email(token="verify-token")


@pytest.mark.asyncio
async def test_verify_email_rejects_missing_user(auth_service, mock_auth_tokens, mock_users):
    record = AuthToken(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        token_type=AuthTokenType.EMAIL_VERIFICATION,
        token_hash=hash_token("verify-token"),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        used_at=None,
        created_at=datetime.now(UTC),
    )
    mock_auth_tokens.get_valid.return_value = record
    mock_users.get_by_id.return_value = None

    with pytest.raises(ValidationError):
        await auth_service.verify_email(token="verify-token")


@pytest.mark.asyncio
async def test_logout_noop_when_token_missing(auth_service, mock_refresh_tokens):
    mock_refresh_tokens.get_active_by_hash.return_value = None
    await auth_service.logout(refresh_token="missing-token-long-enough")
    mock_refresh_tokens.revoke.assert_not_called()
