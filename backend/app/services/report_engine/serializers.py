"""Serializers for professional report output."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from backend.app.services.report_engine.presentation import (
    assert_client_safe_text,
    clean_remedy_items,
    format_confidence,
    format_kp_analysis,
    format_lal_kitab_analysis,
    format_section_facts,
    normalize_client_facts,
    scrub_client_text,
)
from backend.app.services.report_engine.types import (
    ProfessionalReportInput,
    ProfessionalReportResult,
    ReportLanguage,
    ReportSection,
)


def section_to_client_dict(section: ReportSection, *, language: ReportLanguage) -> dict[str, Any]:
    """Serialize one client-safe report section."""
    raw_facts = section.facts
    if isinstance(raw_facts, dict):
        formatted = format_section_facts(section.section_id, raw_facts, language=language)
    else:
        formatted = raw_facts
    facts_display = normalize_client_facts(formatted)
    payload = {
        "section_id": section.section_id,
        "title": scrub_client_text(section.title),
        "narrative": scrub_client_text(section.narrative),
        "facts": facts_display,
        "confidence": section.confidence,
        "confidence_label": format_confidence(section.confidence),
    }
    return payload


def section_to_dict(section: ReportSection) -> dict[str, Any]:
    """Serialize one report section for internal use."""
    return {
        "section_id": section.section_id,
        "title": section.title,
        "narrative": section.narrative,
        "facts": section.facts,
        "confidence": section.confidence,
    }


def professional_report_to_dict(result: ProfessionalReportResult) -> dict[str, Any]:
    """Serialize the full professional report."""
    return {
        "language": result.language.value,
        "overall_confidence": result.overall_confidence,
        "sections": [section_to_dict(section) for section in result.sections],
    }


def _section_narrative(result: ProfessionalReportResult, section_id: str) -> str:
    for section in result.sections:
        if section.section_id == section_id:
            return scrub_client_text(section.narrative)
    return ""


def _legacy_remedies(report_input: ProfessionalReportInput) -> list[dict[str, Any]]:
    generated = report_input.remedy_generation.get("remedies") or []
    if generated:
        return clean_remedy_items(generated)
    matched = (report_input.unified_report.get("remedy_recommendations") or {}).get("matched_remedies") or []
    remedies: list[dict[str, Any]] = []
    for item in matched[:5]:
        remedy = item.get("remedy") or {}
        if remedy:
            remedies.append(
                {
                    "title": remedy.get("title") or remedy.get("name") or "Remedy",
                    "description": scrub_client_text(
                        str(remedy.get("description") or remedy.get("summary") or "")
                    ),
                    "priority": 2,
                }
            )
    return clean_remedy_items(remedies)


def _validate_client_payload(payload: dict[str, Any]) -> None:
    """Ensure serialized client report contains no forbidden diagnostic text."""
    for section in payload.get("sections") or []:
        facts = section.get("facts")
        if not isinstance(facts, list):
            raise ValueError(f"Section {section.get('section_id')} facts must be a list, got {type(facts).__name__}")
        if any(not isinstance(line, str) for line in facts):
            raise ValueError(f"Section {section.get('section_id')} facts must contain only strings")
    serialized = json.dumps(payload, ensure_ascii=False, default=str)
    assert_client_safe_text(serialized)


def professional_report_to_client_json(
    result: ProfessionalReportResult,
    *,
    report_input: ProfessionalReportInput,
) -> dict[str, Any]:
    """
    Map structured sections onto the legacy client_report contract.

    All client-visible strings are scrubbed and facts are formatted for display.
    """
    language = result.language
    sections = [section_to_client_dict(section, language=language) for section in result.sections]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "language": language.value,
        "sections": sections,
        "problem_summary": scrub_client_text(
            report_input.problem_text or "No explicit client problem statement was supplied."
        ),
        "astrological_root_cause": _section_narrative(result, "problem_analysis"),
        "planet_analysis": _section_narrative(result, "planet_wise_interpretation"),
        "dasha_analysis": _section_narrative(result, "current_dasha"),
        "transit_analysis": _section_narrative(result, "transit_analysis"),
        "kp_analysis": format_kp_analysis(report_input.unified_report, language=language),
        "lal_kitab_analysis": format_lal_kitab_analysis(report_input.unified_report, language=language),
        "remedies": _legacy_remedies(report_input),
        "short_term_outlook": _section_narrative(result, "current_dasha"),
        "long_term_outlook": _section_narrative(result, "final_summary"),
        "metadata": {
            "version": "2.0",
            "language": language.value,
            "overall_confidence": result.overall_confidence,
            "section_count": len(sections),
        },
    }
    _validate_client_payload(payload)
    return payload
