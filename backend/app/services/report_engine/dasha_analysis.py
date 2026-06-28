"""Dasha analysis section (H)."""

from __future__ import annotations

from typing import Any

from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.narrative_models import NarrativeSectionId
from backend.app.services.report_engine.base import section
from backend.app.services.report_engine.confidence import section_confidence
from backend.app.services.report_engine.consultation_brain_integration import BrainReportContext
from backend.app.services.report_engine.language import localize
from backend.app.services.report_engine.presentation import format_dasha_narrative, scrub_client_text
from backend.app.services.report_engine.types import ReportLanguage, ReportSection


def build_dasha_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
    brain_context: BrainReportContext | None = None,
) -> ReportSection:
    dasha = unified_report.get("dasha") or {}
    current = dasha.get("current") or {}
    mahadasha = current.get("mahadasha") or {}
    antardasha = current.get("antardasha") or {}
    balance = dasha.get("balance") or {}
    facts = {
        "balance_lord": balance.get("lord"),
        "current_mahadasha": mahadasha.get("lord"),
        "current_mahadasha_start": mahadasha.get("start"),
        "current_mahadasha_end": mahadasha.get("end"),
        "current_antardasha": antardasha.get("lord"),
        "current_antardasha_start": antardasha.get("start"),
        "current_antardasha_end": antardasha.get("end"),
    }
    narrative = format_dasha_narrative(facts, language=language)
    if brain_context is not None:
        brain_narrative = brain_context.section_narrative(NarrativeSectionId.DASHA_DISCUSSION)
        dasha_evidence = [
            item.summary for item in brain_context.evidence_for_source(EvidenceSource.DASHA) if item.summary
        ]
        extra = [line for line in (brain_narrative, *dasha_evidence[:3]) if line]
        if extra:
            narrative = "\n".join([narrative, *extra])
    return section(
        section_id="current_dasha",
        title=localize(
            language,
            hi="वर्तमान महादशा और अंतर्दशा",
            en="Current Mahadasha & Antardasha",
        ),
        narrative=scrub_client_text(narrative),
        facts=facts,
        confidence=section_confidence(unified_report, has_data=bool(mahadasha.get("lord"))),
    )
