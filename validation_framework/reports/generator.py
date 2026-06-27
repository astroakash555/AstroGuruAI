"""Validation report generator."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from validation_framework.metrics.accuracy import metrics_to_dict
from validation_framework.types import (
    AccuracyMetrics,
    CaseValidationResult,
    FailedCaseRecord,
    RetrainingRecommendation,
    ValidationReport,
)


def generate_validation_report(
    *,
    case_results: tuple[CaseValidationResult, ...],
    failed_records: tuple[FailedCaseRecord, ...],
    retraining_recommendations: tuple[RetrainingRecommendation, ...],
    dataset_version: str = "1.0",
) -> ValidationReport:
    passed = sum(1 for result in case_results if result.passed)
    failed = len(case_results) - passed

    category_summary = _category_summary(case_results)
    aggregate_metrics = _aggregate_metrics(case_results)

    return ValidationReport(
        report_id=str(uuid4()),
        generated_at=datetime.now(timezone.utc),
        dataset_version=dataset_version,
        total_cases=len(case_results),
        passed_cases=passed,
        failed_cases=failed,
        category_summary=category_summary,
        aggregate_metrics=aggregate_metrics,
        case_results=case_results,
        failed_case_records=failed_records,
        retraining_recommendations=retraining_recommendations,
        metadata={
            "engine": "validation_framework_v1",
            "ai_prediction": False,
            "aggregate_match_percentage": aggregate_metrics.overall_match_percentage,
        },
    )


def _category_summary(case_results: tuple[CaseValidationResult, ...]) -> dict[str, dict]:
    summary: dict[str, dict] = {}
    for result in case_results:
        bucket = summary.setdefault(
            result.category,
            {"total": 0, "passed": 0, "failed": 0, "average_match_percentage": 0.0},
        )
        bucket["total"] += 1
        if result.passed:
            bucket["passed"] += 1
        else:
            bucket["failed"] += 1
        bucket["average_match_percentage"] += result.match_percentage

    for bucket in summary.values():
        total = bucket["total"]
        bucket["average_match_percentage"] = round(bucket["average_match_percentage"] / total, 2)
    return summary


def _aggregate_metrics(case_results: tuple[CaseValidationResult, ...]) -> AccuracyMetrics:
    if not case_results:
        return AccuracyMetrics(0, 0, 0, 0, 0)

    totals = {"planet": 0.0, "house": 0.0, "dasha": 0.0, "transit": 0.0, "remedy": 0.0}
    for result in case_results:
        metrics = result.accuracy_metrics
        totals["planet"] += metrics.planet_accuracy
        totals["house"] += metrics.house_accuracy
        totals["dasha"] += metrics.dasha_accuracy
        totals["transit"] += metrics.transit_accuracy
        totals["remedy"] += metrics.remedy_accuracy

    count = len(case_results)
    return AccuracyMetrics(
        planet_accuracy=round(totals["planet"] / count, 4),
        house_accuracy=round(totals["house"] / count, 4),
        dasha_accuracy=round(totals["dasha"] / count, 4),
        transit_accuracy=round(totals["transit"] / count, 4),
        remedy_accuracy=round(totals["remedy"] / count, 4),
    )


def report_summary_dict(report: ValidationReport) -> dict:
    return {
        "report_id": report.report_id,
        "generated_at": report.generated_at.isoformat(),
        "dataset_version": report.dataset_version,
        "total_cases": report.total_cases,
        "passed_cases": report.passed_cases,
        "failed_cases": report.failed_cases,
        "aggregate_metrics": metrics_to_dict(report.aggregate_metrics),
        "category_summary": report.category_summary,
    }
