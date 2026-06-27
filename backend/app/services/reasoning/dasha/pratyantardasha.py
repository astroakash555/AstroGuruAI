"""Pratyantardasha interpretation for the Dasha intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.dasha.constants import (
    DashaObservationCategory,
    PLANET_DASHA_THEMES,
)
from backend.app.services.reasoning.dasha.models import DashaChartContext, ReasoningObservation, make_observation


def analyze_pratyantardasha(context: DashaChartContext) -> tuple[ReasoningObservation, ...]:
    """Interpret the active pratyantardasha for near-term event modulation."""
    period = context.active_period("pratyantar")
    if period is None:
        return ()

    lord = period.lord
    ad_lord = context.active_period("antardasha")
    ad_name = ad_lord.lord if ad_lord is not None else "the antardasha lord"
    theme = PLANET_DASHA_THEMES.get(lord, "immediate triggers linked to the pratyantar lord")

    occupied_house = context.house_of(lord)
    houses = context.houses_ruled(lord)
    affected_houses: list[int] = list(houses)
    if occupied_house is not None and occupied_house not in affected_houses:
        affected_houses.append(occupied_house)

    planets: list[str] = [lord]
    if ad_lord is not None and ad_lord.lord not in planets:
        planets.insert(0, ad_lord.lord)

    return (
        make_observation(
            observation_id=f"dasha-pratyantar-{lord.lower()}",
            category=DashaObservationCategory.PRATYANTAR,
            title=f"Active Pratyantardasha: {lord}",
            explanation=(
                f"Under {ad_name} antardasha, {lord} pratyantardasha is active. "
                f"Near-term events lean toward {theme}."
            ),
            affected_planets=tuple(planets),
            affected_houses=tuple(sorted(affected_houses)),
            severity=0.62,
            confidence=0.84,
            metadata={
                "level": "pratyantar",
                "lord": lord,
                "antardasha_lord": ad_lord.lord if ad_lord else None,
                "system": context.dasha.system,
                "occupied_house": occupied_house,
                "ruled_houses": houses,
                "start": period.start.isoformat() if period.start else None,
                "end": period.end.isoformat() if period.end else None,
            },
        ),
    )
