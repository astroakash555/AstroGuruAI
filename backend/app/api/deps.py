"""Shared FastAPI dependencies."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import Settings, get_settings
from backend.app.db.redis import get_redis_client
from backend.app.db.session import get_db_session


async def get_settings_dep() -> Settings:
    """Inject application settings."""
    return get_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Inject async database session."""
    async for session in get_db_session():
        yield session


async def get_redis(settings: Settings = Depends(get_settings_dep)):
    """Inject Redis client when enabled."""
    return await get_redis_client(settings)
