"""Chart rendering from existing kundali JSON (display only, no recalculation)."""

from __future__ import annotations

from typing import Any

from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.platypus import Flowable, Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.theme import THEME


class ChartDrawing(Flowable):
    """Flowable wrapper for a ReportLab drawing."""

    def __init__(self, drawing: Drawing, width: float, height: float) -> None:
        self.drawing = drawing
        self.width = width
        self.height = height

    def draw(self) -> None:
        renderPDF.draw(self.drawing, self.canv, 0, 0)


def _planets_by_house(chart: dict[str, Any]) -> dict[int, list[str]]:
    mapping: dict[int, list[str]] = {number: [] for number in range(1, 13)}
    for planet in chart.get("planets") or []:
        house = planet.get("house")
        if isinstance(house, int):
            mapping.setdefault(house, []).append(str(planet.get("name", "")))
    return mapping


def _moon_chart_from_lagna(kundali: dict[str, Any]) -> dict[int, list[str]]:
    """Rotate existing whole-sign houses so Moon becomes the reference lagna."""
    moon = next((p for p in kundali.get("planets") or [] if p.get("name") == "Moon"), None)
    if not moon or not isinstance(moon.get("house"), int):
        return _planets_by_house(kundali)
    moon_house = int(moon["house"])
    rotated: dict[int, list[str]] = {number: [] for number in range(1, 13)}
    for planet in kundali.get("planets") or []:
        house = planet.get("house")
        if not isinstance(house, int):
            continue
        display_house = ((house - moon_house) % 12) + 1
        rotated.setdefault(display_house, []).append(str(planet.get("name", "")))
    return rotated


def _north_indian_drawing(planets_by_house: dict[int, list[str]], title: str) -> Drawing:
    width, height = 340, 340
    drawing = Drawing(width, height)
    drawing.add(Rect(0, 0, width, height, fillColor=THEME.white, strokeColor=THEME.dark_blue, strokeWidth=1.2))
    drawing.add(String(width / 2, height - 18, title, fontSize=11, fillColor=THEME.dark_blue, textAnchor="middle"))

    # North Indian diamond house layout coordinates (approximate)
    positions = {
        1: (170, 285),
        2: (255, 250),
        3: (285, 170),
        4: (255, 90),
        5: (170, 55),
        6: (85, 90),
        7: (55, 170),
        8: (85, 250),
        9: (170, 220),
        10: (220, 170),
        11: (170, 120),
        12: (120, 170),
    }
    for house, (x, y) in positions.items():
        occupants = ", ".join(planets_by_house.get(house, [])) or "-"
        label = f"H{house}"
        drawing.add(String(x, y + 8, label, fontSize=8, fillColor=THEME.gold, textAnchor="middle"))
        drawing.add(String(x, y - 6, occupants[:18], fontSize=7, fillColor=THEME.text_dark, textAnchor="middle"))
    return drawing


def build_chart_flowables(
    *,
    title: str,
    chart: dict[str, Any],
    styles: dict,
    moon_reference: bool = False,
) -> list:
    """Render a chart section from existing JSON."""
    planets_by_house = _moon_chart_from_lagna(chart) if moon_reference else _planets_by_house(chart)
    drawing = _north_indian_drawing(planets_by_house, title)
    lagna = (chart.get("ascendant") or {}).get("sign", {}).get("name_en", "—")
    caption = Paragraph(
        f"<b>{escape_text(title)}</b><br/>Lagna sign: {escape_text(lagna)}",
        styles["body"],
    )
    return [caption, Spacer(1, 8), ChartDrawing(drawing, 340, 340), Spacer(1, 14)]
