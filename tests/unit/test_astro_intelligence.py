"""Astro Intelligence engine unit tests."""

from __future__ import annotations

import json

from astro_intelligence import AstroIntelligenceEngine, AstroIntelligenceInput


def _sample_input(**overrides) -> AstroIntelligenceInput:
    base = {
        "kundali": {
            "ascendant": {"sign": {"name_en": "Aries"}},
            "planets": [
                {"name": "Sun", "house": 5, "sign": {"name_en": "Leo"}},
                {"name": "Moon", "house": 2, "sign": {"name_en": "Taurus"}},
                {"name": "Mars", "house": 8, "sign": {"name_en": "Scorpio"}},
                {"name": "Mercury", "house": 3, "sign": {"name_en": "Gemini"}},
                {"name": "Jupiter", "house": 9, "sign": {"name_en": "Sagittarius"}},
                {"name": "Venus", "house": 7, "sign": {"name_en": "Libra"}},
                {"name": "Saturn", "house": 7, "sign": {"name_en": "Libra"}},
                {"name": "Rahu", "house": 6, "sign": {"name_en": "Virgo"}},
                {"name": "Ketu", "house": 12, "sign": {"name_en": "Pisces"}},
            ],
        },
        "navamsha": {"chart_type": "d9_navamsha"},
        "dasha": {
            "current": {
                "mahadasha": {"lord": "Saturn"},
                "antardasha": {"lord": "Venus"},
            }
        },
        "yogas": {
            "present_yogas": [
                {
                    "yoga_id": "gaj_kesari",
                    "strength": 0.8,
                    "planets_involved": ["Moon", "Jupiter"],
                    "houses_involved": [2, 9],
                }
            ]
        },
        "doshas": {
            "present_doshas": [
                {
                    "dosha_id": "mangal_dosha",
                    "severity": 0.75,
                    "planets_involved": ["Mars", "Venus"],
                    "houses_involved": [7, 8],
                }
            ]
        },
        "transits": {
            "saturn": {
                "planet": "Saturn",
                "natal_impacts": [{"strength": 0.7, "impact_type": "sade_sati_phase"}],
                "current": {"house_from_lagna": 10},
            },
            "jupiter": {"planet": "Jupiter", "natal_impacts": [], "current": {"house_from_lagna": 4}},
            "rahu": {"planet": "Rahu", "natal_impacts": [], "current": {"house_from_lagna": 12}},
            "ketu": {"planet": "Ketu", "natal_impacts": [], "current": {"house_from_lagna": 6}},
        },
        "problem_analysis": {
            "category": {"category": "marriage"},
            "severity": {"level": "high", "score": 0.8},
            "planets": {"primary": ["Venus", "Saturn"], "shadow": ["Mars"]},
            "houses": {"primary": [7], "secondary": [2], "supporting": [11]},
        },
        "lal_kitab": {
            "dosh_findings": [
                {
                    "finding_id": "saturn_rahu_dosh",
                    "is_present": True,
                    "strength": 0.8,
                    "planets_involved": ["Saturn", "Rahu"],
                    "houses_involved": [7, 12],
                }
            ]
        },
        "kp_analysis": {
            "events": [
                {
                    "event_id": "marriage_event",
                    "is_supported": True,
                    "support_score": 0.6,
                    "significators_matched": ["Venus"],
                    "target_houses": [2, 7, 11],
                }
            ]
        },
    }
    base.update(overrides)
    return AstroIntelligenceInput(**base)


def test_astro_intelligence_output_structure():
    engine = AstroIntelligenceEngine()
    result = engine.analyze(_sample_input())

    assert result.root_cause_planets
    assert result.affected_houses
    assert 0.0 <= result.severity_score <= 1.0
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.recommended_remedies
    assert result.metadata["ai_interpretation"] is False


def test_astro_intelligence_json_contract():
    engine = AstroIntelligenceEngine()
    payload = engine.analyze_json(_sample_input())

    required = {
        "root_cause_planets",
        "supportive_planets",
        "affected_houses",
        "planetary_conflicts",
        "severity_score",
        "recommended_remedies",
        "confidence_score",
    }
    assert required.issubset(payload.keys())
    assert payload["metadata"]["ai_interpretation"] is False
    assert json.dumps(payload)


def test_planetary_conflicts_detected_for_saturn_venus_conjunction():
    engine = AstroIntelligenceEngine()
    payload = engine.analyze_json(_sample_input())

    conflict_types = {item["conflict_type"] for item in payload["planetary_conflicts"]}
    assert "malefic_benefic_conjunction" in conflict_types or "dosha_pair" in conflict_types
