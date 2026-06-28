"""Shared FastAPI dependencies."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator, Callable

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.email import EmailDeliveryService
from backend.app.auth.repositories import AuthTokenRepository, RefreshTokenRepository, UserRepository
from backend.app.auth.security import decode_token
from backend.app.auth.service import AuthService
from backend.app.billing.service import BillingService
from backend.app.billing.usage import UsageService
from backend.app.core.config import Settings, get_settings
from backend.app.core.exceptions import QuotaExceededError, forbidden_error, quota_exceeded_error, unauthorized_error
from backend.app.db.redis import get_redis_client
from backend.app.db.session import get_db_session
from backend.app.models.enums import UsageMetric, UserRole
from backend.app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_settings_dep() -> Settings:
    """Inject application settings."""
    return get_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Inject async database session."""
    async for session in get_db_session():
        yield session


async def get_redis(settings: Settings = Depends(get_settings_dep)):
    """Inject Redis client when enabled."""
    return await get_redis_client(settings)


def get_auth_service(
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> AuthService:
    return AuthService(
        settings=settings,
        users=UserRepository(session),
        refresh_tokens=RefreshTokenRepository(session),
        auth_tokens=AuthTokenRepository(session),
        email_service=EmailDeliveryService(),
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> User:
    """Resolve the authenticated user from a bearer access token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized_error()

    try:
        payload = decode_token(credentials.credentials, settings)
    except jwt.PyJWTError as exc:
        raise unauthorized_error("Invalid or expired access token.") from exc

    if payload.get("type") != "access":
        raise unauthorized_error("Invalid access token.")

    try:
        user_id = uuid.UUID(str(payload["sub"]))
    except (KeyError, ValueError) as exc:
        raise unauthorized_error("Invalid access token.") from exc

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise unauthorized_error("Invalid or expired access token.")
    return user


def require_roles(*roles: UserRole) -> Callable[..., User]:
    """Dependency factory that restricts access to specific user roles."""

    async def _require(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise forbidden_error()
        return current_user

    return _require


def user_owner_id(user: User) -> uuid.UUID | None:
    """Return owner filter for multi-tenant queries; admins see all records."""
    if user.role == UserRole.ADMIN:
        return None
    return user.id


def get_billing_service(
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> BillingService:
    from backend.app.billing.service import BillingService

    return BillingService(session=session, settings=settings)


def get_usage_service(session: AsyncSession = Depends(get_db)) -> UsageService:
    return UsageService(session)


def get_analytics_service(session: AsyncSession = Depends(get_db)) -> "AnalyticsService":
    from backend.app.services.analytics.analytics_service import AnalyticsService

    return AnalyticsService(session)


def require_usage(metric: UsageMetric) -> Callable[..., User]:
    """Dependency factory that enforces monthly subscription quotas."""

    async def _require(
        current_user: User = Depends(get_current_user),
        usage_service: UsageService = Depends(get_usage_service),
        settings: Settings = Depends(get_settings_dep),
    ) -> User:
        if current_user.role == UserRole.ADMIN:
            return current_user
        if not settings.quota_enforcement_enabled:
            return current_user
        try:
            await usage_service.check_quota(current_user.id, metric)
        except QuotaExceededError as exc:
            raise quota_exceeded_error(exc.message) from exc
        return current_user

    return _require
