"""Lal Kitab planetary combination analysis for the reasoning layer."""

from __future__ import annotations

from backend.app.services.reasoning.lal_kitab.constants import PLANETARY_COMBINATIONS, LalKitabObservationCategory
from backend.app.services.reasoning.lal_kitab.models import LalKitabChartContext, ReasoningObservation, make_observation


def analyze_planetary_combinations(context: LalKitabChartContext) -> tuple[ReasoningObservation, ...]:
    """Detect key Lal Kitab planetary combinations."""
    observations: list[ReasoningObservation] = []

    for template in PLANETARY_COMBINATIONS:
        combination_id = str(template["combination_id"])
        title = str(template["title"])
        planets = tuple(template["planets"])  # type: ignore[arg-type]
        description = str(template["description"])
        is_present, severity, houses = _evaluate_combination(context, combination_id, planets)

        if not is_present:
            continue

        observations.append(
            make_observation(
                observation_id=f"lk-combination-{combination_id}",
                category=LalKitabObservationCategory.COMBINATION,
                title=title,
                explanation=(
                    f"{description} This combination is active in the chart with houses "
                    f"{', '.join(str(house) for house in sorted(houses))} involved."
                ),
                affected_planets=planets,
                affected_houses=houses,
                severity=severity,
                confidence=0.87,
                metadata={
                    "combination_id": combination_id,
                    "houses": houses,
                },
            )
        )

    return tuple(observations)


def _evaluate_combination(
    context: LalKitabChartContext,
    combination_id: str,
    planets: tuple[str, ...],
) -> tuple[bool, float, tuple[int, ...]]:
    """Evaluate whether a Lal Kitab combination is present."""
    if len(planets) != 2:
        return False, 0.0, ()

    first, second = planets
    if not context.has_planet(first) or not context.has_planet(second):
        return False, 0.0, ()

    first_house = context.house_of(first)
    second_house = context.house_of(second)
    houses = tuple(sorted({first_house, second_house}))

    if combination_id == "saturn_rahu":
        same_house = first_house == second_house
        dusthana_pair = first_house in {6, 8, 12} and second_house in {6, 8, 12}
        is_present = same_house or dusthana_pair
        severity = 0.84 if same_house else 0.72
        return is_present, severity, houses

    if combination_id == "mars_saturn":
        same_house = first_house == second_house
        pressure_axis = {first_house, second_house} & {1, 4, 7, 8, 10, 12}
        is_present = same_house or len(pressure_axis) >= 2
        severity = 0.78 if same_house else 0.66
        return is_present, severity, houses

    if combination_id == "sun_moon":
        is_present = first_house == second_house
        return is_present, 0.70, houses

    if combination_id == "venus_mars":
        is_present = first_house == second_house or {first_house, second_house} <= {7, 8}
        severity = 0.76 if first_house == second_house else 0.68
        return is_present, severity, houses

    if combination_id == "jupiter_rahu":
        same_house = first_house == second_house
        dharma_axis = first_house in {9, 12} or second_house in {9, 12}
        is_present = same_house or dharma_axis
        severity = 0.74 if same_house else 0.64
        return is_present, severity, houses

    return False, 0.0, houses
