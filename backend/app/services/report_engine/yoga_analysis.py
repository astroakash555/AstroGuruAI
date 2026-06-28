"""Yoga analysis section (G)."""

from __future__ import annotations

from typing import Any

from backend.app.services.report_engine.base import join_lines, section
from backend.app.services.report_engine.confidence import section_confidence
from backend.app.services.report_engine.language import localize
from backend.app.services.report_engine.presentation import scrub_client_text
from backend.app.services.report_engine.types import ReportLanguage, ReportSection


def build_yoga_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
) -> ReportSection:
    yogas = unified_report.get("yogas") or {}
    present = yogas.get("present_yogas") or []
    facts = {
        "present_count": (yogas.get("summary") or {}).get("present_count", len(present)),
        "yogas": [
            {
                "name": item.get("yoga_name") or item.get("yoga_id"),
                "meaning": item.get("description") or localize(
                    language,
                    hi="यह योग कुंडली में सक्रिय है।",
                    en="This yoga is active in the chart.",
                ),
            }
            for item in present
        ],
    }
    if present:
        lines = [
            localize(
                language,
                hi=f"{item.get('yoga_name')}: {item.get('description') or 'यह योग सक्रिय है।'}",
                en=f"{item.get('yoga_name')}: {item.get('description') or 'This yoga is active.'}",
            )
            for item in present
        ]
        narrative = join_lines(lines)
    else:
        narrative = localize(
            language,
            hi="इस कुंडली में कोई सक्रिय योग पहचाना नहीं गया।",
            en="No active yogas were detected for this chart.",
        )
    return section(
        section_id="yoga_analysis",
        title=localize(language, hi="योग विश्लेषण", en="Yoga Analysis"),
        narrative=scrub_client_text(narrative),
        facts=facts,
        confidence=section_confidence(unified_report, has_data=bool(present)),
    )
