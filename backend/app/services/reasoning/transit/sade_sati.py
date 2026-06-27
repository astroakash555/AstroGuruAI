"""Sade Sati detection for the transit intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.transit.constants import (
    SADE_SATI_HOUSES_FROM_MOON,
    TransitObservationCategory,
)
from backend.app.services.reasoning.transit.models import ReasoningObservation, TransitChartContext, make_observation

SADE_SATI_PHASES: dict[int, str] = {
    12: "rising",
    1: "peak",
    2: "setting",
}


def analyze_sade_sati(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Detect active Sade Sati when Saturn transits 12th, 1st, or 2nd from Moon."""
    if not context.has_transit("Saturn"):
        return ()

    saturn = context.get_transit("Saturn")
    if saturn.house_from_moon not in SADE_SATI_HOUSES_FROM_MOON:
        return ()

    phase = SADE_SATI_PHASES.get(saturn.house_from_moon, "active")
    houses = tuple(
        house
        for house in (saturn.house_from_moon, saturn.house_from_lagna)
        if house is not None
    )

    return (
        make_observation(
            observation_id=f"transit-sade-sati-{phase}",
            category=TransitObservationCategory.SADE_SATI,
            title=f"Sade Sati {phase.title()} Phase Active",
            explanation=(
                f"Saturn transits house {saturn.house_from_moon} from Moon, indicating the "
                f"{phase} phase of Sade Sati with karmic pressure on emotional and material stability."
            ),
            affected_planets=("Saturn", "Moon"),
            affected_houses=houses,
            severity=0.82,
            confidence=0.90,
            metadata={
                "phase": phase,
                "house_from_moon": saturn.house_from_moon,
                "house_from_lagna": saturn.house_from_lagna,
                "sign": saturn.sign_name,
                "is_retrograde": saturn.is_retrograde,
            },
        ),
    )
