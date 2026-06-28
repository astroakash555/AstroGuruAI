"""House-wise interpretation section (F)."""

from __future__ import annotations

from typing import Any

from backend.app.services.report_engine.base import join_lines, planet_lookup, section
from backend.app.services.report_engine.confidence import section_confidence
from backend.app.services.report_engine.language import localize
from backend.app.services.report_engine.presentation import scrub_client_text
from backend.app.services.report_engine.types import ReportLanguage, ReportSection


def _house_observations(unified_report: dict[str, Any], house_number: int) -> list[str]:
    vedic = unified_report.get("vedic") or {}
    titles: list[str] = []
    for item in vedic.get("observations", []):
        houses = item.get("affected_houses") or []
        if house_number in houses:
            title = item.get("title") or item.get("summary")
            if title:
                titles.append(str(title))
    return titles


def build_house_wise_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
) -> ReportSection:
    kundali = unified_report.get("kundali") or {}
    houses = kundali.get("houses") or []
    planets_by_house: dict[int, list[str]] = {number: [] for number in range(1, 13)}
    for planet in planet_lookup(kundali).values():
        house = planet.get("house")
        if isinstance(house, int):
            planets_by_house.setdefault(house, []).append(planet["name"])

    house_facts: list[dict[str, Any]] = []
    lines: list[str] = []
    for house in houses:
        number = house.get("number")
        if not isinstance(number, int):
            continue
        sign = (house.get("sign") or {}).get("name_en")
        occupants = planets_by_house.get(number, [])
        observations = _house_observations(unified_report, number)
        summary = (
            "; ".join(observations[:2])
            if observations
            else localize(language, hi="कोई विशेष टिप्पणी नहीं", en="No specific note")
        )
        house_facts.append(
            {
                "house": number,
                "sign": sign,
                "occupants": occupants,
                "summary": summary,
            }
        )
        occupant_text = ", ".join(occupants) if occupants else localize(language, hi="कोई ग्रह नहीं", en="empty")
        lines.append(
            localize(
                language,
                hi=f"भाव {number} ({sign}): ग्रह — {occupant_text}। {summary}",
                en=f"House {number} ({sign}): planets — {occupant_text}. {summary}",
            )
        )

    return section(
        section_id="house_wise_interpretation",
        title=localize(language, hi="भाव-वार विश्लेषण", en="House-wise Interpretation"),
        narrative=scrub_client_text(join_lines(lines)),
        facts={"houses": house_facts},
        confidence=section_confidence(unified_report, has_data=bool(house_facts)),
    )
