"""Bhava strength, occupancy, and lordship analysis."""

from __future__ import annotations

from backend.app.services.reasoning.vedic.constants import (
    DUSTHANA_HOUSES,
    KENDRA_HOUSES,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
    SIGN_NAMES,
    TRIKONA_HOUSES,
    ObservationCategory,
    VedicChartContext,
    VedicObservation,
    make_observation,
)
from backend.app.services.reasoning.vedic.planet_strength import classify_dignity


def analyze_houses(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    """Evaluate all twelve houses for strength, occupancy, and influences."""
    observations: list[VedicObservation] = []

    for house in range(1, 13):
        observations.extend(_analyze_single_house(context, house))

    observations.extend(_analyze_house_lord_placements(context))
    return tuple(observations)


def _analyze_single_house(context: VedicChartContext, house: int) -> tuple[VedicObservation, ...]:
    occupants = context.planets_in_house(house)
    house_lord = context.house_lord(house)
    lord_house = context.house_of_planet(house_lord)
    sign_name = context.lagna_sign_name if house == 1 else None
    if sign_name is None:
        sign_index = context.house_sign_index(house)
        sign_name = SIGN_NAMES[sign_index]

    strength_score = _house_strength_score(context, house, occupants, house_lord, lord_house)
    observations: list[VedicObservation] = []

    observations.append(
        make_observation(
            observation_id=f"house-{house:02d}-strength",
            category=ObservationCategory.HOUSE,
            title=f"House {house} Strength Assessment",
            explanation=(
                f"House {house} ({sign_name}) has strength score {strength_score:.2f}. "
                f"Lord {house_lord} occupies house {lord_house}."
                + (" House is unoccupied." if not occupants else f" Occupants: {', '.join(occupants)}.")
            ),
            affected_planets=occupants + (house_lord,),
            affected_houses=(house, lord_house),
            severity=strength_score,
            confidence=0.88,
            metadata={
                "strength_score": strength_score,
                "occupants": occupants,
                "house_lord": house_lord,
                "lord_house": lord_house,
                "sign_name": sign_name,
            },
        )
    )

    if not occupants:
        observations.append(
            make_observation(
                observation_id=f"house-{house:02d}-empty",
                category=ObservationCategory.HOUSE,
                title=f"House {house} Unoccupied",
                explanation=(
                    f"No graha occupies house {house}. Results depend primarily on "
                    f"its lord {house_lord} placed in house {lord_house}."
                ),
                affected_planets=(house_lord,),
                affected_houses=(house, lord_house),
                severity=0.4,
                confidence=0.95,
                metadata={"is_empty": True},
            )
        )

    benefics = tuple(name for name in occupants if name in NATURAL_BENEFICS)
    malefics = tuple(name for name in occupants if name in NATURAL_MALEFICS)

    if benefics:
        observations.append(
            make_observation(
                observation_id=f"house-{house:02d}-benefic-influence",
                category=ObservationCategory.HOUSE,
                title=f"Benefic Influence on House {house}",
                explanation=(
                    f"Natural benefics {', '.join(benefics)} occupy house {house}, "
                    "supporting constructive outcomes for its significations."
                ),
                affected_planets=benefics,
                affected_houses=(house,),
                severity=0.35 + (0.1 * len(benefics)),
                confidence=0.86,
                metadata={"benefics": benefics},
            )
        )

    if malefics:
        observations.append(
            make_observation(
                observation_id=f"house-{house:02d}-malefic-influence",
                category=ObservationCategory.HOUSE,
                title=f"Malefic Influence on House {house}",
                explanation=(
                    f"Natural malefics {', '.join(malefics)} occupy house {house}, "
                    "adding pressure or karmic friction to its themes."
                ),
                affected_planets=malefics,
                affected_houses=(house,),
                severity=0.45 + (0.12 * len(malefics)),
                confidence=0.86,
                metadata={"malefics": malefics},
            )
        )

    return tuple(observations)


def _analyze_house_lord_placements(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    observations: list[VedicObservation] = []

    for house in range(1, 13):
        house_lord = context.house_lord(house)
        lord_house = context.house_of_planet(house_lord)
        dignity = classify_dignity(house_lord, context.sign_of_planet(house_lord))
        placement_quality = _lord_placement_quality(lord_house)

        observations.append(
            make_observation(
                observation_id=f"house-{house:02d}-lord-placement",
                category=ObservationCategory.HOUSE,
                title=f"House {house} Lord Placement",
                explanation=(
                    f"Lord of house {house} ({house_lord}) sits in house {lord_house} "
                    f"with dignity {dignity.value.replace('_', ' ')} and placement quality "
                    f"{placement_quality}."
                ),
                affected_planets=(house_lord,),
                affected_houses=(house, lord_house),
                severity=_lord_severity(dignity.value, placement_quality),
                confidence=0.84,
                metadata={
                    "house_lord": house_lord,
                    "lord_house": lord_house,
                    "dignity": dignity.value,
                    "placement_quality": placement_quality,
                },
            )
        )

    return tuple(observations)


def _house_strength_score(
    context: VedicChartContext,
    house: int,
    occupants: tuple[str, ...],
    house_lord: str,
    lord_house: int,
) -> float:
    score = 0.5

    if house in KENDRA_HOUSES or house in TRIKONA_HOUSES:
        score += 0.1
    if house in DUSTHANA_HOUSES:
        score -= 0.08

    benefic_count = sum(1 for name in occupants if name in NATURAL_BENEFICS)
    malefic_count = sum(1 for name in occupants if name in NATURAL_MALEFICS)
    score += benefic_count * 0.07
    score -= malefic_count * 0.06

    lord_dignity = classify_dignity(house_lord, context.sign_of_planet(house_lord))
    dignity_bonus = {
        "exaltation": 0.15,
        "moolatrikona": 0.12,
        "own_sign": 0.1,
        "friendly_sign": 0.05,
        "neutral_sign": 0.0,
        "enemy_sign": -0.06,
        "debilitation": -0.1,
    }
    score += dignity_bonus.get(lord_dignity.value, 0.0)

    if lord_house in KENDRA_HOUSES or lord_house in TRIKONA_HOUSES:
        score += 0.06
    if lord_house in DUSTHANA_HOUSES:
        score -= 0.08

    if lord_house == house:
        score += 0.05

    return round(min(max(score, 0.1), 0.95), 4)


def _lord_placement_quality(lord_house: int) -> str:
    if lord_house in KENDRA_HOUSES:
        return "kendra"
    if lord_house in TRIKONA_HOUSES:
        return "trikona"
    if lord_house in DUSTHANA_HOUSES:
        return "dusthana"
    return "neutral"


def _lord_severity(dignity: str, placement_quality: str) -> float:
    dignity_scores = {
        "exaltation": 0.82,
        "moolatrikona": 0.78,
        "own_sign": 0.72,
        "friendly_sign": 0.58,
        "neutral_sign": 0.5,
        "enemy_sign": 0.62,
        "debilitation": 0.68,
    }
    placement_scores = {
        "kendra": 0.08,
        "trikona": 0.06,
        "dusthana": -0.1,
        "neutral": 0.0,
    }
    base = dignity_scores.get(dignity, 0.5)
    return round(min(max(base + placement_scores.get(placement_quality, 0.0), 0.2), 0.9), 4)
