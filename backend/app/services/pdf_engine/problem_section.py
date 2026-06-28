"""Problem analysis PDF section."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.section_utils import append_section_content, find_section as _find_section_impl
from backend.app.services.pdf_engine.theme import THEME


def build_problem_section(
    *,
    styles: dict,
    client_report: dict[str, Any],
    unified_report: dict[str, Any] | None,
) -> list:
    section = _find_section(client_report, "problem_analysis")
    facts = section.get("facts")
    if isinstance(facts, list):
        flowables = [Paragraph("Problem-specific Analysis", styles["heading1"]), Spacer(1, 8)]
        append_section_content(flowables, section, styles)
        return flowables

    consultation = (unified_report or {}).get("consultation_brain") or {}
    domain = _matching_consultation_section(consultation, section)

    cards = [
        ("Current Situation", domain.get("current_situation") or section.get("narrative") or "—"),
        ("Root Cause", domain.get("root_cause") or client_report.get("astrological_root_cause") or "—"),
        ("Positive Factors", _join(domain.get("positive_factors")) or "—"),
        ("Challenges", _join(domain.get("challenges")) or "—"),
        ("Timeline", domain.get("timeline") or "—"),
    ]
    flowables = [Paragraph("Problem-specific Analysis", styles["heading1"]), Spacer(1, 8)]
    for title, content in cards:
        flowables.extend(_card(title, escape_text(content), styles))
        flowables.append(Spacer(1, 6))
        flowables.append(Paragraph("↓", styles["footer"]))
        flowables.append(Spacer(1, 6))
    return flowables


def _card(title: str, content: str, styles: dict) -> list:
    table = Table(
        [[Paragraph(f"<b>{title}</b>", styles["heading2"])], [Paragraph(content, styles["body"])]],
        colWidths=[460],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), THEME.light_grey),
                ("BOX", (0, 0), (-1, -1), 0.8, THEME.dark_blue),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return [table]


def _join(values: Any) -> str:
    if isinstance(values, list):
        return "; ".join(str(item) for item in values if item)
    return str(values or "")


def _matching_consultation_section(consultation: dict, problem_section: dict) -> dict:
    sections = consultation.get("sections") or []
    category = ((problem_section.get("facts") or {}).get("category") or "").lower()
    for item in sections:
        if category and category in str(item.get("section_id", "")).lower():
            return item
    return sections[0] if sections else {}


def _find_section(client_report: dict, section_id: str) -> dict:
    return _find_section_impl(client_report, section_id)
