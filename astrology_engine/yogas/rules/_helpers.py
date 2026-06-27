"""Shared helpers for yoga rule implementations."""

from __future__ import annotations

from astrology_engine.yogas.constants import YOGA_CATEGORIES
from astrology_engine.yogas.types import YogaCondition, YogaDetection


def build_detection(
    *,
    yoga_id: str,
    yoga_name: str,
    category_key: str,
    is_present: bool,
    strength: float,
    description: str,
    planets: tuple[str, ...],
    houses: tuple[int, ...],
    conditions: list[YogaCondition],
    evidence: list[str],
) -> YogaDetection:
    return YogaDetection(
        yoga_id=yoga_id,
        yoga_name=yoga_name,
        category=YOGA_CATEGORIES[category_key],
        is_present=is_present,
        strength=round(min(max(strength, 0.0), 1.0), 3),
        description=description,
        planets_involved=planets,
        houses_involved=houses,
        conditions=tuple(conditions),
        evidence=tuple(evidence),
    )


def condition(name: str, met: bool, detail: str) -> YogaCondition:
    return YogaCondition(name=name, met=met, detail=detail)
