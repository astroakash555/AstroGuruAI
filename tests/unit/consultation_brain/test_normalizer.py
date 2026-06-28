"""Tests for EvidenceNormalizer."""

from datetime import UTC, datetime

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence
from backend.app.services.consultation_brain.normalizer import EvidenceNormalizer


def test_normalizer_clamps_confidence_and_strips_labels(sample_evidence):
    noisy = ConsultationEvidence(
        evidence_id="  evidence-yogas-1  ",
        source=sample_evidence.source,
        category=sample_evidence.category,
        title="  Yoga Signal  ",
        summary="  Summary text  ",
        weight=1.5,
        confidence=2.0,
        raw_reference=" yogas ",
        tags=(" YOGAS ", "yogas"),
    )
    normalized = EvidenceNormalizer().normalize_item(noisy)
    assert normalized.evidence_id == "evidence-yogas-1"
    assert normalized.title == "Yoga Signal"
    assert normalized.confidence == 1.0
    assert normalized.weight == 1.0
    assert normalized.tags == ("yogas",)


def test_normalizer_removes_duplicate_evidence_ids():
    first = ConsultationEvidence(
        evidence_id="duplicate",
        source=EvidenceSource.YOGAS,
        category=EvidenceCategory.GENERAL,
        title="First",
        summary="First",
        weight=0.6,
        confidence=0.4,
    )
    second = ConsultationEvidence(
        evidence_id="duplicate",
        source=EvidenceSource.DASHA,
        category=EvidenceCategory.TIMING,
        title="Second",
        summary="Second",
        weight=0.7,
        confidence=0.5,
    )
    normalized = EvidenceNormalizer().normalize((first, second))
    assert len(normalized) == 1
    assert normalized[0].evidence_id == "duplicate"
    assert normalized[0].source == EvidenceSource.YOGAS


def test_normalizer_sorts_by_source_weight_and_title():
    yoga = ConsultationEvidence(
        evidence_id="yoga-1",
        source=EvidenceSource.YOGAS,
        category=EvidenceCategory.GENERAL,
        title="Beta",
        summary="Beta",
        weight=0.6,
        confidence=0.4,
    )
    dasha = ConsultationEvidence(
        evidence_id="dasha-1",
        source=EvidenceSource.DASHA,
        category=EvidenceCategory.TIMING,
        title="Alpha",
        summary="Alpha",
        weight=0.7,
        confidence=0.5,
    )
    normalized = EvidenceNormalizer().normalize((yoga, dasha))
    assert [item.source for item in normalized] == [EvidenceSource.YOGAS, EvidenceSource.DASHA]


def test_normalizer_builds_bundle_groups_by_source(sample_evidence):
    dasha = ConsultationEvidence(
        evidence_id="dasha-1",
        source=EvidenceSource.DASHA,
        category=EvidenceCategory.TIMING,
        title="Dasha",
        summary="Dasha",
        weight=0.7,
        confidence=0.5,
    )
    bundle = EvidenceNormalizer().build_bundle(
        (sample_evidence, dasha),
        metadata={"engine": "test"},
    )
    assert len(bundle.yogas) == 1
    assert len(bundle.dasha) == 1
    assert bundle.evidence_count == 2
    assert bundle.metadata["engine"] == "test"


def test_normalizer_normalizes_timestamp_and_priority_metadata():
    evidence = ConsultationEvidence(
        evidence_id="meta-1",
        source=EvidenceSource.FUSION,
        category=EvidenceCategory.GENERAL,
        title="Meta",
        summary="Meta",
        weight=0.5,
        confidence=0.5,
        metadata={
            "priority": 150,
            "collected_at": datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
            "timestamp": " 2026-01-01T12:00:00+00:00 ",
        },
    )
    normalized = EvidenceNormalizer().normalize_item(evidence)
    assert normalized.metadata["priority"] == 100
    assert normalized.metadata["collected_at"] == "2026-01-01T12:00:00+00:00"
    assert normalized.metadata["timestamp"] == "2026-01-01T12:00:00+00:00"
