"""Transit analysis PDF section."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.section_utils import append_section_content, find_section as _find_section


def build_transit_section(*, styles: dict, client_report: dict[str, Any]) -> list:
    section = _find_section(client_report, "transit_analysis")
    flowables = [
        Paragraph("Transit Analysis", styles["heading1"]),
        Spacer(1, 8),
    ]
    if isinstance(section.get("facts"), list):
        append_section_content(flowables, section, styles)
    else:
        flowables.append(
            Paragraph(
                escape_text(section.get("narrative") or client_report.get("transit_analysis") or "—"),
                styles["body"],
            )
        )
    flowables.append(Spacer(1, 8))
    flowables.append(
        Paragraph(
            f"Section confidence: {section.get('confidence_label', section.get('confidence', '—'))}",
            styles["small"],
        )
    )
    return flowables
