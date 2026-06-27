"""Zodiac sign calculations."""

from __future__ import annotations

from astrology_engine.core.types import ZodiacSign
from astrology_engine.utilities.vedic import get_zodiac_sign


def resolve_sign(longitude: float) -> ZodiacSign:
    """Resolve full zodiac sign metadata from sidereal longitude."""
    return get_zodiac_sign(longitude)


def sign_name_en(longitude: float) -> str:
    """Return English sign name for a longitude."""
    return resolve_sign(longitude).name_en


def sign_name_sa(longitude: float) -> str:
    """Return Sanskrit sign name for a longitude."""
    return resolve_sign(longitude).name_sa


def sign_lord(longitude: float) -> str:
    """Return planetary lord of the sign occupied by the longitude."""
    return resolve_sign(longitude).lord
