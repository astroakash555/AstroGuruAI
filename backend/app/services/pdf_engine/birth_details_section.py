"""Birth details PDF section."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.tables import build_table


def build_birth_details_section(
    *,
    styles: dict,
    client_report: dict[str, Any],
    unified_report: dict[str, Any] | None,
    client_name: str | None,
) -> list:
    section = _find_section(client_report, "birth_details")
    dasha_birth = ((unified_report or {}).get("dasha") or {}).get("birth") or {}
    subject = (unified_report or {}).get("subject") or {}
    summary = (unified_report or {}).get("summary") or {}
    kundali = (unified_report or {}).get("kundali") or {}
    metadata = kundali.get("metadata") or {}
    ascendant = (kundali.get("ascendant") or {}).get("sign", {}).get("name_en")

    rows = [
        ["Field", "Value"],
        ["Name", client_name or "Native"],
        ["Date of Birth", dasha_birth.get("date_of_birth") or "—"],
        ["Time", dasha_birth.get("birth_time") or "—"],
        ["Place", subject.get("birth_place") or dasha_birth.get("birth_place") or "—"],
        ["Latitude", subject.get("latitude") or "—"],
        ["Longitude", subject.get("longitude") or "—"],
        ["Timezone", subject.get("timezone") or dasha_birth.get("timezone") or "—"],
        ["Ayanamsa", metadata.get("ayanamsa") or "lahiri"],
        ["Ascendant", ascendant or summary.get("lagna_sign") or "—"],
        ["Moon Sign", summary.get("moon_sign") or "—"],
        ["Nakshatra", summary.get("moon_nakshatra") or "—"],
    ]
    flowables = [
        Paragraph("Birth Details", styles["heading1"]),
        Spacer(1, 8),
        build_table(rows, col_widths=[130, 330]),
        Spacer(1, 12),
    ]
    if section.get("narrative"):
        flowables.append(Paragraph(escape_text(section["narrative"]), styles["body"]))
    return flowables


def _find_section(client_report: dict, section_id: str) -> dict:
    for section in client_report.get("sections") or []:
        if section.get("section_id") == section_id:
            return section
    return {}
