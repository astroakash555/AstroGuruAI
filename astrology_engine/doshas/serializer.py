"""Serialize dosha detection results to JSON."""

from __future__ import annotations

from typing import Any

from astrology_engine.doshas.schemas import DoshaDetectionJSON
from astrology_engine.doshas.types import DoshaDetection, DoshaDetectionResult


def _dosha_to_dict(dosha: DoshaDetection) -> dict[str, Any]:
    return {
        "dosha_id": dosha.dosha_id,
        "dosha_name": dosha.dosha_name,
        "category": dosha.category,
        "is_present": dosha.is_present,
        "severity": dosha.severity,
        "severity_level": dosha.severity_level,
        "subtype": dosha.subtype,
        "description": dosha.description,
        "planets_involved": list(dosha.planets_involved),
        "houses_involved": list(dosha.houses_involved),
        "conditions": [
            {"name": item.name, "met": item.met, "detail": item.detail}
            for item in dosha.conditions
        ],
        "mitigating_factors": list(dosha.mitigating_factors),
        "evidence": list(dosha.evidence),
    }


def to_json_dict(result: DoshaDetectionResult) -> dict[str, Any]:
    """Convert dosha detection result to JSON-serializable dictionary."""
    payload = DoshaDetectionJSON(
        detected_at=result.detected_at,
        lagna_sign=result.lagna_sign,
        moon_sign=result.moon_sign,
        doshas=[_dosha_to_dict(item) for item in result.doshas],
        present_doshas=[_dosha_to_dict(item) for item in result.present_doshas],
        summary={
            "total_rules": result.summary.total_rules,
            "present_count": result.summary.present_count,
            "absent_count": result.summary.absent_count,
            "average_severity": result.summary.average_severity,
            "highest_severity": result.summary.highest_severity,
        },
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: DoshaDetectionResult, *, indent: int | None = 2) -> str:
    """Convert dosha detection result to formatted JSON string."""
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
