"""Rules for structured recommendation generation."""

from __future__ import annotations

from collections.abc import Sequence

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence
from backend.app.services.consultation_brain.priority_models import DomainPriority, PriorityDomain
from backend.app.services.consultation_brain.recommendation_models import RecommendationCategory, RecommendationTier

HIGH_SCORE_THRESHOLD = 0.65
MEDIUM_SCORE_THRESHOLD = 0.40
LOW_SCORE_THRESHOLD = 0.20
HIGH_PRIORITY_RANK_LIMIT = 2

DOMAIN_CATEGORY_MAP: dict[PriorityDomain, tuple[RecommendationCategory, ...]] = {
    PriorityDomain.CAREER: (RecommendationCategory.CAREER_ADVICE, RecommendationCategory.TIMING_ADVICE),
    PriorityDomain.FINANCE: (RecommendationCategory.FINANCIAL_ADVICE, RecommendationCategory.GENERAL_GUIDANCE),
    PriorityDomain.MARRIAGE: (RecommendationCategory.MARRIAGE_ADVICE, RecommendationCategory.BEHAVIOURAL),
    PriorityDomain.RELATIONSHIP: (RecommendationCategory.MARRIAGE_ADVICE, RecommendationCategory.LIFESTYLE),
    PriorityDomain.HEALTH: (RecommendationCategory.HEALTH_ADVICE, RecommendationCategory.LIFESTYLE),
    PriorityDomain.EDUCATION: (RecommendationCategory.EDUCATION_ADVICE, RecommendationCategory.GENERAL_GUIDANCE),
    PriorityDomain.CHILDREN: (RecommendationCategory.GENERAL_GUIDANCE, RecommendationCategory.LIFESTYLE),
    PriorityDomain.PROPERTY: (RecommendationCategory.FINANCIAL_ADVICE, RecommendationCategory.GENERAL_GUIDANCE),
    PriorityDomain.BUSINESS: (RecommendationCategory.CAREER_ADVICE, RecommendationCategory.FINANCIAL_ADVICE),
    PriorityDomain.SPIRITUALITY: (RecommendationCategory.SPIRITUAL, RecommendationCategory.MANTRA),
    PriorityDomain.FOREIGN_TRAVEL: (RecommendationCategory.TIMING_ADVICE, RecommendationCategory.GENERAL_GUIDANCE),
    PriorityDomain.LEGAL: (RecommendationCategory.GENERAL_GUIDANCE, RecommendationCategory.IMMEDIATE_ACTIONS),
    PriorityDomain.MENTAL_WELLBEING: (RecommendationCategory.HEALTH_ADVICE, RecommendationCategory.LIFESTYLE),
    PriorityDomain.FAMILY: (RecommendationCategory.GENERAL_GUIDANCE, RecommendationCategory.LIFESTYLE),
}

SOURCE_CATEGORY_MAP: dict[EvidenceSource, tuple[RecommendationCategory, ...]] = {
    EvidenceSource.LAL_KITAB: (RecommendationCategory.DONATION, RecommendationCategory.GEMSTONE, RecommendationCategory.MANTRA),
    EvidenceSource.RULE_STUDIO: (RecommendationCategory.IMMEDIATE_ACTIONS, RecommendationCategory.BEHAVIOURAL),
    EvidenceSource.DASHA: (RecommendationCategory.TIMING_ADVICE,),
    EvidenceSource.TRANSIT: (RecommendationCategory.TIMING_ADVICE,),
    EvidenceSource.CASE_LEARNING: (RecommendationCategory.BEHAVIOURAL,),
    EvidenceSource.FUSION: (RecommendationCategory.GENERAL_GUIDANCE,),
    EvidenceSource.KP: (RecommendationCategory.TIMING_ADVICE, RecommendationCategory.IMMEDIATE_ACTIONS),
    EvidenceSource.YOGAS: (RecommendationCategory.SPIRITUAL, RecommendationCategory.GENERAL_GUIDANCE),
    EvidenceSource.GOLDEN_DATASET: (RecommendationCategory.GENERAL_GUIDANCE,),
    EvidenceSource.PROFESSIONAL_REPORT: (RecommendationCategory.IMMEDIATE_ACTIONS,),
}

