"""Pydantic schemas for authentication APIs."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from backend.app.models.enums import UserRole
from backend.app.schemas.common import BaseSchema


class SignupRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class RefreshRequest(BaseSchema):
    refresh_token: str = Field(..., min_length=10)


class LogoutRequest(BaseSchema):
    refresh_token: str = Field(..., min_length=10)


class ChangePasswordRequest(BaseSchema):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class ForgotPasswordRequest(BaseSchema):
    email: EmailStr


class ResetPasswordRequest(BaseSchema):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8, max_length=128)


class VerifyEmailRequest(BaseSchema):
    token: str = Field(..., min_length=10)


class ResendVerificationRequest(BaseSchema):
    email: EmailStr


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseSchema):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseSchema):
    user: UserResponse
    tokens: TokenResponse


class MessageResponse(BaseSchema):
    message: str
