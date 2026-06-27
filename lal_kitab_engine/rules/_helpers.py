"""Shared helpers for Lal Kitab rules."""

from __future__ import annotations

from lal_kitab_engine.constants import LAL_KITAB_CATEGORIES
from lal_kitab_engine.types import LalKitabCondition, LalKitabFinding


def condition(name: str, met: bool, detail: str) -> LalKitabCondition:
    return LalKitabCondition(name=name, met=met, detail=detail)


def build_finding(
    *,
    finding_id: str,
    finding_name: str,
    category_key: str,
    is_present: bool,
    strength: float,
    description: str,
    planets: tuple[str, ...],
    houses: tuple[int, ...],
    conditions: list[LalKitabCondition],
    evidence: list[str],
    recommendation_ids: tuple[str, ...] = (),
) -> LalKitabFinding:
    return LalKitabFinding(
        finding_id=finding_id,
        finding_name=finding_name,
        category=LAL_KITAB_CATEGORIES[category_key],
        is_present=is_present,
        strength=round(min(max(strength, 0.0), 1.0), 3),
        description=description,
        planets_involved=planets,
        houses_involved=houses,
        conditions=tuple(conditions),
        evidence=tuple(evidence),
        recommendation_ids=recommendation_ids,
    )
