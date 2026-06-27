"""House (Bhava) cusp calculations."""

from __future__ import annotations

import logging

from astrology_engine.calculations.ephemeris import EphemerisService
from astrology_engine.core.constants import NUM_HOUSES
from astrology_engine.core.types import Ascendant, HouseCusp, HouseSystemType, PlanetPosition
from astrology_engine.utilities.angles import longitude_in_arc, normalize_longitude
from astrology_engine.utilities.vedic import get_whole_sign_house, get_zodiac_sign

logger = logging.getLogger(__name__)


def _validate_geographic_coordinates(latitude: float, longitude: float) -> None:
    """Validate latitude and longitude before Swiss Ephemeris house calculations."""
    if not -90.0 <= latitude <= 90.0:
        raise ValueError(
            f"Invalid latitude {latitude}: must be between -90 and 90 degrees."
        )
    if not -180.0 <= longitude <= 180.0:
        raise ValueError(
            f"Invalid longitude {longitude}: must be between -180 and 180 degrees."
        )


def _log_house_cusp_diagnostics(
    *,
    latitude: float,
    longitude: float,
    julian_day: float,
    house_system: HouseSystemType | None,
    cusps: tuple[float, ...],
) -> None:
    logger.debug(
        "House cusp calculation: latitude=%s longitude=%s julian_day=%s "
        "house_system=%s len(cusps)=%s cusps=%s",
        latitude,
        longitude,
        julian_day,
        house_system,
        len(cusps),
        cusps,
    )


def _house_cusp_longitude(cusps: tuple[float, ...], house_number: int) -> float:
    """
    Extract sidereal cusp longitude for a house from a Swiss Ephemeris cusps tuple.

    Swiss Ephemeris C API (and pysweph) return 13 elements: index 0 unused,
    houses 1-12 at indices 1-12. pyswisseph returns 12 elements with houses 1-12
    at indices 0-11.
    """
    if len(cusps) >= NUM_HOUSES + 1:
        index = house_number
    elif len(cusps) == NUM_HOUSES:
        index = house_number - 1
    else:
        raise ValueError(
            f"Swiss Ephemeris returned unexpected cusps tuple length {len(cusps)}; "
            f"expected {NUM_HOUSES} (pyswisseph) or {NUM_HOUSES + 1} (Swiss Ephemeris C API). "
            f"cusps={cusps}"
        )
    return cusps[index]


def calculate_house_cusps(
    ephemeris: EphemerisService,
    julian_day: float,
    latitude: float,
    longitude: float,
    *,
    house_system: HouseSystemType | None = None,
) -> tuple[HouseCusp, ...]:
    """Compute sidereal house cusps using the configured house system."""
    _validate_geographic_coordinates(latitude, longitude)

    cusps, _ascmc = ephemeris.calc_houses_ut(
        julian_day,
        latitude,
        longitude,
        house_system=house_system,
    )

    _log_house_cusp_diagnostics(
        latitude=latitude,
        longitude=longitude,
        julian_day=julian_day,
        house_system=house_system,
        cusps=cusps,
    )

    if len(cusps) not in (NUM_HOUSES, NUM_HOUSES + 1):
        raise ValueError(
            f"Swiss Ephemeris returned unexpected cusps tuple length {len(cusps)}; "
            f"expected {NUM_HOUSES} (pyswisseph) or {NUM_HOUSES + 1} (Swiss Ephemeris C API). "
            f"latitude={latitude} longitude={longitude} julian_day={julian_day} "
            f"house_system={house_system} cusps={cusps}"
        )

    houses: list[HouseCusp] = []
    for house_number in range(1, NUM_HOUSES + 1):
        cusp_longitude = normalize_longitude(_house_cusp_longitude(cusps, house_number))
        sign = get_zodiac_sign(cusp_longitude)
        houses.append(
            HouseCusp(
                number=house_number,
                longitude=cusp_longitude,
                sign=sign,
            )
        )
    return tuple(houses)


def calculate_whole_sign_houses(ascendant: Ascendant) -> tuple[HouseCusp, ...]:
    """Build whole-sign houses where each house equals one complete rashi."""
    lagna_sign = ascendant.sign.index
    houses: list[HouseCusp] = []
    for house_number in range(1, NUM_HOUSES + 1):
        sign_index = (lagna_sign + house_number - 1) % 12
        cusp_longitude = sign_index * 30.0
        houses.append(
            HouseCusp(
                number=house_number,
                longitude=cusp_longitude,
                sign=get_zodiac_sign(cusp_longitude),
            )
        )
    return tuple(houses)


def assign_whole_sign_houses(
    planets: tuple[PlanetPosition, ...],
    ascendant: Ascendant,
) -> tuple[PlanetPosition, ...]:
    """Assign whole-sign house numbers to planets relative to lagna."""
    lagna_sign = ascendant.sign.index
    updated: list[PlanetPosition] = []
    for planet in planets:
        house = get_whole_sign_house(planet.sign.index, lagna_sign)
        updated.append(
            PlanetPosition(
                name=planet.name,
                longitude=planet.longitude,
                latitude=planet.latitude,
                speed=planet.speed,
                is_retrograde=planet.is_retrograde,
                sign=planet.sign,
                nakshatra=planet.nakshatra,
                house=house,
            )
        )
    return tuple(updated)


def assign_cusp_houses(
    planets: tuple[PlanetPosition, ...],
    house_cusps: tuple[HouseCusp, ...],
) -> tuple[PlanetPosition, ...]:
    """Assign planets to bhavas using house cusp boundaries."""
    cusp_longitudes = [item.longitude for item in house_cusps]
    updated: list[PlanetPosition] = []

    for planet in planets:
        house_number = _find_house_for_longitude(planet.longitude, cusp_longitudes)
        updated.append(
            PlanetPosition(
                name=planet.name,
                longitude=planet.longitude,
                latitude=planet.latitude,
                speed=planet.speed,
                is_retrograde=planet.is_retrograde,
                sign=planet.sign,
                nakshatra=planet.nakshatra,
                house=house_number,
            )
        )
    return tuple(updated)


def group_planets_by_house(
    planets: tuple[PlanetPosition, ...],
) -> dict[int, tuple[str, ...]]:
    """Group planet names by assigned house number."""
    grouped: dict[int, list[str]] = {number: [] for number in range(1, NUM_HOUSES + 1)}
    for planet in planets:
        if planet.house is not None:
            grouped[planet.house].append(planet.name)
    return {key: tuple(value) for key, value in grouped.items()}


def _find_house_for_longitude(planet_longitude: float, cusp_longitudes: list[float]) -> int:
    """Locate the house whose cusp arc contains the planet longitude."""
    for index in range(NUM_HOUSES):
        start = cusp_longitudes[index]
        end = cusp_longitudes[(index + 1) % NUM_HOUSES]
        if longitude_in_arc(planet_longitude, start, end):
            return index + 1
    return 1
