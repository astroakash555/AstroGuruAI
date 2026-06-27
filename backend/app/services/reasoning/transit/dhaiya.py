"""Saturn Dhaiya detection for the transit intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.transit.constants import (
    DHAIYA_HOUSES_FROM_MOON,
    TransitObservationCategory,
)
from backend.app.services.reasoning.transit.models import ReasoningObservation, TransitChartContext, make_observation

DHAIYA_PHASES: dict[int, str] = {
    4: "kantaka",
    8: "ashtama",
}


def analyze_dhaiya(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Detect Saturn Dhaiya when Saturn transits 4th or 8th from Moon."""
    if not context.has_transit("Saturn"):
        return ()

    saturn = context.get_transit("Saturn")
    if saturn.house_from_moon not in DHAIYA_HOUSES_FROM_MOON:
        return ()

    phase = DHAIYA_PHASES.get(saturn.house_from_moon, "dhaiya")
    houses = tuple(
        house
        for house in (saturn.house_from_moon, saturn.house_from_lagna)
        if house is not None
    )

    return (
        make_observation(
            observation_id=f"transit-dhaiya-{phase}",
            category=TransitObservationCategory.DHAIYA,
            title=f"Saturn Dhaiya ({phase.title()} Shani) Active",
            explanation=(
                f"Saturn transits house {saturn.house_from_moon} from Moon, activating "
                f"{phase} Shani pressure on home, mind, and endurance themes."
            ),
            affected_planets=("Saturn", "Moon"),
            affected_houses=houses,
            severity=0.78,
            confidence=0.88,
            metadata={
                "phase": phase,
                "house_from_moon": saturn.house_from_moon,
                "house_from_lagna": saturn.house_from_lagna,
                "sign": saturn.sign_name,
                "is_retrograde": saturn.is_retrograde,
            },
        ),
    )
