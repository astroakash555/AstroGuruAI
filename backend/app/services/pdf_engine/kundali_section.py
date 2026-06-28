"""Kundali charts PDF section."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import PageBreak, Paragraph, Spacer

from backend.app.services.pdf_engine.charts import build_chart_flowables


def build_kundali_section(*, styles: dict, unified_report: dict[str, Any] | None) -> list:
    if not unified_report:
        return [Paragraph("Kundali charts unavailable.", styles["body"])]

    kundali = unified_report.get("kundali") or {}
    navamsha = unified_report.get("navamsha") or {}
    flowables = [Paragraph("Kundali Charts", styles["heading1"]), Spacer(1, 8)]
    flowables.extend(build_chart_flowables(title="Lagna Kundali (D1)", chart=kundali, styles=styles))
    if navamsha:
        flowables.extend(build_chart_flowables(title="Navamsha Kundali (D9)", chart=navamsha, styles=styles))
    flowables.extend(
        build_chart_flowables(
            title="Moon Chart (Moon as Lagna reference)",
            chart=kundali,
            styles=styles,
            moon_reference=True,
        )
    )
    flowables.append(PageBreak())
    return flowables
