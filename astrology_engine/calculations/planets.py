"""Planetary position calculations using Swiss Ephemeris."""

from __future__ import annotations

from astrology_engine.calculations.ephemeris import EphemerisService
from astrology_engine.core.constants import PLANET_IDS, PLANET_ORDER
from astrology_engine.core.types import PlanetPosition
from astrology_engine.utilities.angles import normalize_longitude
from astrology_engine.utilities.vedic import get_nakshatra, get_zodiac_sign, ketu_longitude


def _build_planet_position(
    name: str,
    longitude: float,
    latitude: float,
    speed: float,
    house: int | None = None,
) -> PlanetPosition:
    return PlanetPosition(
        name=name,
        longitude=normalize_longitude(longitude),
        latitude=latitude,
        speed=speed,
        is_retrograde=speed < 0,
        sign=get_zodiac_sign(longitude),
        nakshatra=get_nakshatra(longitude),
        house=house,
    )


def calculate_planetary_positions(
    ephemeris: EphemerisService,
    julian_day: float,
    *,
    house_map: dict[str, int] | None = None,
) -> tuple[PlanetPosition, ...]:
    """
    Compute sidereal positions for the standard Vedic grahas.

    Includes Rahu (mean/true node) and Ketu (180° opposite Rahu).
    """
    house_map = house_map or {}
    positions: list[PlanetPosition] = []

    planet_ids = dict(PLANET_IDS)
    planet_ids["Rahu"] = ephemeris.node_planet_id()

    for name in PLANET_ORDER:
        if name == "Ketu":
            rahu = next(item for item in positions if item.name == "Rahu")
            longitude = ketu_longitude(rahu.longitude)
            position = _build_planet_position(
                name="Ketu",
                longitude=longitude,
                latitude=-rahu.latitude,
                speed=-rahu.speed,
                house=house_map.get("Ketu"),
            )
            positions.append(position)
            continue

        planet_id = planet_ids[name]
        longitude, latitude, _distance, speed = ephemeris.calc_planet_ut(julian_day, planet_id)
        positions.append(
            _build_planet_position(
                name=name,
                longitude=longitude,
                latitude=latitude,
                speed=speed,
                house=house_map.get(name),
            )
        )

    return tuple(positions)


def get_planet_by_name(
    planets: tuple[PlanetPosition, ...],
    name: str,
) -> PlanetPosition:
    """Return a planet by name or raise KeyError."""
    for planet in planets:
        if planet.name == name:
            return planet
    raise KeyError(f"Planet '{name}' not found.")
