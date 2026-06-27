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
