"""Remedy engine unit tests."""

from __future__ import annotations

import json

from remedy_engine import RemedyEngine, RemedyMatchContext, RemedyKnowledgeRegistry
from remedy_engine.models import RemedyRecord


def test_knowledge_registry_contains_all_systems():
    registry = RemedyKnowledgeRegistry()
    systems = {remedy.astrology_system for remedy in registry.remedies}

    assert systems == {"vedic", "lal_kitab", "kp"}
    assert len(registry.remedies) >= 15


def test_remedy_record_fields():
    remedy = RemedyRecord(
        remedy_id="test_remedy",
        remedy_name="Test Remedy",
        remedy_type="mantra",
        astrology_system="vedic",
        planet="Saturn",
        house=7,
        severity="high",
        category="marriage",
        description="Test description.",
        expected_effect="Test effect.",
        confidence_score=0.8,
        priority=1,
    )

    assert remedy.remedy_id == "test_remedy"
    assert remedy.confidence_score == 0.8


def test_remedy_matching_for_marriage_context():
    engine = RemedyEngine()
    result = engine.match(
        RemedyMatchContext(
            root_cause_planets=("Saturn", "Venus"),
            affected_houses=(7,),
            categories=("marriage",),
            severity_level="high",
        )
    )

    payload = engine.match_json(
        RemedyMatchContext(
            root_cause_planets=("Saturn", "Venus"),
            affected_houses=(7,),
            categories=("marriage",),
            severity_level="high",
        )
    )

    assert result.matched_remedies
    assert payload["metadata"]["ai_interpretation"] is False
    assert "remedy_id" in payload["matched_remedies"][0]["remedy"]
    assert json.dumps(payload)


def test_knowledge_json_contract():
    engine = RemedyEngine()
    payload = engine.list_knowledge_json()

    assert payload["total_count"] >= 15
    assert payload["remedies"][0]["astrology_system"] in {"vedic", "lal_kitab", "kp"}
