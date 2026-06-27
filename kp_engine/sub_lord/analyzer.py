"""KP sub lord analysis."""

from __future__ import annotations

from astrology_engine.core.types import PlanetPosition
from kp_engine.lords import get_sub_lord
from kp_engine.types import SubLordAnalysis


def analyze_sub_lords(planets: tuple[PlanetPosition, ...]) -> tuple[SubLordAnalysis, ...]:
    """Analyze sub lords for all grahas."""
    analyses: list[SubLordAnalysis] = []
    for planet in planets:
        nakshatra, star_lord, sub_lord = get_sub_lord(planet.longitude)
        analyses.append(
            SubLordAnalysis(
                planet=planet.name,
                longitude=planet.longitude,
                nakshatra=nakshatra,
                star_lord=star_lord,
                sub_lord=sub_lord,
                house=planet.house,
            )
        )
    return tuple(analyses)
