"""Accuracy metric computation."""

from __future__ import annotations

from validation_framework.types import AccuracyMetrics, GroundTruth, SystemPrediction


def compute_accuracy_metrics(
    ground_truth: GroundTruth,
    prediction: SystemPrediction,
) -> AccuracyMetrics:
    return AccuracyMetrics(
        planet_accuracy=_set_overlap(ground_truth.planets, prediction.planets),
        house_accuracy=_set_overlap(ground_truth.houses, prediction.houses),
        dasha_accuracy=_set_overlap(ground_truth.dasha_lords, prediction.dasha_lords),
        transit_accuracy=_set_overlap(
            ground_truth.transit_indicators,
            prediction.transit_indicators,
        ),
        remedy_accuracy=_remedy_overlap(ground_truth.remedies, prediction.remedies),
    )


def _set_overlap(expected: tuple, predicted: tuple) -> float:
    expected_set = set(expected)
    predicted_set = set(predicted)
    if not expected_set:
        return 1.0 if not predicted_set else 0.5
    if not predicted_set:
        return 0.0
    intersection = expected_set & predicted_set
    return round(len(intersection) / len(expected_set), 4)


def _remedy_overlap(expected: tuple[str, ...], predicted: tuple[str, ...]) -> float:
    if not expected:
        return 1.0 if not predicted else 0.5
    if not predicted:
        return 0.0

    matched = 0
    for expected_id in expected:
        if any(
            expected_id in predicted_id or predicted_id in expected_id
            for predicted_id in predicted
        ):
            matched += 1
    return round(matched / len(expected), 4)


def metrics_to_dict(metrics: AccuracyMetrics) -> dict[str, float]:
    return {
        "planet_accuracy": metrics.planet_accuracy,
        "house_accuracy": metrics.house_accuracy,
        "dasha_accuracy": metrics.dasha_accuracy,
        "transit_accuracy": metrics.transit_accuracy,
        "remedy_accuracy": metrics.remedy_accuracy,
        "overall_match_percentage": metrics.overall_match_percentage,
    }


def failed_metric_names(metrics: AccuracyMetrics, threshold: float) -> tuple[str, ...]:
    failed: list[str] = []
    for name in (
        "planet_accuracy",
        "house_accuracy",
        "dasha_accuracy",
        "transit_accuracy",
        "remedy_accuracy",
    ):
        if getattr(metrics, name) < threshold:
            failed.append(name)
    return tuple(failed)
