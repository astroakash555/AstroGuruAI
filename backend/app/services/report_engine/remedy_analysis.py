"""Personalized remedies section (K)."""

from __future__ import annotations

from typing import Any

from backend.app.services.report_engine.base import join_lines, section
from backend.app.services.report_engine.confidence import section_confidence
from backend.app.services.report_engine.language import localize
from backend.app.services.report_engine.presentation import scrub_client_text
from backend.app.services.report_engine.types import ReportLanguage, ReportSection


def _priority_label(priority: Any, *, language: ReportLanguage) -> str:
    if priority == 1 or str(priority).lower() == "high":
        return localize(language, hi="उच्च", en="High")
    if priority == 2 or str(priority).lower() == "medium":
        return localize(language, hi="मध्यम", en="Medium")
    return localize(language, hi="निम्न", en="Low")


def build_remedy_section(
    unified_report: dict[str, Any],
    *,
    remedy_generation: dict[str, Any],
    language: ReportLanguage,
) -> ReportSection:
    matched = (unified_report.get("remedy_recommendations") or {}).get("matched_remedies") or []
    generated = remedy_generation.get("remedies") or []
    remedies: list[dict[str, Any]] = []

    for item in generated[:5]:
        remedies.append(
            {
                "title": item.get("title") or item.get("name"),
                "description": item.get("description") or item.get("summary") or "",
                "priority": _priority_label(item.get("priority", 2), language=language),
            }
        )
    if not remedies:
        for item in matched[:5]:
            remedy = item.get("remedy") or {}
            title = remedy.get("title") or remedy.get("name")
            if title:
                remedies.append(
                    {
                        "title": title,
                        "description": remedy.get("description") or remedy.get("summary") or "",
                        "priority": _priority_label(2, language=language),
                    }
                )

    lines = [
        localize(language, hi=f"{item['priority']} प्राथमिकता: {item['title']}", en=f"{item['priority']} priority: {item['title']}")
        for item in remedies
        if item.get("title")
    ]
    if not lines:
        lines.append(
            localize(
                language,
                hi="इस समय कोई व्यक्तिगत उपाय उपलब्ध नहीं है।",
                en="No personalized remedies are available at this time.",
            )
        )
    return section(
        section_id="personalized_remedies",
        title=localize(language, hi="व्यक्तिगत उपाय", en="Personalized Remedies"),
        narrative=scrub_client_text(join_lines(lines)),
        facts={"remedies": remedies},
        confidence=section_confidence(unified_report, has_data=bool(remedies)),
    )
