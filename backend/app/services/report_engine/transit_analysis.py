"""Transit analysis section (I)."""

from __future__ import annotations

from typing import Any

from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.narrative_models import NarrativeSectionId
from backend.app.services.report_engine.base import join_lines, section
from backend.app.services.report_engine.confidence import section_confidence
from backend.app.services.report_engine.consultation_brain_integration import BrainReportContext
from backend.app.services.report_engine.language import localize
from backend.app.services.report_engine.types import ReportLanguage, ReportSection

TRANSIT_KEYS = ("saturn", "jupiter", "rahu", "ketu")


def build_transit_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
    brain_context: BrainReportContext | None = None,
) -> ReportSection:
    transits = unified_report.get("transits") or {}
    facts: list[dict[str, Any]] = []
    lines: list[str] = []

    for key in TRANSIT_KEYS:
        block = transits.get(key) or {}
        current = block.get("current") or {}
        sign = (current.get("sign") or {}).get("name_en")
        house = current.get("house_from_lagna")
        if sign is None and house is None:
            continue
        facts.append({"planet": block.get("planet") or key.title(), "sign": sign, "house_from_lagna": house})
        lines.append(
            localize(
                language,
                hi=f"{facts[-1]['planet']}: {sign}, लग्न से भाव {house}",
                en=f"{facts[-1]['planet']}: {sign}, house {house} from lagna",
            )
        )

    highlights = transits.get("highlights") or []
    for highlight in highlights[:5]:
        text = highlight if isinstance(highlight, str) else highlight.get("summary") or highlight.get("title")
        if text:
            lines.append(str(text))

    narrative = join_lines(lines) if lines else localize(
        language,
        hi="कोई transit विवरण engine output में उपलब्ध नहीं।",
        en="No transit details available in engine output.",
    )
    if brain_context is not None:
        brain_narrative = brain_context.section_narrative(NarrativeSectionId.TRANSIT_DISCUSSION)
        transit_evidence = [
            item.summary for item in brain_context.evidence_for_source(EvidenceSource.TRANSIT) if item.summary
        ]
        extra = [line for line in (brain_narrative, *transit_evidence[:3]) if line]
        if extra:
            narrative = join_lines([narrative, *extra])
    return section(
        section_id="transit_analysis",
        title=localize(language, hi="गोचर विश्लेषण", en="Transit Analysis"),
        narrative=narrative,
        facts={"transits": facts, "highlights": highlights},
        confidence=section_confidence(unified_report, has_data=bool(facts)),
    )
