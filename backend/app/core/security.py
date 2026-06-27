"""Security utilities and authentication placeholders."""

from backend.app.core.config import Settings


def validate_secret_key(settings: Settings) -> None:
    """Warn when default secret key is used outside development."""
    if settings.app_env != "development" and settings.secret_key == "change-me":
        raise ValueError("SECRET_KEY must be set in non-development environments.")
