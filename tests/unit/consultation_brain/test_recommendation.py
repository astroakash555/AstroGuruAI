"""Tests for recommendation generation."""

from backend.app.services.consultation_brain.constants import MAX_RECOMMENDATIONS
from backend.app.services.consultation_brain.models import ConsultationPriority
from backend.app.services.consultation_brain.priority_models import PriorityDomain
from backend.app.services.consultation_brain.recommendation import generate_recommendations


def test_generate_recommendations_from_priorities():
    priorities = (
        ConsultationPriority(
            rank=1,
            domain="marriage",
            title="Marriage timing",
            rationale="Saturn influence",
            confidence=0.7,
            evidence_ids=("evidence-1",),
        ),
    )
    recommendations = generate_recommendations(priorities, problem_text="Marriage delay")
    assert len(recommendations) >= 1
    assert recommendations[0].narrative.startswith("category=")
    assert recommendations[0].action_items


def test_generate_recommendations_respects_max_limit():
    priorities = tuple(
        ConsultationPriority(
            rank=index,
            domain="marriage",
            title=f"P{index}",
            rationale="r",
            confidence=0.6,
            evidence_ids=(f"e{index}",),
        )
        for index in range(1, MAX_RECOMMENDATIONS + 3)
    )
    recommendations = generate_recommendations(priorities)
    assert len(recommendations) <= MAX_RECOMMENDATIONS


def test_domain_from_legacy_falls_back_for_unknown_domain():
    from backend.app.services.consultation_brain.recommendation import _domain_from_legacy

    assert _domain_from_legacy("unknown_domain") == PriorityDomain.FAMILY

