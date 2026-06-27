"""Tests for consultation prioritization helpers."""

from __future__ import annotations

from backend.app.services.consultation.recommendation_prioritizer import build_priorities, build_risks, build_strengths
from backend.app.services.reasoning.fusion.models import FusionResult
from tests.consultation.conftest import fused_observation


class TestRecommendationPrioritizer:
    def test_build_priorities_from_recommendations(self, rich_fusion_result: FusionResult) -> None:
        priorities = build_priorities(rich_fusion_result)

        assert len(priorities) == 5
        assert priorities[0].title == "Strengthen Venus remedies"
        assert priorities[0].domain == "relationship"
        assert priorities[1].title == "Career patience protocol"

    def test_build_priorities_fills_from_root_causes_and_observations(
        self,
        rich_fusion_result: FusionResult,
    ) -> None:
        extended = FusionResult(
            analyzed_at=rich_fusion_result.analyzed_at,
            observations=rich_fusion_result.observations
            + (
                fused_observation(
                    fusion_id="obs-edu",
                    title="Mercury education focus",
                    planets=("Mercury",),
                    houses=(5,),
                    category="vedic:education",
                ),
            ),
            root_causes=rich_fusion_result.root_causes
            + (
                rich_fusion_result.root_causes[0],
                rich_fusion_result.root_causes[1],
            ),
            recommendations=rich_fusion_result.recommendations,
            confidence_score=rich_fusion_result.confidence_score,
            conflicts=rich_fusion_result.conflicts,
            metadata=rich_fusion_result.metadata,
        )
        priorities = build_priorities(extended)
        assert len(priorities) == 5

    def test_build_strengths_prefers_supportive_observations(self, rich_fusion_result: FusionResult) -> None:
        strengths = build_strengths(rich_fusion_result)

        assert strengths
        assert strengths[0].confidence >= 0.75
        assert strengths[0].supporting_engines

    def test_build_strengths_fallback_when_no_high_confidence(self, empty_fusion_result: FusionResult) -> None:
        assert build_strengths(empty_fusion_result) == ()

    def test_build_risks_includes_conflicts_first(self, rich_fusion_result: FusionResult) -> None:
        risks = build_risks(rich_fusion_result)

        assert risks[0].title == "Health interpretation split"
        assert risks[0].has_conflict is True

    def test_infer_domain_general_fallback(self, empty_fusion_result: FusionResult) -> None:
        assert build_priorities(empty_fusion_result) == ()

    def test_infer_domain_keywords(self, rich_fusion_result: FusionResult) -> None:
        from backend.app.services.consultation.recommendation_prioritizer import _infer_domain

        assert _infer_domain("Marriage delay", "spouse timing") == "marriage"
        assert _infer_domain("Business trade", "commerce profit") == "business"
        assert _infer_domain("Foreign travel abroad", "settlement") == "foreign_travel"
        assert _infer_domain("Spiritual dharma", "meditation") == "spiritual_growth"
        assert _infer_domain("Family home", "4th house") == "family"
        assert _infer_domain("Children progeny", "5th house") == "children"
        assert _infer_domain("Career profession", "10th house") == "career"
        assert _infer_domain("Education study", "learning path") == "education"
        assert _infer_domain("Health vitality", "6th house") == "health"
        assert _infer_domain("Generic note", "no keyword here") == "general"

    def test_build_priorities_skips_duplicate_root_titles(self, rich_fusion_result: FusionResult) -> None:
        duplicate = FusionResult(
            analyzed_at=rich_fusion_result.analyzed_at,
            observations=(),
            root_causes=(
                rich_fusion_result.root_causes[0],
                rich_fusion_result.root_causes[0],
            ),
            recommendations=(
                rich_fusion_result.recommendations[0],
            ),
            confidence_score=0.5,
        )
        priorities = build_priorities(duplicate)
        assert sum(item.title == "Venus relationship pressure" for item in priorities) == 1

    def test_build_priorities_skips_duplicate_roots_without_recommendations(
        self,
        rich_fusion_result: FusionResult,
    ) -> None:
        duplicate_roots = FusionResult(
            analyzed_at=rich_fusion_result.analyzed_at,
            observations=(),
            root_causes=(
                rich_fusion_result.root_causes[0],
                rich_fusion_result.root_causes[0],
            ),
            recommendations=(),
            confidence_score=0.5,
        )
        priorities = build_priorities(duplicate_roots)
        assert len(priorities) == 1

    def test_build_priorities_stops_adding_roots_when_full(self, rich_fusion_result: FusionResult) -> None:
        from backend.app.services.reasoning.fusion.models import FusionRecommendation

        recommendations = tuple(
            FusionRecommendation(
                recommendation_id=f"rec-{index}",
                title=f"Recommendation {index}",
                explanation="Action step.",
                priority="medium",
                supporting_root_causes=(),
                confidence=0.7,
            )
            for index in range(5)
        )
        extended = FusionResult(
            analyzed_at=rich_fusion_result.analyzed_at,
            observations=(),
            root_causes=rich_fusion_result.root_causes,
            recommendations=recommendations,
            confidence_score=0.5,
        )
        assert len(build_priorities(extended)) == 5

    def test_build_risks_skips_duplicate_observation_titles(self, rich_fusion_result: FusionResult) -> None:
        risks = build_risks(rich_fusion_result)
        titles = [item.title for item in risks]
        assert len(titles) == len(set(titles))

    def test_build_risks_stops_after_five_items(self, rich_fusion_result: FusionResult) -> None:
        from backend.app.services.reasoning.fusion.models import FusionEngineId, InterpretationConflict

        conflicts = tuple(
            InterpretationConflict(
                conflict_id=f"conf-{index}",
                title=f"Conflict {index}",
                explanation="Split interpretation.",
                engines=(FusionEngineId.VEDIC, FusionEngineId.KP),
                observation_ids=(f"obs-{index}",),
                affected_planets=("Mars",),
                affected_houses=(6,),
                severity_spread=0.2,
                confidence=0.7,
            )
            for index in range(6)
        )
        extended = FusionResult(
            analyzed_at=rich_fusion_result.analyzed_at,
            observations=rich_fusion_result.observations,
            root_causes=rich_fusion_result.root_causes,
            recommendations=rich_fusion_result.recommendations,
            confidence_score=rich_fusion_result.confidence_score,
            conflicts=conflicts,
        )
        assert len(build_risks(extended)) == 5

    def test_build_risks_skips_observation_matching_conflict_title(self, rich_fusion_result: FusionResult) -> None:
        from backend.app.services.reasoning.fusion.models import FusionEngineId, InterpretationConflict

        conflict = InterpretationConflict(
            conflict_id="conf-dup",
            title="Mars health sensitivity",
            explanation="Duplicate title conflict.",
            engines=(FusionEngineId.VEDIC, FusionEngineId.KP),
            observation_ids=("obs-health",),
            affected_planets=("Mars",),
            affected_houses=(6,),
            severity_spread=0.2,
            confidence=0.7,
        )
        extended = FusionResult(
            analyzed_at=rich_fusion_result.analyzed_at,
            observations=rich_fusion_result.observations,
            root_causes=rich_fusion_result.root_causes,
            recommendations=rich_fusion_result.recommendations,
            confidence_score=rich_fusion_result.confidence_score,
            conflicts=(conflict,),
        )
        risks = build_risks(extended)
        assert sum(item.title == "Mars health sensitivity" for item in risks) == 1
