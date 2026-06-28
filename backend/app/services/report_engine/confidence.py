"""Fusion confidence helpers for report sections."""

from __future__ import annotations

from typing import Any


def fusion_confidence(unified_report: dict[str, Any]) -> float:
    """Return fusion confidence on a 0.0-1.0 scale."""
    fusion = unified_report.get("fusion") or {}
    if fusion.get("confidence") is not None:
        return max(0.0, min(1.0, float(fusion["confidence"])))

    consultation = unified_report.get("consultation_brain") or {}
    if consultation.get("overall_confidence") is not None:
        return max(0.0, min(1.0, float(consultation["overall_confidence"])))

    summary = unified_report.get("summary") or {}
    reasoning_score = summary.get("reasoning_confidence_score")
    if reasoning_score is not None:
        return max(0.0, min(1.0, float(reasoning_score) / 100.0))

    intelligence = unified_report.get("astro_intelligence") or {}
    if intelligence.get("confidence_score") is not None:
        return max(0.0, min(1.0, float(intelligence["confidence_score"])))

    return 0.5


def section_confidence(
    unified_report: dict[str, Any],
    *,
    has_data: bool,
    minimum: float = 0.35,
) -> float:
    """Scale fusion confidence when a section has sparse supporting data."""
    base = fusion_confidence(unified_report)
    if not has_data:
        return round(min(base, minimum), 4)
    return round(base, 4)
