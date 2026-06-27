"""Consultation layer unit tests."""

from __future__ import annotations

import json
from pathlib import Path

from consultation_layer import ConsultationEngine, ConsultationInput, consultation_input_from_unified_report
from reasoning_layer import ReasoningEngine, ReasoningInput


def _sample_unified_report(**overrides) -> dict:
    reasoning_engine = ReasoningEngine()
    reasoning_input = ReasoningInput(
        kundali={
            "ascendant": {"sign": {"name_en": "Aries"}},
            "planets": [
                {"name": "Saturn", "house": 7, "sign": {"name_en": "Libra"}, "nakshatra": {"name": "Swati"}},
                {"name": "Mars", "house": 8, "sign": {"name_en": "Scorpio"}, "nakshatra": {"name": "Anuradha"}},
                {"name": "Venus", "house": 7, "sign": {"name_en": "Libra"}, "nakshatra": {"name": "Swati"}},
                {"name": "Jupiter", "house": 9, "sign": {"name_en": "Sagittarius"}, "nakshatra": {"name": "Mula"}},
            ],
        },
        navamsha={"chart_type": "d9_navamsha"},
        dasha={
            "system": "vimshottari",
            "moon": {"nakshatra": "Rohini"},
            "current": {"mahadasha": {"lord": "Saturn"}, "antardasha": {"lord": "Venus"}},
        },
        yogas={
            "present_yogas": [
                {
                    "yoga_id": "gaj_kesari",
                    "strength": 0.8,
                    "planets_involved": ["Moon", "Jupiter"],
                    "houses_involved": [2, 9],
                }
            ]
        },
        doshas={
            "present_doshas": [
                {
                    "dosha_id": "mangal_dosha",
                    "severity": 0.75,
                    "planets_involved": ["Mars", "Venus"],
                    "houses_involved": [7, 8],
                }
            ]
        },
        transits={
            "saturn": {
                "planet": "Saturn",
                "natal_impacts": [{"strength": 0.7, "impact_type": "sade_sati_phase"}],
                "current": {"house_from_lagna": 10},
            },
            "jupiter": {"planet": "Jupiter", "natal_impacts": [], "current": {"house_from_lagna": 4}},
            "rahu": {"planet": "Rahu", "natal_impacts": [], "current": {"house_from_lagna": 12}},
            "ketu": {"planet": "Ketu", "natal_impacts": [], "current": {"house_from_lagna": 6}},
        },
        problem_analysis={
            "original_text": "No marriage till age 38",
            "category": {"category": "marriage", "confidence": 0.9},
            "severity": {"level": "high", "score": 0.8},
            "planets": {"primary": ["Venus", "Saturn"], "shadow": ["Mars"]},
            "houses": {"primary": [7], "secondary": [2], "supporting": [11]},
            "root_cause_indicators": ["7th_house_affliction"],
        },
        lal_kitab={
            "rin_findings": [],
            "dosh_findings": [
                {
                    "finding_id": "saturn_rahu_dosh",
                    "finding_name": "Saturn Rahu Dosh",
                    "is_present": True,
                    "strength": 0.8,
                    "planets_involved": ["Saturn", "Rahu"],
                    "recommendation_ids": ["lk_remedy_saturn"],
                }
            ],
            "recommendations": [],
            "summary": {"present_count": 1, "dosh_count": 1, "rin_count": 0},
        },
        kp_analysis={
            "cusps": [
                {"house": 7, "sign": "Libra", "star_lord": "Rahu", "sub_lord": "Saturn"},
                {"house": 2, "sign": "Taurus", "star_lord": "Moon", "sub_lord": "Venus"},
            ],
            "significators": [
                {"house": 7, "level_a": ["Venus"], "level_b": ["Saturn"], "combined": ["Venus", "Saturn"]},
            ],
            "events": [
                {
                    "event_id": "marriage_event",
                    "event_type": "marriage",
                    "is_supported": False,
                    "support_score": 0.35,
                    "target_houses": [2, 7, 11],
                    "significators_matched": ["Venus"],
                }
            ],
            "summary": {"supported_events": 0, "total_events": 1},
        },
        astro_intelligence={
            "root_cause_planets": ["Saturn", "Mars"],
            "supportive_planets": ["Jupiter"],
            "affected_houses": [7, 8],
            "confidence_score": 0.75,
            "recommended_remedies": [{"remedy_id": "vedic_saturn_shani_mantra", "match_score": 0.8}],
        },
        problem_text="No marriage till age 38",
    )
    reasoning = reasoning_engine.analyze(reasoning_input)
    from reasoning_layer.serializers.serializer import to_json_dict as reasoning_to_json

    base = {
        "version": "unified_report_v2",
        "subject": {"client_id": "client-001"},
        "kundali": reasoning_input.kundali,
        "navamsha": reasoning_input.navamsha,
        "dasha": reasoning_input.dasha,
        "yogas": reasoning_input.yogas,
        "doshas": reasoning_input.doshas,
        "transits": reasoning_input.transits,
        "problem_analysis": reasoning_input.problem_analysis,
        "lal_kitab": reasoning_input.lal_kitab,
        "kp_analysis": reasoning_input.kp_analysis,
        "astro_intelligence": reasoning_input.astro_intelligence,
        "reasoning": reasoning_to_json(reasoning),
        "remedy_recommendations": {
            "matched_remedies": [
                {
                    "remedy": {
                        "remedy_id": "vedic_saturn_shani_mantra",
                        "remedy_name": "Shani Mantra",
                        "astrology_system": "vedic",
                    },
                    "match_score": 0.82,
                    "match_reasons": ["Targets root cause planet Saturn."],
                },
                {
                    "remedy": {
                        "remedy_id": "lk_remedy_saturn",
                        "remedy_name": "Lal Kitab Saturn Remedy",
                        "astrology_system": "lal_kitab",
                    },
                    "match_score": 0.71,
                    "match_reasons": ["Matches Lal Kitab dosh finding."],
                },
            ],
            "metadata": {"engine": "remedy_engine_v1"},
        },
    }
    base.update(overrides)
    return base


