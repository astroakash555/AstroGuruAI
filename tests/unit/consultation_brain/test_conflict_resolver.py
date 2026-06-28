"""Tests for conflict detection and resolution adapters."""

from backend.app.services.consultation_brain.conflict_engine import ConflictEngine
from backend.app.services.consultation_brain.conflict_resolver import apply_conflict_resolution, detect_conflicts
from backend.app.services.consultation_brain.constants import CONFLICT_CONFIDENCE_PENALTY, EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationConflict, ConsultationEvidence, ConsultationEvidenceBundle


def _evidence(
    evidence_id: str,
    *,
    source: EvidenceSource,
    category: EvidenceCategory,
    confidence: float,
    metadata: dict | None = None,
):
    return ConsultationEvidence(
        evidence_id=evidence_id,
        source=source,
        category=category,
        title=evidence_id,
        summary="summary",
        weight=0.6,
        confidence=confidence,
        metadata=metadata or {},
    )


def test_detect_conflicts_returns_empty_for_single_item():
    single = (
        _evidence("a", source=EvidenceSource.YOGAS, category=EvidenceCategory.GENERAL, confidence=0.6),
    )
    assert detect_conflicts(single) == ()


def test_detect_conflicts_finds_cross_source_conflict():
    items = (
        _evidence(
            "fusion-1",
            source=EvidenceSource.FUSION,
            category=EvidenceCategory.RELATIONSHIP,
            confidence=0.8,
            metadata={"is_supported": True},
        ),
        _evidence(
            "kp-1",
            source=EvidenceSource.KP,
            category=EvidenceCategory.RELATIONSHIP,
            confidence=0.35,
            metadata={"is_supported": False},
        ),
    )
    conflicts = detect_conflicts(items)
    assert len(conflicts) == 1
    assert set(conflicts[0].evidence_ids) == {"fusion-1", "kp-1"}


def test_apply_conflict_resolution_penalizes_involved_evidence():
    items = (
        _evidence("a", source=EvidenceSource.YOGAS, category=EvidenceCategory.GENERAL, confidence=0.6),
        _evidence("b", source=EvidenceSource.DASHA, category=EvidenceCategory.CAREER, confidence=0.4),
    )
    conflicts = (
        ConsultationConflict(
            conflict_id="conflict-general",
            evidence_ids=("a",),
            description="test",
            resolution="defer",
            resolved_confidence=0.5,
        ),
    )
    resolved = apply_conflict_resolution(items, conflicts)
    assert resolved[0].confidence == 0.6 - CONFLICT_CONFIDENCE_PENALTY
    assert resolved[1].confidence == 0.4


def test_conflict_engine_accepts_injected_weights():
    bundle = ConsultationEvidenceBundle(
        fusion=(
            _evidence(
                "fusion-1",
                source=EvidenceSource.FUSION,
                category=EvidenceCategory.GENERAL,
                confidence=0.5,
                metadata={"is_supported": True},
            ),
        ),
        kp=(
            _evidence(
                "kp-1",
                source=EvidenceSource.KP,
                category=EvidenceCategory.GENERAL,
                confidence=0.5,
                metadata={"is_supported": False},
            ),
        ),
    )
    result = ConflictEngine(weights={EvidenceSource.KP: 0.99, EvidenceSource.FUSION: 0.1}).resolve(bundle)
    assert result.resolutions[0].winning_sources == (EvidenceSource.KP,)
