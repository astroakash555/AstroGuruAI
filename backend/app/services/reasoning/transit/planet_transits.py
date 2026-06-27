"""Planet transit interpretation for the transit intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.transit.constants import (
    DASHA_TRANSIT_SUPPORT_THRESHOLD,
    PLANET_TRANSIT_THEMES,
    TransitObservationCategory,
)
from backend.app.services.reasoning.transit.models import ReasoningObservation, TransitChartContext, make_observation


def analyze_planet_transits(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Interpret each active transiting graha."""
    observations: list[ReasoningObservation] = []

    for planet, transit in context.transits.items():
        theme = PLANET_TRANSIT_THEMES.get(planet, "general transit effects")
        houses = tuple(
            house
            for house in (transit.house_from_lagna, transit.house_from_moon)
            if house is not None
        )
        retrograde_note = " Retrograde motion intensifies internalized results." if transit.is_retrograde else ""

        observations.append(
            make_observation(
                observation_id=f"transit-planet-{planet.lower()}",
                category=TransitObservationCategory.PLANET_TRANSIT,
                title=f"Transiting {planet} in {transit.sign_name}",
                explanation=(
                    f"Transiting {planet} occupies {transit.sign_name}, activating themes of "
                    f"{theme}.{retrograde_note}"
                ),
                affected_planets=(planet,),
                affected_houses=houses,
                severity=0.68 if planet in {"Saturn", "Rahu", "Ketu"} else 0.62,
                confidence=0.86,
                metadata={
                    "planet": planet,
                    "sign": transit.sign_name,
                    "house_from_lagna": transit.house_from_lagna,
                    "house_from_moon": transit.house_from_moon,
                    "is_retrograde": transit.is_retrograde,
                },
            )
        )

    return tuple(observations)


def analyze_dasha_transit_interaction(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Score interaction between active dasha lords and current transits."""
    dasha_lords = context.active_dasha_lords()
    if not dasha_lords:
        return ()

    observations: list[ReasoningObservation] = []

    for lord in dasha_lords:
        if not context.has_transit(lord):
            continue

        transit = context.get_transit(lord)
        natal_house = context.natal_house(lord)
        score = 0.45
        evidence: list[str] = [f"{lord} is both an active dasha lord and current transiting graha."]

        if natal_house is not None and transit.house_from_lagna == natal_house:
            score += 0.25
            evidence.append(f"Transit {lord} re-activates natal house {natal_house}.")

        md = context.active_period("mahadasha")
        if md is not None and md.lord == lord:
            score += 0.15
            evidence.append(f"{lord} mahadasha aligns with the same transiting graha.")

        score = min(score, 1.0)
        is_supported = score >= DASHA_TRANSIT_SUPPORT_THRESHOLD

        observations.append(
            make_observation(
                observation_id=f"transit-dasha-interaction-{lord.lower()}",
                category=TransitObservationCategory.DASHA_INTERACTION,
                title=f"Dasha-Transit Convergence: {lord}",
                explanation=(
                    f"Active dasha and transit converge on {lord} with interaction score "
                    f"{score:.2f}. {'; '.join(evidence)}"
                ),
                affected_planets=(lord,),
                affected_houses=tuple(
                    house
                    for house in (transit.house_from_lagna, natal_house)
                    if house is not None
                ),
                severity=score,
                confidence=0.89 if is_supported else 0.82,
                metadata={
                    "dasha_lord": lord,
                    "interaction_score": score,
                    "is_supported": is_supported,
                    "evidence": tuple(evidence),
                },
            )
        )

    for lord in dasha_lords:
        if context.has_transit(lord):
            continue
        for transit_planet, transit in context.transits.items():
            if not context.has_natal(lord):
                continue
            natal = context.natal_planets[lord]
            if transit.sign_index != natal.sign_index:
                continue

            observations.append(
                make_observation(
                    observation_id=f"transit-dasha-overlay-{lord.lower()}-{transit_planet.lower()}",
                    category=TransitObservationCategory.DASHA_INTERACTION,
                    title=f"Dasha Lord {lord} Triggered by Transiting {transit_planet}",
                    explanation=(
                        f"Transiting {transit_planet} crosses the natal sign of dasha lord "
                        f"{lord}, linking dasha timing with transit activation."
                    ),
                    affected_planets=(lord, transit_planet),
                    affected_houses=tuple(
                        house
                        for house in (natal.house, transit.house_from_lagna)
                        if house is not None
                    ),
                    severity=0.72,
                    confidence=0.85,
                    metadata={
                        "dasha_lord": lord,
                        "transit_planet": transit_planet,
                        "natal_sign": natal.sign_name,
                    },
                )
            )

    return tuple(observations)
