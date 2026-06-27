"""Single case validation module."""

from __future__ import annotations

from typing import Any

from validation_framework.constants import FAILURE_THRESHOLD, LOW_METRIC_THRESHOLD
from validation_framework.metrics.accuracy import compute_accuracy_metrics, metrics_to_dict
from validation_framework.metrics.comparison import extract_system_prediction, prediction_to_dict
from validation_framework.types import (
    ActualOutcome,
    CaseStudy,
    CaseValidationResult,
    GroundTruth,
)


def validate_case(case: CaseStudy) -> CaseValidationResult:
    if not case.unified_report:
        raise ValueError(f"Case {case.case_id} requires unified_report for validation.")

    prediction = extract_system_prediction(case.unified_report)
    metrics = compute_accuracy_metrics(case.ground_truth, prediction)
    match_percentage = metrics.overall_match_percentage

    passed = (
        match_percentage >= FAILURE_THRESHOLD
        and all(
            getattr(metrics, name) >= LOW_METRIC_THRESHOLD
            for name in (
                "planet_accuracy",
                "house_accuracy",
                "dasha_accuracy",
                "transit_accuracy",
                "remedy_accuracy",
            )
        )
    )

    return CaseValidationResult(
        case_id=case.case_id,
        category=case.category,
        actual_outcome=outcome_to_dict(case.actual_outcome),
        system_prediction=prediction_to_dict(prediction),
        match_percentage=match_percentage,
        accuracy_metrics=metrics,
        passed=passed,
        comparison_details=_comparison_details(case.ground_truth, prediction, metrics),
    )


def case_from_dict(data: dict[str, Any]) -> CaseStudy:
    ground_truth_data = data["ground_truth"]
    outcome_data = data["actual_outcome"]
    return CaseStudy(
        case_id=data["case_id"],
        category=data["category"],
        title=data["title"],
        problem_text=data.get("problem_text", ""),
        source=data.get("source", "benchmark"),
        actual_outcome=ActualOutcome(
            event=outcome_data["event"],
            outcome_type=outcome_data["outcome_type"],
            description=outcome_data["description"],
            occurred_at_age=outcome_data.get("occurred_at_age"),
            metadata=outcome_data.get("metadata", {}),
        ),
        ground_truth=GroundTruth(
            planets=tuple(ground_truth_data.get("planets", [])),
            houses=tuple(ground_truth_data.get("houses", [])),
            dasha_lords=tuple(ground_truth_data.get("dasha_lords", [])),
            transit_indicators=tuple(ground_truth_data.get("transit_indicators", [])),
            remedies=tuple(ground_truth_data.get("remedies", [])),
            consensus_outcome=ground_truth_data.get("consensus_outcome"),
        ),
        unified_report=data.get("unified_report"),
        metadata=data.get("metadata", {}),
    )


def outcome_to_dict(outcome: ActualOutcome) -> dict[str, Any]:
    return {
        "event": outcome.event,
        "outcome_type": outcome.outcome_type,
        "description": outcome.description,
        "occurred_at_age": outcome.occurred_at_age,
        "metadata": outcome.metadata,
    }


def validation_result_to_dict(result: CaseValidationResult) -> dict[str, Any]:
    return {
        "case_id": result.case_id,
        "category": result.category,
        "actual_outcome": result.actual_outcome,
        "system_prediction": result.system_prediction,
        "match_percentage": result.match_percentage,
        "accuracy_metrics": metrics_to_dict(result.accuracy_metrics),
        "passed": result.passed,
        "comparison_details": result.comparison_details,
    }


def _comparison_details(
    ground_truth: GroundTruth,
    prediction,
    metrics,
) -> dict[str, Any]:
    return {
        "planets": {
            "expected": list(ground_truth.planets),
            "predicted": list(prediction.planets),
            "matched": list(set(ground_truth.planets) & set(prediction.planets)),
            "accuracy": metrics.planet_accuracy,
        },
        "houses": {
            "expected": list(ground_truth.houses),
            "predicted": list(prediction.houses),
            "matched": list(set(ground_truth.houses) & set(prediction.houses)),
            "accuracy": metrics.house_accuracy,
        },
        "dasha_lords": {
            "expected": list(ground_truth.dasha_lords),
            "predicted": list(prediction.dasha_lords),
            "matched": list(set(ground_truth.dasha_lords) & set(prediction.dasha_lords)),
            "accuracy": metrics.dasha_accuracy,
        },
        "transit_indicators": {
            "expected": list(ground_truth.transit_indicators),
            "predicted": list(prediction.transit_indicators),
            "matched": list(
                set(ground_truth.transit_indicators) & set(prediction.transit_indicators)
            ),
            "accuracy": metrics.transit_accuracy,
        },
        "remedies": {
            "expected": list(ground_truth.remedies),
            "predicted": list(prediction.remedies),
            "accuracy": metrics.remedy_accuracy,
        },
        "consensus": {
            "expected": ground_truth.consensus_outcome,
            "predicted": prediction.consensus_outcome,
            "matched": ground_truth.consensus_outcome == prediction.consensus_outcome,
        },
    }
