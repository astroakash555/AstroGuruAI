"""Angle and longitude utility functions."""

from __future__ import annotations

from astrology_engine.core.constants import DEGREES_PER_SIGN, NUM_SIGNS


def normalize_longitude(longitude: float) -> float:
    """Normalize any longitude to the [0, 360) range."""
    value = longitude % 360.0
    return value + 360.0 if value < 0 else value


def get_sign_index(longitude: float) -> int:
    """Return zodiac sign index (0-11) for a sidereal longitude."""
    return int(normalize_longitude(longitude) // DEGREES_PER_SIGN) % NUM_SIGNS


def get_degree_in_sign(longitude: float) -> float:
    """Return degree position within the current sign (0-30)."""
    return normalize_longitude(longitude) % DEGREES_PER_SIGN


def angular_difference(first: float, second: float) -> float:
    """Return smallest signed angular distance from first to second (-180, 180]."""
    diff = (second - first + 180.0) % 360.0 - 180.0
    return diff


def longitude_in_arc(longitude: float, start: float, end: float) -> bool:
    """Return True when longitude lies on the arc from start to end (clockwise)."""
    longitude = normalize_longitude(longitude)
    start = normalize_longitude(start)
    end = normalize_longitude(end)
    if start <= end:
        return start <= longitude < end
    return longitude >= start or longitude < end


def format_dms(longitude: float) -> str:
    """Format longitude as D°M'S\" within sign."""
    degree_in_sign = get_degree_in_sign(longitude)
    degrees = int(degree_in_sign)
    minutes_float = (degree_in_sign - degrees) * 60.0
    minutes = int(minutes_float)
    seconds = int(round((minutes_float - minutes) * 60.0))
    if seconds == 60:
        minutes += 1
        seconds = 0
    if minutes == 60:
        degrees += 1
        minutes = 0
    return f"{degrees}°{minutes:02d}'{seconds:02d}\""
