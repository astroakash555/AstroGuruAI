"""Shared fixtures for PDF engine tests."""

from __future__ import annotations

import pytest

from backend.app.services.pdf_engine.fonts import reset_font_registration_for_tests
from backend.app.services.report_engine.report_builder import ProfessionalReportBuilder
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage


@pytest.fixture(autouse=True)
def _reset_pdf_fonts():
    reset_font_registration_for_tests()
    yield
    reset_font_registration_for_tests()


@pytest.fixture
def sample_unified_report() -> dict:
    return {
        "subject": {
            "birth_place": "New Delhi, India",
            "timezone": "Asia/Kolkata",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "datetime_utc": "1990-01-15T05:00:00Z",
        },
        "summary": {
            "lagna_sign": "Aries",
            "moon_sign": "Aries",
            "moon_nakshatra": "Ashwini",
            "current_mahadasha": "Saturn",
            "current_antardasha": "Venus",
            "reasoning_confidence_score": 82,
        },
        "kundali": {
            "metadata": {"ayanamsa": "lahiri", "house_system": "whole_sign"},
            "ascendant": {
                "longitude": 5.0,
                "sign": {"name_en": "Aries", "degree_in_sign": 5.0},
                "nakshatra": {"name": "Ashwini", "pada": 1},
            },
            "planets": [
                {
                    "name": name,
                    "longitude": index * 30.0 + 5.0,
                    "sign": {"name_en": sign, "degree_in_sign": 5.0},
                    "nakshatra": {"name": "Ashwini", "pada": 1},
                    "house": index + 1,
                    "is_retrograde": name == "Saturn",
                }
                for index, (name, sign) in enumerate(
                    [
                        ("Sun", "Leo"),
                        ("Moon", "Aries"),
                        ("Mars", "Scorpio"),
                        ("Mercury", "Gemini"),
                        ("Jupiter", "Sagittarius"),
                        ("Venus", "Taurus"),
                        ("Saturn", "Capricorn"),
                        ("Rahu", "Cancer"),
                        ("Ketu", "Capricorn"),
                    ]
                )
            ],
            "houses": [
                {
                    "number": number,
                    "sign": {
                        "name_en": [
                            "Aries",
                            "Taurus",
                            "Gemini",
                            "Cancer",
                            "Leo",
                            "Virgo",
                            "Libra",
                            "Scorpio",
                            "Sagittarius",
                            "Capricorn",
                            "Aquarius",
                            "Pisces",
                        ][number - 1]
                    },
                }
                for number in range(1, 13)
            ],
        },
        "navamsha": {
            "ascendant": {
                "sign": {"name_en": "Leo"},
            },
            "planets": [
                {"name": "Moon", "house": 1, "sign": {"name_en": "Leo"}},
                {"name": "Sun", "house": 5, "sign": {"name_en": "Sagittarius"}},
            ],
            "houses": [{"number": number, "sign": {"name_en": "Leo"}} for number in range(1, 13)],
        },
        "dasha": {
            "birth": {
                "birth_place": "New Delhi, India",
                "timezone": "Asia/Kolkata",
                "date_of_birth": "1990-01-15",
                "birth_time": "10:30:00",
            },
            "moon": {"nakshatra": "Ashwini", "pada": 1, "lord": "Ketu"},
            "balance": {"lord": "Ketu"},
            "current": {
                "mahadasha": {
                    "lord": "Saturn",
                    "start": "2020-01-01T00:00:00Z",
                    "end": "2039-01-01T00:00:00Z",
                },
                "antardasha": {
                    "lord": "Venus",
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2027-01-01T00:00:00Z",
                },
            },
        },
        "yogas": {
            "present_yogas": [
                {
                    "yoga_id": "gaja_kesari",
                    "yoga_name": "Gaja Kesari Yoga",
                    "strength": 0.8,
                    "description": "Moon and Jupiter yoga",
                }
            ],
            "summary": {"present_count": 1},
        },
        "transits": {
            "saturn": {
                "planet": "Saturn",
                "current": {"sign": {"name_en": "Aquarius"}, "house_from_lagna": 10},
            },
            "highlights": ["Saturn transiting 10th house"],
        },
        "problem_analysis": {"category": {"category": "marriage"}, "severity": {"level": "high"}},
        "fusion": {
            "confidence": 0.82,
            "root_causes": [{"title": "Saturn pressure on marriage houses"}],
        },
        "consultation_brain": {
            "executive_summary": "Marriage timing needs patience.",
            "priorities": [{"title": "Focus on Saturn remedies", "explanation": "Reduce delay"}],
            "sections": [
                {
                    "section_id": "relationship",
                    "current_situation": "Delay observed",
                    "root_cause": "Saturn influence",
                    "positive_factors": ["Jupiter support"],
                    "challenges": ["Saturn delay"],
                    "timeline": "2024-2027",
                }
            ],
            "strengths": [{"title": "Jupiter support"}],
            "risks": [{"title": "Saturn delay"}],
        },
        "vedic": {
            "observations": [
                {"title": "Saturn in 10th house", "affected_planets": ["Saturn"], "affected_houses": [10]},
                {"title": "Venus marriage factor", "affected_planets": ["Venus"], "affected_houses": [7]},
            ]
        },
    }


@pytest.fixture
def sample_remedy_generation() -> dict:
    return {"remedies": [{"title": "Hanuman Chalisa", "priority": 1, "description": "Daily recitation"}]}


@pytest.fixture
def sample_client_report(sample_unified_report, sample_remedy_generation) -> dict:
    return ProfessionalReportBuilder().build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
        )
    )
