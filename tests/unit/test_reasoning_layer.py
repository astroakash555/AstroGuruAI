"""Reasoning layer unit tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from reasoning_layer import ClientHistoryStore, ReasoningEngine, ReasoningInput


def _marriage_delay_input(**overrides) -> ReasoningInput:
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
            ],
            "summary": {"present_count": 1},
        },
        "kp_analysis": {
            "events": [
                {
                    "event_id": "marriage_event",
                    "is_supported": False,
                    "support_score": 0.35,
                    "significators_matched": ["Venus"],
                    "target_houses": [2, 7, 11],
                }
            ],
            "summary": {"supported_events": 0},
        },
        "astro_intelligence": {
            "root_cause_planets": ["Saturn", "Mars", "Venus"],
            "supportive_planets": ["Jupiter"],
            "affected_houses": [7, 8],
            "ranked_causes": [
                {"planet": "Saturn", "severity": 0.8, "reasons": ["Active mahadasha lord."]},
                {"planet": "Mars", "severity": 0.7, "reasons": ["Dosha mangal_dosha severity 0.75."]},
            ],
        },
        "client_id": "client-001",
        "problem_text": "No marriage till age 38",
    }
    base.update(overrides)
    return ReasoningInput(**base)


def test_root_cause_engine_marriage_delay():
    engine = ReasoningEngine()
    result = engine.analyze(_marriage_delay_input())

    cause_types = {item.cause_type for item in result.root_causes}
    assert "actual" in cause_types
    assert result.root_causes[0].triggering_planet
    assert result.root_causes[0].dasha_influence["active_periods"]
    assert result.root_causes[0].transit_influence["influence_type"] in {
        "block",
        "mixed",
        "neutral",
    }
    assert all(item.audit for item in result.root_causes)


def test_contradiction_engine_detects_opposing_systems():
    engine = ReasoningEngine()
    payload = engine.analyze_json(
        _marriage_delay_input(
            doshas={"present_doshas": []},
            yogas={
                "present_yogas": [
                    {
                        "yoga_id": "gaj_kesari",
                        "strength": 0.95,
                        "planets_involved": ["Moon", "Jupiter"],
                        "houses_involved": [2, 9],
                    },
                    {
                        "yoga_id": "malavya",
                        "strength": 0.9,
                        "planets_involved": ["Venus"],
                        "houses_involved": [7],
                    },
                ]
            },
            problem_analysis={
                "category": {"category": "marriage"},
                "severity": {"level": "moderate", "score": 0.4},
                "planets": {"primary": ["Venus"], "shadow": []},
                "houses": {"primary": [7], "secondary": [2], "supporting": [11]},
            },
        )
    )

    assert payload["contradictions"]
    contradiction = payload["contradictions"][0]
    assert contradiction["supporting_evidence"]
    assert contradiction["opposing_evidence"]
    assert 0 <= contradiction["confidence_score"] <= 100


def test_confidence_engine_score_range():
    engine = ReasoningEngine()
    result = engine.analyze(_marriage_delay_input())

    assert 0 <= result.confidence.overall_score <= 100
    assert 0.0 <= result.confidence.vedic_agreement <= 1.0
    assert 0.0 <= result.confidence.kp_agreement <= 1.0
    assert 0.0 <= result.confidence.lal_kitab_agreement <= 1.0


def test_consensus_engine_structure():
    engine = ReasoningEngine()
    payload = engine.analyze_json(_marriage_delay_input())

    consensus = payload["consensus"]
    assert "final_consensus" in consensus
    assert "system_stances" in consensus
    assert set(consensus["system_stances"].keys()) == {"vedic", "kp", "lal_kitab"}
    assert consensus["audit"]


def test_client_history_engine_patterns(tmp_path: Path):
    store = ClientHistoryStore(tmp_path / "history.json")
    store.add_record(
        client_id="client-001",
        record_type="report",
        problem_domain="marriage",
        problem_text="delay in marriage",
        outcome="unresolved",
    )
    store.add_record(
        client_id="client-001",
        record_type="report",
        problem_domain="marriage",
        problem_text="still unmarried",
        outcome="partial",
    )
    store.add_record(
        client_id="client-001",
        record_type="remedy",
        problem_domain="marriage",
        remedies_applied=("venus_mantra",),
        outcome="partial",
    )

    engine = ReasoningEngine(history_store=store)
    result = engine.analyze(_marriage_delay_input())

    assert result.client_history is not None
    assert "marriage" in result.client_history.repeated_problems
    assert result.client_history.report_count >= 2
    assert result.client_history.remedy_effectiveness


def test_audit_engine_traces_all_conclusions():
    engine = ReasoningEngine()
    payload = engine.analyze_json(_marriage_delay_input())

    assert payload["audit_trail"]
    for entry in payload["audit_trail"]:
        assert entry["rule_source"]
        assert entry["engine_source"]
        assert entry["reason_used"]

    assert payload["metadata"]["ai_prediction"] is False
    assert payload["metadata"]["ai_storytelling"] is False
    assert payload["metadata"]["audit_validation_errors"] == []
    assert json.dumps(payload)


def test_reasoning_json_contract():
    engine = ReasoningEngine()
    payload = engine.analyze_json(_marriage_delay_input())

    required = {
        "analyzed_at",
        "problem_domain",
        "root_causes",
        "contradictions",
        "confidence",
        "consensus",
        "audit_trail",
        "metadata",
    }
    assert required.issubset(payload.keys())
    assert payload["problem_domain"] == "marriage"
