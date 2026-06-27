"""Centralized application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with environment-based overrides."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="AstroGuruAI", alias="APP_NAME")
    app_env: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        alias="APP_ENV",
    )
    debug: bool = Field(default=False, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    password_reset_expire_minutes: int = Field(default=60, alias="PASSWORD_RESET_EXPIRE_MINUTES")
    email_verification_expire_hours: int = Field(default=24, alias="EMAIL_VERIFICATION_EXPIRE_HOURS")
    auth_frontend_url: str = Field(default="http://localhost:5173", alias="AUTH_FRONTEND_URL")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    allowed_origins: str = Field(
        default="http://localhost:3000",
        alias="ALLOWED_ORIGINS",
    )

    # PostgreSQL
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_user: str = Field(default="astroguru", alias="POSTGRES_USER")
    postgres_password: str = Field(default="astroguru", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="astroguru_db", alias="POSTGRES_DB")
    database_url: PostgresDsn | None = Field(default=None, alias="DATABASE_URL")

    # Redis (future-ready)
    redis_enabled: bool = Field(default=False, alias="REDIS_ENABLED")
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: str | None = Field(default=None, alias="REDIS_PASSWORD")
    redis_url: RedisDsn | None = Field(default=None, alias="REDIS_URL")

    # Gemini API (future-ready)
    gemini_enabled: bool = Field(default=False, alias="GEMINI_ENABLED")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")
    gemini_max_retries: int = Field(default=3, alias="GEMINI_MAX_RETRIES")
    gemini_retry_delay: float = Field(default=1.0, alias="GEMINI_RETRY_DELAY")
    gemini_rpm_limit: int = Field(default=30, alias="GEMINI_RPM_LIMIT")
    gemini_max_output_tokens: int = Field(default=8192, alias="GEMINI_MAX_OUTPUT_TOKENS")
    gemini_temperature: float = Field(default=0.4, alias="GEMINI_TEMPERATURE")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: Literal["json", "text"] = Field(default="json", alias="LOG_FORMAT")

    # Paths
    knowledgebase_path: str = Field(default="knowledgebase", alias="KNOWLEDGEBASE_PATH")
    reports_output_path: str = Field(default="reports/generated", alias="REPORTS_OUTPUT_PATH")
    pdf_templates_path: str = Field(default="pdf_templates", alias="PDF_TEMPLATES_PATH")
    prompts_path: str = Field(default="prompts", alias="PROMPTS_PATH")
    rule_studio_data_path: str = Field(default="rule_studio_data", alias="RULE_STUDIO_DATA_PATH")
    case_learning_data_path: str = Field(default="case_learning_data", alias="CASE_LEARNING_DATA_PATH")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_database_uri(self) -> str:
        """Resolved async SQLAlchemy connection string."""
        if self.database_url:
            url = str(self.database_url)
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_sync_database_uri(self) -> str:
        """Resolved sync SQLAlchemy connection string (Alembic)."""
        async_uri = self.sqlalchemy_database_uri
        return async_uri.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def resolved_redis_url(self) -> str | None:
        """Resolved Redis URL when Redis is enabled."""
        if not self.redis_enabled:
            return None
        if self.redis_url:
            return str(self.redis_url)
        password = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        """Parsed CORS allowed origins."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton for dependency injection."""
    return Settings()
