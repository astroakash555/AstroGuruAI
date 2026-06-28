"""Priority ranking adapters."""

from __future__ import annotations

from typing import Iterable

from backend.app.services.consultation_brain.conflict_engine import ConflictEngineResult
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationPriority
from backend.app.services.consultation_brain.priority_engine import PriorityEngine, to_legacy_priorities


def rank_priorities(evidence: Iterable[ConsultationEvidence]) -> tuple[ConsultationPriority, ...]:
    """Rank priorities via the priority intelligence engine."""
    items = tuple(evidence)
    conflict_result = ConflictEngineResult(resolutions=(), resolved_evidence=items, legacy_conflicts=())
    priority_result = PriorityEngine().rank(conflict_result, items)
    return to_legacy_priorities(priority_result)
