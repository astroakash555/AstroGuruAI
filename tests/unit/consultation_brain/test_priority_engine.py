"""Tests for PriorityEngine."""

from backend.app.services.consultation_brain.conflict_engine import ConflictEngineResult
from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence
from backend.app.services.consultation_brain.priority_engine import PriorityEngine, to_legacy_priorities
from backend.app.services.consultation_brain.priority_models import PriorityDomain


def _evidence(**kwargs) -> ConsultationEvidence:
    defaults = {
        "evidence_id": "evidence-1",
        "source": EvidenceSource.RULE_STUDIO,
        "category": EvidenceCategory.RELATIONSHIP,
        "title": "Marriage delay",
        "summary": "Summary",
        "weight": 0.5,
        "confidence": 0.8,
        "metadata": {"domain": "marriage"},
    }
    defaults.update(kwargs)
    return ConsultationEvidence(**defaults)


def test_priority_engine_ranks_relationship_domain_highest():
    evidence = (
        _evidence(evidence_id="marriage-1"),
        _evidence(
            evidence_id="career-1",
            source=EvidenceSource.FUSION,
            category=EvidenceCategory.CAREER,
            confidence=0.4,
            metadata={"domain": "career"},
        ),
    )
    result = PriorityEngine().rank(
        ConflictEngineResult(resolutions=(), resolved_evidence=evidence, legacy_conflicts=()),
        evidence,
    )
    assert result.highest_priority is not None
    assert result.highest_priority.domain == PriorityDomain.MARRIAGE
    assert result.priorities[0].rank == 1
    assert result.secondary_priorities


def test_priority_engine_suppresses_low_score_domains():
    low = _evidence(evidence_id="low-1", confidence=0.01, metadata={"domain": "legal"})
    result = PriorityEngine(suppression_threshold=0.5).rank(
        ConflictEngineResult(resolutions=(), resolved_evidence=(low,), legacy_conflicts=()),
        (low,),
    )
    assert PriorityDomain.LEGAL in result.suppressed_topics
    assert result.highest_priority is None


def test_priority_engine_suppresses_domains_without_evidence():
    result = PriorityEngine().rank(
        ConflictEngineResult(resolutions=(), resolved_evidence=(_evidence(),), legacy_conflicts=()),
        (_evidence(),),
    )
    assert PriorityDomain.LEGAL in result.suppressed_topics
    assert result.metadata["suppressed_domain_count"] > 0


def test_priority_engine_excludes_conflict_losers():
    winner = _evidence(evidence_id="winner-1", metadata={"domain": "marriage"})
    loser = _evidence(
        evidence_id="loser-1",
        source=EvidenceSource.KP,
        metadata={"domain": "marriage", "conflict_loser": True},
        confidence=0.9,
    )
    result = PriorityEngine().rank(
        ConflictEngineResult(resolutions=(), resolved_evidence=(winner, loser), legacy_conflicts=()),
        (winner, loser),
    )
    marriage = next(item for item in result.priorities if item.domain == PriorityDomain.MARRIAGE)
    assert "loser-1" not in marriage.evidence_ids


def test_priority_engine_is_deterministic():
    evidence = (_evidence(evidence_id="marriage-1"), _evidence(evidence_id="career-1", metadata={"domain": "career"}, category=EvidenceCategory.CAREER))
    conflict_result = ConflictEngineResult(resolutions=(), resolved_evidence=evidence, legacy_conflicts=())
    first = PriorityEngine().rank(conflict_result, evidence)
    second = PriorityEngine().rank(conflict_result, evidence)
    assert first == second


def test_to_legacy_priorities_maps_domain_output():
    evidence = (_evidence(),)
    result = PriorityEngine().rank(
        ConflictEngineResult(resolutions=(), resolved_evidence=evidence, legacy_conflicts=()),
        evidence,
    )
    legacy = to_legacy_priorities(result)
    assert legacy[0].domain == PriorityDomain.MARRIAGE.value
    assert legacy[0].evidence_ids
