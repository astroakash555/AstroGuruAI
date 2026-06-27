"""Tests for the consultation brain orchestrator."""

from __future__ import annotations

import json

import pytest

from backend.app.services.consultation import ConsultationEngine, generate_consultation
from backend.app.services.consultation.consultation_models import consultation_result_to_dict
from backend.app.services.reasoning.fusion.models import FusionResult


class TestConsultationEngine:
    def test_generate_returns_twelve_sections(self, rich_fusion_result: FusionResult) -> None:
        result = ConsultationEngine().generate(rich_fusion_result)

        assert len(result.sections) == 12
        section_ids = {section.section_id for section in result.sections}
        assert section_ids == {
            "executive_summary",
            "relationship",
            "marriage",
            "career",
            "business",
            "finance",
            "health",
            "education",
            "spiritual_growth",
            "foreign_travel",
            "family",
            "children",
        }

    def test_each_section_has_required_fields(self, rich_fusion_result: FusionResult) -> None:
        result = ConsultationEngine().generate(rich_fusion_result)

        for section in result.sections:
            assert section.title
            assert section.current_situation
            assert section.root_cause
            assert len(section.positive_factors) >= 1
            assert len(section.challenges) >= 1
            assert section.timeline
            assert len(section.actionable_advice) >= 1
            assert 0.0 <= section.confidence <= 1.0

    def test_priorities_strengths_and_risks_are_top_five(self, rich_fusion_result: FusionResult) -> None:
        result = ConsultationEngine().generate(rich_fusion_result)

        assert len(result.priorities) <= 5
        assert len(result.strengths) <= 5
        assert len(result.risks) <= 5
        assert result.priorities[0].rank == 1
        assert result.strengths[0].rank == 1
        assert result.risks[0].rank == 1

    def test_overall_confidence_matches_fusion(self, rich_fusion_result: FusionResult) -> None:
        result = ConsultationEngine().generate(rich_fusion_result)

        assert result.overall_confidence == round(rich_fusion_result.confidence_score, 4)
        assert result.executive_summary
        assert result.metadata["engine"] == "consultation_brain_v1"
        assert result.metadata["section_count"] == 12

    def test_generate_json_is_serializable(self, rich_fusion_result: FusionResult) -> None:
        payload = ConsultationEngine().generate_json(rich_fusion_result)

        serialized = json.dumps(payload)
        parsed = json.loads(serialized)
        assert parsed["overall_confidence"] == 0.79
        assert len(parsed["sections"]) == 12
        assert parsed["metadata"]["conflict_count"] == 1

    def test_generate_consultation_wrapper(self, rich_fusion_result: FusionResult) -> None:
        result = generate_consultation(rich_fusion_result)
        assert consultation_result_to_dict(result)["executive_summary"]

    def test_empty_fusion_still_returns_complete_result(self, empty_fusion_result: FusionResult) -> None:
        result = ConsultationEngine().generate(empty_fusion_result)

        assert len(result.sections) == 12
        assert result.priorities == ()
        assert result.strengths == ()
        assert result.risks == ()
        assert "neutral" in result.executive_summary.lower()

    def test_frozen_datetime(self, rich_fusion_result: FusionResult, monkeypatch: pytest.MonkeyPatch) -> None:
        import backend.app.services.consultation.consultation_engine as engine_module
        from datetime import datetime, timezone

        fixed = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None):  # noqa: ANN001
                return fixed if tz is None else fixed.astimezone(tz)

        monkeypatch.setattr(engine_module, "datetime", FixedDateTime)
        result = ConsultationEngine().generate(rich_fusion_result)
        assert result.generated_at == fixed
