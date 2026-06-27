"""PDF report generator using ReportLab."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


@dataclass(frozen=True)
class PDFGenerationResult:
    file_path: str
    file_name: str
    file_size_bytes: int
    generated_at: datetime


class PDFReportGenerator:
    """Generate downloadable PDF reports from client report JSON."""

    def __init__(self, output_dir: str | Path = "reports/generated") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        *,
        client_report_json: dict[str, Any],
        unified_report_json: dict[str, Any] | None = None,
        file_prefix: str = "astroguru_report",
    ) -> PDFGenerationResult:
        file_name = f"{file_prefix}_{uuid4().hex[:10]}.pdf"
        file_path = self._output_dir / file_name
        styles = getSampleStyleSheet()
        story: list[Any] = [
            Paragraph("AstroGuruAI Client Report", styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"<b>Generated:</b> {datetime.now(timezone.utc).isoformat()}", styles["Normal"]),
            Spacer(1, 12),
        ]

        sections = [
            ("Problem Summary", client_report_json.get("problem_summary", "")),
            ("Astrological Root Cause", client_report_json.get("astrological_root_cause", "")),
            ("Planet Analysis", client_report_json.get("planet_analysis", "")),
            ("Dasha Analysis", client_report_json.get("dasha_analysis", "")),
            ("Transit Analysis", client_report_json.get("transit_analysis", "")),
            ("KP Analysis", client_report_json.get("kp_analysis", "")),
            ("Lal Kitab Analysis", client_report_json.get("lal_kitab_analysis", "")),
            ("Short Term Outlook", client_report_json.get("short_term_outlook", "")),
            ("Long Term Outlook", client_report_json.get("long_term_outlook", "")),
        ]
        for title, content in sections:
            story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
            story.append(Paragraph(str(content).replace("\n", "<br/>"), styles["BodyText"]))
            story.append(Spacer(1, 10))

        remedies = client_report_json.get("remedies", [])
        if remedies:
            story.append(Paragraph("<b>Remedies</b>", styles["Heading2"]))
            for remedy in remedies[:10]:
                line = (
                    f"{remedy.get('title')} ({remedy.get('astrology_system')}, "
                    f"priority {remedy.get('priority')}): {remedy.get('description')}"
                )
                story.append(Paragraph(line, styles["BodyText"]))
                story.append(Spacer(1, 6))

        if unified_report_json:
            summary = unified_report_json.get("summary", {})
            story.append(Paragraph("<b>Chart Summary</b>", styles["Heading2"]))
            story.append(
                Paragraph(
                    (
                        f"Lagna: {summary.get('lagna_sign')} | Moon: {summary.get('moon_sign')} | "
                        f"Nakshatra: {summary.get('moon_nakshatra')}"
                    ),
                    styles["BodyText"],
                )
            )

        doc = SimpleDocTemplate(str(file_path), pagesize=A4)
        doc.build(story)
        size = file_path.stat().st_size
        return PDFGenerationResult(
            file_path=str(file_path),
            file_name=file_name,
            file_size_bytes=size,
            generated_at=datetime.now(timezone.utc),
        )
