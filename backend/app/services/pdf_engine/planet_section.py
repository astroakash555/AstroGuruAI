"""Planet table PDF section."""

from __future__ import annotations

from typing import Any

from reportlab.platypus import Paragraph, Spacer

from backend.app.services.pdf_engine.renderer import escape_text
from backend.app.services.pdf_engine.tables import build_table


def build_planet_section(
    *,
    styles: dict,
    client_report: dict[str, Any],
    unified_report: dict[str, Any] | None,
) -> list:
    section = _find_section(client_report, "planet_wise_interpretation")
    facts = section.get("facts")
    planets = facts.get("planets") if isinstance(facts, dict) else None
    if not planets:
        planets = _planets_from_unified(unified_report)
    rows = [
        [
            "Planet",
            "Sign",
            "House",
            "Degree",
            "Nakshatra",
            "Pada",
            "Retrograde",
            "Combust",
            "Strength",
        ]
    ]
    for planet in planets:
        rows.append(
            [
                planet.get("name"),
                planet.get("sign"),
                planet.get("house"),
                _format_degree(planet.get("degree_in_sign")),
                planet.get("nakshatra"),
                planet.get("pada"),
                "Yes" if planet.get("is_retrograde") else "No",
                planet.get("combust") or "—",
                planet.get("strength") or "—",
            ]
        )
    flowables = [
        Paragraph("Planetary Positions", styles["heading1"]),
        Spacer(1, 8),
        build_table(rows, col_widths=[48, 48, 36, 44, 72, 32, 48, 44, 48]),
        Spacer(1, 10),
    ]
    if section.get("narrative"):
        flowables.append(Paragraph(escape_text(section["narrative"]), styles["body"]))
    return flowables


def _planets_from_unified(unified_report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not unified_report:
        return []
    planets = []
    for planet in (unified_report.get("kundali") or {}).get("planets") or []:
        sign = planet.get("sign") or {}
        nakshatra = planet.get("nakshatra") or {}
        planets.append(
            {
                "name": planet.get("name"),
                "sign": sign.get("name_en"),
                "house": planet.get("house"),
                "degree_in_sign": sign.get("degree_in_sign"),
                "nakshatra": nakshatra.get("name"),
                "pada": nakshatra.get("pada"),
                "is_retrograde": planet.get("is_retrograde"),
            }
        )
    return planets


def _format_degree(value: Any) -> str:
    if value is None:
        return "—"
    return f"{float(value):.2f}°"


def _find_section(client_report: dict, section_id: str) -> dict:
    for section in client_report.get("sections") or []:
        if section.get("section_id") == section_id:
            return section
    return {}
