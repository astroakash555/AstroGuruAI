"""Low-level PDF rendering utilities."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable, SimpleDocTemplate

from backend.app.services.pdf_engine.theme import THEME


class SectionMarker(Flowable):
    """Invisible marker used to capture section page numbers during pass one."""

    width = height = 0

    def __init__(self, section_key: str) -> None:
        self.section_key = section_key

    def draw(self) -> None:
        pages = getattr(self.canv, "_astro_section_pages", None)
        if pages is None:
            pages = {}
            setattr(self.canv, "_astro_section_pages", pages)
        pages[self.section_key] = self.canv.getPageNumber()


class PageNumberCanvas(canvas.Canvas):
    """Two-pass canvas that renders footer with page X of Y."""

    def __init__(self, *args, generated_at: datetime | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict[str, Any]] = []
        self._generated_at = generated_at or datetime.utcnow()

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(total_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_footer(self, total_pages: int) -> None:
        self.saveState()
        self.setStrokeColor(THEME.gold)
        self.setLineWidth(0.6)
        self.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
        self.setFillColor(THEME.dark_blue)
        self.setFont("Helvetica", 8)
        footer_text = (
            f"AstroGuruAI  |  Page {self._pageNumber} of {total_pages}  |  "
            f"Generated {self._generated_at.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        self.drawCentredString(A4[0] / 2.0, 1.0 * cm, footer_text)
        self.restoreState()


def create_document(file_path: str) -> SimpleDocTemplate:
    """Create an A4 document template with premium margins."""
    return SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.2 * cm,
        title="AstroGuruAI Premium Report",
        author="AstroGuruAI",
    )


def escape_text(value: Any) -> str:
    """Escape text for ReportLab Paragraph markup."""
    text = str(value or "")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
