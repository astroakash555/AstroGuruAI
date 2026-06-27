"""Case learning API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from backend.app.schemas.common import BaseSchema
from case_learning.serializers.schemas import (
    ConsultationCaseCreateSchema,
    ConsultationFromReportSchema,
    FollowUpCreateSchema,
)


class CaseRecordResponse(BaseSchema):
    recorded: bool | None = None
    updated: bool | None = None
    case: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CaseListResponse(BaseSchema):
    count: int
    cases: list[dict[str, Any]]
    metadata: dict[str, Any]


class LearningReportResponse(BaseSchema):
    report_id: str
    generated_at: str
    total_cases: int
    metrics: dict[str, Any]
    category_tracking: dict[str, Any]
    suggestions: list[dict[str, Any]]
    feedback_loops: list[dict[str, Any]]
    metadata: dict[str, Any]
