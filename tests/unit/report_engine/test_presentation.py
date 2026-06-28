"""Unit tests for client report presentation helpers."""

from __future__ import annotations

import pytest

from backend.app.services.report_engine.presentation import (
    assert_client_safe_text,
    clean_remedy_items,
    format_confidence,
    format_dasha_narrative,
    format_iso_date,
    format_kp_analysis,
    format_lal_kitab_analysis,
    format_planet_interpretation,
    format_planet_position_line,
    format_section_facts,
    normalize_client_facts,
    scrub_client_text,
)
from backend.app.services.report_engine.types import ReportLanguage


def test_assert_client_safe_text_raises_on_forbidden():
    with pytest.raises(ValueError, match="Forbidden"):
        assert_client_safe_text("supported=true")


def test_scrub_client_text_replaces_diagnostics():
    text = scrub_client_text("Engine remedy with supported=false and engine output")
    assert "supported=" not in text.lower()
    assert "Engine remedy" not in text


def test_format_confidence_variants():
    assert format_confidence(None) == "—"
    assert format_confidence(0.82) == "82%"
    assert format_confidence(75) == "75%"


def test_format_iso_date_handles_invalid_and_english():
    assert format_iso_date(None, language=ReportLanguage.HINDI) == "—"
    assert format_iso_date("2020-01-01T00:00:00Z", language=ReportLanguage.ENGLISH).startswith("01 ")
    assert format_iso_date("bad-date", language=ReportLanguage.HINDI) == "bad-date"
    assert format_iso_date("2020-01-01T00:00:00Z", language=ReportLanguage.HINDI) == "01/01/2020"


def test_format_planet_position_line_english_and_hindi():
    planet = {
        "name": "Moon",
        "sign": "Aries",
        "house": 1,
        "nakshatra": "Ashwini",
        "pada": 1,
        "degree_in_sign": 5.0,
        "is_retrograde": True,
    }
    assert "retrograde" in format_planet_position_line(planet, language=ReportLanguage.ENGLISH)
    assert "वक्री" in format_planet_position_line(planet, language=ReportLanguage.HINDI)


def test_format_planet_interpretation_with_and_without_observations():
    planet = {"name": "Sun", "sign": "Leo", "house": 5, "nakshatra": "Magha", "pada": 2}
    empty = format_planet_interpretation(planet, [], language=ReportLanguage.HINDI)
    assert "विशेष टिप्पणी" in empty
    with_obs = format_planet_interpretation(
        planet, ["Leadership quality"], language=ReportLanguage.ENGLISH
    )
    assert "Key influence" in with_obs


def test_format_kp_analysis_all_branches():
    empty = format_kp_analysis({}, language=ReportLanguage.HINDI)
    assert "उपलब्ध नहीं" in empty

    payload = {
        "kp_analysis": {
            "events": [
                {"event_type": "marriage", "is_supported": True},
                {"event_type": "career", "is_supported": False},
                {"event_type": "health"},
                {"is_supported": True},
            ]
        }
    }
    hi = format_kp_analysis(payload, language=ReportLanguage.HINDI)
    en = format_kp_analysis(payload, language=ReportLanguage.ENGLISH)
    assert "supported=" not in hi.lower()
    assert "marriage" in en
    assert "mixed or weak" in en


def test_format_lal_kitab_analysis_remedies_and_empty():
    empty = format_lal_kitab_analysis({}, language=ReportLanguage.ENGLISH)
    assert "No Lal Kitab" in empty

    payload = {
        "lal_kitab": {
            "dosh_findings": [{"finding_name": "Mars 8th House Dosh"}, {"name": ""}],
            "remedies": [{"title": "Feed birds"}],
        },
        "lal_kitab_intelligence": {"remedies": [{"remedy": "Donate red cloth"}]},
    }
    hi = format_lal_kitab_analysis(payload, language=ReportLanguage.HINDI)
    en = format_lal_kitab_analysis(payload, language=ReportLanguage.ENGLISH)
    assert "लाल किताब" in hi
    assert "Lal Kitab note" in en


