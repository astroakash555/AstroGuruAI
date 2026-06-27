"""Tests for domain consultation modules."""

from __future__ import annotations

from backend.app.services.consultation.career_consultant import build_business_section, build_career_section
from backend.app.services.consultation.education_consultant import build_education_section
from backend.app.services.consultation.finance_consultant import build_finance_section
from backend.app.services.consultation.health_consultant import build_health_section
from backend.app.services.consultation.relationship_consultant import (
    build_children_section,
    build_family_section,
    build_marriage_section,
    build_relationship_section,
)
from backend.app.services.consultation.spiritual_consultant import build_foreign_travel_section, build_spiritual_section
from backend.app.services.consultation.summary_generator import build_executive_summary_section
from backend.app.services.reasoning.fusion.models import FusionResult


class TestDomainConsultants:
    def test_relationship_section_matches_domain(self, rich_fusion_result: FusionResult) -> None:
        section = build_relationship_section(rich_fusion_result)
        assert section.section_id == "relationship"
        assert "Venus" in section.current_situation or "relationship" in section.current_situation.lower()

    def test_career_section_uses_dasha_timeline(self, rich_fusion_result: FusionResult) -> None:
        section = build_career_section(rich_fusion_result)
        assert section.section_id == "career"
        assert "Saturn" in section.current_situation or "career" in section.current_situation.lower()

    def test_all_domain_builders(self, rich_fusion_result: FusionResult) -> None:
        builders = (
            build_marriage_section,
            build_business_section,
            build_finance_section,
            build_health_section,
            build_education_section,
            build_spiritual_section,
            build_foreign_travel_section,
            build_family_section,
            build_children_section,
            build_executive_summary_section,
        )
        for builder in builders:
            section = builder(rich_fusion_result)
            assert section.title
            assert section.confidence > 0

    def test_empty_fusion_fallback_copy(self, empty_fusion_result: FusionResult) -> None:
        section = build_finance_section(empty_fusion_result)
        assert "steady" in section.current_situation.lower()
        assert section.positive_factors
        assert section.challenges
