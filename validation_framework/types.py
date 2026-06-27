"""Validation framework typed models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class GroundTruth:
    planets: tuple[str, ...]
    houses: tuple[int, ...]
    dasha_lords: tuple[str, ...]
    transit_indicators: tuple[str, ...]
    remedies: tuple[str, ...]
    consensus_outcome: str | None = None


@dataclass(frozen=True)
class ActualOutcome:
    event: str
    outcome_type: str
    description: str
    occurred_at_age: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CaseStudy:
    case_id: str
    category: str
    title: str
    problem_text: str
    actual_outcome: ActualOutcome
    ground_truth: GroundTruth
    source: str = "benchmark"
    unified_report: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SystemPrediction:
    planets: tuple[str, ...]
    houses: tuple[int, ...]
    dasha_lords: tuple[str, ...]
    transit_indicators: tuple[str, ...]
    remedies: tuple[str, ...]
    consensus_outcome: str | None
    confidence_score: int | None = None


@dataclass(frozen=True)
class AccuracyMetrics:
    planet_accuracy: float
    house_accuracy: float
    dasha_accuracy: float
    transit_accuracy: float
    remedy_accuracy: float

    @property
    def overall_match_percentage(self) -> float:
        values = (
            self.planet_accuracy,
            self.house_accuracy,
            self.dasha_accuracy,
            self.transit_accuracy,
            self.remedy_accuracy,
        )
        return round(sum(values) / len(values) * 100, 2)


@dataclass(frozen=True)
class CaseValidationResult:
    case_id: str
    category: str
    actual_outcome: dict[str, Any]
    system_prediction: dict[str, Any]
    match_percentage: float
    accuracy_metrics: AccuracyMetrics
    passed: bool
    comparison_details: dict[str, Any]


@dataclass(frozen=True)
class FailedCaseRecord:
    case_id: str
    category: str
    match_percentage: float
    failed_metrics: tuple[str, ...]
    recorded_at: datetime
    case_snapshot: dict[str, Any]


@dataclass(frozen=True)
class RetrainingRecommendation:
    recommendation_id: str
    target_module: str
    metric: str
    priority: str
    reason: str
    suggested_action: str


@dataclass(frozen=True)
class ValidationReport:
    report_id: str
    generated_at: datetime
    dataset_version: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    category_summary: dict[str, Any]
    aggregate_metrics: AccuracyMetrics
    case_results: tuple[CaseValidationResult, ...]
    failed_case_records: tuple[FailedCaseRecord, ...]
    retraining_recommendations: tuple[RetrainingRecommendation, ...]
    metadata: dict[str, object] = field(default_factory=dict)
