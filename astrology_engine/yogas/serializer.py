"""Serialize yoga detection results to JSON."""

from __future__ import annotations

from typing import Any

from astrology_engine.yogas.schemas import YogaDetectionJSON
from astrology_engine.yogas.types import YogaDetection, YogaDetectionResult


def _yoga_to_dict(yoga: YogaDetection) -> dict[str, Any]:
    return {
        "yoga_id": yoga.yoga_id,
        "yoga_name": yoga.yoga_name,
        "category": yoga.category,
        "is_present": yoga.is_present,
        "strength": yoga.strength,
        "description": yoga.description,
        "planets_involved": list(yoga.planets_involved),
        "houses_involved": list(yoga.houses_involved),
        "conditions": [
            {"name": c.name, "met": c.met, "detail": c.detail}
            for c in yoga.conditions
        ],
        "evidence": list(yoga.evidence),
    }


def to_json_dict(result: YogaDetectionResult) -> dict[str, Any]:
    """Convert yoga detection result to JSON-serializable dictionary."""
    payload = YogaDetectionJSON(
        detected_at=result.detected_at,
        lagna_sign=result.lagna_sign,
        moon_sign=result.moon_sign,
        yogas=[_yoga_to_dict(yoga) for yoga in result.yogas],
        present_yogas=[_yoga_to_dict(yoga) for yoga in result.present_yogas],
        summary={
            "total_rules": result.summary.total_rules,
            "present_count": result.summary.present_count,
            "absent_count": result.summary.absent_count,
            "average_strength": result.summary.average_strength,
        },
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: YogaDetectionResult, *, indent: int | None = 2) -> str:
    """Convert yoga detection result to formatted JSON string."""
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
