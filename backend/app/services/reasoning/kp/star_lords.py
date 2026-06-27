"""KP star lord analysis for the reasoning intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.kp.constants import KPObservationCategory
from backend.app.services.reasoning.kp.models import KPChartContext, ReasoningObservation, make_observation


def analyze_star_lords(context: KPChartContext) -> tuple[ReasoningObservation, ...]:
    """Emit structured observations for graha star-lord placements."""
    observations: list[ReasoningObservation] = []

    for planet_name, planet in context.planets.items():
        observations.append(
            make_observation(
                observation_id=f"kp-star-lord-{planet_name.lower()}",
                category=KPObservationCategory.STAR_LORD,
                title=f"{planet_name} Star Lord",
                explanation=(
                    f"{planet_name} at {planet.longitude:.2f}° in {planet.sign_name} "
                    f"(house {planet.house}) operates under star lord {planet.star_lord}."
                ),
                affected_planets=(planet_name, planet.star_lord),
                affected_houses=(planet.house,),
                severity=0.55,
                confidence=0.92,
                metadata={
                    "planet": planet_name,
                    "longitude": round(planet.longitude, 4),
                    "nakshatra": planet.nakshatra,
                    "star_lord": planet.star_lord,
                },
            )
        )

    grouped: dict[str, list[str]] = {}
    for planet_name, planet in context.planets.items():
        grouped.setdefault(planet.star_lord, []).append(planet_name)

    for star_lord, planets in sorted(grouped.items()):
        if len(planets) < 2:
            continue
        observations.append(
            make_observation(
                observation_id=f"kp-star-lord-cluster-{star_lord.lower()}",
                category=KPObservationCategory.STAR_LORD,
                title=f"{star_lord} Star Lord Cluster",
                explanation=(
                    f"Multiple grahas ({', '.join(planets)}) share star lord {star_lord}, "
                    "concentrating KP significations for that nakshatra chain."
                ),
                affected_planets=(*planets, star_lord),
                affected_houses=tuple(sorted({context.planets[name].house for name in planets})),
                severity=min(0.5 + (0.08 * len(planets)), 0.85),
                confidence=0.88,
                metadata={"star_lord": star_lord, "planets": planets},
            )
        )

    return tuple(observations)
