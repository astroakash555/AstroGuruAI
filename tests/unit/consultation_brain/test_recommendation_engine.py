"""Tests for RecommendationEngine."""

from backend.app.services.consultation_brain.conflict_engine import ConflictEngineResult
from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationEvidenceBundle
from backend.app.services.consultation_brain.models import ConsultationConflictResolution
from backend.app.services.consultation_brain.priority_models import ConsultationPriorityResult, DomainPriority, PriorityDomain
from backend.app.services.consultation_brain.recommendation_engine import RecommendationEngine, to_legacy_recommendations
from backend.app.services.consultation_brain.recommendation_models import RecommendationCategory, RecommendationTier


def _evidence(**kwargs) -> ConsultationEvidence:
    defaults = {
        "evidence_id": "marriage-1",
        "source": EvidenceSource.RULE_STUDIO,
        "category": EvidenceCategory.RELATIONSHIP,
        "title": "Marriage signal",
        "summary": "Summary",
        "weight": 0.5,
        "confidence": 0.8,
        "metadata": {"domain": "marriage"},
    }
    defaults.update(kwargs)
    return ConsultationEvidence(**defaults)


def _priority_result() -> ConsultationPriorityResult:
    marriage = DomainPriority(
        domain=PriorityDomain.MARRIAGE,
        rank=1,
        priority_score=0.82,
        urgency=0.75,
        importance=0.78,
        evidence_count=1,
        confidence=0.8,
        supporting_sources=(EvidenceSource.RULE_STUDIO,),
        evidence_ids=("marriage-1",),
    )
    return ConsultationPriorityResult(
        priorities=(marriage,),
        highest_priority=marriage,
        secondary_priorities=(),
        suppressed_topics=(PriorityDomain.LEGAL,),
    )


def test_recommendation_engine_generates_tiered_recommendations():
    evidence = _evidence()
    bundle = ConsultationEvidenceBundle(rule_studio=(evidence,))
    result = RecommendationEngine().generate(
        _priority_result(),
        ConflictEngineResult(resolutions=(), resolved_evidence=(evidence,), legacy_conflicts=()),
        bundle,
    )
    assert result.high_priority or result.medium_priority
    assert result.deferred
    assert any(item.category == RecommendationCategory.MARRIAGE_ADVICE for item in result.all_recommendations)


def test_recommendation_engine_adds_immediate_action_for_conflict_winner():
    winner = _evidence(evidence_id="winner-1", metadata={"domain": "marriage", "conflict_winner": True})
    resolution = ConsultationConflictResolution(
        resolution_id="conflict-1",
        conflict_type="positive_vs_negative",
        resolved_signal=winner,
        winning_sources=(EvidenceSource.RULE_STUDIO,),
        losing_sources=(EvidenceSource.KP,),
        resolution_reason="weighted",
        confidence=0.8,
        evidence_ids=("winner-1", "kp-1"),
    )
    bundle = ConsultationEvidenceBundle(rule_studio=(winner,))
    result = RecommendationEngine().generate(
        _priority_result(),
        ConflictEngineResult(
            resolutions=(resolution,),
            resolved_evidence=(winner,),
            legacy_conflicts=(),
        ),
        bundle,
    )
    assert any(item.category == RecommendationCategory.IMMEDIATE_ACTIONS for item in result.all_recommendations)


def test_recommendation_engine_is_deterministic():
    evidence = _evidence()
    bundle = ConsultationEvidenceBundle(rule_studio=(evidence,))
    conflict = ConflictEngineResult(resolutions=(), resolved_evidence=(evidence,), legacy_conflicts=())
    priority = _priority_result()
    first = RecommendationEngine().generate(priority, conflict, bundle)
    second = RecommendationEngine().generate(priority, conflict, bundle)
    assert first == second


def test_to_legacy_recommendations_maps_structured_output():
    evidence = _evidence()
    bundle = ConsultationEvidenceBundle(rule_studio=(evidence,))
    result = RecommendationEngine().generate(
        _priority_result(),
        ConflictEngineResult(resolutions=(), resolved_evidence=(evidence,), legacy_conflicts=()),
        bundle,
    )
    legacy = to_legacy_recommendations(result)
    assert legacy[0].recommendation_id
    assert legacy[0].narrative.startswith("category=")
    assert legacy[0].action_items


def test_recommendation_engine_returns_empty_when_no_priorities():
    result = RecommendationEngine().generate(
        ConsultationPriorityResult(
            priorities=(),
            highest_priority=None,
            secondary_priorities=(),
            suppressed_topics=tuple(PriorityDomain),
        ),
        ConflictEngineResult(resolutions=(), resolved_evidence=(), legacy_conflicts=()),
        ConsultationEvidenceBundle(),
    )
    assert result.all_recommendations == ()

