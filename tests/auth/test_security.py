"""Tests for auth security helpers."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import jwt
import pytest

from backend.app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_token_value,
    hash_password,
    hash_token,
    validate_secret_key,
    verify_password,
)
from backend.app.core.config import Settings


def test_hash_and_verify_password():
    hashed = hash_password("StrongPass123!")
    assert hashed.startswith("$argon2")
    assert verify_password("StrongPass123!", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_generate_token_value_is_unique():
    assert generate_token_value() != generate_token_value()


def test_hash_token_is_deterministic():
    assert hash_token("abc") == hash_token("abc")
    assert hash_token("abc") != hash_token("xyz")


def test_access_and_refresh_tokens(auth_settings):
    user_id = uuid.uuid4()
    access = create_access_token(user_id=user_id, role="user", settings=auth_settings)
    refresh, expires_at = create_refresh_token(user_id=user_id, role="user", settings=auth_settings)

    access_payload = decode_token(access, auth_settings)
    refresh_payload = decode_token(refresh, auth_settings)

    assert access_payload["sub"] == str(user_id)
    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"
    assert expires_at > datetime.now(UTC)


def test_decode_token_rejects_tampered_token(auth_settings):
    token = create_access_token(user_id=uuid.uuid4(), role="user", settings=auth_settings)
    with pytest.raises(jwt.PyJWTError):
        decode_token(token + "tampered", auth_settings)


def test_validate_secret_key_blocks_default_in_production():
    settings = Settings.model_construct(app_env="production", secret_key="change-me")
    with pytest.raises(ValueError):
        validate_secret_key(settings)


def test_validate_secret_key_allows_default_in_development():
    validate_secret_key(Settings(app_env="development", secret_key="change-me"))
