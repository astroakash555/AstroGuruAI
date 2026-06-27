"""KP ruling planet analysis for the reasoning intelligence layer."""

from __future__ import annotations

from datetime import datetime

from kp_engine.lords import get_sub_lord

from backend.app.services.reasoning.kp.constants import WEEKDAY_LORDS, KPObservationCategory, lord_of_sign
from backend.app.services.reasoning.kp.models import (
    KPChartContext,
    ReasoningObservation,
    RulingPlanets,
    make_observation,
)


def compute_ruling_planets(context: KPChartContext) -> RulingPlanets | None:
    """Compute classical KP ruling planets for the chart judgement moment."""
    if context.reference_datetime is None:
        return None
    if not context.has_planet("Moon"):
        return None

    moon = context.get_planet("Moon")
    lagna_sign_lord = lord_of_sign(context.lagna_sign_index)
    _, lagna_star_lord, lagna_sub_lord = get_sub_lord(context.lagna_longitude)
    day_lord = _day_lord(context.reference_datetime)
    moon_sign_lord = lord_of_sign(moon.sign_index)

    components = (
        day_lord,
        moon_sign_lord,
        moon.star_lord,
        moon.sub_lord,
        lagna_sign_lord,
        lagna_star_lord,
        lagna_sub_lord,
    )

    return RulingPlanets(
        day_lord=day_lord,
        moon_sign_lord=moon_sign_lord,
        moon_star_lord=moon.star_lord,
        moon_sub_lord=moon.sub_lord,
        lagna_sign_lord=lagna_sign_lord,
        lagna_star_lord=lagna_star_lord,
        lagna_sub_lord=lagna_sub_lord,
        components=components,
        ruling_set=tuple(dict.fromkeys(components)),
    )


def analyze_ruling_planets(context: KPChartContext) -> tuple[ReasoningObservation, ...]:
    """Emit structured observations for ruling planet groups."""
    ruling = context.ruling_planets
    if ruling is None:
        return (
            make_observation(
                observation_id="kp-ruling-planets-unavailable",
                category=KPObservationCategory.RULING_PLANET,
                title="Ruling Planets Unavailable",
                explanation=(
                    "Ruling planets require a reference datetime and Moon placement; "
                    "provide both to enable KP judgement support."
                ),
                severity=0.35,
                confidence=0.95,
                metadata={"available": False},
            ),
        )

    observations: list[ReasoningObservation] = [
        make_observation(
            observation_id="kp-ruling-planets-set",
            category=KPObservationCategory.RULING_PLANET,
            title="KP Ruling Planets",
            explanation=(
                "Classical ruling planets for this judgement moment are "
                f"{', '.join(ruling.ruling_set)}."
            ),
            affected_planets=ruling.ruling_set,
            severity=0.7,
            confidence=0.93,
            metadata={
                "day_lord": ruling.day_lord,
                "moon_sign_lord": ruling.moon_sign_lord,
                "moon_star_lord": ruling.moon_star_lord,
                "moon_sub_lord": ruling.moon_sub_lord,
                "lagna_sign_lord": ruling.lagna_sign_lord,
                "lagna_star_lord": ruling.lagna_star_lord,
                "lagna_sub_lord": ruling.lagna_sub_lord,
            },
        )
    ]

    repeated = _repeated_components(ruling.components)
    if repeated:
        observations.append(
            make_observation(
                observation_id="kp-ruling-planets-reinforced",
                category=KPObservationCategory.RULING_PLANET,
                title="Reinforced Ruling Planet Emphasis",
                explanation=(
                    f"Ruling planet(s) {', '.join(repeated)} appear more than once in the "
                    "judgement set, increasing KP timing weight."
                ),
                affected_planets=tuple(repeated),
                severity=min(0.65 + (0.08 * len(repeated)), 0.9),
                confidence=0.88,
                metadata={"repeated_planets": repeated},
            )
        )

    return tuple(observations)


def _day_lord(reference_datetime: datetime) -> str:
    return WEEKDAY_LORDS[reference_datetime.weekday()]


def _repeated_components(components: tuple[str, ...]) -> tuple[str, ...]:
    counts: dict[str, int] = {}
    for planet in components:
        counts[planet] = counts.get(planet, 0) + 1
    return tuple(sorted(planet for planet, count in counts.items() if count > 1))
