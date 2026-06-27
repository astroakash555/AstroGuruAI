"""Authentication business logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt

from backend.app.auth.email import EmailDeliveryService
from backend.app.auth.repositories import AuthTokenRepository, RefreshTokenRepository, UserRepository
from backend.app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_token_value,
    hash_password,
    hash_token,
    verify_password,
)
from backend.app.core.config import Settings
from backend.app.core.exceptions import ConflictError, UnauthorizedError, ValidationError
from backend.app.models.enums import AuthTokenType, UserRole
from backend.app.models.user import User
from backend.app.schemas.auth import AuthResponse, TokenResponse, UserResponse


class AuthService:
    """Orchestrates signup, login, token rotation, and account recovery."""

    def __init__(
        self,
        *,
        settings: Settings,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        auth_tokens: AuthTokenRepository,
        email_service: EmailDeliveryService | None = None,
    ) -> None:
        self._settings = settings
        self._users = users
        self._refresh_tokens = refresh_tokens
        self._auth_tokens = auth_tokens
        self._email = email_service or EmailDeliveryService()

    async def signup(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
    ) -> AuthResponse:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise ConflictError("An account with this email already exists.")

        user = await self._users.create_user(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=UserRole.USER,
        )
        await self._send_verification_email(user)
        tokens = await self._issue_tokens(user)
        return AuthResponse(user=self._to_user_response(user), tokens=tokens)

    async def login(self, *, email: str, password: str) -> AuthResponse:
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("This account has been deactivated.")

        tokens = await self._issue_tokens(user)
        return AuthResponse(user=self._to_user_response(user), tokens=tokens)

    async def logout(self, *, refresh_token: str) -> None:
        stored = await self._get_active_refresh_record(refresh_token)
        if stored is not None:
            await self._refresh_tokens.revoke(stored)

    async def refresh(self, *, refresh_token: str) -> TokenResponse:
        payload = self._decode_refresh_jwt(refresh_token)
        user_id = uuid.UUID(payload["sub"])
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Invalid refresh token.")

        stored = await self._get_active_refresh_record(refresh_token)
        if stored is None or stored.user_id != user.id:
            raise UnauthorizedError("Invalid refresh token.")
        if stored.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            await self._refresh_tokens.revoke(stored)
            raise UnauthorizedError("Refresh token has expired.")

        await self._refresh_tokens.revoke(stored)
        return await self._issue_tokens(user)

    async def get_current_user(self, user_id: uuid.UUID) -> UserResponse:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError("User not found.")
        return self._to_user_response(user)

    async def change_password(
        self,
        *,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedError("Current password is incorrect.")
        user.hashed_password = hash_password(new_password)
        await self._refresh_tokens.revoke_all_for_user(user.id)

    async def forgot_password(self, *, email: str) -> str:
        user = await self._users.get_by_email(email)
        if user is not None and user.is_active:
            raw_token = generate_token_value()
            expires_at = datetime.now(UTC) + timedelta(minutes=self._settings.password_reset_expire_minutes)
            await self._auth_tokens.create(
                user_id=user.id,
                token_type=AuthTokenType.PASSWORD_RESET,
                token_hash=hash_token(raw_token),
                expires_at=expires_at,
            )
            reset_url = f"{self._settings.auth_frontend_url.rstrip('/')}/reset-password?token={raw_token}"
            self._email.send_password_reset(to_email=user.email, reset_url=reset_url)
        return "If an account exists for that email, password reset instructions have been sent."

    async def reset_password(self, *, token: str, new_password: str) -> None:
        record = await self._auth_tokens.get_valid(
            token_hash=hash_token(token),
            token_type=AuthTokenType.PASSWORD_RESET,
        )
        if record is None or record.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            raise ValidationError("Invalid or expired password reset token.")

        user = await self._users.get_by_id(record.user_id)
        if user is None or not user.is_active:
            raise ValidationError("Invalid or expired password reset token.")

        user.hashed_password = hash_password(new_password)
        await self._auth_tokens.mark_used(record)
        await self._refresh_tokens.revoke_all_for_user(user.id)

    async def verify_email(self, *, token: str) -> None:
        record = await self._auth_tokens.get_valid(
            token_hash=hash_token(token),
            token_type=AuthTokenType.EMAIL_VERIFICATION,
        )
        if record is None or record.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            raise ValidationError("Invalid or expired verification token.")

        user = await self._users.get_by_id(record.user_id)
        if user is None:
            raise ValidationError("Invalid or expired verification token.")

        user.is_verified = True
        await self._auth_tokens.mark_used(record)

    async def resend_verification(self, *, email: str) -> str:
        user = await self._users.get_by_email(email)
        if user is not None and user.is_active and not user.is_verified:
            await self._send_verification_email(user)
        return "If an unverified account exists for that email, a verification link has been sent."

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(
            user_id=user.id,
            role=user.role.value,
            settings=self._settings,
        )
        refresh_token, expires_at = create_refresh_token(
            user_id=user.id,
            role=user.role.value,
            settings=self._settings,
        )
        await self._refresh_tokens.create(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._settings.access_token_expire_minutes * 60,
        )

    async def _send_verification_email(self, user: User) -> None:
        raw_token = generate_token_value()
        expires_at = datetime.now(UTC) + timedelta(hours=self._settings.email_verification_expire_hours)
        await self._auth_tokens.create(
            user_id=user.id,
            token_type=AuthTokenType.EMAIL_VERIFICATION,
            token_hash=hash_token(raw_token),
            expires_at=expires_at,
        )
        verify_url = f"{self._settings.auth_frontend_url.rstrip('/')}/verify-email?token={raw_token}"
        self._email.send_email_verification(to_email=user.email, verify_url=verify_url)

    async def _get_active_refresh_record(self, refresh_token: str):
        return await self._refresh_tokens.get_active_by_hash(hash_token(refresh_token))

    def _decode_refresh_jwt(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token, self._settings)
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid refresh token.") from exc
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token.")
        return payload

    @staticmethod
    def _to_user_response(user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
