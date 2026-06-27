"""Tests for shared consultation domain helpers."""

from __future__ import annotations

from backend.app.services.consultation._domain_utils import (
    build_consultation_section,
    filter_observations,
    matching_recommendations,
    matching_root_causes,
    score_observation,
)
from backend.app.services.consultation.consultation_models import DomainConsultationConfig
from backend.app.services.reasoning.fusion.models import FusionResult
from tests.consultation.conftest import fused_observation


CONFIG = DomainConsultationConfig(
    section_id="test",
    title="Test",
    keywords=("venus", "relationship"),
    primary_planets=("Venus",),
    target_houses=(7,),
    timeline_hint="Test timeline hint.",
)


class TestDomainUtils:
    def test_score_observation_boosts_keyword_and_planet_matches(self, rich_fusion_result: FusionResult) -> None:
        observation = rich_fusion_result.observations[0]
        score = score_observation(observation, CONFIG)
        assert score > observation.rank_score

    def test_filter_observations_returns_ranked_matches(self, rich_fusion_result: FusionResult) -> None:
        matched = filter_observations(rich_fusion_result, CONFIG)
        assert matched[0].fusion_id == "obs-rel"

    def test_matching_root_causes_by_observation_and_keyword(self, rich_fusion_result: FusionResult) -> None:
        observations = filter_observations(rich_fusion_result, CONFIG)
        roots = matching_root_causes(rich_fusion_result, observations, CONFIG)
        assert roots[0].title == "Venus relationship pressure"

    def test_matching_recommendations_by_root_and_keyword(self, rich_fusion_result: FusionResult) -> None:
        observations = filter_observations(rich_fusion_result, CONFIG)
        roots = matching_root_causes(rich_fusion_result, observations, CONFIG)
        recommendations = matching_recommendations(rich_fusion_result, roots, CONFIG)
        assert recommendations[0].title == "Strengthen Venus remedies"

    def test_build_consultation_section_uses_dasha_timeline(self, rich_fusion_result: FusionResult) -> None:
        section = build_consultation_section(rich_fusion_result, CONFIG)
        assert "Saturn career discipline indicates" not in section.timeline
        career_config = DomainConsultationConfig(
            section_id="career",
            title="Career",
            keywords=("career", "10th"),
            primary_planets=("Saturn",),
            target_houses=(10,),
            timeline_hint="Career hint.",
        )
        career_section = build_consultation_section(rich_fusion_result, career_config)
        assert "Saturn career discipline indicates" in career_section.timeline

    def test_build_consultation_section_fallback_advice(self, empty_fusion_result: FusionResult) -> None:
        section = build_consultation_section(empty_fusion_result, CONFIG)
        assert "Monitor test themes" in section.actionable_advice[0]

    def test_build_consultation_section_conflict_challenge(self, rich_fusion_result: FusionResult) -> None:
        health_config = DomainConsultationConfig(
            section_id="health",
            title="Health",
            keywords=("health",),
            primary_planets=("Mars",),
            target_houses=(6, 8),
        )
        section = build_consultation_section(rich_fusion_result, health_config)
        assert "Mars health sensitivity" in section.challenges

    def test_matching_root_causes_by_keyword_only(self, rich_fusion_result: FusionResult) -> None:
        roots = matching_root_causes(rich_fusion_result, (), CONFIG)
        assert roots[0].title == "Venus relationship pressure"

    def test_matching_recommendations_by_keyword_only(self, rich_fusion_result: FusionResult) -> None:
        recommendations = matching_recommendations(rich_fusion_result, (), CONFIG)
        assert recommendations[0].title == "Strengthen Venus remedies"

    def test_build_consultation_section_uses_first_recommendation_when_no_domain_match(
        self,
        rich_fusion_result: FusionResult,
    ) -> None:
        unrelated_config = DomainConsultationConfig(
            section_id="other",
            title="Other",
            keywords=("pluto",),
            primary_planets=("Pluto",),
            target_houses=(3,),
        )
        section = build_consultation_section(rich_fusion_result, unrelated_config)
        assert rich_fusion_result.recommendations[0].explanation in section.actionable_advice[0]

    def test_section_confidence_with_observations_only(self, rich_fusion_result: FusionResult) -> None:
        obs_only = FusionResult(
            analyzed_at=rich_fusion_result.analyzed_at,
            observations=rich_fusion_result.observations[:1],
            root_causes=(),
            recommendations=(),
            confidence_score=0.6,
        )
        section = build_consultation_section(obs_only, CONFIG)
        assert section.confidence > 0

    def test_join_unique_skips_duplicates(self) -> None:
        from backend.app.services.consultation._domain_utils import _join_unique

        assert _join_unique(("a", "a", "b")) == "a b"

    def test_build_consultation_section_uses_global_recommendation_fallback(
        self,
        rich_fusion_result: FusionResult,
    ) -> None:
        finance_config = DomainConsultationConfig(
            section_id="finance",
            title="Finance",
            keywords=("wealth",),
            primary_planets=("Jupiter",),
            target_houses=(2, 11),
        )
        limited = FusionResult(
            analyzed_at=rich_fusion_result.analyzed_at,
            observations=rich_fusion_result.observations[2:3],
            root_causes=(),
            recommendations=rich_fusion_result.recommendations,
            confidence_score=0.7,
        )
        section = build_consultation_section(limited, finance_config)
        assert limited.recommendations[0].explanation in section.actionable_advice[0]

    def test_low_rank_observation_filtered_out(self, rich_fusion_result: FusionResult) -> None:
        low_rank = FusionResult(
            analyzed_at=rich_fusion_result.analyzed_at,
            observations=(
                fused_observation(
                    fusion_id="low",
                    title="Unrelated theme",
                    planets=("Pluto",),
                    houses=(3,),
                    rank_score=0.05,
                    severity=0.2,
                    confidence=0.4,
                ),
            ),
            root_causes=(),
            recommendations=(),
            confidence_score=0.5,
        )
        section = build_consultation_section(low_rank, CONFIG)
        assert "steady" in section.current_situation.lower()
