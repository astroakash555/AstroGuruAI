"""Retraining recommendation generator."""

from __future__ import annotations

from uuid import uuid4

from validation_framework.constants import LOW_METRIC_THRESHOLD, METRIC_RETRAINING_MAP
from validation_framework.types import (
    AccuracyMetrics,
    CaseValidationResult,
    FailedCaseRecord,
    RetrainingRecommendation,
)


MODULE_MAP = {
    "planet_accuracy": "astro_intelligence",
    "house_accuracy": "problem_analyzer",
    "dasha_accuracy": "reasoning_layer",
    "transit_accuracy": "astrology_engine.transits",
    "remedy_accuracy": "remedy_engine",
}


def generate_retraining_recommendations(
    case_results: tuple[CaseValidationResult, ...],
    failed_records: tuple[FailedCaseRecord, ...],
) -> tuple[RetrainingRecommendation, ...]:
    metric_failures: dict[str, int] = {}
    category_failures: dict[str, int] = {}

    for result in case_results:
        if result.passed:
            continue
        for metric_name in _failed_metrics(result.accuracy_metrics):
            metric_failures[metric_name] = metric_failures.get(metric_name, 0) + 1
        category_failures[result.category] = category_failures.get(result.category, 0) + 1

    recommendations: list[RetrainingRecommendation] = []

    for metric_name, count in sorted(metric_failures.items(), key=lambda item: item[1], reverse=True):
        priority = "high" if count >= 3 else "medium" if count >= 2 else "low"
        recommendations.append(
            RetrainingRecommendation(
                recommendation_id=str(uuid4()),
                target_module=MODULE_MAP.get(metric_name, "validation_framework"),
                metric=metric_name,
                priority=priority,
                reason=f"{count} benchmark case(s) failed {metric_name}.",
                suggested_action=METRIC_RETRAINING_MAP.get(
                    metric_name,
                    "Review benchmark ground truth and engine scoring weights.",
                ),
            )
        )

    for category, count in sorted(category_failures.items(), key=lambda item: item[1], reverse=True):
        if count < 2:
            continue
        recommendations.append(
            RetrainingRecommendation(
                recommendation_id=str(uuid4()),
                target_module="knowledge_brain",
                metric="category_coverage",
                priority="medium",
                reason=f"{count} failed cases in category {category}.",
                suggested_action=(
                    f"Add domain-specific rules and case studies for {category} in knowledge_brain."
                ),
            )
        )

    if failed_records and not recommendations:
        recommendations.append(
            RetrainingRecommendation(
                recommendation_id=str(uuid4()),
                target_module="consultation_layer",
                metric="overall_match_percentage",
                priority="medium",
                reason=f"{len(failed_records)} failed benchmark cases recorded.",
                suggested_action="Review senior_guru synthesis weights and consensus mapping.",
            )
        )

    return tuple(recommendations)


def _failed_metrics(metrics: AccuracyMetrics) -> list[str]:
    return [
        name
        for name in (
            "planet_accuracy",
            "house_accuracy",
            "dasha_accuracy",
            "transit_accuracy",
            "remedy_accuracy",
        )
        if getattr(metrics, name) < LOW_METRIC_THRESHOLD
    ]
