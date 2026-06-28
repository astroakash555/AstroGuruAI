"""Yoga analysis PDF section."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.section_utils import append_section_content, find_section as _find_section
from backend.app.services.pdf_engine.tables import build_table


def build_yoga_section(*, styles: dict, client_report: dict[str, Any], unified_report: dict[str, Any] | None) -> list:
    section = _find_section(client_report, "yoga_analysis")
    facts = section.get("facts")
    yogas = (facts or {}).get("yogas") if isinstance(facts, dict) else []
    if not yogas and unified_report:
        yogas = (unified_report.get("yogas") or {}).get("present_yogas") or []

    flowables = [
        Paragraph("Yoga Analysis", styles["heading1"]),
        Spacer(1, 8),
    ]
    if isinstance(facts, list):
        append_section_content(flowables, section, styles)
        return flowables

    rows = [["Yoga", "Meaning", "Confidence"]]
    confidence = section.get("confidence_label", section.get("confidence", "—"))
    for yoga in yogas:
        rows.append(
            [
                yoga.get("yoga_name") or yoga.get("yoga_id"),
                yoga.get("description") or yoga.get("category") or "Present in chart",
                confidence,
            ]
        )
    if len(rows) == 1:
        flowables.append(Paragraph("No active yogas recorded.", styles["body"]))
    else:
        flowables.append(build_table(rows, col_widths=[140, 220, 80]))
    if section.get("narrative"):
        flowables.append(Spacer(1, 8))
        flowables.append(Paragraph(escape_text(section["narrative"]), styles["body"]))
    return flowables
