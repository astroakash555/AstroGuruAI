"""Ascendant and Moon analysis sections (C, D)."""

from __future__ import annotations

from typing import Any

from backend.app.services.report_engine.base import moon_planet, section
from backend.app.services.report_engine.confidence import section_confidence
from backend.app.services.report_engine.language import format_degree, localize
from backend.app.services.report_engine.consultation_brain_integration import BrainReportContext
from backend.app.services.report_engine.types import ReportLanguage, ReportSection


def build_ascendant_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
    brain_context: BrainReportContext | None = None,
) -> ReportSection:
    kundali = unified_report.get("kundali") or {}
    ascendant = kundali.get("ascendant") or {}
    sign = ascendant.get("sign") or {}
    nakshatra = ascendant.get("nakshatra") or {}
    degree = format_degree(language, float(sign.get("degree_in_sign") or 0.0))
    facts = {
        "longitude": ascendant.get("longitude"),
        "sign": sign.get("name_en"),
        "degree_in_sign": sign.get("degree_in_sign"),
        "nakshatra": nakshatra.get("name"),
        "pada": nakshatra.get("pada"),
    }
    narrative = localize(
        language,
        hi=(
            f"लग्न {sign.get('name_en')} {degree} पर है "
            f"({nakshatra.get('name')} नक्षत्र, पada {nakshatra.get('pada')})।"
        ),
        en=(
            f"The ascendant is in {sign.get('name_en')} at {degree} "
            f"({nakshatra.get('name')} nakshatra, pada {nakshatra.get('pada')})."
        ),
    )
    return section(
        section_id="ascendant_analysis",
        title=localize(language, hi="लग्न विश्लेषण", en="Ascendant Analysis"),
        narrative=narrative,
        facts=facts,
        confidence=section_confidence(unified_report, has_data=bool(sign.get("name_en"))),
    )


def build_moon_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
    brain_context: BrainReportContext | None = None,
) -> ReportSection:
    kundali = unified_report.get("kundali") or {}
    dasha = unified_report.get("dasha") or {}
    moon = moon_planet(kundali) or {}
    sign = moon.get("sign") or {}
    nakshatra = moon.get("nakshatra") or {}
    dasha_moon = dasha.get("moon") or {}
    facts = {
        "longitude": moon.get("longitude"),
        "sign": sign.get("name_en"),
        "degree_in_sign": sign.get("degree_in_sign"),
        "house": moon.get("house"),
        "nakshatra": nakshatra.get("name") or dasha_moon.get("nakshatra"),
        "pada": nakshatra.get("pada") or dasha_moon.get("pada"),
        "dasha_lord": dasha_moon.get("lord"),
        "balance_lord": (dasha.get("balance") or {}).get("lord"),
    }
    narrative = localize(
        language,
        hi=(
            f"चंद्र {sign.get('name_en')} में, भाव {moon.get('house')}, "
            f"{facts['nakshatra']} पada {facts['pada']}। "
            f"जन्म शेष dasha: {facts['balance_lord']}।"
        ),
        en=(
            f"Moon is in {sign.get('name_en')}, house {moon.get('house')}, "
            f"{facts['nakshatra']} pada {facts['pada']}. "
            f"Birth dasha balance lord: {facts['balance_lord']}."
        ),
    )
    return section(
        section_id="moon_analysis",
        title=localize(language, hi="चंद्र विश्लेषण", en="Moon Analysis"),
        narrative=narrative,
        facts=facts,
        confidence=section_confidence(unified_report, has_data=bool(moon)),
    )
