"""Serialize Vedic chart bundles to JSON chart sections."""

from __future__ import annotations

from typing import Any

from astrology_engine.core.types import (
    Ascendant,
    ChartMetadata,
    HouseCusp,
    LagnaKundali,
    NavamshaChart,
    PlanetPosition,
    VedicChartBundle,
    ZodiacSign,
)
from reports.charts.schemas import LagnaKundaliJSON, NavamshaChartJSON


def _sign_dict(sign: ZodiacSign) -> dict[str, Any]:
    return {
        "index": sign.index,
        "name_en": sign.name_en,
        "name_sa": sign.name_sa,
        "lord": sign.lord,
        "degree_in_sign": sign.degree_in_sign,
    }


def _nakshatra_dict(nakshatra) -> dict[str, Any]:
    return {
        "index": nakshatra.index,
        "name": nakshatra.name,
        "lord": nakshatra.lord,
        "pada": nakshatra.pada,
    }


def _planet_dict(planet: PlanetPosition) -> dict[str, Any]:
    return {
        "name": planet.name,
        "longitude": planet.longitude,
        "latitude": planet.latitude,
        "speed": planet.speed,
        "is_retrograde": planet.is_retrograde,
        "sign": _sign_dict(planet.sign),
        "nakshatra": _nakshatra_dict(planet.nakshatra),
        "house": planet.house,
    }


def _ascendant_dict(ascendant: Ascendant) -> dict[str, Any]:
    return {
        "longitude": ascendant.longitude,
        "sign": _sign_dict(ascendant.sign),
        "nakshatra": _nakshatra_dict(ascendant.nakshatra),
    }


def _house_dict(house: HouseCusp) -> dict[str, Any]:
    return {
        "number": house.number,
        "longitude": house.longitude,
        "sign": _sign_dict(house.sign),
    }


def _metadata_dict(metadata: ChartMetadata) -> dict[str, Any]:
    return {
        "julian_day": metadata.julian_day,
        "ayanamsa": metadata.ayanamsa,
        "house_system": metadata.house_system,
        "latitude": metadata.latitude,
        "longitude": metadata.longitude,
        "datetime_utc": metadata.datetime_utc,
    }


def kundali_to_json_dict(
    lagna: LagnaKundali,
    metadata: ChartMetadata,
) -> dict[str, Any]:
    """Serialize D1 lagna kundali to JSON."""
    payload = LagnaKundaliJSON(
        metadata=_metadata_dict(metadata),
        ascendant=_ascendant_dict(lagna.ascendant),
        planets=[_planet_dict(planet) for planet in lagna.planets],
        houses=[_house_dict(house) for house in lagna.houses],
    )
    return payload.model_dump(mode="json")


def navamsha_to_json_dict(
    navamsha: NavamshaChart,
    metadata: ChartMetadata,
) -> dict[str, Any]:
    """Serialize D9 navamsha chart to JSON."""
    payload = NavamshaChartJSON(
        metadata=_metadata_dict(metadata),
        ascendant=_ascendant_dict(navamsha.ascendant),
        planets=[_planet_dict(planet) for planet in navamsha.planets],
        houses=[_house_dict(house) for house in navamsha.houses],
    )
    return payload.model_dump(mode="json")


def charts_from_bundle(bundle: VedicChartBundle) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract kundali and navamsha JSON sections from a chart bundle."""
    return (
        kundali_to_json_dict(bundle.lagna_kundali, bundle.metadata),
        navamsha_to_json_dict(bundle.navamsha_chart, bundle.metadata),
    )
