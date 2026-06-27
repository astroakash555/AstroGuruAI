"""Jupiter transit effects for the transit intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.transit.constants import (
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
    TransitObservationCategory,
)
from backend.app.services.reasoning.transit.models import ReasoningObservation, TransitChartContext, make_observation


def analyze_jupiter_transits(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Interpret Jupiter transit effects on growth and opportunity houses."""
    if not context.has_transit("Jupiter"):
        return ()

    jupiter = context.get_transit("Jupiter")
    observations: list[ReasoningObservation] = []

    houses = tuple(
        house
        for house in (jupiter.house_from_lagna, jupiter.house_from_moon)
        if house is not None
    )

    if jupiter.house_from_lagna in KENDRA_HOUSES or jupiter.house_from_moon in KENDRA_HOUSES:
        observations.append(
            make_observation(
                observation_id="transit-jupiter-kendra",
                category=TransitObservationCategory.JUPITER,
                title="Jupiter Kendra Transit",
                explanation=(
                    f"Transiting Jupiter influences a kendra from the chart, supporting "
                    f"growth in visibility, dharma, and structured opportunity."
                ),
                affected_planets=("Jupiter",),
                affected_houses=houses,
                severity=0.74,
                confidence=0.87,
                metadata={"effect": "kendra_blessing", "sign": jupiter.sign_name},
            )
        )

    if jupiter.house_from_lagna in TRIKONA_HOUSES or jupiter.house_from_moon in TRIKONA_HOUSES:
        observations.append(
            make_observation(
                observation_id="transit-jupiter-trikona",
                category=TransitObservationCategory.JUPITER,
                title="Jupiter Trikona Transit",
                explanation=(
                    f"Transiting Jupiter activates a trikona house, favoring fortune, "
                    f"learning, and dharmic expansion."
                ),
                affected_planets=("Jupiter",),
                affected_houses=houses,
                severity=0.72,
                confidence=0.86,
                metadata={"effect": "trikona_blessing", "sign": jupiter.sign_name},
            )
        )

    if not observations:
        observations.append(
            make_observation(
                observation_id="transit-jupiter-general",
                category=TransitObservationCategory.JUPITER,
                title="Jupiter Transit Influence",
                explanation=(
                    f"Transiting Jupiter in {jupiter.sign_name} modulates growth and "
                    f"optimism through its current house placements."
                ),
                affected_planets=("Jupiter",),
                affected_houses=houses,
                severity=0.66,
                confidence=0.84,
                metadata={"effect": "general", "sign": jupiter.sign_name},
            )
        )

    return tuple(observations)
