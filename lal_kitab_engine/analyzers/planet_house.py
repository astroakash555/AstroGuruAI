"""Planet-by-house Lal Kitab analyzer."""

from __future__ import annotations

from lal_kitab_engine.constants import PLANET_EFFECT_CODES
from lal_kitab_engine.context import LalKitabContext
from lal_kitab_engine.rules._helpers import condition
from lal_kitab_engine.types import PlanetHouseAnalysis


def analyze_planet_by_house(context: LalKitabContext) -> tuple[PlanetHouseAnalysis, ...]:
    """Analyze each graha placement using Lal Kitab house-effect mappings."""
    analyses: list[PlanetHouseAnalysis] = []

    for planet_name, position in context.planets.items():
        house = position.house or 0
        effect_code = PLANET_EFFECT_CODES.get(
            (planet_name, house),
            "general_house_influence",
        )
        strength = _placement_strength(context, planet_name, house)
        conditions = [
            condition(
                "house_placement",
                house > 0,
                f"{planet_name} occupies house {house} in sign {position.sign.name_en}.",
            ),
            condition(
                "dusthana_flag",
                context.is_dusthana(house),
                f"House {house} is dusthana: {context.is_dusthana(house)}.",
            ),
            condition(
                "kendra_flag",
                context.is_kendra(house),
                f"House {house} is kendra: {context.is_kendra(house)}.",
            ),
        ]
        evidence = (
            f"{planet_name} in {position.sign.name_en} at house {house}.",
            f"Effect code: {effect_code}.",
        )
        analyses.append(
            PlanetHouseAnalysis(
                planet=planet_name,
                house=house,
                sign=position.sign.name_en,
                effect_code=effect_code,
                strength=round(strength, 3),
                conditions=tuple(conditions),
                evidence=evidence,
            )
        )

    return tuple(analyses)


def _placement_strength(context: LalKitabContext, planet: str, house: int) -> float:
    strength = 0.45
    if (planet, house) in PLANET_EFFECT_CODES:
        strength += 0.25
    if context.is_dusthana(house):
        strength += 0.15
    if context.is_kendra(house):
        strength += 0.1
    return min(strength, 1.0)
