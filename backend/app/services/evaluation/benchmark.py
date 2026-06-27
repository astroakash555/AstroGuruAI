"""Intelligence evaluation benchmark orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.services.evaluation.agreement import compute_cross_engine_agreement
from backend.app.services.evaluation.confidence import compute_confidence_calibration
from backend.app.services.evaluation.drift import detect_output_drift
from backend.app.services.evaluation.metrics import (
    compute_fusion_consistency,
    compute_recommendation_consistency,
)
from backend.app.services.evaluation.models import (
    EvaluationInput,
    EvaluationResult,
    MetricRecord,
    clamp_score,
    extract_engine_observations,
    resolve_fusion_payload,
)
from backend.app.services.evaluation.regression import compare_reports


class IntelligenceEvaluationBenchmark:
    """
    Evaluates intelligence quality from unified report and fusion outputs.

    Computes cross-engine agreement, fusion consistency, recommendation
    alignment, confidence calibration, drift, regression, and an overall score.
    """

    ENGINE_VERSION = "intelligence_evaluation_v1"

    def evaluate(self, evaluation_input: EvaluationInput) -> EvaluationResult:
        """Run all evaluation modules and return structured metrics."""
        unified_report = evaluation_input.unified_report
        fusion = resolve_fusion_payload(unified_report, evaluation_input.fusion)
        observations = evaluation_input.observations or extract_engine_observations(unified_report)

        agreement = compute_cross_engine_agreement(observations)
        fusion_consistency = compute_fusion_consistency(fusion, observations)
        recommendation_consistency = compute_recommendation_consistency(unified_report, fusion)
        confidence_calibration = compute_confidence_calibration(fusion, observations)

        drift = None
        if evaluation_input.baseline_report is not None:
            drift = detect_output_drift(unified_report, evaluation_input.baseline_report)

        regression = None
        comparison_report = evaluation_input.comparison_report or evaluation_input.baseline_report
        if comparison_report is not None:
            regression = compare_reports(comparison_report, unified_report)

        completeness = _coverage_metric(observations, fusion)
        metric_records = (
            agreement,
            fusion_consistency,
            recommendation_consistency,
            confidence_calibration,
            completeness,
        )

        intelligence_quality_score = _overall_quality_score(
            metric_records,
            drift=drift,
            regression=regression,
        )

        return EvaluationResult(
            evaluated_at=datetime.now(timezone.utc),
            cross_engine_agreement=agreement.score,
            fusion_consistency=fusion_consistency.score,
            recommendation_consistency=recommendation_consistency.score,
            confidence_calibration=confidence_calibration.score,
            drift=drift,
            regression=regression,
            intelligence_quality_score=intelligence_quality_score,
            metrics=metric_records,
            metadata={
                "engine": self.ENGINE_VERSION,
                "engines_observed": sorted(observations.keys()),
                "fusion_observation_count": len(fusion.get("observations", [])),
                "drift_detected": drift.is_drift_detected if drift else False,
                "has_regression": regression.has_regression if regression else False,
            },
        )


def evaluate_intelligence(evaluation_input: EvaluationInput) -> EvaluationResult:
    """Convenience wrapper for benchmark evaluation."""
    return IntelligenceEvaluationBenchmark().evaluate(evaluation_input)


def _coverage_metric(
    observations: dict[str, tuple],
    fusion: dict,
) -> MetricRecord:
    """Score intelligence section coverage across available engines."""
    expected_engines = ("vedic", "kp", "lal_kitab")
    present = sum(1 for engine in expected_engines if observations.get(engine))
    engine_coverage = present / len(expected_engines)

    has_fusion = bool(fusion.get("observations") or fusion.get("root_causes"))
    fusion_coverage = 1.0 if has_fusion else 0.0

    score = clamp_score((0.65 * engine_coverage) + (0.35 * fusion_coverage))
    return MetricRecord(
        metric_id="section_coverage",
        name="Intelligence Section Coverage",
        score=score,
        weight=0.10,
        details={
            "engines_present": present,
            "expected_engines": len(expected_engines),
            "has_fusion_output": has_fusion,
        },
    )


def _overall_quality_score(
    metrics: tuple[MetricRecord, ...],
    *,
    drift: object | None,
    regression: object | None,
) -> float:
    """Compute weighted overall intelligence quality score."""
    weights = {metric.metric_id: metric.weight for metric in metrics}
    weighted_sum = sum(metric.score * metric.weight for metric in metrics)
    total_weight = sum(weights.values())

    if drift is not None:
        drift_score = clamp_score(1.0 - drift.drift_score)  # type: ignore[attr-defined]
        drift_weight = 0.10
        weighted_sum += drift_score * drift_weight
        total_weight += drift_weight

    if regression is not None:
        regression_score = regression.regression_score  # type: ignore[attr-defined]
        regression_weight = 0.10
        weighted_sum += regression_score * regression_weight
        total_weight += regression_weight

    if total_weight == 0:
        return 0.0
    return clamp_score(weighted_sum / total_weight)
