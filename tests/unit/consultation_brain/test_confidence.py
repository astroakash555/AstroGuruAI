"""Tests for unified confidence calculation."""

from backend.app.services.consultation_brain.confidence import compute_overall_confidence
from backend.app.services.consultation_brain.constants import DEFAULT_OVERALL_CONFIDENCE
from backend.app.services.consultation_brain.models import ConsultationConflict, ConsultationPriority


def test_compute_overall_confidence_default_without_evidence():
    assert compute_overall_confidence(evidence=[], conflicts=[], priorities=[]) == DEFAULT_OVERALL_CONFIDENCE


def test_compute_overall_confidence_blends_signals(sample_evidence):
    priorities = (
        ConsultationPriority(
            rank=1,
            domain="general",
            title="Focus",
            rationale="Because",
            confidence=0.5,
            evidence_ids=(sample_evidence.evidence_id,),
        ),
    )
    conflicts = (
        ConsultationConflict(
            conflict_id="c1",
            evidence_ids=(sample_evidence.evidence_id,),
            description="d",
            resolution="r",
            resolved_confidence=0.4,
        ),
    )
    score = compute_overall_confidence(
        evidence=[sample_evidence],
        conflicts=conflicts,
        priorities=priorities,
    )
    assert 0.0 <= score <= 1.0
