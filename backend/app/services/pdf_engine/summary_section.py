"""Final summary PDF section and QR page."""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text


def build_summary_section(*, styles: dict, client_report: dict[str, Any], unified_report: dict[str, Any] | None) -> list:
    strengths = _find_section(client_report, "strengths")
    challenges = _find_section(client_report, "challenges")
    final = _find_section(client_report, "final_summary")
    consultation = (unified_report or {}).get("consultation_brain") or {}
    recommendations = [
        item.get("title") or item.get("explanation")
        for item in (consultation.get("priorities") or [])[:5]
        if item.get("title") or item.get("explanation")
    ]
    return [
        Paragraph("Final Summary", styles["heading1"]),
        Spacer(1, 8),
        Paragraph("<b>Strengths</b>", styles["heading2"]),
        Paragraph(escape_text(strengths.get("narrative") or "—"), styles["body"]),
        Spacer(1, 8),
        Paragraph("<b>Challenges</b>", styles["heading2"]),
        Paragraph(escape_text(challenges.get("narrative") or "—"), styles["body"]),
        Spacer(1, 8),
        Paragraph("<b>Recommendations</b>", styles["heading2"]),
        Paragraph(escape_text("; ".join(recommendations) or final.get("narrative") or "—"), styles["body"]),
    ]


def build_qr_page(
    *,
    styles: dict,
    online_report_url: str | None,
    ai_chat_url: str | None,
) -> list:
    flowables = [Paragraph("Digital Access", styles["heading1"]), Spacer(1, 12)]
    if online_report_url:
        flowables.extend(
            [
                Paragraph("Open Online Report", styles["heading2"]),
                _qr_image(online_report_url, styles),
                Paragraph(escape_text(online_report_url), styles["small"]),
                Spacer(1, 12),
            ]
        )
    if ai_chat_url:
        flowables.extend(
            [
                Paragraph("Ask AI About Report", styles["heading2"]),
                _qr_image(ai_chat_url, styles),
                Paragraph(escape_text(ai_chat_url), styles["small"]),
            ]
        )
    if not online_report_url and not ai_chat_url:
        flowables.append(Paragraph("Online access links were not supplied for this report.", styles["body"]))
    return flowables


def _qr_image(url: str, styles: dict):
    try:
        import qrcode

        qr = qrcode.make(url)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        return Image(buffer, width=4 * cm, height=4 * cm)
    except Exception:
        return Paragraph(f"QR unavailable. URL: {escape_text(url)}", styles["body"])


def _find_section(client_report: dict, section_id: str) -> dict:
    for section in client_report.get("sections") or []:
        if section.get("section_id") == section_id:
            return section
    return {}
