"""Serialize Astro Intelligence output to JSON."""

from __future__ import annotations

from typing import Any

from astro_intelligence.serializers.schemas import AstroIntelligenceJSON
from astro_intelligence.types import AstroIntelligenceResult, PlanetaryConflict, RankedCause


def _conflict_dict(conflict: PlanetaryConflict) -> dict[str, Any]:
    return {
        "planets": list(conflict.planets),
        "conflict_type": conflict.conflict_type,
        "severity": conflict.severity,
        "evidence": list(conflict.evidence),
    }


def _ranked_cause_dict(item: RankedCause) -> dict[str, Any]:
    return {
        "planet": item.planet,
        "severity": item.severity,
        "reasons": list(item.reasons),
    }


def to_json_dict(result: AstroIntelligenceResult) -> dict[str, Any]:
    payload = AstroIntelligenceJSON(
        analyzed_at=result.analyzed_at,
        root_cause_planets=list(result.root_cause_planets),
        supportive_planets=list(result.supportive_planets),
        affected_houses=list(result.affected_houses),
        planetary_conflicts=[_conflict_dict(item) for item in result.planetary_conflicts],
        severity_score=result.severity_score,
        recommended_remedies=list(result.recommended_remedies),
        confidence_score=result.confidence_score,
        ranked_causes=[_ranked_cause_dict(item) for item in result.ranked_causes],
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: AstroIntelligenceResult, *, indent: int | None = 2) -> str:
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
