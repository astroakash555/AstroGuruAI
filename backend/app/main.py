"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import api_router
from backend.app.core.config import get_settings
from backend.app.core.logging import configure_logging, get_logger
from backend.app.core.security import validate_secret_key
from backend.app.db.redis import close_redis_client

settings = get_settings()
configure_logging(settings)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown lifecycle hooks."""
    validate_secret_key(settings)
    logger.info("Starting %s (%s)", settings.app_name, settings.app_env)
    logger.info(
        "Runtime Settings",
        extra={
            "app_env": settings.app_env,
            "debug": settings.debug,
            "quota_enforcement_enabled": settings.quota_enforcement_enabled,
        },
    )
    yield
    await close_redis_client()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Application factory for FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
