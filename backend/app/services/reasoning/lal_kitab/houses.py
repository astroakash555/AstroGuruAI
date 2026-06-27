"""Lal Kitab house-based rules for the reasoning layer."""

from __future__ import annotations

from backend.app.services.reasoning.lal_kitab.constants import HOUSE_THEMES, LalKitabObservationCategory
from backend.app.services.reasoning.lal_kitab.models import LalKitabChartContext, ReasoningObservation, make_observation


def analyze_house_rules(context: LalKitabChartContext) -> tuple[ReasoningObservation, ...]:
    """Emit structured observations for Lal Kitab house-level patterns."""
    observations: list[ReasoningObservation] = []

    for house in range(1, 13):
        occupants = context.planets_in_house(house)
        house_lord = context.house_lord(house)
        theme = HOUSE_THEMES[house]

        observations.append(
            make_observation(
                observation_id=f"lk-house-{house:02d}-profile",
                category=LalKitabObservationCategory.HOUSE,
                title=f"House {house} Lal Kitab Profile",
                explanation=(
                    f"House {house} ({theme}) is ruled by {house_lord} with occupants "
                    f"{', '.join(occupants) or 'none'}."
                ),
                affected_planets=occupants + ((house_lord,) if house_lord in context.planets else ()),
                affected_houses=(house,),
                severity=min(0.42 + (0.06 * len(occupants)), 0.78),
                confidence=0.88,
                metadata={
                    "house_lord": house_lord,
                    "occupants": occupants,
                    "theme": theme,
                    "is_dusthana": context.is_dusthana(house),
                    "is_kendra": context.is_kendra(house),
                },
            )
        )

        if len(occupants) >= 3:
            observations.append(
                make_observation(
                    observation_id=f"lk-house-{house:02d}-crowded",
                    category=LalKitabObservationCategory.HOUSE,
                    title=f"House {house} Crowded Placement",
                    explanation=(
                        f"House {house} holds {len(occupants)} grahas "
                        f"({', '.join(occupants)}), intensifying Lal Kitab house pressure."
                    ),
                    affected_planets=occupants,
                    affected_houses=(house,),
                    severity=min(0.58 + (0.05 * len(occupants)), 0.85),
                    confidence=0.86,
                    metadata={"occupant_count": len(occupants)},
                )
            )

        if context.is_dusthana(house) and occupants:
            observations.append(
                make_observation(
                    observation_id=f"lk-house-{house:02d}-dusthana-activation",
                    category=LalKitabObservationCategory.HOUSE,
                    title=f"Dusthana House {house} Activation",
                    explanation=(
                        f"Dusthana house {house} is occupied by {', '.join(occupants)}, "
                        "activating Lal Kitab obstacle themes for that bhava."
                    ),
                    affected_planets=occupants,
                    affected_houses=(house,),
                    severity=0.72,
                    confidence=0.87,
                    metadata={"dusthana": True},
                )
            )

        lord_house = context.house_of(house_lord) if context.has_planet(house_lord) else None
        if lord_house is not None and context.is_dusthana(lord_house) and context.is_kendra(house):
            observations.append(
                make_observation(
                    observation_id=f"lk-house-{house:02d}-lord-dusthana",
                    category=LalKitabObservationCategory.HOUSE,
                    title=f"House {house} Lord in Dusthana",
                    explanation=(
                        f"Lord of house {house} ({house_lord}) sits in dusthana house {lord_house}, "
                        "creating Lal Kitab strain on the bhava significations."
                    ),
                    affected_planets=(house_lord,),
                    affected_houses=(house, lord_house),
                    severity=0.68,
                    confidence=0.85,
                    metadata={"house_lord": house_lord, "lord_house": lord_house},
                )
            )

    return tuple(observations)
