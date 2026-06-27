"""Tests for AuthService."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from backend.app.auth.security import create_refresh_token, hash_password, hash_token
from backend.app.core.exceptions import ConflictError, UnauthorizedError, ValidationError
from backend.app.models.auth_token import AuthToken
from backend.app.models.enums import AuthTokenType
from backend.app.models.refresh_token import RefreshToken


@pytest.mark.asyncio
async def test_signup_creates_user_and_returns_tokens(auth_service, mock_users, mock_auth_tokens):
    result = await auth_service.signup(
        email="new@example.com",
        password="Password123!",
        full_name="New User",
    )

    assert result.user.email == "new@example.com"
    assert result.tokens.access_token
    assert result.tokens.refresh_token
    mock_users.create_user.assert_awaited_once()
    mock_auth_tokens.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_signup_rejects_duplicate_email(auth_service, mock_users, sample_user):
    mock_users.get_by_email.return_value = sample_user
    with pytest.raises(ConflictError):
        await auth_service.signup(
            email="user@example.com",
            password="Password123!",
            full_name="Duplicate",
        )


@pytest.mark.asyncio
async def test_login_success(auth_service, mock_users, sample_user):
    sample_user.hashed_password = hash_password("Password123!")
    mock_users.get_by_email.return_value = sample_user

    result = await auth_service.login(email="user@example.com", password="Password123!")
    assert result.user.email == sample_user.email
    assert result.tokens.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials(auth_service, mock_users):
    mock_users.get_by_email.return_value = None
    with pytest.raises(UnauthorizedError):
        await auth_service.login(email="missing@example.com", password="Password123!")


@pytest.mark.asyncio
async def test_login_rejects_inactive_user(auth_service, mock_users, sample_user):
    sample_user.hashed_password = hash_password("Password123!")
    sample_user.is_active = False
    mock_users.get_by_email.return_value = sample_user
    with pytest.raises(UnauthorizedError):
        await auth_service.login(email="user@example.com", password="Password123!")


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(auth_service, mock_refresh_tokens):
    token = RefreshToken(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        token_hash=hash_token("refresh"),
        expires_at=datetime.now(UTC) + timedelta(days=1),
        revoked_at=None,
        created_at=datetime.now(UTC),
    )
    mock_refresh_tokens.get_active_by_hash.return_value = token

    await auth_service.logout(refresh_token="refresh")
    mock_refresh_tokens.revoke.assert_awaited_once_with(token)


@pytest.mark.asyncio
async def test_refresh_rotates_tokens(auth_service, auth_settings, mock_refresh_tokens, sample_user):
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

    tokens = await auth_service.refresh(refresh_token=refresh_token)
    assert tokens.access_token
    mock_refresh_tokens.revoke.assert_awaited_once_with(stored)


@pytest.mark.asyncio
async def test_refresh_rejects_invalid_token(auth_service):
    with pytest.raises(UnauthorizedError):
        await auth_service.refresh(refresh_token="not-a-valid-token")


@pytest.mark.asyncio
async def test_change_password(auth_service, sample_user, mock_refresh_tokens):
    sample_user.hashed_password = hash_password("OldPassword1!")
    await auth_service.change_password(
        user=sample_user,
        current_password="OldPassword1!",
        new_password="NewPassword2!",
    )
    from backend.app.auth.security import verify_password

    assert verify_password("NewPassword2!", sample_user.hashed_password)
    mock_refresh_tokens.revoke_all_for_user.assert_awaited_once_with(sample_user.id)


@pytest.mark.asyncio
async def test_change_password_rejects_wrong_current(auth_service, sample_user):
    sample_user.hashed_password = hash_password("OldPassword1!")
    with pytest.raises(UnauthorizedError):
        await auth_service.change_password(
            user=sample_user,
            current_password="WrongPassword!",
            new_password="NewPassword2!",
        )


@pytest.mark.asyncio
async def test_forgot_password_sends_email(auth_service, mock_users, mock_auth_tokens, sample_user):
    mock_users.get_by_email.return_value = sample_user
    message = await auth_service.forgot_password(email=sample_user.email)
    assert "If an account exists" in message
    mock_auth_tokens.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_forgot_password_is_generic_for_unknown_email(auth_service, mock_users, mock_auth_tokens):
    mock_users.get_by_email.return_value = None
    message = await auth_service.forgot_password(email="missing@example.com")
    assert "If an account exists" in message
    mock_auth_tokens.create.assert_not_called()


@pytest.mark.asyncio
async def test_reset_password(auth_service, mock_auth_tokens, mock_users, mock_refresh_tokens, sample_user):
    record = AuthToken(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        token_type=AuthTokenType.PASSWORD_RESET,
        token_hash=hash_token("reset-token"),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        used_at=None,
        created_at=datetime.now(UTC),
    )
    mock_auth_tokens.get_valid.return_value = record
    mock_users.get_by_id.return_value = sample_user

    await auth_service.reset_password(token="reset-token", new_password="ResetPass123!")
    mock_auth_tokens.mark_used.assert_awaited_once_with(record)
    mock_refresh_tokens.revoke_all_for_user.assert_awaited_once_with(sample_user.id)


@pytest.mark.asyncio
async def test_reset_password_rejects_invalid_token(auth_service, mock_auth_tokens):
    mock_auth_tokens.get_valid.return_value = None
    with pytest.raises(ValidationError):
        await auth_service.reset_password(token="bad", new_password="ResetPass123!")


@pytest.mark.asyncio
async def test_verify_email(auth_service, mock_auth_tokens, mock_users, sample_user):
    record = AuthToken(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        token_type=AuthTokenType.EMAIL_VERIFICATION,
        token_hash=hash_token("verify-token"),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        used_at=None,
        created_at=datetime.now(UTC),
    )
    mock_auth_tokens.get_valid.return_value = record
    mock_users.get_by_id.return_value = sample_user

    await auth_service.verify_email(token="verify-token")
    assert sample_user.is_verified is True
    mock_auth_tokens.mark_used.assert_awaited_once_with(record)


@pytest.mark.asyncio
async def test_resend_verification(auth_service, mock_users, mock_auth_tokens, sample_user):
    sample_user.is_verified = False
    mock_users.get_by_email.return_value = sample_user
    message = await auth_service.resend_verification(email=sample_user.email)
    assert "verification link" in message
    mock_auth_tokens.create.assert_awaited()


@pytest.mark.asyncio
async def test_get_current_user(auth_service, sample_user):
    response = await auth_service.get_current_user(sample_user.id)
    assert response.email == sample_user.email


@pytest.mark.asyncio
async def test_get_current_user_missing(auth_service, mock_users):
    mock_users.get_by_id.return_value = None
    with pytest.raises(UnauthorizedError):
        await auth_service.get_current_user(uuid.uuid4())
