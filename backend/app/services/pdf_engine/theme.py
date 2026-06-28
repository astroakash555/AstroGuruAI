"""Premium PDF color palette and paragraph styles."""

from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


@dataclass(frozen=True)
class PDFTheme:
    dark_blue: colors.Color
    gold: colors.Color
    white: colors.Color
    light_grey: colors.Color
    text_dark: colors.Color


THEME = PDFTheme(
    dark_blue=colors.HexColor("#0B1F3A"),
    gold=colors.HexColor("#C9A227"),
    white=colors.white,
    light_grey=colors.HexColor("#F4F6F8"),
    text_dark=colors.HexColor("#1F2933"),
)


def build_styles(font_regular: str, font_bold: str) -> dict[str, ParagraphStyle]:
    """Create themed paragraph styles."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PremiumTitle",
            parent=base["Title"],
            fontName=font_bold,
            fontSize=24,
            leading=28,
            textColor=THEME.white,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "PremiumSubtitle",
            parent=base["Normal"],
            fontName=font_regular,
            fontSize=12,
            leading=16,
            textColor=THEME.gold,
            alignment=TA_CENTER,
        ),
        "heading1": ParagraphStyle(
            "PremiumHeading1",
            parent=base["Heading1"],
            fontName=font_bold,
            fontSize=18,
            leading=22,
            textColor=THEME.dark_blue,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "heading2": ParagraphStyle(
            "PremiumHeading2",
            parent=base["Heading2"],
            fontName=font_bold,
            fontSize=14,
            leading=18,
            textColor=THEME.dark_blue,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "PremiumBody",
            parent=base["BodyText"],
            fontName=font_regular,
            fontSize=10,
            leading=14,
            textColor=THEME.text_dark,
            alignment=TA_JUSTIFY,
        ),
        "small": ParagraphStyle(
            "PremiumSmall",
            parent=base["Normal"],
            fontName=font_regular,
            fontSize=8,
            leading=10,
            textColor=THEME.text_dark,
            alignment=TA_LEFT,
        ),
        "footer": ParagraphStyle(
            "PremiumFooter",
            parent=base["Normal"],
            fontName=font_regular,
            fontSize=8,
            leading=10,
            textColor=THEME.dark_blue,
            alignment=TA_CENTER,
        ),
        "toc": ParagraphStyle(
            "PremiumTOC",
            parent=base["Normal"],
            fontName=font_regular,
            fontSize=10,
            leading=14,
            textColor=THEME.text_dark,
            leftIndent=12,
        ),
        "confidential": ParagraphStyle(
            "PremiumConfidential",
            parent=base["Normal"],
            fontName=font_bold,
            fontSize=10,
            leading=12,
            textColor=THEME.gold,
            alignment=TA_CENTER,
        ),
    }
