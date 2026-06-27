"""Rule studio unit tests."""

from __future__ import annotations

import json

import pytest

from rule_studio import RuleStudioEngine


SAMPLE_RULE = {
    "rule_name": "Saturn 7th House Marriage Delay",
    "system": "vedic",
    "description": "Saturn in 7th house delays marriage.",
    "conditions": {
        "planets": ["Saturn", "Mars"],
        "houses": [7, 8],
        "dasha_lords": ["Saturn"],
        "transits": ["sade_sati_phase"],
        "tags": ["marriage", "delay"],
    },
    "weight": 0.8,
    "confidence": 0.75,
    "outcome": "delayed_outcome",
    "source_book": "Brihat Parashara Hora Shastra",
    "notes": "Classical delay indicator.",
    "domain": "marriage",
    "category": "delayed_marriage",
}


@pytest.fixture
def studio(tmp_path):
    return RuleStudioEngine(tmp_path)


def test_create_and_get_rule(studio):
    created = studio.create_rule_json(SAMPLE_RULE)
    assert created["created"] is True
    rule_id = created["rule"]["rule_id"]

    detail = studio.get_rule_json(rule_id)
    assert detail["rule"]["rule_name"] == SAMPLE_RULE["rule_name"]
    assert detail["rule"]["source_book"] == SAMPLE_RULE["source_book"]
    assert detail["versions"]


def test_rule_versioning_on_update(studio):
    created = studio.create_rule_json(SAMPLE_RULE)
    rule_id = created["rule"]["rule_id"]
    updated = studio.update_rule_json(rule_id, {"description": "Updated description"})
    assert updated["updated"] is True
    assert updated["rule"]["version"] == 2

    versions = studio.get_rule_json(rule_id)["versions"]
    assert len(versions) == 2


def test_approval_workflow(studio):
    rule_id = studio.create_rule_json(SAMPLE_RULE)["rule"]["rule_id"]
    assert studio.submit_for_review_json(rule_id, actor="expert")["success"] is True
    assert studio.approve_json(rule_id, actor="senior_guru")["success"] is True
    assert studio.activate_json(rule_id, actor="senior_guru")["success"] is True

    rule = studio.get_rule_json(rule_id)["rule"]
    assert rule["status"] == "active"
    assert rule["is_active"] is True


def test_deactivate_rule(studio):
    rule_id = studio.create_rule_json(SAMPLE_RULE)["rule"]["rule_id"]
    studio.submit_for_review_json(rule_id, actor="expert")
    studio.approve_json(rule_id, actor="senior_guru")
    studio.activate_json(rule_id, actor="senior_guru")
    result = studio.deactivate_json(rule_id, actor="senior_guru")
    assert result["success"] is True
    assert result["rule"]["status"] == "inactive"


def test_sandbox_testing(studio):
    rule_id = studio.create_rule_json(SAMPLE_RULE)["rule"]["rule_id"]
    payload = studio.sandbox_test_json(rule_id)
    assert "sandbox" in payload
    assert payload["sandbox"]["rule_id"] == rule_id
    assert "match_score" in payload["sandbox"]
    assert payload["performance_run"]["run_id"]


def test_conflict_detection(studio):
    rule_a = studio.create_rule_json(SAMPLE_RULE)["rule"]
    studio.submit_for_review_json(rule_a["rule_id"], actor="expert")
    studio.approve_json(rule_a["rule_id"], actor="senior_guru")
    studio.activate_json(rule_a["rule_id"], actor="senior_guru")

    conflicting = dict(SAMPLE_RULE)
    conflicting["rule_name"] = "Conflicting Marriage Rule"
    conflicting["outcome"] = "strong_support"
    rule_b = studio.create_rule_json(conflicting)["rule"]
    studio.submit_for_review_json(rule_b["rule_id"], actor="expert")
    studio.approve_json(rule_b["rule_id"], actor="senior_guru")
    studio.activate_json(rule_b["rule_id"], actor="senior_guru")

    conflicts = studio.detect_conflicts_json()
    assert conflicts["conflict_count"] >= 1


def test_performance_tracking(studio):
    rule_id = studio.create_rule_json(SAMPLE_RULE)["rule"]["rule_id"]
    studio.sandbox_test_json(rule_id)
    performance = studio.get_rule_json(rule_id)["performance"]
    assert performance["runs"] >= 1


def test_studio_report_json(studio):
    studio.create_rule_json(SAMPLE_RULE)
    report = studio.studio_report_json()
    assert report["total_rules"] >= 1
    assert report["metadata"]["ai_prediction"] is False
    assert json.dumps(report)


def test_create_validation_errors(studio):
    result = studio.create_rule_json({"rule_name": "Incomplete"})
    assert result["created"] is False
    assert result["validation_errors"]
