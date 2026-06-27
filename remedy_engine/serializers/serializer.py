"""Serialize remedy engine outputs to JSON."""

from __future__ import annotations

from typing import Any

from remedy_engine.models.remedy import RemedyMatch, RemedyMatchResult, RemedyRecord
from remedy_engine.serializers.schemas import RemedyKnowledgeJSON, RemedyMatchResultJSON


def _remedy_dict(remedy: RemedyRecord) -> dict[str, Any]:
    return {
        "remedy_id": remedy.remedy_id,
        "remedy_name": remedy.remedy_name,
        "remedy_type": remedy.remedy_type,
        "astrology_system": remedy.astrology_system,
        "planet": remedy.planet,
        "house": remedy.house,
        "severity": remedy.severity,
        "category": remedy.category,
        "description": remedy.description,
        "expected_effect": remedy.expected_effect,
        "confidence_score": remedy.confidence_score,
        "priority": remedy.priority,
    }


def _match_dict(match: RemedyMatch) -> dict[str, Any]:
    return {
        "remedy": _remedy_dict(match.remedy),
        "match_score": match.match_score,
        "match_reasons": list(match.match_reasons),
    }


def remedies_to_json_dict(remedies: tuple[RemedyRecord, ...]) -> dict[str, Any]:
    payload = RemedyKnowledgeJSON(
        remedies=[_remedy_dict(remedy) for remedy in remedies],
        total_count=len(remedies),
        metadata={"source": "remedy_knowledge_engine_v1"},
    )
    return payload.model_dump(mode="json")


def to_json_dict(result: RemedyMatchResult) -> dict[str, Any]:
    payload = RemedyMatchResultJSON(
        matched_remedies=[_match_dict(match) for match in result.matched_remedies],
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: RemedyMatchResult, *, indent: int | None = 2) -> str:
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
