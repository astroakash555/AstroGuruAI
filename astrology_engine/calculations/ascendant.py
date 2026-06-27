"""Ascendant (Lagna) calculation."""

from __future__ import annotations

from astrology_engine.calculations.ephemeris import EphemerisService
from astrology_engine.core.types import Ascendant, HouseSystemType
from astrology_engine.utilities.angles import normalize_longitude
from astrology_engine.utilities.vedic import get_nakshatra, get_zodiac_sign


def calculate_ascendant(
    ephemeris: EphemerisService,
    julian_day: float,
    latitude: float,
    longitude: float,
    *,
    house_system: HouseSystemType | None = None,
) -> Ascendant:
    """
    Compute sidereal ascendant (Lagna) for the given birth coordinates.

    Uses Swiss Ephemeris house computation; ascendant is taken from the
    1st house cusp for cusp-based systems and from ascmc[0] when available.
    """
    cusps, ascmc = ephemeris.calc_houses_ut(
        julian_day,
        latitude,
        longitude,
        house_system=house_system,
    )

    ascendant_longitude = normalize_longitude(ascmc[0] if ascmc else cusps[1])
    sign = get_zodiac_sign(ascendant_longitude)
    nakshatra = get_nakshatra(ascendant_longitude)

    return Ascendant(
        longitude=ascendant_longitude,
        sign=sign,
        nakshatra=nakshatra,
    )
