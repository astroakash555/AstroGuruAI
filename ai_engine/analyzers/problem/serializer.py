"""Serialize problem analysis results to JSON."""

from __future__ import annotations

from typing import Any

from ai_engine.analyzers.problem.schemas import ProblemAnalysisJSON
from ai_engine.analyzers.problem.types import ProblemAnalysisResult


def to_json_dict(result: ProblemAnalysisResult) -> dict[str, Any]:
    """Convert analysis result to JSON-serializable dictionary."""
    payload = ProblemAnalysisJSON(
        original_text=result.original_text,
        normalized_text=result.normalized_text,
        category={
            "category": result.category.category.value,
            "label": result.category.label,
            "confidence": result.category.confidence,
        },
        alternative_categories=[
            {
                "category": match.category.value,
                "label": match.label,
                "confidence": match.confidence,
            }
            for match in result.alternative_categories
        ],
        houses={
            "primary": list(result.houses.primary),
            "secondary": list(result.houses.secondary),
            "supporting": list(result.houses.supporting),
            "all_houses": list(result.houses.all_houses),
        },
        planets={
            "primary": list(result.planets.primary),
            "secondary": list(result.planets.secondary),
            "shadow": list(result.planets.shadow),
            "all_planets": list(result.planets.all_planets),
        },
        severity={
            "score": result.severity.score,
            "level": result.severity.level,
            "signals": list(result.severity.signals),
        },
        root_cause_indicators=[
            {
                "indicator": item.indicator,
                "relevance": item.relevance,
                "source": item.source,
            }
            for item in result.root_cause_indicators
        ],
        analysis_notes=list(result.analysis_notes),
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: ProblemAnalysisResult, *, indent: int | None = 2) -> str:
    """Convert analysis result to formatted JSON string."""
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
