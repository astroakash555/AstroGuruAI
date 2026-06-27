"""Serialize validation results to JSON."""

from __future__ import annotations

from typing import Any

from validation_framework.metrics.accuracy import metrics_to_dict
from validation_framework.reports.generator import report_summary_dict
from validation_framework.serializers.schemas import ValidationReportSchema
from validation_framework.types import ValidationReport


def to_json_dict(report: ValidationReport) -> dict[str, Any]:
    payload = ValidationReportSchema(
        report_id=report.report_id,
        generated_at=report.generated_at,
        dataset_version=report.dataset_version,
        total_cases=report.total_cases,
        passed_cases=report.passed_cases,
        failed_cases=report.failed_cases,
        category_summary=report.category_summary,
        aggregate_metrics=metrics_to_dict(report.aggregate_metrics),
        case_results=[
            {
                "case_id": result.case_id,
                "category": result.category,
                "actual_outcome": result.actual_outcome,
                "system_prediction": result.system_prediction,
                "match_percentage": result.match_percentage,
                "accuracy_metrics": metrics_to_dict(result.accuracy_metrics),
                "passed": result.passed,
                "comparison_details": result.comparison_details,
            }
            for result in report.case_results
        ],
        failed_case_records=[
            {
                "case_id": record.case_id,
                "category": record.category,
                "match_percentage": record.match_percentage,
                "failed_metrics": list(record.failed_metrics),
                "recorded_at": record.recorded_at,
                "case_snapshot": record.case_snapshot,
            }
            for record in report.failed_case_records
        ],
        retraining_recommendations=[
            {
                "recommendation_id": item.recommendation_id,
                "target_module": item.target_module,
                "metric": item.metric,
                "priority": item.priority,
                "reason": item.reason,
                "suggested_action": item.suggested_action,
            }
            for item in report.retraining_recommendations
        ],
        metadata={
            **report.metadata,
            "summary": report_summary_dict(report),
        },
    )
    return payload.model_dump(mode="json")


def to_json_string(report: ValidationReport, *, indent: int | None = 2) -> str:
    import json

    return json.dumps(to_json_dict(report), indent=indent, ensure_ascii=False)
