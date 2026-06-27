"""Serialize case learning objects to JSON."""

from __future__ import annotations

from typing import Any

from case_learning.store.repository import _case_to_dict
from case_learning.types import ConsultationCase, LearningMetrics, LearningReport


def case_to_dict(case: ConsultationCase) -> dict[str, Any]:
    return _case_to_dict(case)


def metrics_to_dict(metrics: LearningMetrics) -> dict[str, Any]:
    return {
        "prediction_accuracy": metrics.prediction_accuracy,
        "remedy_success_rate": metrics.remedy_success_rate,
        "rule_accuracy": metrics.rule_accuracy,
        "cases_analyzed": metrics.cases_analyzed,
        "category_breakdown": metrics.category_breakdown,
    }


def learning_report_to_dict(report: LearningReport) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "generated_at": report.generated_at.isoformat(),
        "total_cases": report.total_cases,
        "metrics": metrics_to_dict(report.metrics),
        "category_tracking": report.category_tracking,
        "suggestions": [
            {
                "suggestion_id": item.suggestion_id,
                "suggestion_type": item.suggestion_type,
                "rule_id": item.rule_id,
                "category": item.category,
                "priority": item.priority,
                "reason": item.reason,
                "suggested_action": item.suggested_action,
                "evidence": item.evidence,
            }
            for item in report.suggestions
        ],
        "feedback_loops": [
            {
                "loop_id": loop.loop_id,
                "category": loop.category,
                "trigger": loop.trigger,
                "metrics_snapshot": loop.metrics_snapshot,
                "target_module": loop.target_module,
                "suggestions": [
                    {
                        "suggestion_id": item.suggestion_id,
                        "suggestion_type": item.suggestion_type,
                        "rule_id": item.rule_id,
                        "priority": item.priority,
                        "suggested_action": item.suggested_action,
                    }
                    for item in loop.suggestions
                ],
            }
            for loop in report.feedback_loops
        ],
        "metadata": dict(report.metadata),
    }
