"""Injectable clock implementations for deterministic consultation runs."""

from __future__ import annotations

from datetime import UTC, datetime


class UtcClock:
    """Production clock returning the current UTC time."""

    def now_utc(self) -> datetime:
        return datetime.now(UTC)


class FixedClock:
    """Deterministic clock for tests and replay scenarios."""

    __slots__ = ("_fixed_time",)

    def __init__(self, fixed_time: datetime) -> None:
        self._fixed_time = fixed_time

    def now_utc(self) -> datetime:
        return self._fixed_time
