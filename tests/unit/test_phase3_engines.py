"""Phase 3 interpreter and writer tests."""

from __future__ import annotations

import json
from datetime import date

import pytest

from ai_engine.interpreters.astro import AstroInterpretationEngine, AstroInterpretationInput
from ai_engine.interpreters.remedy import RemedyGenerationEngine, RemedyGenerationInput
from ai_engine.providers.gemini.config import GeminiConfig
from ai_engine.providers.gemini.client import GeminiClient
from ai_engine.writers.client_report import ClientReportInput, ClientReportWriter
from horoscope_engine import HoroscopeEngine, HoroscopeInput
from naming_engine import NamingEngine, NamingInput
from reports.pdf import PDFReportGenerator


SAMPLE_REPORT = {
    "summary": {"lagna_sign": "Aries", "moon_sign": "Taurus", "moon_nakshatra": "Rohini"},
    "astro_intelligence": {
        "root_cause_planets": ["Saturn", "Mars"],
        "supportive_planets": ["Jupiter"],
        "affected_houses": [7, 8],
        "severity_score": 0.7,
        "confidence_score": 0.8,
    },
    "dasha": {"current": {"mahadasha": {"lord": "Saturn"}, "antardasha": {"lord": "Venus"}}},
    "transits": {
        "saturn": {"planet": "Saturn", "current": {"sign": {"name_en": "Aquarius"}, "house_from_lagna": 10}},
        "jupiter": {"planet": "Jupiter", "current": {"sign": {"name_en": "Taurus"}, "house_from_lagna": 4}},
        "rahu": {"planet": "Rahu", "current": {"sign": {"name_en": "Pisces"}, "house_from_lagna": 12}},
        "ketu": {"planet": "Ketu", "current": {"sign": {"name_en": "Virgo"}, "house_from_lagna": 6}},
    },
    "kp_analysis": {"events": [{"event_type": "marriage", "is_supported": True}]},
    "lal_kitab": {"rin_findings": [], "dosh_findings": [{"finding_name": "Mars 8th House Dosh", "is_present": True}]},
    "problem_analysis": {"category": {"category": "marriage"}, "severity": {"level": "high", "score": 0.8}},
}


@pytest.fixture
def disabled_gemini():
    return GeminiClient(config=GeminiConfig(api_key=None, enabled=False))


@pytest.mark.asyncio
async def test_astro_interpretation_fallback(disabled_gemini):
    engine = AstroInterpretationEngine(gemini_client=disabled_gemini)
    payload = await engine.interpret_json(AstroInterpretationInput(report_json=SAMPLE_REPORT))
    assert payload["root_cause_explanation"]
    assert payload["metadata"]["source"] == "rule_based_fallback"
    assert json.dumps(payload)


@pytest.mark.asyncio
async def test_remedy_generation_fallback(disabled_gemini):
    engine = RemedyGenerationEngine(gemini_client=disabled_gemini)
    payload = await engine.generate_json(RemedyGenerationInput(report_json=SAMPLE_REPORT))
    assert payload["remedies"]
    assert payload["metadata"]["source"] == "rule_based_fallback"


def test_client_report_writer_sections():
    interpretation = {
        "root_cause_explanation": "Saturn-Mars pressure.",
        "affected_planets_explanation": "Venus under stress.",
        "dasha_impact_explanation": "Saturn-Venus dasha.",
        "transit_impact_explanation": "Saturn in 10th.",
        "kp_findings_explanation": "Marriage channel supported.",
        "lal_kitab_findings_explanation": "Mars dosh present.",
    }
    remedy_generation = {"remedies": [{"title": "Hanuman Worship", "priority": 1}]}
    writer = ClientReportWriter()
    payload = writer.write_json(
        ClientReportInput(
            report_json=SAMPLE_REPORT,
            interpretation_json=interpretation,
            remedy_generation_json=remedy_generation,
            problem_text="Marriage delay.",
        )
    )
    assert payload["problem_summary"] == "Marriage delay."
    assert payload["remedies"]
    assert payload["short_term_outlook"]


def test_pdf_generator_creates_file(tmp_path):
    generator = PDFReportGenerator(output_dir=tmp_path)
    result = generator.generate(
        client_report_json={
            "problem_summary": "Test",
            "astrological_root_cause": "Root",
            "planet_analysis": "Planets",
            "dasha_analysis": "Dasha",
            "transit_analysis": "Transit",
            "kp_analysis": "KP",
            "lal_kitab_analysis": "LK",
            "short_term_outlook": "Short",
            "long_term_outlook": "Long",
            "remedies": [{"title": "Mantra", "astrology_system": "vedic", "priority": 1, "description": "Chant"}],
        }
    )
    assert result.file_size_bytes > 0
    assert (tmp_path / result.file_name).exists()


def test_horoscope_engine_json():
    payload = HoroscopeEngine().generate_json(
        HoroscopeInput(
            moon_sign_index=1,
            lagna_sign_index=0,
            current_mahadasha="Saturn",
            current_antardasha="Venus",
            transit_summary={"Saturn": "Discipline focus"},
            target_date=date(2024, 6, 15),
        )
    )
    assert payload["daily"]["period_type"] == "daily"
    assert payload["weekly"]["period_type"] == "weekly"
    assert payload["monthly"]["period_type"] == "monthly"


def test_naming_engine_suggestions():
    payload = NamingEngine().suggest_json(
        NamingInput(nakshatra="Ashwini", pada=1, rashi_sign_index=0, gender="male", count=5)
    )
    assert len(payload["suggestions"]) <= 5
    assert payload["suggestions"][0]["name"]
