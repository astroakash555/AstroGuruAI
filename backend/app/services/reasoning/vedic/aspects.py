"""Classical Vedic aspect and nodal influence analysis."""

from __future__ import annotations

from backend.app.services.reasoning.vedic.constants import (
    DEFAULT_ASPECTS,
    JUPITER_ASPECTS,
    MARS_ASPECTS,
    NODE_ASPECTS,
    PLANET_ASPECTS,
    SATURN_ASPECTS,
    ObservationCategory,
    VedicChartContext,
    VedicObservation,
    house_distance,
    make_observation,
)


def _ordinal_house(number: int) -> str:
    """Return an ordinal label for a house aspect distance."""
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def analyze_aspects(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    """Detect classical aspects and nodal influences across the chart."""
    observations: list[VedicObservation] = []
    observations.extend(_standard_aspects(context))
    observations.extend(_special_mars_aspects(context))
    observations.extend(_special_jupiter_aspects(context))
    observations.extend(_special_saturn_aspects(context))
    observations.extend(_rahu_ketu_influences(context))
    return tuple(observations)


def _standard_aspects(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    observations: list[VedicObservation] = []

    for source_name, source in context.planets.items():
        aspects = PLANET_ASPECTS.get(source_name, DEFAULT_ASPECTS)
        for target_name, target in context.planets.items():
            if source_name == target_name:
                continue

            distance = house_distance(source.house, target.house)
            if distance not in aspects:
                continue

            is_special_only = source_name in PLANET_ASPECTS and distance != 7
            if is_special_only:
                continue

            observations.append(
                make_observation(
                    observation_id=f"aspect-{source_name.lower()}-{target_name.lower()}-{distance}",
                    category=ObservationCategory.ASPECT,
                    title=f"{source_name} Aspects {target_name}",
                    explanation=(
                        f"{source_name} in house {source.house} casts a {_ordinal_house(distance)}-house "
                        f"aspect on {target_name} in house {target.house}."
                    ),
                    affected_planets=(source_name, target_name),
                    affected_houses=(source.house, target.house),
                    severity=_aspect_severity(source_name, target_name, distance),
                    confidence=0.88,
                    metadata={"aspect_distance": distance, "aspect_type": "standard"},
                )
            )

    return tuple(observations)


def _special_mars_aspects(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    return _special_aspects_for_planet(context, "Mars", MARS_ASPECTS, "mars_special")


def _special_jupiter_aspects(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    return _special_aspects_for_planet(context, "Jupiter", JUPITER_ASPECTS, "jupiter_special")


def _special_saturn_aspects(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    return _special_aspects_for_planet(context, "Saturn", SATURN_ASPECTS, "saturn_special")


def _special_aspects_for_planet(
    context: VedicChartContext,
    source_name: str,
    aspect_set: frozenset[int],
    aspect_type: str,
) -> tuple[VedicObservation, ...]:
    if not context.has_planet(source_name):
        return ()

    source = context.get_planet(source_name)
    special_distances = aspect_set - {7}
    observations: list[VedicObservation] = []

    for target_name, target in context.planets.items():
        if target_name == source_name:
            continue

        distance = house_distance(source.house, target.house)
        if distance not in special_distances:
            continue

        observations.append(
            make_observation(
                observation_id=f"aspect-{aspect_type}-{source_name.lower()}-{target_name.lower()}-{distance}",
                category=ObservationCategory.ASPECT,
                title=f"{source_name} Special {_ordinal_house(distance)} Aspect on {target_name}",
                explanation=(
                    f"{source_name} applies its classical special {_ordinal_house(distance)}-house aspect "
                    f"from house {source.house} onto {target_name} in house {target.house}."
                ),
                affected_planets=(source_name, target_name),
                affected_houses=(source.house, target.house),
                severity=_aspect_severity(source_name, target_name, distance),
                confidence=0.9,
                metadata={"aspect_distance": distance, "aspect_type": aspect_type},
            )
        )

    return tuple(observations)


def _rahu_ketu_influences(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    observations: list[VedicObservation] = []

    for node_name in ("Rahu", "Ketu"):
        if not context.has_planet(node_name):
            continue

        node = context.get_planet(node_name)
        observations.append(
            make_observation(
                observation_id=f"aspect-{node_name.lower()}-placement",
                category=ObservationCategory.ASPECT,
                title=f"{node_name} Axis Influence",
                explanation=(
                    f"{node_name} in {node.sign_name} (house {node.house}) anchors nodal "
                    "karmic themes for the chart."
                ),
                affected_planets=(node_name,),
                affected_houses=(node.house,),
                severity=0.62,
                confidence=0.87,
                metadata={"sign_name": node.sign_name},
            )
        )

        for target_name, target in context.planets.items():
            if target_name in {"Rahu", "Ketu"}:
                continue

            if context.planets_in_same_sign(node_name, target_name):
                observations.append(
                    make_observation(
                        observation_id=f"aspect-{node_name.lower()}-conjunct-{target_name.lower()}",
                        category=ObservationCategory.ASPECT,
                        title=f"{node_name} Conjoins {target_name}",
                        explanation=(
                            f"{node_name} shares {target.sign_name} with {target_name}, "
                            "intensifying karmic amplification of that graha."
                        ),
                        affected_planets=(node_name, target_name),
                        affected_houses=(node.house, target.house),
                        severity=0.68,
                        confidence=0.89,
                        metadata={"influence_type": "conjunction"},
                    )
                )
                continue

            distance = house_distance(node.house, target.house)
            if distance not in NODE_ASPECTS:
                continue

            observations.append(
                make_observation(
                    observation_id=f"aspect-{node_name.lower()}-{target_name.lower()}-{distance}",
                    category=ObservationCategory.ASPECT,
                    title=f"{node_name} Aspects {target_name}",
                    explanation=(
                        f"{node_name} casts a {_ordinal_house(distance)}-house aspect on {target_name}, "
                        "adding obsessive or detaching nodal pressure."
                    ),
                    affected_planets=(node_name, target_name),
                    affected_houses=(node.house, target.house),
                    severity=0.64,
                    confidence=0.86,
                    metadata={"aspect_distance": distance, "influence_type": "aspect"},
                )
            )

    return tuple(observations)


def _aspect_severity(source: str, target: str, distance: int) -> float:
    base = 0.5
    if source in {"Saturn", "Mars", "Rahu", "Ketu"}:
        base += 0.08
    if target in {"Moon", "Sun"}:
        base += 0.04
    if distance in {4, 8, 10}:
        base += 0.06
    return round(min(base, 0.82), 4)
