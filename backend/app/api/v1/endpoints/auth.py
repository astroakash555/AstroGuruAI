"""Authentication API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import get_auth_service, get_current_user
from backend.app.auth.service import AuthService
from backend.app.core.exceptions import (
    ConflictError,
    UnauthorizedError,
    ValidationError,
    conflict_error,
    unauthorized_error,
)
from backend.app.models.user import User
from backend.app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    try:
        return await service.signup(
            email=str(payload.email),
            password=payload.password,
            full_name=payload.full_name,
        )
    except ConflictError as exc:
        raise conflict_error(exc.message) from exc


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    try:
        return await service.login(email=str(payload.email), password=payload.password)
    except UnauthorizedError as exc:
        raise unauthorized_error(exc.message) from exc


@router.post("/logout", response_model=MessageResponse)
async def logout(payload: LogoutRequest, service: AuthService = Depends(get_auth_service)) -> MessageResponse:
    await service.logout(refresh_token=payload.refresh_token)
    return MessageResponse(message="Logged out successfully.")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(payload: RefreshRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    try:
        return await service.refresh(refresh_token=payload.refresh_token)
    except UnauthorizedError as exc:
        raise unauthorized_error(exc.message) from exc


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    try:
        await service.change_password(
            user=current_user,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except UnauthorizedError as exc:
        raise unauthorized_error(exc.message) from exc
    return MessageResponse(message="Password updated successfully.")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    message = await service.forgot_password(email=str(payload.email))
    return MessageResponse(message=message)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    try:
        await service.reset_password(token=payload.token, new_password=payload.new_password)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    return MessageResponse(message="Password reset successfully.")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    try:
        await service.verify_email(token=payload.token)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    return MessageResponse(message="Email verified successfully.")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    payload: ResendVerificationRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    message = await service.resend_verification(email=str(payload.email))
    return MessageResponse(message=message)
