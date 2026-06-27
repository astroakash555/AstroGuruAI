"""Mahadasha interpretation for the Dasha intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.dasha.constants import (
    DashaObservationCategory,
    PLANET_DASHA_THEMES,
)
from backend.app.services.reasoning.dasha.models import DashaChartContext, ReasoningObservation, make_observation


def analyze_mahadasha(context: DashaChartContext) -> tuple[ReasoningObservation, ...]:
    """Interpret the active mahadasha lord in chart and timeline context."""
    period = context.active_period("mahadasha")
    if period is None:
        return ()

    lord = period.lord
    theme = PLANET_DASHA_THEMES.get(lord, "karmic themes linked to the dasha lord")
    houses = context.houses_ruled(lord)
    occupied_house = context.house_of(lord)

    affected_houses: list[int] = list(houses)
    if occupied_house is not None and occupied_house not in affected_houses:
        affected_houses.append(occupied_house)

    placement_note = ""
    if occupied_house is not None:
        placement_note = f" It occupies house {occupied_house} in the natal chart."
    if houses:
        placement_note += f" It rules houses {', '.join(str(house) for house in houses)}."

    base_severity = 0.72
    base_confidence = 0.9

    return (
        make_observation(
            observation_id=f"dasha-mahadasha-{lord.lower()}",
            category=DashaObservationCategory.MAHADASHA,
            title=f"Active Mahadasha: {lord}",
            explanation=(
                f"The native is running {lord} mahadasha under {context.dasha.system} dasha. "
                f"This period emphasizes {theme}.{placement_note}"
            ),
            affected_planets=(lord,),
            affected_houses=tuple(sorted(affected_houses)),
            severity=base_severity,
            confidence=base_confidence,
            metadata={
                "level": "mahadasha",
                "lord": lord,
                "system": context.dasha.system,
                "occupied_house": occupied_house,
                "ruled_houses": houses,
                "start": period.start.isoformat() if period.start else None,
                "end": period.end.isoformat() if period.end else None,
            },
        ),
    )
