"""Analytics constants and shared helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Final

DEFAULT_COUNT: Final[int] = 0
DEFAULT_AMOUNT_PAISE: Final[int] = 0
DEFAULT_RATE: Final[float] = 0.0
UNKNOWN_LABEL: Final[str] = "unknown"

METRIC_LABEL_TOTAL_USERS: Final[str] = "total_users"
METRIC_LABEL_ACTIVE_USERS: Final[str] = "active_users"
METRIC_LABEL_VERIFIED_USERS: Final[str] = "verified_users"
METRIC_LABEL_TOTAL_CLIENTS: Final[str] = "total_clients"
METRIC_LABEL_TOTAL_REPORTS: Final[str] = "total_reports"
METRIC_LABEL_TOTAL_CHAT_QUERIES: Final[str] = "total_chat_queries"
METRIC_LABEL_TOTAL_REVENUE_PAISE: Final[str] = "total_revenue_paise"
METRIC_LABEL_ACTIVE_SUBSCRIPTIONS: Final[str] = "active_subscriptions"
METRIC_LABEL_CAPTURED_PAYMENTS: Final[str] = "captured_payments"


def utc_now() -> datetime:
    """Return the current UTC timestamp for analytics snapshots."""
    return datetime.now(UTC)


def period_start_datetime(period_start: date) -> datetime:
    """Convert a billing period start date to a timezone-aware UTC datetime."""
    return datetime.combine(period_start, datetime.min.time(), tzinfo=UTC)


def safe_rate(numerator: int | float, denominator: int) -> float:
    """Return a ratio in the range [0.0, inf), defaulting to 0 when empty."""
    if denominator <= DEFAULT_COUNT:
        return DEFAULT_RATE
    return float(numerator) / float(denominator)


def safe_average(total: int, count: int) -> float:
    """Return an arithmetic mean, defaulting to 0 when there are no items."""
    if count <= DEFAULT_COUNT:
        return DEFAULT_RATE
    return float(total) / float(count)


def enum_value_label(value: object | None) -> str:
    """Normalize enum or scalar values into stable analytics labels."""
    if value is None:
        return UNKNOWN_LABEL
    enum_value = getattr(value, "value", value)
    return str(enum_value)
