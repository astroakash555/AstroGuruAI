"""Navamsha (D9) divisional chart builder."""

from __future__ import annotations

from astrology_engine.calculations.houses import calculate_whole_sign_houses
from astrology_engine.core.constants import DEGREES_PER_NAVAMSHA
from astrology_engine.core.types import Ascendant, NavamshaChart, PlanetPosition
from astrology_engine.utilities.angles import get_degree_in_sign, normalize_longitude
from astrology_engine.utilities.vedic import (
    get_navamsha_sign_index,
    get_nakshatra,
    get_whole_sign_house,
    get_zodiac_sign,
)


def _build_d9_planet(source: PlanetPosition) -> PlanetPosition:
    navamsha_sign_index = get_navamsha_sign_index(source.longitude)
    degree_in_sign = get_degree_in_sign(source.longitude)
    degree_in_navamsha = degree_in_sign % DEGREES_PER_NAVAMSHA
    navamsha_longitude = normalize_longitude(navamsha_sign_index * 30.0 + degree_in_navamsha)

    sign = get_zodiac_sign(navamsha_longitude)
    sign = type(sign)(
        index=navamsha_sign_index,
        name_en=sign.name_en,
        name_sa=sign.name_sa,
        lord=sign.lord,
        degree_in_sign=degree_in_navamsha,
    )

    return PlanetPosition(
        name=source.name,
        longitude=navamsha_longitude,
        latitude=source.latitude,
        speed=source.speed,
        is_retrograde=source.is_retrograde,
        sign=sign,
        nakshatra=get_nakshatra(source.longitude),
        house=None,
    )


def build_navamsha_chart(
    ascendant: Ascendant,
    planets: tuple[PlanetPosition, ...],
) -> NavamshaChart:
    """
    Build the D9 Navamsha chart from D1 longitudes.

    Uses Parashari navamsha sign rules; whole-sign houses are counted from D9 lagna.
    """
    d9_ascendant_sign = get_navamsha_sign_index(ascendant.longitude)
    d9_ascendant_longitude = normalize_longitude(
        d9_ascendant_sign * 30.0 + get_degree_in_sign(ascendant.longitude) % DEGREES_PER_NAVAMSHA
    )
    d9_ascendant = Ascendant(
        longitude=d9_ascendant_longitude,
        sign=get_zodiac_sign(d9_ascendant_longitude),
        nakshatra=get_nakshatra(ascendant.longitude),
    )

    lagna_sign = d9_ascendant.sign.index
    d9_planets: list[PlanetPosition] = []
    for planet in planets:
        converted = _build_d9_planet(planet)
        house = get_whole_sign_house(converted.sign.index, lagna_sign)
        d9_planets.append(
            PlanetPosition(
                name=converted.name,
                longitude=converted.longitude,
                latitude=converted.latitude,
                speed=converted.speed,
                is_retrograde=converted.is_retrograde,
                sign=converted.sign,
                nakshatra=converted.nakshatra,
                house=house,
            )
        )

    houses = calculate_whole_sign_houses(d9_ascendant)
    return NavamshaChart(
        ascendant=d9_ascendant,
        planets=tuple(d9_planets),
        houses=houses,
    )
