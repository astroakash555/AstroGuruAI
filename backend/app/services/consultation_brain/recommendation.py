"""Recommendation generation adapters."""

from __future__ import annotations

from typing import Iterable

from backend.app.services.consultation_brain.conflict_engine import ConflictEngineResult
from backend.app.services.consultation_brain.models import (
    ConsultationEvidenceBundle,
    ConsultationPriority,
    ConsultationRecommendation,
)
from backend.app.services.consultation_brain.priority_models import ConsultationPriorityResult, DomainPriority, PriorityDomain
from backend.app.services.consultation_brain.recommendation_engine import RecommendationEngine, to_legacy_recommendations


def generate_recommendations(
    priorities: Iterable[ConsultationPriority],
    *,
    problem_text: str | None = None,
) -> tuple[ConsultationRecommendation, ...]:
    """Generate recommendations via the recommendation intelligence engine."""
    del problem_text  # structured engine does not use free-text concerns
    priority_items = tuple(priorities)
    priority_result = _priority_result_from_legacy(priority_items)
    conflict_result = ConflictEngineResult(resolutions=(), resolved_evidence=(), legacy_conflicts=())
    bundle = ConsultationEvidenceBundle()
    result = RecommendationEngine().generate(priority_result, conflict_result, bundle)
    return to_legacy_recommendations(result)


def _priority_result_from_legacy(priorities: tuple[ConsultationPriority, ...]) -> ConsultationPriorityResult:
    domain_priorities: list[DomainPriority] = []
    for item in priorities:
        domain = _domain_from_legacy(item.domain)
        domain_priorities.append(
            DomainPriority(
                domain=domain,
                rank=item.rank,
                priority_score=item.confidence,
                urgency=item.confidence,
                importance=item.confidence,
                evidence_count=len(item.evidence_ids),
                confidence=item.confidence,
                supporting_sources=(),
                evidence_ids=item.evidence_ids,
            )
        )
    ranked = tuple(domain_priorities)
    highest = ranked[0] if ranked else None
    secondary = ranked[1:4]
    return ConsultationPriorityResult(
        priorities=ranked,
        highest_priority=highest,
        secondary_priorities=secondary,
        suppressed_topics=(),
    )


def _domain_from_legacy(value: str) -> PriorityDomain:
    try:
        return PriorityDomain(value)
    except ValueError:
        return PriorityDomain.FAMILY
