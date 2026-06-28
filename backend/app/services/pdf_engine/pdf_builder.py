"""Premium PDF builder orchestrating all report sections."""

from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from reportlab.platypus import PageBreak

from backend.app.services.pdf_engine.birth_details_section import build_birth_details_section
from backend.app.services.pdf_engine.cover_page import build_cover_page
from backend.app.services.pdf_engine.dasha_section import build_dasha_section
from backend.app.services.pdf_engine.fonts import register_pdf_fonts
from backend.app.services.pdf_engine.house_section import build_house_section
from backend.app.services.pdf_engine.kundali_section import build_kundali_section
from backend.app.services.pdf_engine.planet_section import build_planet_section
from backend.app.services.pdf_engine.problem_section import build_problem_section
from backend.app.services.pdf_engine.remedy_section import build_remedy_section
from backend.app.services.pdf_engine.renderer import PageNumberCanvas, SectionMarker, create_document
from backend.app.services.pdf_engine.summary_section import build_qr_page, build_summary_section
from backend.app.services.pdf_engine.table_of_contents import build_table_of_contents
from backend.app.services.pdf_engine.theme import build_styles
from backend.app.services.pdf_engine.transit_section import build_transit_section
from backend.app.services.pdf_engine.types import PDFBuildInput, PDFBuildResult
from backend.app.services.pdf_engine.yoga_section import build_yoga_section


SECTION_CATALOG: list[tuple[str, str]] = [
    ("birth_details", "Birth Details"),
    ("kundali_charts", "Kundali Charts"),
    ("planetary_positions", "Planetary Positions"),
    ("house_analysis", "House-wise Analysis"),
    ("yoga_analysis", "Yoga Analysis"),
    ("dasha_timeline", "Vimshottari Dasha Timeline"),
    ("transit_analysis", "Transit Analysis"),
    ("problem_analysis", "Problem-specific Analysis"),
    ("personalized_remedies", "Personalized Remedies"),
    ("final_summary", "Final Summary"),
    ("digital_access", "Digital Access"),
]


