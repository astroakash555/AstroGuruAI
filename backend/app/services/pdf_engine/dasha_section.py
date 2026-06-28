"""Dasha timeline PDF section."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.section_utils import append_section_content, find_section as _find_section


def build_dasha_section(*, styles: dict, client_report: dict[str, Any]) -> list:
    section = _find_section(client_report, "current_dasha")
    facts = section.get("facts")
    flowables = [
        Paragraph("Vimshottari Dasha Timeline", styles["heading1"]),
        Spacer(1, 8),
    ]
    if isinstance(facts, list):
        append_section_content(flowables, section, styles)
        return flowables

    facts = facts or {}
    md = facts.get("current_mahadasha") or "—"
    ad = facts.get("current_antardasha") or "—"
    timeline = (
        f"Mahadasha: {md}<br/>"
        f"↓<br/>"
        f"Antardasha: {ad}<br/>"
        f"↓<br/>"
        f"Current Period: {md} / {ad}<br/>"
        f"MD Window: {escape_text(facts.get('current_mahadasha_start'))} → "
        f"{escape_text(facts.get('current_mahadasha_end'))}<br/>"
        f"AD Window: {escape_text(facts.get('current_antardasha_start'))} → "
        f"{escape_text(facts.get('current_antardasha_end'))}"
    )
    flowables.extend(
        [
            Paragraph(timeline, styles["body"]),
            Spacer(1, 8),
            Paragraph(f"Balance at birth: {escape_text(facts.get('balance_lord'))}", styles["body"]),
            Spacer(1, 8),
            Paragraph(escape_text(section.get("narrative") or ""), styles["body"]),
        ]
    )
    return flowables
