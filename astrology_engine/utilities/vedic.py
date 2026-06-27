"""Vedic astrology helper functions."""

from __future__ import annotations

from astrology_engine.core.constants import (
    DEGREES_PER_NAKSHATRA,
    DEGREES_PER_NAVAMSHA,
    DEGREES_PER_SIGN,
    NAKSHATRA_LORDS,
    NAKSHATRA_NAMES,
    NUM_SIGNS,
    SIGN_LORDS,
    SIGN_NAMES_EN,
    SIGN_NAMES_SA,
)
from astrology_engine.core.types import NakshatraInfo, ZodiacSign
from astrology_engine.utilities.angles import get_degree_in_sign, get_sign_index, normalize_longitude


def get_zodiac_sign(longitude: float) -> ZodiacSign:
    """Build zodiac sign metadata from sidereal longitude."""
    normalized = normalize_longitude(longitude)
    index = get_sign_index(normalized)
    return ZodiacSign(
        index=index,
        name_en=SIGN_NAMES_EN[index],
        name_sa=SIGN_NAMES_SA[index],
        lord=SIGN_LORDS[index],
        degree_in_sign=get_degree_in_sign(normalized),
    )


def get_nakshatra(longitude: float) -> NakshatraInfo:
    """Compute nakshatra and pada from sidereal longitude."""
    normalized = normalize_longitude(longitude)
    index = int(normalized // DEGREES_PER_NAKSHATRA) % len(NAKSHATRA_NAMES)
    offset_in_nakshatra = normalized % DEGREES_PER_NAKSHATRA
    pada = int(offset_in_nakshatra // (DEGREES_PER_NAKSHATRA / 4.0)) + 1
    pada = min(max(pada, 1), 4)
    return NakshatraInfo(
        index=index,
        name=NAKSHATRA_NAMES[index],
        lord=NAKSHATRA_LORDS[index],
        pada=pada,
    )


def get_whole_sign_house(planet_sign: int, lagna_sign: int) -> int:
    """Return whole-sign house number (1-12) for a planet sign relative to lagna."""
    return ((planet_sign - lagna_sign) % NUM_SIGNS) + 1


def get_navamsha_sign_index(longitude: float) -> int:
    """
    Compute D9 navamsha sign index using Parashari rules.

    Movable signs start from the same sign, fixed from the 9th, dual from the 5th.
    """
    normalized = normalize_longitude(longitude)
    sign_index = get_sign_index(normalized)
    degree_in_sign = get_degree_in_sign(normalized)
    navamsha_part = min(8, int((degree_in_sign * 9.0) / DEGREES_PER_SIGN))

    if sign_index % 3 == 0:
        start_sign = sign_index
    elif sign_index % 3 == 1:
        start_sign = (sign_index + 8) % NUM_SIGNS
    else:
        start_sign = (sign_index + 4) % NUM_SIGNS

    return (start_sign + navamsha_part) % NUM_SIGNS


def get_navamsha_longitude(sign_index: int, degree_in_sign: float | None = None) -> float:
    """Return representative D9 longitude (midpoint of navamsha division)."""
    if degree_in_sign is None:
        return sign_index * 30.0 + 15.0
    navamsha_part = int(degree_in_sign // DEGREES_PER_NAVAMSHA)
    return sign_index * 30.0 + (navamsha_part + 0.5) * DEGREES_PER_NAVAMSHA


def ketu_longitude(rahu_longitude: float) -> float:
    """Ketu is always 180 degrees opposite Rahu."""
    return normalize_longitude(rahu_longitude + 180.0)
