"""Tests for consultation dataclass models."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.services.consultation.consultation_models import (
    ConsultationPriorityItem,
    ConsultationResult,
    ConsultationRiskItem,
    ConsultationSection,
    ConsultationStrengthItem,
    consultation_result_to_dict,
    consultation_section_to_dict,
)


def test_consultation_section_to_dict():
    section = ConsultationSection(
        section_id="career",
        title="Career",
        current_situation="Stable growth.",
        root_cause="Saturn pressure.",
        positive_factors=("Strong Mercury support",),
        challenges=("Delay risk",),
        timeline="Next 6 months.",
        actionable_advice=("Avoid impulsive moves",),
        confidence=0.8,
        supporting_observation_ids=("obs-1",),
    )
    payload = consultation_section_to_dict(section)
    assert payload["section_id"] == "career"
    assert payload["positive_factors"] == ("Strong Mercury support",)


def test_consultation_result_to_dict():
    section = ConsultationSection(
        section_id="finance",
        title="Finance",
        current_situation="Stable.",
        root_cause="Jupiter support.",
        positive_factors=("Income growth",),
        challenges=("Expense control",),
        timeline="Quarterly.",
        actionable_advice=("Budget review",),
        confidence=0.7,
    )
    result = ConsultationResult(
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        executive_summary="Overview.",
        sections=(section,),
        priorities=(
            ConsultationPriorityItem(
                rank=1,
                title="Priority",
                explanation="Do this.",
                domain="finance",
                confidence=0.8,
            ),
        ),
        strengths=(
            ConsultationStrengthItem(
                rank=1,
                title="Strength",
                explanation="Good support.",
                confidence=0.9,
                supporting_engines=("vedic",),
            ),
        ),
        risks=(
            ConsultationRiskItem(
                rank=1,
                title="Risk",
                explanation="Watch this.",
                severity=0.7,
                confidence=0.6,
                has_conflict=True,
            ),
        ),
        overall_confidence=0.75,
        metadata={"engine": "consultation_brain_v1"},
    )
    payload = consultation_result_to_dict(result)
    assert payload["overall_confidence"] == 0.75
    assert payload["sections"][0]["title"] == "Finance"
    assert payload["priorities"][0]["domain"] == "finance"
