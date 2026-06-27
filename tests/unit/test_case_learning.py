"""Case learning unit tests."""

from __future__ import annotations

import json

import pytest

from case_learning import CaseLearningEngine


SAMPLE_CASE = {
    "client_id": "client-001",
    "category": "marriage",
    "problem_text": "No marriage till age 38",
    "kundali_snapshot": {
        "planets": [
            {"name": "Saturn", "house": 7},
            {"name": "Mars", "house": 8},
        ]
    },
    "system_prediction": {
        "planets": ["Saturn", "Mars"],
        "houses": [7, 8],
        "consensus_outcome": "delayed_outcome",
    },
    "applied_rules": ["marriage_delay_saturn_7th"],
    "applied_remedies": ["vedic_saturn_shani_mantra"],
    "predicted_outcome": "delayed_outcome",
    "final_outcome": "delayed_outcome",
}


@pytest.fixture
def engine(tmp_path):
    return CaseLearningEngine(tmp_path)


def test_record_consultation_case(engine):
    result = engine.record_consultation_json(SAMPLE_CASE)
    assert result["recorded"] is True
    assert result["case"]["category"] == "marriage"


def test_add_follow_up(engine):
    case_id = engine.record_consultation_json(SAMPLE_CASE)["case"]["case_id"]
    result = engine.add_follow_up_json(
        case_id,
        {
            "outcome_type": "success",
            "description": "Marriage occurred after remedies",
            "remedy_effectiveness": "effective",
            "final_outcome": "success",
        },
    )
    assert result["updated"] is True
    assert len(result["case"]["follow_up_results"]) == 1


def test_learning_metrics(engine):
    engine.record_consultation_json(SAMPLE_CASE)
    metrics = engine.metrics_json()["metrics"]
    assert 0.0 <= metrics["prediction_accuracy"] <= 1.0
    assert 0.0 <= metrics["remedy_success_rate"] <= 1.0
    assert 0.0 <= metrics["rule_accuracy"] <= 1.0


def test_suggestions_generated(engine):
    engine.record_consultation_json(SAMPLE_CASE)
    for _ in range(2):
        weak_case = dict(SAMPLE_CASE)
        weak_case["applied_rules"] = ["weak_rule_1"]
        weak_case["predicted_outcome"] = "strong_support"
        weak_case["final_outcome"] = "blocked_outcome"
        weak_case["system_prediction"] = {"consensus_outcome": "strong_support"}
        engine.record_consultation_json(weak_case)

    suggestions = engine.suggestions_json()
    assert suggestions["count"] >= 1
    types = {item["suggestion_type"] for item in suggestions["suggestions"]}
    assert types & {"weak_rule", "rule_improvement", "obsolete_rule"}


def test_new_rule_candidate_suggestion(engine):
    for _ in range(2):
        case = dict(SAMPLE_CASE)
        case["applied_rules"] = []
        case["category"] = "career"
        case["problem_text"] = "Job loss"
        case["final_outcome"] = "unemployment"
        engine.record_consultation_json(case)

    suggestions = engine.suggestions_json(category="career")
    assert any(item["suggestion_type"] == "new_rule_candidate" for item in suggestions["suggestions"])


def test_feedback_loops(engine):
    engine.record_consultation_json(SAMPLE_CASE)
    bad_case = dict(SAMPLE_CASE)
    bad_case["predicted_outcome"] = "strong_support"
    bad_case["final_outcome"] = "blocked_outcome"
    bad_case["applied_remedies"] = ["failed_remedy"]
    engine.record_consultation_json(bad_case)
    engine.add_follow_up_json(
        engine.list_cases_json()["cases"][1]["case_id"],
        {"outcome_type": "failure", "remedy_effectiveness": "ineffective"},
    )

    loops = engine.feedback_loops_json()
    assert loops["count"] >= 1


def test_learning_report_json(engine):
    engine.record_consultation_json(SAMPLE_CASE)
    report = engine.learning_report_json()
    assert report["total_cases"] >= 1
    assert "metrics" in report
    assert "category_tracking" in report
    assert report["metadata"]["ai_prediction"] is False
    assert json.dumps(report)


def test_record_from_consultation(engine):
    unified_report = {
        "kundali": SAMPLE_CASE["kundali_snapshot"],
        "astro_intelligence": {"root_cause_planets": ["Saturn"], "affected_houses": [7]},
        "reasoning": {"consensus": {"final_consensus": "delayed_outcome"}, "confidence": {"overall_score": 65}},
    }
    result = engine.record_from_consultation(
        client_id="client-002",
        category="marriage",
        problem_text="Marriage delay",
        unified_report=unified_report,
        applied_rules=("rule_1",),
        applied_remedies=("remedy_1",),
    )
    assert result["recorded"] is True
