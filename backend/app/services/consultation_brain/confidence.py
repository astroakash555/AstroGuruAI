"""Unified confidence calculation (foundation placeholders)."""

from __future__ import annotations

from typing import Iterable

from backend.app.services.consultation_brain.constants import DEFAULT_OVERALL_CONFIDENCE
from backend.app.services.consultation_brain.models import ConsultationConflict, ConsultationEvidence, ConsultationPriority
from backend.app.services.consultation_brain.reasoning import score_evidence


def compute_overall_confidence(
    *,
    evidence: Iterable[ConsultationEvidence],
    conflicts: Iterable[ConsultationConflict],
    priorities: Iterable[ConsultationPriority],
) -> float:
    """Combine evidence, conflict, and priority signals into one score."""
    evidence_score = score_evidence(evidence)
    if not tuple(evidence):
        return DEFAULT_OVERALL_CONFIDENCE

    conflict_items = tuple(conflicts)
    conflict_penalty = 0.0
    if conflict_items:
        conflict_penalty = sum(item.resolved_confidence for item in conflict_items) / len(conflict_items)
        conflict_penalty = max(0.0, 1.0 - conflict_penalty)

    priority_items = tuple(priorities)
    priority_score = 0.0
    if priority_items:
        priority_score = sum(item.confidence for item in priority_items) / len(priority_items)

    blended = (evidence_score * 0.5) + (priority_score * 0.35) + ((1.0 - conflict_penalty) * 0.15)
    return round(min(1.0, max(0.0, blended)), 4)
