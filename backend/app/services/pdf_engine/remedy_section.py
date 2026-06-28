"""Remedies PDF section."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.tables import build_table


def build_remedy_section(*, styles: dict, client_report: dict[str, Any]) -> list:
    section = _find_section(client_report, "personalized_remedies")
    remedies = client_report.get("remedies") or []
    grouped = {"High": [], "Medium": [], "Low": []}
    for remedy in remedies:
        priority = remedy.get("priority")
        if priority == 1 or str(priority).lower() == "high":
            grouped["High"].append(remedy)
        elif priority == 2 or str(priority).lower() == "medium":
            grouped["Medium"].append(remedy)
        else:
            grouped["Low"].append(remedy)

    rows = [["Priority", "Remedy", "Description"]]
    for label in ("High", "Medium", "Low"):
        for remedy in grouped[label]:
            rows.append(
                [
                    label,
                    remedy.get("title") or remedy.get("name") or "—",
                    remedy.get("description") or remedy.get("summary") or "—",
                ]
            )

    flowables = [Paragraph("Personalized Remedies", styles["heading1"]), Spacer(1, 8)]
    if len(rows) == 1:
        flowables.append(Paragraph("No remedies available.", styles["body"]))
    else:
        flowables.append(build_table(rows, col_widths=[70, 150, 240]))
    if section.get("narrative"):
        flowables.append(Spacer(1, 8))
        flowables.append(Paragraph(escape_text(section["narrative"]), styles["body"]))
    return flowables


def _find_section(client_report: dict, section_id: str) -> dict:
    for section in client_report.get("sections") or []:
        if section.get("section_id") == section_id:
            return section
    return {}
