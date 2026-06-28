"""Tests for recommendation ranking rules."""

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence
from backend.app.services.consultation_brain.priority_models import DomainPriority, PriorityDomain
from backend.app.services.consultation_brain.recommendation_models import RecommendationCategory, RecommendationTier
from backend.app.services.consultation_brain.recommendation_rules import (
    build_reason,
    categories_for_domain,
    categories_for_evidence,
    classify_tier,
    compute_recommendation_score,
)


def _domain_priority(**kwargs) -> DomainPriority:
    defaults = {
        "domain": PriorityDomain.MARRIAGE,
        "rank": 1,
        "priority_score": 0.8,
        "urgency": 0.7,
        "importance": 0.75,
        "evidence_count": 2,
        "confidence": 0.7,
        "supporting_sources": (EvidenceSource.RULE_STUDIO,),
        "evidence_ids": ("evidence-1", "evidence-2"),
    }
    defaults.update(kwargs)
    return DomainPriority(**defaults)


def _evidence(**kwargs) -> ConsultationEvidence:
    defaults = {
        "evidence_id": "evidence-1",
        "source": EvidenceSource.RULE_STUDIO,
        "category": EvidenceCategory.RELATIONSHIP,
        "title": "Title",
        "summary": "Summary",
        "weight": 0.5,
        "confidence": 0.7,
    }
    defaults.update(kwargs)
    return ConsultationEvidence(**defaults)


def test_categories_for_domain_maps_marriage_topics():
    categories = categories_for_domain(PriorityDomain.MARRIAGE)
    assert RecommendationCategory.MARRIAGE_ADVICE in categories


def test_categories_for_evidence_uses_source_and_category():
    evidence = _evidence(source=EvidenceSource.LAL_KITAB, category=EvidenceCategory.REMEDY)
    categories = categories_for_evidence(evidence)
    assert RecommendationCategory.DONATION in categories
    assert RecommendationCategory.MANTRA in categories


def test_compute_recommendation_score_includes_conflict_boost():
    domain = _domain_priority()
    evidence = (_evidence(),)
    without = compute_recommendation_score(domain_priority=domain, evidence_items=evidence, conflict_resolved=False)
    with_boost = compute_recommendation_score(domain_priority=domain, evidence_items=evidence, conflict_resolved=True)
    assert with_boost > without


def test_classify_tier_assigns_high_medium_low_and_deferred():
    assert classify_tier(score=0.7, domain_rank=1) == RecommendationTier.HIGH
    assert classify_tier(score=0.5, domain_rank=3) == RecommendationTier.MEDIUM
    assert classify_tier(score=0.25, domain_rank=5) == RecommendationTier.LOW
    assert classify_tier(score=0.1, domain_rank=5, deferred=True) == RecommendationTier.DEFERRED
    assert classify_tier(score=0.1, domain_rank=5) == RecommendationTier.DEFERRED


def test_categories_for_evidence_falls_back_to_general_guidance():
    evidence = _evidence(source=EvidenceSource.PROFESSIONAL_REPORT, category=EvidenceCategory.GENERAL)
    categories = categories_for_evidence(evidence)
    assert RecommendationCategory.IMMEDIATE_ACTIONS in categories
    assert RecommendationCategory.GENERAL_GUIDANCE in categories


def test_average_confidence_returns_zero_for_empty_items():
    from backend.app.services.consultation_brain.recommendation_rules import average_confidence

    assert average_confidence(()) == 0.0



def test_build_reason_is_structured_without_free_text():
    reason = build_reason(
        category=RecommendationCategory.MARRIAGE_ADVICE,
        domain=PriorityDomain.MARRIAGE,
        domain_rank=1,
        evidence_count=2,
        source_count=1,
        conflict_resolved=True,
        score=0.72,
    )
    assert reason.startswith("category=marriage_advice|")
    assert "conflict_resolved=true" in reason