class PremiumPDFBuilder:
    """Build premium book-style PDF reports from professional report JSON."""

    def __init__(self, output_dir: str | Path = "reports/generated") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def build(self, build_input: PDFBuildInput) -> PDFBuildResult:
        generated_at = datetime.now(timezone.utc)
        file_name = f"{build_input.file_prefix}_{uuid4().hex[:10]}.pdf"
        file_path = self._output_dir / file_name

        font_regular, font_bold = register_pdf_fonts()
        styles = build_styles(font_regular, font_bold)
        client_report = build_input.client_report_json
        unified_report = build_input.unified_report_json
        language = client_report.get("language") or client_report.get("metadata", {}).get("language") or "hi"

        section_pages = self._collect_section_pages(
            build_input=build_input,
            styles=styles,
            generated_at=generated_at,
        )

        story: list[Any] = []
        story.extend(
            build_cover_page(
                styles=styles,
                client_name=build_input.client_name,
                report_id=build_input.report_id,
                language=str(language),
                generated_at=generated_at,
            )
        )
        story.append(PageBreak())
        story.extend(
            build_table_of_contents(
                styles=styles,
                entries=[(key, title, section_pages.get(key)) for key, title in SECTION_CATALOG],
            )
        )
        story.append(PageBreak())
        story.extend(self._compose_sections(build_input, styles))
        story.append(PageBreak())
        story.extend(
            build_qr_page(
                styles=styles,
                online_report_url=build_input.online_report_url,
                ai_chat_url=build_input.ai_chat_url,
            )
        )

        doc = create_document(str(file_path))
        doc.build(
            story,
            canvasmaker=lambda *args, **kwargs: PageNumberCanvas(
                *args,
                generated_at=generated_at,
                **kwargs,
            ),
        )
        size = file_path.stat().st_size
        return PDFBuildResult(
            file_path=str(file_path),
            file_name=file_name,
            file_size_bytes=size,
            generated_at=generated_at,
            page_count=max(section_pages.values(), default=0),
            section_pages=section_pages,
        )

    def _compose_sections(self, build_input: PDFBuildInput, styles: dict) -> list[Any]:
        client_report = build_input.client_report_json
        unified_report = build_input.unified_report_json
        flowables: list[Any] = []
        flowables.extend(
            build_birth_details_section(
                styles=styles,
                client_report=client_report,
                unified_report=unified_report,
                client_name=build_input.client_name,
            )
        )
        flowables.append(PageBreak())
        flowables.extend(build_kundali_section(styles=styles, unified_report=unified_report))
        flowables.extend(
            build_planet_section(
                styles=styles,
                client_report=client_report,
                unified_report=unified_report,
            )
        )
        flowables.append(PageBreak())
        flowables.extend(build_house_section(styles=styles, client_report=client_report))
        flowables.extend(build_yoga_section(styles=styles, client_report=client_report, unified_report=unified_report))
        flowables.append(PageBreak())
        flowables.extend(build_dasha_section(styles=styles, client_report=client_report))
        flowables.extend(build_transit_section(styles=styles, client_report=client_report))
        flowables.append(PageBreak())
        flowables.extend(
            build_problem_section(
                styles=styles,
                client_report=client_report,
                unified_report=unified_report,
            )
        )
        flowables.extend(build_remedy_section(styles=styles, client_report=client_report))
        flowables.append(PageBreak())
        flowables.extend(
            build_summary_section(
                styles=styles,
                client_report=client_report,
                unified_report=unified_report,
            )
        )
        return flowables

    def _collect_section_pages(
        self,
        *,
        build_input: PDFBuildInput,
        styles: dict,
        generated_at: datetime,
    ) -> dict[str, int]:
        section_pages: dict[str, int] = {}

        class MarkerCanvas(PageNumberCanvas):
            def showPage(self) -> None:
                pages = getattr(self, "_astro_section_pages", None)
                if pages:
                    section_pages.update(pages)
                super().showPage()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            temp_path = tmp.name

        story: list[Any] = [SectionMarker("cover")]
        story.extend(
            build_cover_page(
                styles=styles,
                client_name=build_input.client_name,
                report_id=build_input.report_id,
                language=str(build_input.client_report_json.get("language") or "hi"),
                generated_at=generated_at,
            )
        )
        story.append(PageBreak())
        for key, _title in SECTION_CATALOG:
            story.append(SectionMarker(key))
            if key == "birth_details":
                story.extend(
                    build_birth_details_section(
                        styles=styles,
                        client_report=build_input.client_report_json,
                        unified_report=build_input.unified_report_json,
                        client_name=build_input.client_name,
                    )
                )
            elif key == "kundali_charts":
                story.extend(build_kundali_section(styles=styles, unified_report=build_input.unified_report_json))
            elif key == "planetary_positions":
                story.extend(
                    build_planet_section(
                        styles=styles,
                        client_report=build_input.client_report_json,
                        unified_report=build_input.unified_report_json,
                    )
                )
            elif key == "house_analysis":
                story.extend(build_house_section(styles=styles, client_report=build_input.client_report_json))
            elif key == "yoga_analysis":
                story.extend(
                    build_yoga_section(
                        styles=styles,
                        client_report=build_input.client_report_json,
                        unified_report=build_input.unified_report_json,
                    )
                )
            elif key == "dasha_timeline":
                story.extend(build_dasha_section(styles=styles, client_report=build_input.client_report_json))
            elif key == "transit_analysis":
                story.extend(build_transit_section(styles=styles, client_report=build_input.client_report_json))
            elif key == "problem_analysis":
                story.extend(
                    build_problem_section(
                        styles=styles,
                        client_report=build_input.client_report_json,
                        unified_report=build_input.unified_report_json,
                    )
                )
            elif key == "personalized_remedies":
                story.extend(build_remedy_section(styles=styles, client_report=build_input.client_report_json))
            elif key == "final_summary":
                story.extend(
                    build_summary_section(
                        styles=styles,
                        client_report=build_input.client_report_json,
                        unified_report=build_input.unified_report_json,
                    )
                )
            elif key == "digital_access":
                story.extend(
                    build_qr_page(
                        styles=styles,
                        online_report_url=build_input.online_report_url,
                        ai_chat_url=build_input.ai_chat_url,
                    )
                )
            story.append(PageBreak())

        doc = create_document(temp_path)
        doc.build(
            story,
            canvasmaker=lambda *args, **kwargs: MarkerCanvas(
                *args,
                generated_at=generated_at,
                **kwargs,
            ),
        )
        Path(temp_path).unlink(missing_ok=True)
        return section_pages
