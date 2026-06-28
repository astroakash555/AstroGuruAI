"""Conflict detection and resolution adapters."""

from __future__ import annotations

from typing import Iterable

from backend.app.services.consultation_brain.conflict_engine import ConflictEngine, bundle_from_evidence
from backend.app.services.consultation_brain.constants import CONFLICT_CONFIDENCE_PENALTY
from backend.app.services.consultation_brain.models import ConsultationConflict, ConsultationEvidence


def detect_conflicts(evidence: Iterable[ConsultationEvidence]) -> tuple[ConsultationConflict, ...]:
    """Detect conflicts from flat evidence via the conflict engine."""
    bundle = bundle_from_evidence(tuple(evidence))
    return ConflictEngine().resolve(bundle).legacy_conflicts


def apply_conflict_resolution(
    evidence: Iterable[ConsultationEvidence],
    conflicts: Iterable[ConsultationConflict],
) -> tuple[ConsultationEvidence, ...]:
    """Apply confidence penalties to evidence listed in conflict records."""
    conflict_items = tuple(conflicts)
    if not conflict_items:
        return tuple(evidence)

    adjusted: list[ConsultationEvidence] = []
    for item in evidence:
        matching = next(
            (conflict for conflict in conflict_items if item.evidence_id in conflict.evidence_ids),
            None,
        )
        if matching is None:
            adjusted.append(item)
            continue
        adjusted.append(
            ConsultationEvidence(
                evidence_id=item.evidence_id,
                source=item.source,
                category=item.category,
                title=item.title,
                summary=item.summary,
                weight=item.weight,
                confidence=max(0.0, item.confidence - CONFLICT_CONFIDENCE_PENALTY),
                raw_reference=item.raw_reference,
                tags=item.tags,
                metadata={**item.metadata, "conflict_id": matching.conflict_id},
            )
        )
    return tuple(adjusted)
