"""Architectural source weights for deterministic conflict resolution."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence

DEFAULT_CONFLICT_WEIGHT = 0.5

# Architectural defaults only — not astrological judgement.
CONFLICT_RESOLUTION_WEIGHTS: Mapping[EvidenceSource, float] = MappingProxyType(
    {
        EvidenceSource.RULE_STUDIO: 0.95,
        EvidenceSource.GOLDEN_DATASET: 0.92,
        EvidenceSource.FUSION: 0.90,
        EvidenceSource.KP: 0.88,
        EvidenceSource.DASHA: 0.86,
        EvidenceSource.TRANSIT: 0.82,
        EvidenceSource.YOGAS: 0.80,
        EvidenceSource.CASE_LEARNING: 0.78,
        EvidenceSource.LAL_KITAB: 0.72,
    }
)


def get_conflict_weight(
    source: EvidenceSource,
    *,
    weights: Mapping[EvidenceSource, float] | None = None,
) -> float:
    """Return the configured conflict-resolution weight for a source."""
    table = weights or CONFLICT_RESOLUTION_WEIGHTS
    return float(table.get(source, DEFAULT_CONFLICT_WEIGHT))


def weighted_evidence_score(
    evidence: ConsultationEvidence,
    *,
    weights: Mapping[EvidenceSource, float] | None = None,
) -> float:
    """Compute deterministic score used to pick a conflict winner."""
    return round(get_conflict_weight(evidence.source, weights=weights) * evidence.confidence, 6)
