"""Tests for analytics constants."""

from __future__ import annotations

from datetime import UTC, date, datetime

from backend.app.services.analytics.constants import (
    DEFAULT_RATE,
    enum_value_label,
    period_start_datetime,
    safe_average,
    safe_rate,
    utc_now,
)
from backend.app.models.enums import UserRole


def test_safe_rate_returns_zero_for_empty_denominator():
    assert safe_rate(5, 0) == DEFAULT_RATE


def test_safe_rate_calculates_ratio():
    assert safe_rate(1, 4) == 0.25


def test_safe_average_returns_zero_for_empty_count():
    assert safe_average(100, 0) == DEFAULT_RATE


def test_safe_average_calculates_mean():
    assert safe_average(10, 4) == 2.5


def test_enum_value_label_handles_enum_and_none():
    assert enum_value_label(UserRole.ADMIN) == "admin"
    assert enum_value_label(None) == "unknown"
    assert enum_value_label("custom") == "custom"


def test_period_start_datetime_is_utc_aware():
    value = period_start_datetime(date(2026, 6, 1))
    assert value.tzinfo == UTC
    assert value.hour == 0


def test_utc_now_is_timezone_aware():
    assert utc_now().tzinfo == UTC
