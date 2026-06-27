"""Pydantic schemas for validation JSON output."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AccuracyMetricsSchema(BaseSchema):
    planet_accuracy: float = Field(..., ge=0, le=1)
    house_accuracy: float = Field(..., ge=0, le=1)
    dasha_accuracy: float = Field(..., ge=0, le=1)
    transit_accuracy: float = Field(..., ge=0, le=1)
    remedy_accuracy: float = Field(..., ge=0, le=1)
    overall_match_percentage: float = Field(..., ge=0, le=100)


class CaseValidationResultSchema(BaseSchema):
    case_id: str
    category: str
    actual_outcome: dict[str, Any]
    system_prediction: dict[str, Any]
    match_percentage: float = Field(..., ge=0, le=100)
    accuracy_metrics: AccuracyMetricsSchema
    passed: bool
    comparison_details: dict[str, Any]


class FailedCaseRecordSchema(BaseSchema):
    case_id: str
    category: str
    match_percentage: float
    failed_metrics: list[str]
    recorded_at: datetime
    case_snapshot: dict[str, Any]


class RetrainingRecommendationSchema(BaseSchema):
    recommendation_id: str
    target_module: str
    metric: str
    priority: str
    reason: str
    suggested_action: str


class ValidationReportSchema(BaseSchema):
    report_id: str
    generated_at: datetime
    dataset_version: str
    total_cases: int = Field(..., ge=0)
    passed_cases: int = Field(..., ge=0)
    failed_cases: int = Field(..., ge=0)
    category_summary: dict[str, Any]
    aggregate_metrics: AccuracyMetricsSchema
    case_results: list[CaseValidationResultSchema]
    failed_case_records: list[FailedCaseRecordSchema]
    retraining_recommendations: list[RetrainingRecommendationSchema]
    metadata: dict[str, object]
