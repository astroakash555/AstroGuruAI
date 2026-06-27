"""Learning metrics calculator."""

from __future__ import annotations

from case_learning.constants import (
    OUTCOME_FAILURE_TYPES,
    OUTCOME_SUCCESS_TYPES,
    REMEDY_SUCCESS_THRESHOLD,
    TRACKED_CATEGORIES,
)
from case_learning.types import ConsultationCase, LearningMetrics


def compute_metrics(cases: tuple[ConsultationCase, ...]) -> LearningMetrics:
    if not cases:
        return LearningMetrics(
            prediction_accuracy=0.0,
            remedy_success_rate=0.0,
            rule_accuracy=0.0,
            cases_analyzed=0,
            category_breakdown={},
        )

    prediction_scores = [_prediction_match(case) for case in cases]
    remedy_scores = [_remedy_success(case) for case in cases]
    rule_scores = [_rule_match(case) for case in cases]

    category_breakdown = {
        category: _category_stats([case for case in cases if case.category == category])
        for category in TRACKED_CATEGORIES
        if any(case.category == category for case in cases)
    }

    return LearningMetrics(
        prediction_accuracy=round(sum(prediction_scores) / len(prediction_scores), 4),
        remedy_success_rate=round(sum(remedy_scores) / len(remedy_scores), 4),
        rule_accuracy=round(sum(rule_scores) / len(rule_scores), 4),
        cases_analyzed=len(cases),
        category_breakdown=category_breakdown,
    )


def _prediction_match(case: ConsultationCase) -> float:
    if not case.predicted_outcome or not case.final_outcome:
        return 0.0
    if case.predicted_outcome == case.final_outcome:
        return 1.0

    predicted_success = _is_success_outcome(case.predicted_outcome)
    final_success = _is_success_outcome(case.final_outcome)
    predicted_failure = _is_failure_outcome(case.predicted_outcome)
    final_failure = _is_failure_outcome(case.final_outcome)

    if predicted_success == final_success and predicted_failure == final_failure:
        return 0.75
    if (predicted_success and final_failure) or (predicted_failure and final_success):
        return 0.0
    return 0.4


def _remedy_success(case: ConsultationCase) -> float:
    if not case.applied_remedies:
        return 0.5
    if not case.follow_up_results:
        return 0.3

    effective = 0
    for follow_up in case.follow_up_results:
        effectiveness = follow_up.remedy_effectiveness or follow_up.outcome_type
        if effectiveness in {"effective", "partial", "success", "recovery"}:
            effective += 1
        elif effectiveness in {"ineffective", "failure", "no_change"}:
            effective += 0
        else:
            effective += 0.5

    return round(effective / len(case.follow_up_results), 4)


def _rule_match(case: ConsultationCase) -> float:
    if not case.applied_rules:
        return 0.5
    consensus = case.system_prediction.get("consensus_outcome") or case.predicted_outcome
    if consensus == case.final_outcome:
        return 1.0
    if _outcome_family(consensus) == _outcome_family(case.final_outcome):
        return 0.7
    return 0.2


def _category_stats(cases: list[ConsultationCase]) -> dict[str, float | int]:
    if not cases:
        return {"count": 0}
    return {
        "count": len(cases),
        "prediction_accuracy": round(sum(_prediction_match(case) for case in cases) / len(cases), 4),
        "remedy_success_rate": round(sum(_remedy_success(case) for case in cases) / len(cases), 4),
        "rule_accuracy": round(sum(_rule_match(case) for case in cases) / len(cases), 4),
    }


def _is_success_outcome(outcome: str) -> bool:
    return any(token in outcome for token in OUTCOME_SUCCESS_TYPES)


def _is_failure_outcome(outcome: str) -> bool:
    return any(token in outcome for token in OUTCOME_FAILURE_TYPES)


def _outcome_family(outcome: str) -> str:
    if _is_success_outcome(outcome):
        return "success"
    if _is_failure_outcome(outcome):
        return "failure"
    if "delay" in outcome:
        return "delay"
    return "neutral"
