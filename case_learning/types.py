"""Case learning typed models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FollowUpResult:
    follow_up_id: str
    recorded_at: datetime
    outcome_type: str
    description: str
    remedy_effectiveness: str | None = None
    notes: str = ""


@dataclass(frozen=True)
class ConsultationCase:
    case_id: str
    client_id: str
    category: str
    problem_text: str
    kundali_snapshot: dict[str, Any]
    system_prediction: dict[str, Any]
    applied_rules: tuple[str, ...]
    applied_remedies: tuple[str, ...]
    predicted_outcome: str
    final_outcome: str
    follow_up_results: tuple[FollowUpResult, ...]
    recorded_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningMetrics:
    prediction_accuracy: float
    remedy_success_rate: float
    rule_accuracy: float
    cases_analyzed: int
    category_breakdown: dict[str, Any]


@dataclass(frozen=True)
class RuleSuggestion:
    suggestion_id: str
    suggestion_type: str
    rule_id: str | None
    category: str
    priority: str
    reason: str
    suggested_action: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class FeedbackLoop:
    loop_id: str
    category: str
    trigger: str
    metrics_snapshot: dict[str, Any]
    suggestions: tuple[RuleSuggestion, ...]
    target_module: str


@dataclass(frozen=True)
class LearningReport:
    report_id: str
    generated_at: datetime
    total_cases: int
    metrics: LearningMetrics
    category_tracking: dict[str, Any]
    suggestions: tuple[RuleSuggestion, ...]
    feedback_loops: tuple[FeedbackLoop, ...]
    metadata: dict[str, object] = field(default_factory=dict)
