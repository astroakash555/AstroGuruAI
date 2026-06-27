"""Datetime conversion utilities for ephemeris calculations."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def resolve_timezone(timezone_name: str) -> timezone:
    """Resolve an IANA timezone name to a tzinfo object."""
    if timezone_name.upper() in {"UTC", "GMT", "ETC/UTC"}:
        return timezone.utc
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Invalid timezone: {timezone_name}") from exc


def ensure_utc(dt: datetime) -> datetime:
    """Return a timezone-aware UTC datetime."""
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware.")
    return dt.astimezone(timezone.utc)


def datetime_to_julian_day(dt: datetime) -> float:
    """Convert a timezone-aware datetime to Universal Time Julian Day."""
    swe = _import_swisseph()
    utc_dt = ensure_utc(dt)
    hour = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + utc_dt.microsecond / 3_600_000_000.0
    )
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour)


def julian_day_to_datetime(julian_day: float) -> datetime:
    """Convert Julian Day (UT) to timezone-aware UTC datetime."""
    swe = _import_swisseph()
    year, month, day, hour = swe.revjul(julian_day, swe.GREG_CAL)
    whole_hours = int(hour)
    minutes = int((hour - whole_hours) * 60.0)
    seconds = int(round(((hour - whole_hours) * 60.0 - minutes) * 60.0))
    if seconds == 60:
        minutes += 1
        seconds = 0
    if minutes == 60:
        whole_hours += 1
        minutes = 0
    return datetime(year, month, day, whole_hours, minutes, seconds, tzinfo=timezone.utc)


def _import_swisseph():
    try:
        import swisseph as swe
    except ImportError as exc:
        raise ImportError(
            "pyswisseph is required for astrology calculations. "
            "Install with: pip install pyswisseph"
        ) from exc
    return swe
