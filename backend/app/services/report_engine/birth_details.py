"""Birth details section (A)."""

from __future__ import annotations

from typing import Any

from backend.app.services.report_engine.base import section
from backend.app.services.report_engine.confidence import section_confidence
from backend.app.services.report_engine.language import localize
from backend.app.services.report_engine.consultation_brain_integration import BrainReportContext
from backend.app.services.report_engine.types import ReportLanguage, ReportSection


def build_birth_details_section(
    unified_report: dict[str, Any],
    *,
    problem_text: str | None,
    language: ReportLanguage,
    brain_context: BrainReportContext | None = None,
) -> ReportSection:
    subject = unified_report.get("subject") or {}
    dasha = unified_report.get("dasha") or {}
    birth = dasha.get("birth") or {}
    facts = {
        "birth_place": subject.get("birth_place") or birth.get("birth_place"),
        "timezone": subject.get("timezone") or birth.get("timezone"),
        "datetime_utc": subject.get("datetime_utc") or birth.get("datetime"),
        "date_of_birth": birth.get("date_of_birth"),
        "birth_time": birth.get("birth_time"),
        "latitude": subject.get("latitude"),
        "longitude": subject.get("longitude"),
        "problem_text": problem_text,
    }
    narrative = localize(
        language,
        hi=(
            f"जन्म स्थान: {facts['birth_place'] or '—'}। "
            f"तिथि: {facts['date_of_birth'] or '—'}, समय: {facts['birth_time'] or '—'} "
            f"({facts['timezone'] or '—'})।"
        ),
        en=(
            f"Birth place: {facts['birth_place'] or '—'}. "
            f"Date: {facts['date_of_birth'] or '—'}, time: {facts['birth_time'] or '—'} "
            f"({facts['timezone'] or '—'})."
        ),
    )
    if problem_text:
        narrative += " " + localize(
            language,
            hi=f"प्रश्न: {problem_text}",
            en=f"Client concern: {problem_text}",
        )
    return section(
        section_id="birth_details",
        title=localize(language, hi="जन्म विवरण", en="Birth Details"),
        narrative=narrative,
        facts=facts,
        confidence=section_confidence(unified_report, has_data=bool(facts["birth_place"])),
    )
