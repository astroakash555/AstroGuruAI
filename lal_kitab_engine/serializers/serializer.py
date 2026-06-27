"""Serialize Lal Kitab analysis to JSON."""

from __future__ import annotations

from typing import Any

from lal_kitab_engine.serializers.schemas import LalKitabAnalysisJSON
from lal_kitab_engine.types import LalKitabAnalysisResult, LalKitabFinding, PlanetHouseAnalysis


def _condition_dict(condition) -> dict[str, Any]:
    return {"name": condition.name, "met": condition.met, "detail": condition.detail}


def _finding_dict(finding: LalKitabFinding) -> dict[str, Any]:
    return {
        "finding_id": finding.finding_id,
        "finding_name": finding.finding_name,
        "category": finding.category,
        "is_present": finding.is_present,
        "strength": finding.strength,
        "description": finding.description,
        "planets_involved": list(finding.planets_involved),
        "houses_involved": list(finding.houses_involved),
        "conditions": [_condition_dict(item) for item in finding.conditions],
        "evidence": list(finding.evidence),
        "recommendation_ids": list(finding.recommendation_ids),
    }


def _planet_house_dict(item: PlanetHouseAnalysis) -> dict[str, Any]:
    return {
        "planet": item.planet,
        "house": item.house,
        "sign": item.sign,
        "effect_code": item.effect_code,
        "strength": item.strength,
        "conditions": [_condition_dict(condition) for condition in item.conditions],
        "evidence": list(item.evidence),
    }


def to_json_dict(result: LalKitabAnalysisResult) -> dict[str, Any]:
    payload = LalKitabAnalysisJSON(
        analyzed_at=result.analyzed_at,
        lagna_sign=result.lagna_sign,
        planet_by_house=[_planet_house_dict(item) for item in result.planet_by_house],
        rin_findings=[_finding_dict(item) for item in result.rin_findings],
        dosh_findings=[_finding_dict(item) for item in result.dosh_findings],
        recommendations=[_finding_dict(item) for item in result.recommendations],
        summary={
            "total_rules": result.summary.total_rules,
            "present_count": result.summary.present_count,
            "absent_count": result.summary.absent_count,
            "average_strength": result.summary.average_strength,
            "rin_count": result.summary.rin_count,
            "dosh_count": result.summary.dosh_count,
        },
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: LalKitabAnalysisResult, *, indent: int | None = 2) -> str:
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
