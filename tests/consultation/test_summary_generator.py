"""Tests for executive summary generation."""

from __future__ import annotations

from backend.app.services.consultation.summary_generator import build_executive_summary_section, generate_executive_summary
from backend.app.services.reasoning.fusion.models import FusionResult


class TestSummaryGenerator:
    def test_generate_executive_summary_mentions_conflicts(self, rich_fusion_result: FusionResult) -> None:
        summary = generate_executive_summary(rich_fusion_result)

        assert "79%" in summary
        assert "conflict" in summary.lower()

    def test_generate_executive_summary_empty_fusion(self, empty_fusion_result: FusionResult) -> None:
        summary = generate_executive_summary(empty_fusion_result)
        assert "neutral" in summary.lower()

    def test_build_executive_summary_section_structure(self, rich_fusion_result: FusionResult) -> None:
        section = build_executive_summary_section(rich_fusion_result)

        assert section.section_id == "executive_summary"
        assert section.positive_factors
        assert section.challenges
        assert section.actionable_advice

    def test_build_executive_summary_section_empty_challenges(self, empty_fusion_result: FusionResult) -> None:
        section = build_executive_summary_section(empty_fusion_result)
        assert "No major conflict" in section.challenges[0]
