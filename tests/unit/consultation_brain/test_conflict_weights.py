"""Tests for conflict resolution weights."""

from types import MappingProxyType

import pytest

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence
from backend.app.services.consultation_brain.weights import (
    CONFLICT_RESOLUTION_WEIGHTS,
    DEFAULT_CONFLICT_WEIGHT,
    get_conflict_weight,
    weighted_evidence_score,
)


def test_conflict_weight_table_matches_architecture_defaults():
    assert CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.RULE_STUDIO] == 0.95
    assert CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.GOLDEN_DATASET] == 0.92
    assert CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.FUSION] == 0.90
    assert CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.KP] == 0.88
    assert CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.DASHA] == 0.86
    assert CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.TRANSIT] == 0.82
    assert CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.YOGAS] == 0.80
    assert CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.CASE_LEARNING] == 0.78
    assert CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.LAL_KITAB] == 0.72


def test_conflict_weights_are_read_only():
    with pytest.raises(TypeError):
        CONFLICT_RESOLUTION_WEIGHTS[EvidenceSource.KP] = 0.1  # type: ignore[index]


def test_get_conflict_weight_uses_default_for_unknown_source():
    custom = MappingProxyType({EvidenceSource.FUSION: 0.9})
    assert get_conflict_weight(EvidenceSource.KP, weights=custom) == DEFAULT_CONFLICT_WEIGHT


def test_weighted_evidence_score_multiplies_weight_and_confidence():
    evidence = ConsultationEvidence(
        evidence_id="rule-1",
        source=EvidenceSource.RULE_STUDIO,
        category=EvidenceCategory.REMEDY,
        title="Rule",
        summary="Rule",
        weight=0.5,
        confidence=0.5,
    )
    assert weighted_evidence_score(evidence) == round(0.95 * 0.5, 6)
