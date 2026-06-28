"""Integration-style tests for auth API endpoints."""

from __future__ import annotations

import uuid

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.deps import get_auth_service, get_billing_service, get_current_user
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.auth import AuthResponse, TokenResponse, UserResponse
from tests.helpers import override_current_user


@pytest.fixture
def mock_auth_service():
    service = AsyncMock()
    user = UserResponse(
        id=uuid.uuid4(),
        email="user@example.com",
        full_name="User",
        role=UserRole.USER,
        is_active=True,
        is_verified=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    tokens = TokenResponse(access_token="access", refresh_token="refresh", expires_in=1800)
    service.signup.return_value = AuthResponse(user=user, tokens=tokens)
    service.login.return_value = AuthResponse(user=user, tokens=tokens)
    service.refresh.return_value = tokens
    service.forgot_password.return_value = "If an account exists for that email, password reset instructions have been sent."
    service.resend_verification.return_value = "If an unverified account exists for that email, a verification link has been sent."
    return service


@pytest.fixture
def mock_billing_service_for_auth():
    service = AsyncMock()
    service.initialize_new_user = AsyncMock(return_value=None)
    return service


@pytest.fixture
async def auth_client(app, mock_auth_service, mock_billing_service_for_auth, test_user):
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    app.dependency_overrides[get_billing_service] = lambda: mock_billing_service_for_auth
    override_current_user(app, test_user)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_signup_endpoint(auth_client, mock_auth_service):
    response = await auth_client.post(
        "/api/v1/auth/signup",
        json={"email": "user@example.com", "password": "Password123!", "full_name": "User"},
    )
    assert response.status_code == 201
    assert response.json()["tokens"]["access_token"] == "access"
    mock_auth_service.signup.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_endpoint(auth_client, mock_auth_service):
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    mock_auth_service.login.assert_awaited_once()


@pytest.mark.asyncio
async def test_me_endpoint(auth_client, test_user):
    response = await auth_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email


@pytest.mark.asyncio
async def test_refresh_endpoint(auth_client, mock_auth_service):
    response = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "refresh-token-value-long-enough"},
    )
    assert response.status_code == 200
    mock_auth_service.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_protected_client_route_requires_auth(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/clients")
    assert response.status_code == 401
