"""Application-level exceptions and HTTP error mapping."""

from fastapi import HTTPException, status


class AppError(Exception):
    """Base application exception."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""


class ConflictError(AppError):
    """Raised when a resource conflicts with existing data."""


class ValidationError(AppError):
    """Raised for domain-level validation failures."""


class UnauthorizedError(AppError):
    """Raised when authentication fails or is missing."""


class ForbiddenError(AppError):
    """Raised when the user lacks permission for a resource."""


class QuotaExceededError(AppError):
    """Raised when a subscription usage limit has been reached."""


def not_found_error(resource: str, identifier: str) -> HTTPException:
    """Build a standardized 404 HTTP exception."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} with id '{identifier}' was not found.",
    )


def conflict_error(message: str) -> HTTPException:
    """Build a standardized 409 HTTP exception."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )


def unauthorized_error(message: str = "Authentication required.") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


def forbidden_error(message: str = "You do not have permission to access this resource.") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def quota_exceeded_error(message: str = "Monthly usage limit reached. Upgrade your plan to continue.") -> HTTPException:
    return HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=message)
