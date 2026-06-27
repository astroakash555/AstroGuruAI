"""Serialize remedy generation output."""

from __future__ import annotations

from typing import Any

from ai_engine.interpreters.remedy.schemas import RemedyGenerationJSON
from ai_engine.interpreters.remedy.types import GeneratedRemedy, RemedyGenerationResult


def _remedy_dict(remedy: GeneratedRemedy) -> dict[str, Any]:
    return {
        "remedy_type": remedy.remedy_type,
        "astrology_system": remedy.astrology_system,
        "title": remedy.title,
        "description": remedy.description,
        "planet": remedy.planet,
        "house": remedy.house,
        "priority": remedy.priority,
        "confidence_score": remedy.confidence_score,
        "expected_effect": remedy.expected_effect,
    }


def to_json_dict(result: RemedyGenerationResult) -> dict[str, Any]:
    payload = RemedyGenerationJSON(
        generated_at=result.generated_at,
        remedies=[_remedy_dict(item) for item in result.remedies],
        summary=result.summary,
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")
