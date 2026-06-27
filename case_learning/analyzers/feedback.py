"""Feedback loop builder."""

from __future__ import annotations

from uuid import uuid4

from case_learning.types import FeedbackLoop, LearningMetrics, RuleSuggestion


def build_feedback_loops(
    metrics: LearningMetrics,
    suggestions: tuple[RuleSuggestion, ...],
) -> tuple[FeedbackLoop, ...]:
    loops: list[FeedbackLoop] = []

    if metrics.prediction_accuracy < 0.6:
        loops.append(
            FeedbackLoop(
                loop_id=str(uuid4()),
                category="all",
                trigger="low_prediction_accuracy",
                metrics_snapshot={
                    "prediction_accuracy": metrics.prediction_accuracy,
                    "cases_analyzed": metrics.cases_analyzed,
                },
                suggestions=tuple(item for item in suggestions if item.suggestion_type in {"weak_rule", "obsolete_rule"}),
                target_module="reasoning_layer",
            )
        )

    if metrics.remedy_success_rate < 0.5:
        loops.append(
            FeedbackLoop(
                loop_id=str(uuid4()),
                category="all",
                trigger="low_remedy_success",
                metrics_snapshot={"remedy_success_rate": metrics.remedy_success_rate},
                suggestions=tuple(item for item in suggestions if item.suggestion_type == "rule_improvement"),
                target_module="remedy_engine",
            )
        )

    if metrics.rule_accuracy < 0.55:
        loops.append(
            FeedbackLoop(
                loop_id=str(uuid4()),
                category="all",
                trigger="low_rule_accuracy",
                metrics_snapshot={"rule_accuracy": metrics.rule_accuracy},
                suggestions=tuple(item for item in suggestions if item.suggestion_type == "new_rule_candidate"),
                target_module="rule_studio",
            )
        )

    for category, stats in metrics.category_breakdown.items():
        if stats.get("count", 0) < 2:
            continue
        if stats.get("prediction_accuracy", 1.0) < 0.55:
            loops.append(
                FeedbackLoop(
                    loop_id=str(uuid4()),
                    category=category,
                    trigger=f"category_{category}_underperformance",
                    metrics_snapshot=dict(stats),
                    suggestions=tuple(item for item in suggestions if item.category == category),
                    target_module="knowledge_brain",
                )
            )

    return tuple(loops)
