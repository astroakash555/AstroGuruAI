"""Production authentication utilities."""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from passlib.context import CryptContext

from backend.app.core.config import Settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def validate_secret_key(settings: Settings) -> None:
    """Warn when default secret key is used outside development."""
    if settings.app_env != "development" and settings.secret_key == "change-me":
        raise ValueError("SECRET_KEY must be set in non-development environments.")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_token_value() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(*, user_id: UUID, role: str, settings: Settings) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expires,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(*, user_id: UUID, role: str, settings: Settings) -> tuple[str, datetime]:
    expires = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
        "exp": expires,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, expires


def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
