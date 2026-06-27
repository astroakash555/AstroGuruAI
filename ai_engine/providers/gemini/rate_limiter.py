"""Simple in-memory rate limiter for Gemini requests."""

from __future__ import annotations

import asyncio
import time
from collections import deque


class RateLimiter:
    """Token-bucket style RPM limiter."""

    def __init__(self, requests_per_minute: int = 30) -> None:
        self._limit = max(requests_per_minute, 1)
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            cutoff = now - 60.0
            while self._timestamps and self._timestamps[0] < cutoff:
                self._timestamps.popleft()

            if len(self._timestamps) >= self._limit:
                sleep_for = 60.0 - (now - self._timestamps[0])
                if sleep_for > 0:
                    await asyncio.sleep(sleep_for)
                return await self.acquire()

            self._timestamps.append(time.monotonic())
