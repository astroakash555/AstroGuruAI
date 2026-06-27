"""Tests for fusion and recommendation consistency metrics."""

from __future__ import annotations

from backend.app.services.evaluation.metrics import (
    compute_fusion_consistency,
    compute_recommendation_consistency,
)


class TestFusionConsistency:
    def test_fusion_consistency_high_for_aligned_output(
        self,
        sample_fusion,
        sample_observations_by_engine,
    ) -> None:
        metric = compute_fusion_consistency(sample_fusion, sample_observations_by_engine)
        assert metric.metric_id == "fusion_consistency"
        assert metric.score >= 0.7

    def test_fusion_consistency_penalizes_conflicts(
        self,
        sample_fusion,
        sample_observations_by_engine,
    ) -> None:
        fusion = dict(sample_fusion)
        fusion["conflicts"] = [{"conflict_id": "c1"}, {"conflict_id": "c2"}]
        metric = compute_fusion_consistency(fusion, sample_observations_by_engine)
        assert metric.details["conflict_count"] == 2
        assert metric.score < 1.0

    def test_fusion_consistency_empty_fusion_with_observations(
        self,
        sample_observations_by_engine,
    ) -> None:
        metric = compute_fusion_consistency({}, sample_observations_by_engine)
        assert metric.details["empty_fusion_penalty"] is True

    def test_fusion_consistency_empty_inputs(self) -> None:
        metric = compute_fusion_consistency({}, {})
        assert metric.score == 0.0

    def test_fusion_consistency_without_root_cause_supporting_ids(self) -> None:
        fusion = {
            "observations": [{"fusion_id": "f1", "confidence": 0.8, "severity": 0.7, "supporting_engines": ["vedic"]}],
            "root_causes": [{"title": "Cause", "supporting_observations": []}],
            "recommendations": [],
            "conflicts": [],
        }
        metric = compute_fusion_consistency(fusion, {})
        assert metric.details["linked_root_cause_ratio"] == 0.75

    def test_fusion_consistency_without_fused_observations_or_root_causes(self) -> None:
        metric = compute_fusion_consistency(
            {"observations": [], "root_causes": [], "recommendations": [], "conflicts": []},
            {"vedic": ()},
        )
        assert metric.details["empty_fusion_penalty"] is True

    def test_fusion_consistency_with_observations_but_no_root_causes(self) -> None:
        fusion = {
            "observations": [{"fusion_id": "f1", "confidence": 0.8, "severity": 0.7, "supporting_engines": ["vedic"]}],
            "root_causes": [],
            "recommendations": [{"title": "Rec", "supporting_root_causes": []}],
            "conflicts": [],
        }
        metric = compute_fusion_consistency(fusion, {})
        assert metric.details["linked_root_cause_ratio"] == 1.0

    def test_private_metric_helpers(self) -> None:
        from backend.app.services.evaluation.metrics import (
            _confidence_alignment,
            _engine_support_ratio,
            _recommendation_root_cause_coverage,
        )

        assert _engine_support_ratio([]) == 0.0
        assert _confidence_alignment([], 0.5) == 0.0
        assert _recommendation_root_cause_coverage([], [{"title": "Cause"}]) == 0.5


class TestRecommendationConsistency:
    def test_recommendation_consistency_aligned(
        self,
        sample_unified_report,
        sample_fusion,
    ) -> None:
        metric = compute_recommendation_consistency(sample_unified_report, sample_fusion)
        assert metric.metric_id == "recommendation_consistency"
        assert metric.score >= 0.5

    def test_recommendation_consistency_without_fusion_recommendations(
        self,
        sample_unified_report,
    ) -> None:
        fusion = {"recommendations": [], "root_causes": []}
        metric = compute_recommendation_consistency(sample_unified_report, fusion)
        assert metric.score >= 0.5

    def test_recommendation_consistency_without_root_causes(self, sample_unified_report) -> None:
        fusion = {
            "recommendations": [
                {
                    "title": "Action",
                    "supporting_root_causes": ["Missing Cause"],
                }
            ],
            "root_causes": [],
        }
        metric = compute_recommendation_consistency(sample_unified_report, fusion)
        assert metric.details["linked_root_cause_ratio"] == 0.0
