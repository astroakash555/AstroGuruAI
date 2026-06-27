"""KP sub lord analysis for the reasoning intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.kp.constants import KPObservationCategory
from backend.app.services.reasoning.kp.models import KPChartContext, ReasoningObservation, make_observation


def analyze_sub_lords(context: KPChartContext) -> tuple[ReasoningObservation, ...]:
    """Emit structured observations for graha sub-lord placements."""
    observations: list[ReasoningObservation] = []

    for planet_name, planet in context.planets.items():
        same_sub = tuple(
            name
            for name, record in context.planets.items()
            if record.sub_lord == planet.sub_lord
        )
        observations.append(
            make_observation(
                observation_id=f"kp-sub-lord-{planet_name.lower()}",
                category=KPObservationCategory.SUB_LORD,
                title=f"{planet_name} Sub Lord",
                explanation=(
                    f"{planet_name} is ruled by sub lord {planet.sub_lord} "
                    f"under star lord {planet.star_lord} in house {planet.house}."
                ),
                affected_planets=(planet_name, planet.star_lord, planet.sub_lord),
                affected_houses=(planet.house,),
                severity=0.58,
                confidence=0.91,
                metadata={
                    "planet": planet_name,
                    "star_lord": planet.star_lord,
                    "sub_lord": planet.sub_lord,
                    "shared_sub_lord_planets": same_sub,
                },
            )
        )

    for planet_name, planet in context.planets.items():
        if planet.star_lord == planet.sub_lord:
            observations.append(
                make_observation(
                    observation_id=f"kp-sub-lord-own-star-{planet_name.lower()}",
                    category=KPObservationCategory.SUB_LORD,
                    title=f"{planet_name} Own-Star Sub Lord",
                    explanation=(
                        f"{planet_name} occupies its own star lord segment with sub lord "
                        f"{planet.sub_lord}, strengthening direct KP control."
                    ),
                    affected_planets=(planet_name, planet.sub_lord),
                    affected_houses=(planet.house,),
                    severity=0.72,
                    confidence=0.89,
                    metadata={"planet": planet_name, "sub_lord": planet.sub_lord},
                )
            )

    return tuple(observations)
