"""House analysis PDF section."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import PageBreak, Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.section_utils import append_section_content, find_section as _find_section


def build_house_section(*, styles: dict, client_report: dict[str, Any]) -> list:
    section = _find_section(client_report, "house_wise_interpretation")
    facts = section.get("facts")
    houses = facts.get("houses") if isinstance(facts, dict) else []
    flowables = [Paragraph("House-wise Analysis", styles["heading1"]), Spacer(1, 8)]
    if isinstance(facts, list):
        append_section_content(flowables, section, styles)
        return flowables
    if not houses:
        flowables.append(Paragraph("No house analysis available.", styles["body"]))
        return flowables

    for house in houses:
        occupants = ", ".join(house.get("occupants") or []) or "Empty"
        summary = house.get("summary") or "No observations"
        flowables.extend(
            [
                Paragraph(
                    f"House {house.get('house')} — {escape_text(house.get('sign'))}",
                    styles["heading2"],
                ),
                Paragraph(f"Occupants: {escape_text(occupants)}", styles["body"]),
                Paragraph(f"Summary: {escape_text(summary)}", styles["body"]),
                Paragraph(f"Confidence: {section.get('confidence_label', section.get('confidence', '—'))}", styles["small"]),
                Spacer(1, 10),
                PageBreak(),
            ]
        )
    return flowables
