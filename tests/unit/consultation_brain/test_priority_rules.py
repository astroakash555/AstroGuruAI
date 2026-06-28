"""Tests for priority ranking rules."""

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence
from backend.app.services.consultation_brain.priority_models import PriorityDomain
from backend.app.services.consultation_brain.priority_rules import (
    compute_importance,
    compute_priority_score,
    compute_urgency,
    filter_active_evidence,
    is_suppressed,
    map_evidence_to_domains,
    normalize_domain_label,
)
from backend.app.services.consultation_brain.weights import CONFLICT_RESOLUTION_WEIGHTS


def _evidence(**kwargs) -> ConsultationEvidence:
    defaults = {
        "evidence_id": "evidence-1",
        "source": EvidenceSource.FUSION,
        "category": EvidenceCategory.GENERAL,
        "title": "Title",
        "summary": "Summary",
        "weight": 0.5,
        "confidence": 0.6,
    }
    defaults.update(kwargs)
    return ConsultationEvidence(**defaults)


def test_normalize_domain_label_handles_aliases():
    assert normalize_domain_label("relationship") == PriorityDomain.RELATIONSHIP
    assert normalize_domain_label("Foreign Travel") == PriorityDomain.FOREIGN_TRAVEL


def test_map_evidence_to_domains_uses_metadata_and_category():
    evidence = _evidence(
        category=EvidenceCategory.RELATIONSHIP,
        metadata={"domain": "marriage"},
        tags=("relationship",),
    )
    domains = map_evidence_to_domains(evidence)
    assert PriorityDomain.MARRIAGE in domains
    assert PriorityDomain.RELATIONSHIP in domains


def test_filter_active_evidence_excludes_conflict_losers():
    active = _evidence(evidence_id="active-1")
    loser = _evidence(evidence_id="loser-1", metadata={"conflict_loser": True})
    filtered = filter_active_evidence((active, loser))
    assert filtered == (active,)


def test_compute_urgency_favors_timing_sources():
    timing = _evidence(source=EvidenceSource.DASHA, category=EvidenceCategory.TIMING, confidence=0.7)
    general = _evidence(source=EvidenceSource.FUSION, category=EvidenceCategory.GENERAL, confidence=0.7)
    assert compute_urgency((timing,)) > compute_urgency((general,))


def test_compute_importance_uses_architectural_weights():
    rule = _evidence(source=EvidenceSource.RULE_STUDIO, confidence=0.5)
    lk = _evidence(source=EvidenceSource.LAL_KITAB, confidence=0.5)
    assert compute_importance((rule,), weights=CONFLICT_RESOLUTION_WEIGHTS) > compute_importance(
        (lk,), weights=CONFLICT_RESOLUTION_WEIGHTS
    )


def test_compute_priority_score_is_bounded():
    score = compute_priority_score(
        urgency=0.8,
        importance=0.7,
        evidence_count=3,
        confidence=0.6,
        supporting_source_count=2,
    )
    assert 0.0 <= score <= 1.0


def test_empty_metric_helpers_return_zero():
    assert compute_urgency(()) == 0.0
    assert compute_importance((), weights=CONFLICT_RESOLUTION_WEIGHTS) == 0.0
    from backend.app.services.consultation_brain.priority_rules import compute_domain_confidence

    assert compute_domain_confidence(()) == 0.0


def test_is_suppressed_requires_evidence_and_score():
    assert is_suppressed(priority_score=0.05, evidence_count=1) is True
    assert is_suppressed(priority_score=0.4, evidence_count=2) is False
