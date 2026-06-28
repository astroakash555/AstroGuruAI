"""Premium PDF cover page."""

from __future__ import annotations

from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.theme import THEME


def build_cover_page(
    *,
    styles: dict,
    client_name: str | None,
    report_id: str | None,
    language: str,
    generated_at: datetime,
) -> list:
    logo = Table(
        [[Paragraph("AstroGuruAI", styles["title"])]],
        colWidths=[460],
        rowHeights=[80],
    )
    logo.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), THEME.dark_blue),
                ("BOX", (0, 0), (-1, -1), 1.2, THEME.gold),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    lines = [
        logo,
        Spacer(1, 1.2 * cm),
        Paragraph("Premium Vedic Astrology Report", styles["heading1"]),
        Spacer(1, 0.4 * cm),
        Paragraph(f"Client: {escape_text(client_name or 'Native')}", styles["body"]),
        Paragraph(f"Generated: {generated_at.strftime('%d %B %Y, %H:%M UTC')}", styles["body"]),
        Paragraph(f"Report ID: {escape_text(report_id or 'Pending')}", styles["body"]),
        Paragraph(f"Language: {escape_text(language)}", styles["body"]),
        Spacer(1, 0.8 * cm),
        Paragraph("CONFIDENTIAL REPORT", styles["confidential"]),
        Spacer(1, 0.4 * cm),
        Paragraph(
            "This document is generated from validated AstroGuruAI engine outputs only.",
            styles["small"],
        ),
    ]
    return lines
