"""House transit interpretation for the transit intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.transit.constants import (
    DUSTHANA_HOUSES,
    HOUSE_TRANSIT_THEMES,
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
    TransitObservationCategory,
)
from backend.app.services.reasoning.transit.models import ReasoningObservation, TransitChartContext, make_observation


def analyze_house_transits(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Interpret transits through natal houses from lagna and Moon."""
    observations: list[ReasoningObservation] = []
    activated: set[tuple[int, str]] = set()

    for planet, transit in context.transits.items():
        for reference, house in (("lagna", transit.house_from_lagna), ("moon", transit.house_from_moon)):
            if house is None:
                continue
            key = (house, reference)
            if key in activated:
                continue
            activated.add(key)

            house_type = _house_type_label(house)
            theme = HOUSE_TRANSIT_THEMES.get(house, "themes of the activated bhava")

            observations.append(
                make_observation(
                    observation_id=f"transit-house-{house}-{reference}-{planet.lower()}",
                    category=TransitObservationCategory.HOUSE_TRANSIT,
                    title=f"House {house} Transit from {reference.title()}",
                    explanation=(
                        f"Transiting {planet} activates house {house} ({house_type}) from "
                        f"{reference}, emphasizing {theme}."
                    ),
                    affected_planets=(planet,),
                    affected_houses=(house,),
                    severity=0.70 if house in DUSTHANA_HOUSES else 0.64,
                    confidence=0.84,
                    metadata={
                        "planet": planet,
                        "house": house,
                        "reference": reference,
                        "house_type": house_type,
                    },
                )
            )

    return tuple(observations)


def analyze_natal_overlays(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Detect transiting grahas occupying the same sign as natal planets."""
    observations: list[ReasoningObservation] = []

    for planet, transit in context.transits.items():
        for natal_name, natal in context.natal_planets.items():
            if natal_name in {"Rahu", "Ketu"}:
                continue
            if transit.sign_index != natal.sign_index:
                continue

            observations.append(
                make_observation(
                    observation_id=f"transit-natal-{planet.lower()}-over-{natal_name.lower()}",
                    category=TransitObservationCategory.NATAL_OVERLAY,
                    title=f"Transiting {planet} Over Natal {natal_name}",
                    explanation=(
                        f"Transiting {planet} in {transit.sign_name} conjoins natal {natal_name} "
                        f"by sign, triggering combined transit-natal results."
                    ),
                    affected_planets=(planet, natal_name),
                    affected_houses=tuple(
                        house
                        for house in (transit.house_from_lagna, natal.house)
                        if house is not None
                    ),
                    severity=0.76,
                    confidence=0.87,
                    metadata={
                        "transit_planet": planet,
                        "natal_planet": natal_name,
                        "sign": transit.sign_name,
                        "natal_house": natal.house,
                    },
                )
            )

    return tuple(observations)


def _house_type_label(house: int) -> str:
    if house in KENDRA_HOUSES:
        return "kendra bhava"
    if house in TRIKONA_HOUSES:
        return "trikona bhava"
    if house in DUSTHANA_HOUSES:
        return "dusthana bhava"
    return "upachaya or neutral bhava"
