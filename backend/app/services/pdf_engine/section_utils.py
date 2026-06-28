"""Helpers for reading cleaned professional report sections in PDF output."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text


def find_section(client_report: dict[str, Any], section_id: str) -> dict[str, Any]:
    for section in client_report.get("sections") or []:
        if section.get("section_id") == section_id:
            return section
    return {}


def append_section_content(flowables: list, section: dict[str, Any], styles: dict) -> None:
    """Append narrative and formatted fact lines from a cleaned client section."""
    if section.get("narrative"):
        flowables.append(Paragraph(escape_text(section["narrative"]), styles["body"]))
        flowables.append(Spacer(1, 8))
    facts = section.get("facts")
    if isinstance(facts, list):
        for line in facts:
            flowables.append(Paragraph(escape_text(str(line)), styles["body"]))
            flowables.append(Spacer(1, 4))
