"""Weighted reasoning and evidence normalization (foundation placeholders)."""

from __future__ import annotations

from typing import Iterable

from backend.app.services.consultation_brain.constants import (
    MAX_EVIDENCE_CONFIDENCE,
    MIN_EVIDENCE_CONFIDENCE,
    SOURCE_WEIGHTS,
)
from backend.app.services.consultation_brain.models import ConsultationEvidence


def normalize_evidence(evidence: Iterable[ConsultationEvidence]) -> tuple[ConsultationEvidence, ...]:
    """Stage 2 placeholder: clamp confidence and apply source weights."""
    normalized: list[ConsultationEvidence] = []
    for item in evidence:
        source_weight = SOURCE_WEIGHTS.get(item.source, 0.5)
        adjusted_confidence = _clamp(item.confidence * source_weight, MIN_EVIDENCE_CONFIDENCE, MAX_EVIDENCE_CONFIDENCE)
        normalized.append(
            ConsultationEvidence(
                evidence_id=item.evidence_id,
                source=item.source,
                category=item.category,
                title=item.title.strip(),
                summary=item.summary.strip(),
                weight=source_weight,
                confidence=adjusted_confidence,
                raw_reference=item.raw_reference,
                tags=item.tags,
                metadata=dict(item.metadata),
            )
        )
    return tuple(normalized)


def score_evidence(evidence: Iterable[ConsultationEvidence]) -> float:
    """Return aggregate evidence score for confidence calculation."""
    items = tuple(evidence)
    if not items:
        return 0.0
    total_weight = sum(item.weight for item in items)
    if total_weight <= 0:
        return 0.0
    weighted = sum(item.confidence * item.weight for item in items)
    return _clamp(weighted / total_weight, 0.0, 1.0)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))
