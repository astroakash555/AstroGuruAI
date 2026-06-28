"""Configuration unit tests."""

from backend.app.core.config import Settings


def test_settings_defaults():
    """Settings load with sensible defaults."""
    settings = Settings()
    assert settings.app_name == "AstroGuruAI"
    assert settings.api_v1_prefix == "/api/v1"
    assert "postgresql+asyncpg://" in settings.sqlalchemy_database_uri


def test_cors_origins_parsing():
    """CORS origins are parsed from comma-separated string."""
    settings = Settings(ALLOWED_ORIGINS="http://a.com, http://b.com")
    assert settings.cors_origins == ["http://a.com", "http://b.com"]


def test_quota_enforcement_disabled_in_development_and_debug():
    assert Settings(APP_ENV="development", DEBUG="false").quota_enforcement_enabled is False
    assert Settings(APP_ENV="production", DEBUG="true").quota_enforcement_enabled is False


def test_quota_enforcement_enabled_in_production():
    assert Settings(APP_ENV="production", DEBUG="false").quota_enforcement_enabled is True
    assert Settings(APP_ENV="staging", DEBUG="false").quota_enforcement_enabled is True

