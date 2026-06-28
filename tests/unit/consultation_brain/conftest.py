"""Shared fixtures for consultation brain unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationInput


@pytest.fixture
def sample_unified_report() -> dict:
    return {
        "yogas": {
            "present_yogas": [
                {
                    "yoga_id": "gaj_kesari",
                    "name": "Gaj Kesari Yoga",
                    "strength": 0.82,
                    "planets_involved": ["Moon", "Jupiter"],
                    "houses_involved": [1, 7],
                }
            ],
            "summary": {"present_count": 1},
        },
        "dasha": {
            "system": "vimshottari",
            "current": {
                "mahadasha": {"lord": "Saturn", "strength": 0.7},
                "antardasha": {"lord": "Venus", "strength": 0.6},
            },
        },
        "transits": {
            "saturn": {
                "planet": "Saturn",
                "natal_impacts": [{"impact_type": "sade_sati_phase", "strength": 0.75}],
                "current": {"house_from_lagna": 7},
            }
        },
        "kp_analysis": {
            "events": [
                {
                    "event_id": "marriage_event",
                    "event_type": "marriage",
                    "is_supported": False,
                    "support_score": 0.35,
                }
            ],
            "summary": {"supported_events": 0, "total_events": 1},
        },
        "kp": {
            "observations": [
                {
                    "observation_id": "kp-obs-1",
                    "title": "Marriage significators weak",
                    "confidence": 0.62,
                }
            ]
        },
        "lal_kitab": {
            "dosh_findings": [
                {
                    "finding_id": "saturn_rahu_dosh",
                    "finding_name": "Saturn Rahu Dosh",
                    "is_present": True,
                    "strength": 0.8,
                }
            ]
        },
        "lal_kitab_intelligence": {
            "observations": [
                {
                    "observation_id": "lk-obs-1",
                    "title": "House 7 afflicted",
                    "confidence": 0.58,
                }
            ]
        },
        "fusion": {
            "confidence": 0.72,
            "root_causes": [
                {"cause_id": "seventh_house", "label": "7th house affliction", "confidence": 0.7}
            ],
            "observations": [{"observation_id": "fusion-1", "title": "Mixed marriage signals", "confidence": 0.65}],
        },
        "rule_studio": {
            "matched_rules": [
                {
                    "rule_id": "marriage_delay_rule",
                    "title": "Marriage delay indicator",
                    "confidence": 0.66,
                    "domain": "relationship",
                }
            ]
        },
        "case_learning": {
            "matched_patterns": [
                {
                    "pattern_id": "late_marriage_case",
                    "title": "Late marriage pattern",
                    "similarity": 0.71,
                }
            ]
        },
        "golden_dataset": {
            "matches": [
                {
                    "match_id": "benchmark_marriage_001",
                    "title": "Marriage delay benchmark",
                    "match_score": 0.84,
                }
            ]
        },
    }


@pytest.fixture
def sample_consultation_input(sample_unified_report) -> ConsultationInput:
    return ConsultationInput(
        unified_report=sample_unified_report,
        professional_report={
            "sections": [
                {
                    "section_id": "summary",
                    "title": "Executive Summary",
                    "facts": ["Marriage delay indicated.", "Saturn influence on 7th house."],
                    "confidence": 0.68,
                }
            ]
        },
        problem_text="Marriage delay",
        language="hi",
        reference_time=datetime(2026, 6, 15, 12, 0, tzinfo=UTC),
    )


@pytest.fixture
def sample_evidence() -> ConsultationEvidence:
    return ConsultationEvidence(
        evidence_id="evidence-yogas-1",
        source=EvidenceSource.YOGAS,
        category=EvidenceCategory.GENERAL,
        title="Yoga signal",
        summary="Placeholder yoga evidence.",
        weight=0.6,
        confidence=0.4,
        raw_reference="yogas",
        tags=("yogas",),
    )
