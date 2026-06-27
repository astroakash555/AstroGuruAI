"""Shared helpers for dosha rule implementations."""

from __future__ import annotations

from astrology_engine.doshas.constants import DOSHA_CATEGORIES, SEVERITY_LEVELS
from astrology_engine.doshas.types import DoshaCondition, DoshaDetection


def severity_level(score: float) -> str:
    for label, threshold in SEVERITY_LEVELS:
        if score >= threshold:
            return label
    return "minimal"


def build_detection(
    *,
    dosha_id: str,
    dosha_name: str,
    category_key: str,
    is_present: bool,
    severity: float,
    description: str,
    planets: tuple[str, ...],
    houses: tuple[int, ...],
    conditions: list[DoshaCondition],
    evidence: list[str],
    mitigating_factors: list[str] | None = None,
    subtype: str | None = None,
) -> DoshaDetection:
    score = round(min(max(severity, 0.0), 1.0), 3)
    return DoshaDetection(
        dosha_id=dosha_id,
        dosha_name=dosha_name,
        category=DOSHA_CATEGORIES[category_key],
        is_present=is_present,
        severity=score,
        severity_level=severity_level(score),
        subtype=subtype,
        description=description,
        planets_involved=planets,
        houses_involved=houses,
        conditions=tuple(conditions),
        mitigating_factors=tuple(mitigating_factors or []),
        evidence=tuple(evidence),
    )


def condition(name: str, met: bool, detail: str) -> DoshaCondition:
    return DoshaCondition(name=name, met=met, detail=detail)