def test_format_dasha_narrative_english():
    facts = {
        "current_mahadasha": "Saturn",
        "current_antardasha": "Venus",
        "balance_lord": "Ketu",
        "current_mahadasha_start": "2020-01-01T00:00:00Z",
        "current_mahadasha_end": "2039-01-01T00:00:00Z",
        "current_antardasha_start": "2024-01-01T00:00:00Z",
        "current_antardasha_end": "2027-01-01T00:00:00Z",
    }
    text = format_dasha_narrative(facts, language=ReportLanguage.ENGLISH)
    assert "mahadasha" in text
    assert "T00:00:00Z" not in text


def test_format_section_facts_per_section():
    assert format_section_facts("unknown", {}, language=ReportLanguage.HINDI) == []
    assert format_section_facts("unknown", None, language=ReportLanguage.HINDI) == []
    assert format_section_facts("unknown", "plain fact", language=ReportLanguage.HINDI) == ["plain fact"]

    birth = format_section_facts(
        "birth_details",
        {"birth_place": "Delhi", "date_of_birth": "1990-01-15"},
        language=ReportLanguage.HINDI,
    )
    assert any("जन्म स्थान" in line for line in birth)

    planets = format_section_facts(
        "planetary_positions",
        {"planets": [{"name": "Moon", "sign": "Aries", "house": 1, "nakshatra": "Ashwini", "pada": 1}]},
        language=ReportLanguage.HINDI,
    )
    assert planets

    houses = format_section_facts(
        "house_wise_interpretation",
        {"houses": [{"house": 1, "sign": "Aries", "occupants": ["Moon"], "summary": "Strong lagna"}]},
        language=ReportLanguage.ENGLISH,
    )
    assert "House 1" in houses[0]

    yogas = format_section_facts(
        "yoga_analysis",
        {"yogas": [{"name": "Gaja Kesari", "meaning": "Moon-Jupiter yoga"}]},
        language=ReportLanguage.HINDI,
    )
    assert "Gaja Kesari" in yogas[0]

    remedies = format_section_facts(
        "personalized_remedies",
        {"remedies": [{"priority": "High", "title": "Hanuman Chalisa"}]},
        language=ReportLanguage.HINDI,
    )
    assert "Hanuman Chalisa" in remedies[0]

    strengths = format_section_facts(
        "strengths",
        {"items": [{"text": "Jupiter support"}]},
        language=ReportLanguage.HINDI,
    )
    assert strengths == ["Jupiter support"]

    summary = format_section_facts(
        "final_summary",
        {"executive_summary": "Overall positive", "chart_summary": "Aries lagna"},
        language=ReportLanguage.HINDI,
    )
    assert len(summary) == 2

    problem = format_section_facts(
        "problem_analysis",
        {
            "problem_text": "Marriage delay",
            "category": "marriage",
            "severity": "high",
            "root_cause_summaries": ["Saturn influence"],
        },
        language=ReportLanguage.HINDI,
    )
    assert any("प्रश्न" in line for line in problem)

    generic = format_section_facts(
        "transit_analysis",
        {"highlights": ["Saturn in 10th"], "score": 0.8},
        language=ReportLanguage.HINDI,
    )
    assert "Saturn in 10th" in generic


def test_clean_remedy_items_scrubs_descriptions():
    items = clean_remedy_items([{"title": "Mantra", "description": "Engine remedy daily", "priority": 1}])
    assert items[0]["title"] == "Mantra"
    assert "Engine remedy" not in items[0]["description"]


def test_normalize_client_facts_filters_empty_values():
    assert normalize_client_facts(["", "valid", None]) == ["valid"]
    assert normalize_client_facts({"a": "", "b": "kept"}) == ["kept"]
