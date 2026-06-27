"""Antardasha interpretation for the Dasha intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.dasha.constants import (
    DashaObservationCategory,
    PLANET_DASHA_THEMES,
)
from backend.app.services.reasoning.dasha.models import DashaChartContext, ReasoningObservation, make_observation


def analyze_antardasha(context: DashaChartContext) -> tuple[ReasoningObservation, ...]:
    """Interpret the active antardasha lord within the running mahadasha."""
    period = context.active_period("antardasha")
    if period is None:
        return ()

    lord = period.lord
    md_lord = context.active_period("mahadasha")
    md_name = md_lord.lord if md_lord is not None else "the mahadasha lord"
    theme = PLANET_DASHA_THEMES.get(lord, "sub-period themes linked to the antardasha lord")

    houses = context.houses_ruled(lord)
    occupied_house = context.house_of(lord)
    affected_houses: list[int] = list(houses)
    if occupied_house is not None and occupied_house not in affected_houses:
        affected_houses.append(occupied_house)

    return (
        make_observation(
            observation_id=f"dasha-antardasha-{lord.lower()}",
            category=DashaObservationCategory.ANTARDASHA,
            title=f"Active Antardasha: {lord}",
            explanation=(
                f"Within {md_name} mahadasha, {lord} antardasha is active. "
                f"The sub-period modulates outcomes toward {theme}."
            ),
            affected_planets=(lord,) if md_lord is None else (md_lord.lord, lord),
            affected_houses=tuple(sorted(affected_houses)),
            severity=0.68,
            confidence=0.88,
            metadata={
                "level": "antardasha",
                "lord": lord,
                "mahadasha_lord": md_lord.lord if md_lord else None,
                "system": context.dasha.system,
                "occupied_house": occupied_house,
                "ruled_houses": houses,
                "start": period.start.isoformat() if period.start else None,
                "end": period.end.isoformat() if period.end else None,
            },
        ),
    )
