"""KP star lord analysis."""

from __future__ import annotations

from astrology_engine.core.types import PlanetPosition
from kp_engine.lords import get_star_lord
from kp_engine.types import StarLordAnalysis


def analyze_star_lords(planets: tuple[PlanetPosition, ...]) -> tuple[StarLordAnalysis, ...]:
    """Analyze star lords for all grahas."""
    return tuple(
        StarLordAnalysis(
            planet=planet.name,
            longitude=planet.longitude,
            nakshatra=planet.nakshatra.name,
            star_lord=get_star_lord(planet.longitude),
            house=planet.house,
        )
        for planet in planets
    )
