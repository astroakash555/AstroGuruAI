"""Reusable styled table builders."""

from __future__ import annotations

from typing import Any, Sequence

from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

from backend.app.services.pdf_engine.theme import THEME


def build_table(
    data: Sequence[Sequence[Any]],
    *,
    col_widths: list[float] | None = None,
    header_rows: int = 1,
) -> Table:
    """Build a themed table that wraps within page width."""
    table = Table(list(data), colWidths=col_widths, repeatRows=header_rows, hAlign="LEFT")
    style_commands: list[tuple] = [
        ("BACKGROUND", (0, 0), (-1, header_rows - 1), THEME.dark_blue),
        ("TEXTCOLOR", (0, 0), (-1, header_rows - 1), THEME.white),
        ("FONTNAME", (0, 0), (-1, header_rows - 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, header_rows), (-1, -1), [THEME.white, THEME.light_grey]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    table.setStyle(TableStyle(style_commands))
    return table
