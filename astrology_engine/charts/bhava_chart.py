"""Bhava (house cusp) chart builder."""

from __future__ import annotations

from astrology_engine.calculations.ephemeris import EphemerisService
from astrology_engine.calculations.houses import (
    assign_cusp_houses,
    calculate_house_cusps,
    group_planets_by_house,
)
from astrology_engine.core.types import Ascendant, BhavaChart, HouseSystemType, PlanetPosition


def build_bhava_chart(
    ephemeris: EphemerisService,
    julian_day: float,
    latitude: float,
    longitude: float,
    ascendant: Ascendant,
    planets: tuple[PlanetPosition, ...],
    *,
    house_system: HouseSystemType = HouseSystemType.SRIPATHI,
) -> BhavaChart:
    """
    Build a bhava chart using cusp-based house boundaries.

    Default house system is Sripati, commonly used for bhava analysis in Vedic astrology.
    """
    house_cusps = calculate_house_cusps(
        ephemeris,
        julian_day,
        latitude,
        longitude,
        house_system=house_system,
    )
    planets_with_houses = assign_cusp_houses(planets, house_cusps)
    return BhavaChart(
        ascendant=ascendant,
        house_cusps=house_cusps,
        planets=planets_with_houses,
        planets_by_house=group_planets_by_house(planets_with_houses),
    )
