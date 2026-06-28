"""Shared fixtures for professional report engine tests."""

from __future__ import annotations

import pytest


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
                {"number": number, "sign": {"name_en": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"][number - 1]}}
                for number in range(1, 13)
            ],
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
                    "planets_involved": ["Moon", "Jupiter"],
                    "houses_involved": [1, 9],
                }
            ],
            "summary": {"present_count": 1},
        },
        "transits": {
            "saturn": {
                "planet": "Saturn",
                "current": {"sign": {"name_en": "Aquarius"}, "house_from_lagna": 10},
            },
            "jupiter": {
                "planet": "Jupiter",
                "current": {"sign": {"name_en": "Taurus"}, "house_from_lagna": 4},
            },
            "highlights": ["Saturn transiting 10th house"],
        },
        "problem_analysis": {
            "category": {"category": "marriage"},
            "severity": {"level": "high"},
        },
        "fusion": {
            "confidence": 0.82,
            "root_causes": [
                {
                    "title": "Saturn pressure on marriage houses",
                    "confidence": 0.8,
                    "affected_planets": ["Saturn", "Venus"],
                    "affected_houses": [7, 8],
                }
            ],
        },
        "consultation_brain": {
            "executive_summary": "Marriage timing needs patience during Saturn-Venus dasha.",
            "overall_confidence": 0.82,
            "strengths": [{"title": "Jupiter support", "explanation": "Jupiter aspects 7th house"}],
            "risks": [{"title": "Saturn delay", "explanation": "Saturn pressure on 7th house"}],
        },
        "astro_intelligence": {
            "root_cause_planets": ["Saturn", "Mars"],
            "supportive_planets": ["Jupiter"],
            "confidence_score": 0.8,
        },
        "vedic": {
            "observations": [
                {
                    "title": "Saturn in 10th house",
                    "affected_planets": ["Saturn"],
                    "affected_houses": [10],
                },
                {
                    "title": "Venus marriage factor",
                    "affected_planets": ["Venus"],
                    "affected_houses": [7],
                },
            ]
        },
        "remedy_recommendations": {
            "matched_remedies": [{"remedy": {"title": "Shani mantra", "name": "Shani mantra"}}]
        },
        "kp_analysis": {"events": [{"event_type": "marriage", "is_supported": True}]},
        "lal_kitab": {"dosh_findings": [{"finding_name": "Mars 8th House Dosh", "is_present": True}]},
    }


@pytest.fixture
def sample_remedy_generation() -> dict:
    return {"remedies": [{"title": "Hanuman Chalisa", "priority": 1}]}
