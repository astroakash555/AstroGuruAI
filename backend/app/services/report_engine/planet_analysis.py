"""Planetary positions section (B) and planet-wise interpretation (E)."""

from __future__ import annotations

from typing import Any

from backend.app.services.consultation_brain.narrative_models import NarrativeSectionId
from backend.app.services.report_engine.base import join_lines, planet_lookup, section
from backend.app.services.report_engine.confidence import section_confidence
from backend.app.services.report_engine.consultation_brain_integration import BrainReportContext
from backend.app.services.report_engine.language import format_degree, localize
from backend.app.services.report_engine.presentation import format_planet_interpretation, scrub_client_text
from backend.app.services.report_engine.types import ReportLanguage, ReportSection

PLANET_ORDER = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")


def _planet_fact(planet: dict[str, Any]) -> dict[str, Any]:
    sign = planet.get("sign") or {}
    nakshatra = planet.get("nakshatra") or {}
    return {
        "name": planet["name"],
        "sign": sign.get("name_en"),
        "degree_in_sign": sign.get("degree_in_sign"),
        "house": planet.get("house"),
        "nakshatra": nakshatra.get("name"),
        "pada": nakshatra.get("pada"),
        "is_retrograde": planet.get("is_retrograde", False),
    }


def _planet_line(planet: dict[str, Any], language: ReportLanguage) -> str:
    sign = planet.get("sign") or {}
    nakshatra = planet.get("nakshatra") or {}
    degree = format_degree(language, float(sign.get("degree_in_sign") or 0.0))
    retro = planet.get("is_retrograde")
    retro_text = localize(language, hi=" (वक्री)", en=" (retrograde)") if retro else ""
    return localize(
        language,
        hi=(
            f"{planet['name']}: {sign.get('name_en')} {degree}, "
            f"भाव {planet.get('house')}, {nakshatra.get('name')} की {nakshatra.get('pada')}वीं पada{retro_text}"
        ),
        en=(
            f"{planet['name']}: {sign.get('name_en')} {degree}, "
            f"house {planet.get('house')}, {nakshatra.get('name')} pada {nakshatra.get('pada')}{retro_text}"
        ),
    )


def _vedic_observations_for_planet(unified_report: dict[str, Any], planet_name: str) -> list[str]:
    vedic = unified_report.get("vedic") or {}
    observations = []
    for item in vedic.get("observations", []):
        planets = item.get("affected_planets") or []
        if planet_name in planets:
            title = item.get("title") or item.get("summary")
            if title:
                observations.append(str(title))
    return observations


def build_planetary_positions_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
    brain_context: BrainReportContext | None = None,
) -> ReportSection:
    kundali = unified_report.get("kundali") or {}
    planets = [planet_lookup(kundali)[name] for name in PLANET_ORDER if name in planet_lookup(kundali)]
    facts = {"planets": [_planet_fact(planet) for planet in planets]}
    intro = ""
    if brain_context is not None:
        intro = brain_context.section_narrative(NarrativeSectionId.OVERALL_CHART_IMPRESSION)
    narrative = join_lines([part for part in (intro, *[ _planet_line(planet, language) for planet in planets]) if part])
    return section(
        section_id="planetary_positions",
        title=localize(language, hi="ग्रह स्थिति", en="Planetary Positions"),
        narrative=scrub_client_text(narrative),
        facts=facts,
        confidence=section_confidence(unified_report, has_data=bool(planets)),
    )


def build_planet_wise_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
    brain_context: BrainReportContext | None = None,
) -> ReportSection:
    if brain_context is not None:
        lines = brain_context.planet_interpretation_lines()
        if lines:
            interpretations = [
                {"name": line.split(":", 1)[0], "observation_summary": [line.split(":", 1)[1].strip()]}
                for line in lines
                if ":" in line
            ]
            return section(
                section_id="planet_wise_interpretation",
                title=localize(language, hi="ग्रह-वार विश्लेषण", en="Planet-wise Interpretation"),
                narrative=join_lines(lines),
                facts={"planets": interpretations},
                confidence=brain_context.overall_confidence(),
            )

    kundali = unified_report.get("kundali") or {}
    lines: list[str] = []
    interpretations: list[dict[str, Any]] = []

    for name in PLANET_ORDER:
        planet = planet_lookup(kundali).get(name)
        if planet is None:
            continue
        observations = _vedic_observations_for_planet(unified_report, name)
        fact = _planet_fact(planet)
        fact["observation_summary"] = observations[:2]
        interpretations.append(fact)
        lines.append(format_planet_interpretation(fact, observations, language=language))

    return section(
        section_id="planet_wise_interpretation",
        title=localize(language, hi="ग्रह-वार विश्लेषण", en="Planet-wise Interpretation"),
        narrative=join_lines(lines),
        facts={"planets": interpretations},
        confidence=section_confidence(unified_report, has_data=bool(interpretations)),
    )
