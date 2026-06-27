"""Retry helpers for Gemini API calls."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    max_retries: int,
    base_delay_seconds: float,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Execute an async operation with exponential backoff retries."""
    attempt = 0
    while True:
        try:
            return await operation()
        except retryable_exceptions as exc:
            attempt += 1
            if attempt > max_retries:
                logger.error("Gemini operation failed after %s retries: %s", max_retries, exc)
                raise
            delay = base_delay_seconds * (2 ** (attempt - 1))
            logger.warning(
                "Gemini operation failed (attempt %s/%s), retrying in %.1fs: %s",
                attempt,
                max_retries,
                delay,
                exc,
            )
            await asyncio.sleep(delay)
