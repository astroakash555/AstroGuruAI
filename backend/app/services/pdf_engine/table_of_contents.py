"""Table of contents with page numbers."""

from __future__ import annotations

from reportlab.platypus import Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text


def build_table_of_contents(
    *,
    styles: dict,
    entries: list[tuple[str, str, int | None]],
) -> list:
    """Build TOC from (section_key, title, page_number) tuples."""
    flowables = [Paragraph("Table of Contents", styles["heading1"]), Spacer(1, 12)]
    for _key, title, page in entries:
        page_text = str(page) if page is not None else "—"
        dots = "." * max(4, 60 - len(title) - len(page_text))
        line = f"{escape_text(title)} {dots} {page_text}"
        flowables.append(Paragraph(line, styles["toc"]))
        flowables.append(Spacer(1, 4))
    return flowables
