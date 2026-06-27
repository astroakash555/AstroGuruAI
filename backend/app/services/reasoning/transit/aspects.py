"""Transit aspect analysis for the transit intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.transit.constants import PLANET_ASPECTS, TransitObservationCategory
from backend.app.services.reasoning.transit.models import ReasoningObservation, TransitChartContext, make_observation


def analyze_transit_aspects(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Detect classical transit aspects from transiting grahas to natal placements."""
    observations: list[ReasoningObservation] = []
    seen: set[tuple[str, str, int]] = set()

    for transit_planet, transit in context.transits.items():
        if transit.house_from_lagna is None:
            continue

        aspects = PLANET_ASPECTS.get(transit_planet, frozenset({7}))
        for natal_name, natal in context.natal_planets.items():
            if natal_name in {"Rahu", "Ketu"}:
                continue

            distance = _house_distance(transit.house_from_lagna, natal.house)
            if distance not in aspects:
                continue

            key = (transit_planet, natal_name, distance)
            if key in seen:
                continue
            seen.add(key)

            observations.append(
                make_observation(
                    observation_id=f"transit-aspect-{transit_planet.lower()}-{natal_name.lower()}-{distance}",
                    category=TransitObservationCategory.ASPECT,
                    title=f"Transiting {transit_planet} Aspects Natal {natal_name}",
                    explanation=(
                        f"Transiting {transit_planet} in house {transit.house_from_lagna} "
                        f"aspects natal {natal_name} in house {natal.house} by {distance}th house drishti."
                    ),
                    affected_planets=(transit_planet, natal_name),
                    affected_houses=(transit.house_from_lagna, natal.house),
                    severity=0.70,
                    confidence=0.85,
                    metadata={
                        "transit_planet": transit_planet,
                        "natal_planet": natal_name,
                        "aspect_house_distance": distance,
                        "transit_house": transit.house_from_lagna,
                        "natal_house": natal.house,
                    },
                )
            )

    return tuple(observations)


def _house_distance(from_house: int, to_house: int) -> int:
    return ((to_house - from_house + 12) % 12) + 1
