"""Tests for priority ranking."""

from backend.app.services.consultation_brain.constants import MAX_PRIORITIES, EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence
from backend.app.services.consultation_brain.priority import rank_priorities


def _item(evidence_id: str, *, domain: str, weight: float, confidence: float):
    return ConsultationEvidence(
        evidence_id=evidence_id,
        source=EvidenceSource.FUSION,
        category=EvidenceCategory.RELATIONSHIP,
        title=evidence_id,
        summary="summary",
        weight=weight,
        confidence=confidence,
        metadata={"domain": domain},
    )


def test_rank_priorities_orders_domains_by_score():
    ranked = rank_priorities(
        [
            _item("low", domain="legal", weight=0.2, confidence=0.2),
            _item("high", domain="marriage", weight=0.9, confidence=0.9),
        ]
    )
    assert ranked[0].domain == "marriage"
    assert ranked[0].rank == 1


def test_rank_priorities_respects_max_limit():
    items = [
        _item(f"item-{index}", domain=f"domain-{index}", weight=0.5, confidence=0.1 * index)
        for index in range(MAX_PRIORITIES + 3)
    ]
    ranked = rank_priorities(items)
    assert len(ranked) <= MAX_PRIORITIES
