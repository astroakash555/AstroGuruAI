"""Rahu/Ketu transit effects for the transit intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.transit.constants import (
    DUSTHANA_HOUSES,
    TransitObservationCategory,
)
from backend.app.services.reasoning.transit.models import ReasoningObservation, TransitChartContext, make_observation


def analyze_rahu_ketu_transits(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Interpret nodal axis transit effects."""
    observations: list[ReasoningObservation] = []
    rahu = context.transits.get("Rahu")
    ketu = context.transits.get("Ketu")

    if rahu is not None:
        observations.extend(_node_observations(context, "Rahu", rahu))
    if ketu is not None:
        observations.extend(_node_observations(context, "Ketu", ketu))

    if rahu is not None and ketu is not None:
        observations.append(
            make_observation(
                observation_id="transit-rahu-ketu-axis",
                category=TransitObservationCategory.RAHU_KETU,
                title="Rahu-Ketu Axis Transit",
                explanation=(
                    f"The nodal axis spans {rahu.sign_name} and {ketu.sign_name}, "
                    f"amplifying karmic churn across houses "
                    f"{rahu.house_from_lagna} and {ketu.house_from_lagna} from lagna."
                ),
                affected_planets=("Rahu", "Ketu"),
                affected_houses=tuple(
                    house
                    for house in (
                        rahu.house_from_lagna,
                        ketu.house_from_lagna,
                        rahu.house_from_moon,
                        ketu.house_from_moon,
                    )
                    if house is not None
                ),
                severity=0.80,
                confidence=0.88,
                metadata={
                    "rahu_sign": rahu.sign_name,
                    "ketu_sign": ketu.sign_name,
                    "rahu_house_lagna": rahu.house_from_lagna,
                    "ketu_house_lagna": ketu.house_from_lagna,
                },
            )
        )

    return tuple(observations)


def _node_observations(
    context: TransitChartContext,
    planet: str,
    transit,
) -> tuple[ReasoningObservation, ...]:
    houses = tuple(
        house
        for house in (transit.house_from_lagna, transit.house_from_moon)
        if house is not None
    )
    severity = 0.78
    effect = "general_nodal"
    if transit.house_from_lagna in DUSTHANA_HOUSES:
        severity = 0.82
        effect = "dusthana_nodal"

    return (
        make_observation(
            observation_id=f"transit-{planet.lower()}-effect",
            category=TransitObservationCategory.RAHU_KETU,
            title=f"Transiting {planet} Influence",
            explanation=(
                f"Transiting {planet} in {transit.sign_name} activates sudden change, "
                f"obsession, or detachment themes through houses {', '.join(str(h) for h in houses)}."
            ),
            affected_planets=(planet,),
            affected_houses=houses,
            severity=severity,
            confidence=0.86,
            metadata={
                "planet": planet,
                "sign": transit.sign_name,
                "effect": effect,
                "is_retrograde": transit.is_retrograde,
            },
        ),
    )
