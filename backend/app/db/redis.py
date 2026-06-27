"""Redis client factory (future-ready)."""

from typing import TYPE_CHECKING

from backend.app.core.config import Settings, get_settings

if TYPE_CHECKING:
    from redis.asyncio import Redis


_redis_client: "Redis | None" = None


async def get_redis_client(settings: Settings | None = None) -> "Redis | None":
    """
    Return a shared async Redis client when enabled.

    Returns None when Redis is disabled via configuration.
    """
    global _redis_client

    settings = settings or get_settings()
    if not settings.redis_enabled:
        return None

    if _redis_client is None:
        from redis.asyncio import Redis

        _redis_client = Redis.from_url(
            settings.resolved_redis_url or "redis://localhost:6379/0",
            decode_responses=True,
        )

    return _redis_client


async def close_redis_client() -> None:
    """Close the shared Redis connection on application shutdown."""
    global _redis_client

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
