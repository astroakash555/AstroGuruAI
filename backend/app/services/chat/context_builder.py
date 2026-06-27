"""Build compact report context for Kundali chat prompts."""

from __future__ import annotations

from typing import Any

CONTEXT_SECTION_KEYS = (
    "summary",
    "problem_analysis",
    "consultation_brain",
    "fusion",
    "vedic",
    "kp",
    "lal_kitab_intelligence",
    "dasha",
    "transits",
)
MAX_OBSERVATIONS = 5


def build_report_context(unified_report: dict[str, Any]) -> dict[str, Any]:
    """Extract chat-relevant sections from a persisted unified report."""
    return {
        "version": unified_report.get("version"),
        "generated_at": unified_report.get("generated_at"),
        "subject": _compact_subject(unified_report.get("subject")),
        "summary": unified_report.get("summary"),
        "problem_analysis": unified_report.get("problem_analysis"),
        "consultation_brain": _compact_consultation(unified_report.get("consultation_brain")),
        "fusion": _compact_fusion(unified_report.get("fusion")),
        "vedic": _compact_engine_section(unified_report.get("vedic")),
        "kp": _compact_kp(unified_report.get("kp")),
        "lal_kitab_intelligence": _compact_engine_section(unified_report.get("lal_kitab_intelligence")),
        "dasha": _compact_dasha(unified_report.get("dasha")),
        "transits": _compact_transits(unified_report.get("transits")),
    }


def context_section_keys() -> tuple[str, ...]:
    """Return the report sections included in chat context."""
    return CONTEXT_SECTION_KEYS


def _compact_subject(subject: Any) -> dict[str, Any] | None:
    if not isinstance(subject, dict):
        return None
    return {
        key: subject.get(key)
        for key in ("birth_place", "timezone", "client_id")
        if subject.get(key) is not None
    }


def _compact_consultation(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    sections = []
    for section in payload.get("sections", [])[:12]:
        if not isinstance(section, dict):
            continue
        sections.append(
            {
                "section_id": section.get("section_id"),
                "title": section.get("title"),
                "current_situation": section.get("current_situation"),
                "root_cause": section.get("root_cause"),
                "positive_factors": section.get("positive_factors", [])[:3],
                "challenges": section.get("challenges", [])[:3],
                "timeline": section.get("timeline"),
                "actionable_advice": section.get("actionable_advice", [])[:2],
                "confidence": section.get("confidence"),
            }
        )
    return {
        "executive_summary": payload.get("executive_summary"),
        "overall_confidence": payload.get("overall_confidence"),
        "priorities": payload.get("priorities", [])[:5],
        "strengths": payload.get("strengths", [])[:5],
        "risks": payload.get("risks", [])[:5],
        "sections": sections,
    }


def _compact_fusion(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    return {
        "confidence": payload.get("confidence"),
        "observations": _compact_observations(payload.get("observations", [])),
        "root_causes": payload.get("root_causes", [])[:5],
        "conflicts": payload.get("conflicts", [])[:3],
        "recommendations": payload.get("recommendations", [])[:5],
    }


def _compact_engine_section(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    compact = {
        "metadata": payload.get("metadata"),
        "observations": _compact_observations(payload.get("observations", [])),
    }
    remedies = payload.get("remedies")
    if isinstance(remedies, list):
        compact["remedies"] = [item for item in remedies[:3] if isinstance(item, dict)]
    return compact


def _compact_kp(payload: Any) -> dict[str, Any] | None:
    compact = _compact_engine_section(payload)
    if compact is None:
        return None
    event_timing = payload.get("event_timing") if isinstance(payload, dict) else None
    if isinstance(event_timing, list):
        compact["event_timing"] = event_timing[:3]
    return compact


def _compact_observations(observations: Any) -> list[dict[str, Any]]:
    if not isinstance(observations, list):
        return []
    compact: list[dict[str, Any]] = []
    for item in observations[:MAX_OBSERVATIONS]:
        if not isinstance(item, dict):
            continue
        compact.append(
            {
                "title": item.get("title"),
                "explanation": item.get("explanation"),
                "category": item.get("category"),
                "affected_planets": item.get("affected_planets", [])[:4],
                "affected_houses": item.get("affected_houses", [])[:4],
                "severity": item.get("severity"),
                "confidence": item.get("confidence"),
            }
        )
    return compact


def _compact_dasha(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    current = payload.get("current") if isinstance(payload.get("current"), dict) else {}
    return {
        "system": payload.get("system"),
        "moon": payload.get("moon"),
        "current": {
            key: current.get(key)
            for key in ("mahadasha", "antardasha", "pratyantardasha")
            if current.get(key) is not None
        },
        "summary": payload.get("summary"),
    }


def _compact_transits(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    return {
        "metadata": {
            key: metadata.get(key)
            for key in ("engine", "reference_date", "planets_analyzed")
            if metadata.get(key) is not None
        },
        "summary": payload.get("summary"),
        "daily_snapshot": payload.get("daily_snapshot"),
        "significant_transits": payload.get("significant_transits", [])[:5]
        if isinstance(payload.get("significant_transits"), list)
        else None,
    }
