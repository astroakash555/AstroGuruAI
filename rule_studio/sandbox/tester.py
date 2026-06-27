"""Rule testing sandbox."""

from __future__ import annotations

from typing import Any

from rule_studio.constants import SANDBOX_PASS_THRESHOLD
from rule_studio.types import ExpertRule, SandboxTestResult


def test_rule_in_sandbox(
    rule: ExpertRule,
    sample_context: dict[str, Any] | None = None,
) -> SandboxTestResult:
    context = sample_context or _default_sample_context()
    matched: list[str] = []
    unmatched: list[str] = []
    audit: list[dict[str, str]] = []

    conditions = rule.conditions
    chart_planets = _extract_planets(context)
    chart_houses = _extract_houses(context)
    dasha_lords = _extract_dasha_lords(context)
    transits = _extract_transits(context)

    if conditions.planets:
        overlap = set(conditions.planets) & chart_planets
        if overlap:
            matched.append(f"planets:{','.join(sorted(overlap))}")
            audit.append({"check": "planets", "result": "matched", "detail": ",".join(sorted(overlap))})
        else:
            unmatched.append("planets")
            audit.append({"check": "planets", "result": "unmatched"})

    if conditions.houses:
        overlap = set(conditions.houses) & chart_houses
        if overlap:
            matched.append(f"houses:{','.join(str(item) for item in sorted(overlap))}")
            audit.append({"check": "houses", "result": "matched"})
        else:
            unmatched.append("houses")
            audit.append({"check": "houses", "result": "unmatched"})

    if conditions.dasha_lords:
        overlap = set(conditions.dasha_lords) & dasha_lords
        if overlap:
            matched.append(f"dasha_lords:{','.join(sorted(overlap))}")
            audit.append({"check": "dasha_lords", "result": "matched"})
        else:
            unmatched.append("dasha_lords")
            audit.append({"check": "dasha_lords", "result": "unmatched"})

    if conditions.transits:
        overlap = set(conditions.transits) & transits
        if overlap:
            matched.append(f"transits:{','.join(sorted(overlap))}")
            audit.append({"check": "transits", "result": "matched"})
        else:
            unmatched.append("transits")
            audit.append({"check": "transits", "result": "unmatched"})

    total_checks = len(matched) + len(unmatched)
    match_score = len(matched) / total_checks if total_checks else 0.0
    match_score = round(match_score * rule.weight * rule.confidence, 4)
    passed = match_score >= SANDBOX_PASS_THRESHOLD

    return SandboxTestResult(
        rule_id=rule.rule_id,
        passed=passed,
        match_score=match_score,
        matched_conditions=tuple(matched),
        unmatched_conditions=tuple(unmatched),
        sample_context=context,
        audit=tuple(audit),
    )


def _default_sample_context() -> dict[str, Any]:
    return {
        "kundali": {
            "planets": [
                {"name": "Saturn", "house": 7},
                {"name": "Mars", "house": 8},
                {"name": "Venus", "house": 7},
            ]
        },
        "dasha": {"current": {"mahadasha": {"lord": "Saturn"}, "antardasha": {"lord": "Venus"}}},
        "transits": {
            "saturn": {"natal_impacts": [{"impact_type": "sade_sati_phase"}]},
        },
        "problem_analysis": {"category": {"category": "marriage"}},
    }


def _extract_planets(context: dict[str, Any]) -> set[str]:
    planets: set[str] = set()
    for planet in context.get("kundali", {}).get("planets", []):
        if planet.get("name"):
            planets.add(planet["name"])
    for planet in context.get("astro_intelligence", {}).get("root_cause_planets", []):
        planets.add(planet)
    return planets


def _extract_houses(context: dict[str, Any]) -> set[int]:
    houses: set[int] = set()
    for planet in context.get("kundali", {}).get("planets", []):
        if planet.get("house") is not None:
            houses.add(int(planet["house"]))
    for house in context.get("astro_intelligence", {}).get("affected_houses", []):
        houses.add(int(house))
    return houses


def _extract_dasha_lords(context: dict[str, Any]) -> set[str]:
    lords: set[str] = set()
    current = context.get("dasha", {}).get("current", {})
    for key in ("mahadasha", "antardasha"):
        period = current.get(key)
        if period and period.get("lord"):
            lords.add(period["lord"])
    return lords


def _extract_transits(context: dict[str, Any]) -> set[str]:
    indicators: set[str] = set()
    for key in ("saturn", "jupiter", "rahu", "ketu"):
        for impact in context.get("transits", {}).get(key, {}).get("natal_impacts", []):
            if impact.get("impact_type"):
                indicators.add(impact["impact_type"])
    return indicators