EVIDENCE_CATEGORY_MAP: dict[EvidenceCategory, tuple[RecommendationCategory, ...]] = {
    EvidenceCategory.TIMING: (RecommendationCategory.TIMING_ADVICE,),
    EvidenceCategory.REMEDY: (RecommendationCategory.DONATION, RecommendationCategory.MANTRA, RecommendationCategory.GEMSTONE),
    EvidenceCategory.HEALTH: (RecommendationCategory.HEALTH_ADVICE,),
    EvidenceCategory.CAREER: (RecommendationCategory.CAREER_ADVICE,),
    EvidenceCategory.RELATIONSHIP: (RecommendationCategory.MARRIAGE_ADVICE,),
    EvidenceCategory.FINANCE: (RecommendationCategory.FINANCIAL_ADVICE,),
    EvidenceCategory.SPIRITUAL: (RecommendationCategory.SPIRITUAL, RecommendationCategory.MANTRA),
    EvidenceCategory.GENERAL: (RecommendationCategory.GENERAL_GUIDANCE,),
}


def categories_for_domain(domain: PriorityDomain) -> tuple[RecommendationCategory, ...]:
    return DOMAIN_CATEGORY_MAP.get(domain, (RecommendationCategory.GENERAL_GUIDANCE,))


def categories_for_evidence(evidence: ConsultationEvidence) -> tuple[RecommendationCategory, ...]:
    categories: set[RecommendationCategory] = set()
    categories.update(SOURCE_CATEGORY_MAP.get(evidence.source, ()))
    categories.update(EVIDENCE_CATEGORY_MAP.get(evidence.category, ()))
    if not categories:
        categories.add(RecommendationCategory.GENERAL_GUIDANCE)
    return tuple(sorted(categories, key=lambda item: item.value))


def average_confidence(items: Sequence[ConsultationEvidence]) -> float:
    if not items:
        return 0.0
    return round(sum(item.confidence for item in items) / len(items), 4)


def compute_recommendation_score(
    *,
    domain_priority: DomainPriority,
    evidence_items: Sequence[ConsultationEvidence],
    conflict_resolved: bool,
) -> float:
    """Combine priority, conflict, confidence, and source diversity signals."""
    source_factor = min(len({item.source for item in evidence_items}) / 4.0, 1.0)
    confidence = average_confidence(evidence_items) if evidence_items else domain_priority.confidence
    conflict_factor = 0.1 if conflict_resolved else 0.0
    score = (
        domain_priority.priority_score * 0.40
        + confidence * 0.25
        + source_factor * 0.15
        + domain_priority.urgency * 0.10
        + conflict_factor
    )
    return round(min(1.0, max(0.0, score)), 4)


def classify_tier(*, score: float, domain_rank: int, deferred: bool = False) -> RecommendationTier:
    if deferred:
        return RecommendationTier.DEFERRED
    if score >= HIGH_SCORE_THRESHOLD and domain_rank <= HIGH_PRIORITY_RANK_LIMIT:
        return RecommendationTier.HIGH
    if score >= MEDIUM_SCORE_THRESHOLD:
        return RecommendationTier.MEDIUM
    if score >= LOW_SCORE_THRESHOLD:
        return RecommendationTier.LOW
    return RecommendationTier.DEFERRED


def build_reason(
    *,
    category: RecommendationCategory,
    domain: PriorityDomain | None,
    domain_rank: int,
    evidence_count: int,
    source_count: int,
    conflict_resolved: bool,
    score: float,
) -> str:
    """Return a structured machine-readable reason string."""
    domain_value = domain.value if domain is not None else "none"
    return (
        f"category={category.value}|domain={domain_value}|domain_rank={domain_rank}|"
        f"evidence_count={evidence_count}|source_count={source_count}|"
        f"conflict_resolved={str(conflict_resolved).lower()}|score={score:.4f}"
    )


def recommendation_key(category: RecommendationCategory, domain: PriorityDomain | None) -> str:
    domain_value = domain.value if domain is not None else "global"
    return f"{category.value}:{domain_value}"
