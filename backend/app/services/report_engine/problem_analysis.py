"""Problem-specific analysis section (J)."""

from __future__ import annotations

from typing import Any

from backend.app.services.consultation_brain.narrative_models import NarrativeSectionId
from backend.app.services.report_engine.base import join_lines, section
from backend.app.services.report_engine.confidence import section_confidence
from backend.app.services.report_engine.consultation_brain_integration import BrainReportContext
from backend.app.services.report_engine.language import localize
from backend.app.services.report_engine.presentation import scrub_client_text
from backend.app.services.report_engine.types import ReportLanguage, ReportSection


def build_problem_section(
    unified_report: dict[str, Any],
    *,
    problem_text: str | None,
    language: ReportLanguage,
    brain_context: BrainReportContext | None = None,
) -> ReportSection:
    if brain_context is not None:
        lines: list[str] = []
        if problem_text:
            lines.append(localize(language, hi=f"प्रश्न: {problem_text}", en=f"Concern: {problem_text}"))
        lines.extend(brain_context.narrative_paragraphs(NarrativeSectionId.HIGHEST_PRIORITY_TOPIC))
        lines.extend(brain_context.narrative_bullets(NarrativeSectionId.HIGHEST_PRIORITY_TOPIC))
        lines.extend(brain_context.narrative_paragraphs(NarrativeSectionId.SUPPORTING_EVIDENCE))
        lines.extend(brain_context.narrative_bullets(NarrativeSectionId.SUPPORTING_EVIDENCE))
        lines.extend(brain_context.priority_lines()[:3])
        lines.extend(brain_context.conflict_lines()[:2])
        facts = {
            "problem_text": problem_text,
            "priority_summaries": brain_context.priority_lines()[:5],
            "supporting_evidence": brain_context.evidence_summary_lines(limit=5),
            "conflicts": brain_context.conflict_lines()[:3],
        }
        narrative = join_lines(lines) if lines else localize(
            language,
            hi="कोई समस्या-विशिष्ट विश्लेषण उपलब्ध नहीं।",
            en="No problem-specific analysis available.",
        )
        return section(
            section_id="problem_analysis",
            title=localize(language, hi="समस्या-विशिष्ट विश्लेषण", en="Problem-specific Analysis"),
            narrative=scrub_client_text(narrative),
            facts=facts,
            confidence=brain_context.overall_confidence(),
        )

    problem = unified_report.get("problem_analysis") or {}
    fusion = unified_report.get("fusion") or {}
    root_causes = fusion.get("root_causes") or []
    category = (problem.get("category") or {}).get("category")
    severity = (problem.get("severity") or {}).get("level")
    root_summaries = [str(item.get("title")) for item in root_causes[:5] if item.get("title")]
    facts = {
        "problem_text": problem_text,
        "category": category,
        "severity": severity,
        "root_cause_summaries": root_summaries,
    }
    lines: list[str] = []
    if problem_text:
        lines.append(localize(language, hi=f"प्रश्न: {problem_text}", en=f"Concern: {problem_text}"))
    if category:
        lines.append(localize(language, hi=f"श्रेणी: {category}", en=f"Category: {category}"))
    if severity:
        lines.append(localize(language, hi=f"गंभीरता: {severity}", en=f"Severity: {severity}"))
    for summary in root_summaries:
        lines.append(summary)
    if not lines:
        lines.append(
            localize(
                language,
                hi="कोई समस्या-विशिष्ट विश्लेषण उपलब्ध नहीं।",
                en="No problem-specific analysis available.",
            )
        )
    return section(
        section_id="problem_analysis",
        title=localize(language, hi="समस्या-विशिष्ट विश्लेषण", en="Problem-specific Analysis"),
        narrative=scrub_client_text(join_lines(lines)),
        facts=facts,
        confidence=section_confidence(unified_report, has_data=bool(problem_text or category)),
    )
