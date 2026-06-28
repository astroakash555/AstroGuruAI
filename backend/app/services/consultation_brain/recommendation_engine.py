"""Recommendation intelligence engine for consultation brain."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from backend.app.services.consultation_brain.conflict_engine import ConflictEngineResult
from backend.app.services.consultation_brain.constants import MAX_RECOMMENDATIONS
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationEvidenceBundle, ConsultationRecommendation
from backend.app.services.consultation_brain.priority_models import ConsultationPriorityResult, DomainPriority, PriorityDomain
from backend.app.services.consultation_brain.recommendation_models import (
    ConsultationRecommendationResult,
    RecommendationCategory,
    RecommendationTier,
    StructuredRecommendation,
)
from backend.app.services.consultation_brain.recommendation_rules import (
    build_reason,
    categories_for_domain,
    classify_tier,
    compute_recommendation_score,
    recommendation_key,
)


class RecommendationEngine:
    """Generates structured recommendations from priority and conflict outputs."""

    def generate(
        self,
        priority_result: ConsultationPriorityResult,
        conflict_result: ConflictEngineResult,
        evidence_bundle: ConsultationEvidenceBundle,
    ) -> ConsultationRecommendationResult:
        evidence_by_id = _index_evidence(evidence_bundle.all_evidence)
        winning_ids = _winning_evidence_ids(conflict_result)
        candidates: list[StructuredRecommendation] = []
        seen_keys: set[str] = set()

        for domain_priority in priority_result.priorities:
            domain_evidence = _evidence_for_ids(domain_priority.evidence_ids, evidence_by_id)
            for category in categories_for_domain(domain_priority.domain):
                candidate = _build_candidate(
                    category=category,
                    domain_priority=domain_priority,
                    evidence_items=domain_evidence,
                    conflict_resolved=_has_conflict_resolution(domain_evidence, winning_ids),
                    deferred=False,
                    seen_keys=seen_keys,
                )
                if candidate is not None:
                    candidates.append(candidate)

        for resolution in conflict_result.resolutions:
            category = RecommendationCategory.IMMEDIATE_ACTIONS
            evidence_items = (resolution.resolved_signal,)
            candidate = _build_candidate(
                category=category,
                domain_priority=_fallback_domain_priority(resolution.resolved_signal),
                evidence_items=evidence_items,
                conflict_resolved=True,
                deferred=False,
                seen_keys=seen_keys,
                recommendation_suffix=resolution.resolution_id,
            )
            if candidate is not None:
                candidates.append(candidate)

        if priority_result.priorities:
            for suppressed_domain in priority_result.suppressed_topics:
                deferred = _build_deferred_recommendation(suppressed_domain)
                key = recommendation_key(deferred.category, deferred.domain)
                if key not in seen_keys:
                    seen_keys.add(key)
                    candidates.append(deferred)

        grouped = _group_by_tier(candidates)
        return ConsultationRecommendationResult(
            high_priority=grouped[RecommendationTier.HIGH],
            medium_priority=grouped[RecommendationTier.MEDIUM],
            low_priority=grouped[RecommendationTier.LOW],
            deferred=grouped[RecommendationTier.DEFERRED],
            metadata={
                "candidate_count": len(candidates),
                "high_count": len(grouped[RecommendationTier.HIGH]),
                "medium_count": len(grouped[RecommendationTier.MEDIUM]),
                "low_count": len(grouped[RecommendationTier.LOW]),
                "deferred_count": len(grouped[RecommendationTier.DEFERRED]),
                "conflict_resolution_count": len(conflict_result.resolutions),
            },
        )


def to_legacy_recommendations(result: ConsultationRecommendationResult) -> tuple[ConsultationRecommendation, ...]:
    """Convert structured recommendations to legacy consultation output."""
    legacy: list[ConsultationRecommendation] = []
    ordered = (
        result.high_priority + result.medium_priority + result.low_priority + result.deferred
    )
    for index, item in enumerate(ordered[:MAX_RECOMMENDATIONS], start=1):
        legacy.append(
            ConsultationRecommendation(
                recommendation_id=item.recommendation_id,
                title=item.category.value,
                narrative=item.reason,
                priority_rank=item.priority,
                confidence=item.confidence,
                evidence_ids=item.supporting_evidence_ids,
                action_items=(item.category.value, item.tier.value),
            )
        )
    return tuple(legacy)


def _index_evidence(evidence: Sequence[ConsultationEvidence]) -> dict[str, ConsultationEvidence]:
    return {item.evidence_id: item for item in evidence}


def _evidence_for_ids(
    evidence_ids: Sequence[str],
    evidence_by_id: Mapping[str, ConsultationEvidence],
) -> tuple[ConsultationEvidence, ...]:
    return tuple(evidence_by_id[item_id] for item_id in evidence_ids if item_id in evidence_by_id)


def _winning_evidence_ids(conflict_result: ConflictEngineResult) -> set[str]:
    return {resolution.resolved_signal.evidence_id for resolution in conflict_result.resolutions}


def _has_conflict_resolution(evidence_items: Sequence[ConsultationEvidence], winning_ids: set[str]) -> bool:
    return any(item.evidence_id in winning_ids or item.metadata.get("conflict_winner") for item in evidence_items)


def _fallback_domain_priority(evidence: ConsultationEvidence) -> DomainPriority:
    return DomainPriority(
        domain=PriorityDomain.FAMILY,
        rank=99,
        priority_score=evidence.confidence,
        urgency=0.0,
        importance=evidence.weight,
        evidence_count=1,
        confidence=evidence.confidence,
        supporting_sources=(evidence.source,),
        evidence_ids=(evidence.evidence_id,),
    )


def _build_candidate(
    *,
    category: RecommendationCategory,
    domain_priority: DomainPriority,
    evidence_items: Sequence[ConsultationEvidence],
    conflict_resolved: bool,
    deferred: bool,
    seen_keys: set[str],
    recommendation_suffix: str | None = None,
) -> StructuredRecommendation | None:
    key = recommendation_key(category, domain_priority.domain)
    if key in seen_keys:
        return None
    seen_keys.add(key)

    score = compute_recommendation_score(
        domain_priority=domain_priority,
        evidence_items=evidence_items,
        conflict_resolved=conflict_resolved,
    )
    tier = classify_tier(score=score, domain_rank=domain_priority.rank, deferred=deferred)
    sources = tuple(sorted({item.source for item in evidence_items}, key=lambda source: source.value))
    if not sources and domain_priority.supporting_sources:
        sources = domain_priority.supporting_sources
    evidence_ids = tuple(sorted(item.evidence_id for item in evidence_items)) or domain_priority.evidence_ids
    suffix = recommendation_suffix or f"{category.value}-{domain_priority.domain.value}"
    return StructuredRecommendation(
        recommendation_id=f"rec-{suffix}",
        category=category,
        priority=domain_priority.rank,
        confidence=round(score, 4),
        supporting_evidence_ids=evidence_ids,
        supporting_sources=sources,
        reason=build_reason(
            category=category,
            domain=domain_priority.domain,
            domain_rank=domain_priority.rank,
            evidence_count=len(evidence_ids),
            source_count=len(sources),
            conflict_resolved=conflict_resolved,
            score=score,
        ),
        domain=domain_priority.domain,
        tier=tier,
        metadata={"priority_score": domain_priority.priority_score},
    )


def _build_deferred_recommendation(domain: PriorityDomain) -> StructuredRecommendation:
    return StructuredRecommendation(
        recommendation_id=f"rec-deferred-{domain.value}",
        category=RecommendationCategory.GENERAL_GUIDANCE,
        priority=999,
        confidence=0.0,
        supporting_evidence_ids=(),
        supporting_sources=(),
        reason=(
            f"category=general_guidance|domain={domain.value}|domain_rank=0|"
            "evidence_count=0|source_count=0|conflict_resolved=false|score=0.0000|deferred=true"
        ),
        domain=domain,
        tier=RecommendationTier.DEFERRED,
    )


def _group_by_tier(
    candidates: Sequence[StructuredRecommendation],
) -> dict[RecommendationTier, tuple[StructuredRecommendation, ...]]:
    buckets: dict[RecommendationTier, list[StructuredRecommendation]] = {
        RecommendationTier.HIGH: [],
        RecommendationTier.MEDIUM: [],
        RecommendationTier.LOW: [],
        RecommendationTier.DEFERRED: [],
    }
    for candidate in sorted(
        candidates,
        key=lambda item: (
            item.tier.value,
            item.priority,
            -item.confidence,
            item.category.value,
        ),
    ):
        buckets[candidate.tier].append(
            StructuredRecommendation(
                recommendation_id=candidate.recommendation_id,
                category=candidate.category,
                priority=len(buckets[candidate.tier]) + 1,
                confidence=candidate.confidence,
                supporting_evidence_ids=candidate.supporting_evidence_ids,
                supporting_sources=candidate.supporting_sources,
                reason=candidate.reason,
                domain=candidate.domain,
                tier=candidate.tier,
                metadata=candidate.metadata,
            )
        )
    return {tier: tuple(items) for tier, items in buckets.items()}
