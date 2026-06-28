"""Tests for evidence normalization and scoring."""

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence
from backend.app.services.consultation_brain.reasoning import normalize_evidence, score_evidence


def test_normalize_evidence_clamps_and_strips(sample_evidence):
    noisy = ConsultationEvidence(
        evidence_id=sample_evidence.evidence_id,
        source=sample_evidence.source,
        category=sample_evidence.category,
        title="  Title  ",
        summary="  Summary  ",
        weight=sample_evidence.weight,
        confidence=2.0,
        raw_reference=sample_evidence.raw_reference,
        tags=sample_evidence.tags,
    )
    normalized = normalize_evidence([noisy])
    assert normalized[0].title == "Title"
    assert normalized[0].confidence <= 1.0


def test_score_evidence_empty_returns_zero():
    assert score_evidence([]) == 0.0


def test_score_evidence_zero_total_weight_returns_zero():
    zero_weight = ConsultationEvidence(
        evidence_id="z",
        source=EvidenceSource.YOGAS,
        category=EvidenceCategory.GENERAL,
        title="Zero",
        summary="Zero",
        weight=0.0,
        confidence=0.9,
    )
    assert score_evidence([zero_weight]) == 0.0


def test_score_evidence_weighted_average(sample_evidence):
    second = ConsultationEvidence(
        evidence_id="evidence-dasha-2",
        source=EvidenceSource.DASHA,
        category=EvidenceCategory.TIMING,
        title="Dasha",
        summary="Timing",
        weight=0.7,
        confidence=0.5,
    )
    score = score_evidence([sample_evidence, second])
    assert 0.0 < score <= 1.0
