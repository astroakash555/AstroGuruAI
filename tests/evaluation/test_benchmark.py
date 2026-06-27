"""Tests for the intelligence evaluation benchmark orchestrator."""

from __future__ import annotations

import copy
from datetime import datetime, timezone

import pytest

from backend.app.services.evaluation import (
    EvaluationInput,
    IntelligenceEvaluationBenchmark,
    evaluate_intelligence,
)
from tests.evaluation.conftest import GENERATED_AT


class TestIntelligenceEvaluationBenchmark:
    def test_evaluate_returns_structured_metrics(self, sample_unified_report) -> None:
        result = evaluate_intelligence(EvaluationInput(unified_report=sample_unified_report))
        assert result.metadata["engine"] == "intelligence_evaluation_v1"
        assert 0.0 <= result.intelligence_quality_score <= 1.0
        assert 0.0 <= result.cross_engine_agreement <= 1.0
        assert 0.0 <= result.fusion_consistency <= 1.0
        assert 0.0 <= result.recommendation_consistency <= 1.0
        assert 0.0 <= result.confidence_calibration <= 1.0
        assert len(result.metrics) == 5
        assert result.drift is None
        assert result.regression is None

    def test_evaluate_with_explicit_fusion_and_observations(
        self,
        sample_unified_report,
        sample_fusion,
        sample_observations_by_engine,
    ) -> None:
        result = IntelligenceEvaluationBenchmark().evaluate(
            EvaluationInput(
                unified_report=sample_unified_report,
                fusion=sample_fusion,
                observations=sample_observations_by_engine,
            )
        )
        assert result.cross_engine_agreement > 0.0

    def test_evaluate_with_drift_and_regression(
        self,
        sample_unified_report,
        baseline_unified_report,
    ) -> None:
        regressed = copy.deepcopy(sample_unified_report)
        regressed["fusion"]["confidence"] = 0.15
        regressed["vedic"]["observations"] = []

        result = IntelligenceEvaluationBenchmark().evaluate(
            EvaluationInput(
                unified_report=regressed,
                baseline_report=baseline_unified_report,
                comparison_report=baseline_unified_report,
            )
        )
        assert result.drift is not None
        assert result.regression is not None
        assert result.drift.drift_score > 0.0
        assert result.regression.has_regression is True
        assert result.intelligence_quality_score < 0.95

    def test_frozen_evaluated_at_timestamp(self, sample_unified_report, monkeypatch: pytest.MonkeyPatch) -> None:
        import backend.app.services.evaluation.benchmark as benchmark_module

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None) -> datetime:  # noqa: ANN001
                if tz is None:
                    return GENERATED_AT.replace(tzinfo=None)
                return GENERATED_AT

        monkeypatch.setattr(benchmark_module, "datetime", FixedDateTime)
        result = IntelligenceEvaluationBenchmark().evaluate(
            EvaluationInput(unified_report=sample_unified_report)
        )
        assert result.evaluated_at == GENERATED_AT

    def test_metric_records_include_weights(self, sample_unified_report) -> None:
        result = evaluate_intelligence(EvaluationInput(unified_report=sample_unified_report))
        assert {metric.metric_id for metric in result.metrics} == {
            "cross_engine_agreement",
            "fusion_consistency",
            "recommendation_consistency",
            "confidence_calibration",
            "section_coverage",
        }

    def test_empty_report_quality_score(self) -> None:
        result = evaluate_intelligence(EvaluationInput(unified_report={}))
        assert result.intelligence_quality_score >= 0.0

    def test_overall_quality_score_handles_zero_weight(self) -> None:
        from backend.app.services.evaluation.benchmark import _overall_quality_score

        assert _overall_quality_score((), drift=None, regression=None) == 0.0
