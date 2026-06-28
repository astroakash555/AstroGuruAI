"""Unicode-capable font registration for premium PDFs."""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_REGISTERED = False
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"


def _candidate_font_paths() -> list[Path]:
    windir = os.environ.get("WINDIR", "C:/Windows")
    return [
        Path(windir) / "Fonts" / "Nirmala.ttf",
        Path(windir) / "Fonts" / "NirmalaB.ttf",
        Path(windir) / "Fonts" / "arial.ttf",
        Path(windir) / "Fonts" / "Arial.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"),
    ]


def register_pdf_fonts() -> tuple[str, str]:
    """Register Unicode fonts when available; fall back to built-in Helvetica."""
    global _REGISTERED, FONT_REGULAR, FONT_BOLD
    if _REGISTERED:
        return FONT_REGULAR, FONT_BOLD

    regular_path = None
    bold_path = None
    for path in _candidate_font_paths():
        if not path.exists():
            continue
        name = path.name.lower()
        if "bold" in name or name.endswith("b.ttf"):
            bold_path = bold_path or path
        else:
            regular_path = regular_path or path

    try:
        if regular_path:
            pdfmetrics.registerFont(TTFont("AstroRegular", str(regular_path)))
            FONT_REGULAR = "AstroRegular"
            bold_file = bold_path or regular_path
            pdfmetrics.registerFont(TTFont("AstroBold", str(bold_file)))
            FONT_BOLD = "AstroBold"
    except Exception:
        FONT_REGULAR = "Helvetica"
        FONT_BOLD = "Helvetica-Bold"

    _REGISTERED = True
    return FONT_REGULAR, FONT_BOLD


def reset_font_registration_for_tests() -> None:
    """Reset font registration state (tests only)."""
    global _REGISTERED, FONT_REGULAR, FONT_BOLD
    _REGISTERED = False
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