def test_vedic_agent_findings():
    engine = ConsultationEngine()
    payload = engine.consult_json(
        ConsultationInput(unified_report=_sample_unified_report(), problem_text="No marriage till age 38")
    )
    vedic = next(item for item in payload["specialist_agents"] if item["agent_id"] == "vedic_astrologer")
    assert vedic["findings"]["kundali_analysis"]["lagna_sign"] == "Aries"
    assert vedic["findings"]["dasha_analysis"]["active_periods"]
    assert vedic["findings"]["yoga_findings"]
    assert vedic["findings"]["dosha_findings"]
    assert vedic["audit"]


def test_kp_agent_findings():
    payload = ConsultationEngine().consult_json(
        ConsultationInput(unified_report=_sample_unified_report(), problem_text="No marriage till age 38")
    )
    kp = next(item for item in payload["specialist_agents"] if item["agent_id"] == "kp_astrologer")
    assert kp["findings"]["cuspal_analysis"]
    assert kp["findings"]["significator_analysis"]
    assert kp["findings"]["event_timing"]


def test_problem_specialist_rule_groups():
    payload = ConsultationEngine().consult_json(
        ConsultationInput(unified_report=_sample_unified_report(), problem_text="No marriage till age 38")
    )
    problem = next(
        item for item in payload["specialist_agents"] if item["agent_id"] == "problem_specialist"
    )
    assert problem["findings"]["problem_understanding"]["category"] == "marriage"
    assert problem["findings"]["hidden_problem"]
    assert problem["findings"]["matched_rule_groups"]


def test_senior_guru_conclusion():
    payload = ConsultationEngine().consult_json(
        ConsultationInput(unified_report=_sample_unified_report(), problem_text="No marriage till age 38")
    )
    guru = payload["senior_guru"]
    assert guru["compared_findings"]
    assert guru["strongest_causes"]
    assert guru["strongest_remedies"]
    assert guru["final_conclusion"]["consensus_outcome"]
    assert guru["audit"]


def test_self_review_score():
    payload = ConsultationEngine().consult_json(
        ConsultationInput(unified_report=_sample_unified_report(), problem_text="No marriage till age 38")
    )
    review = payload["self_review"]
    assert 0 <= review["review_score"] <= 100
    assert isinstance(review["contradictions_found"], list)
    assert isinstance(review["missing_evidence"], list)
    assert isinstance(review["weak_remedies"], list)


def test_consultation_json_contract():
    payload = ConsultationEngine().consult_json(
        consultation_input_from_unified_report(
            _sample_unified_report(),
            problem_text="No marriage till age 38",
            client_id="client-001",
        )
    )
    required = {
        "consultation_id",
        "analyzed_at",
        "specialist_agents",
        "senior_guru",
        "self_review",
        "audit_trail",
        "metadata",
    }
    assert required.issubset(payload.keys())
    assert payload["metadata"]["ai_prediction"] is False
    assert payload["metadata"]["marketing_text"] is False
    assert len(payload["specialist_agents"]) == 4
    assert json.dumps(payload)


def test_consultation_records_history(tmp_path: Path):
    from reasoning_layer import ClientHistoryStore

    store = ClientHistoryStore(tmp_path / "history.json")
    engine = ConsultationEngine(history_store=store)
    engine.consult(
        consultation_input_from_unified_report(
            _sample_unified_report(),
            problem_text="No marriage till age 38",
            client_id="client-001",
        )
    )
    records = store.consultations_for_client("client-001")
    assert len(records) == 1
    assert records[0].record_type == "consultation"
