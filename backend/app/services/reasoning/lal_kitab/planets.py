"""Lal Kitab planet-specific interpretation for the reasoning layer."""

from __future__ import annotations

from backend.app.services.reasoning.lal_kitab.constants import (
    PLANET_EFFECT_CODES,
    PLANET_EFFECT_DESCRIPTIONS,
    LalKitabObservationCategory,
)
from backend.app.services.reasoning.lal_kitab.models import LalKitabChartContext, ReasoningObservation, make_observation


def analyze_planet_interpretations(context: LalKitabChartContext) -> tuple[ReasoningObservation, ...]:
    """Emit structured observations for each graha's Lal Kitab house placement."""
    observations: list[ReasoningObservation] = []

    for planet_name, planet in context.planets.items():
        effect_code = PLANET_EFFECT_CODES.get(
            (planet_name, planet.house),
            "general_house_influence",
        )
        effect_description = PLANET_EFFECT_DESCRIPTIONS[effect_code]
        severity = _planet_severity(context, planet_name, planet.house, effect_code)
        confidence = 0.90 if effect_code != "general_house_influence" else 0.84

        observations.append(
            make_observation(
                observation_id=f"lk-planet-{planet_name.lower()}-h{planet.house:02d}",
                category=LalKitabObservationCategory.PLANET,
                title=f"{planet_name} in House {planet.house}",
                explanation=(
                    f"In Lal Kitab, {planet_name} in house {planet.house} ({planet.sign_name}) "
                    f"activates effect '{effect_code}'. {effect_description}"
                ),
                affected_planets=(planet_name,),
                affected_houses=(planet.house,),
                severity=severity,
                confidence=confidence,
                metadata={
                    "planet": planet_name,
                    "sign_name": planet.sign_name,
                    "effect_code": effect_code,
                    "is_dusthana": context.is_dusthana(planet.house),
                    "is_kendra": context.is_kendra(planet.house),
                    "is_retrograde": planet.is_retrograde,
                },
            )
        )

    return tuple(observations)


def _planet_severity(
    context: LalKitabChartContext,
    planet_name: str,
    house: int,
    effect_code: str,
) -> float:
    """Estimate severity for a planet-house Lal Kitab placement."""
    severity = 0.48
    if effect_code != "general_house_influence":
        severity += 0.18
    if context.is_dusthana(house):
        severity += 0.14
    if context.is_kendra(house):
        severity += 0.08
    if planet_name in {"Saturn", "Rahu", "Ketu"} and context.is_dusthana(house):
        severity += 0.06
    return min(severity, 0.88)
