"""Pydantic schemas for case learning JSON."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class FollowUpCreateSchema(BaseSchema):
    outcome_type: str
    description: str = ""
    remedy_effectiveness: str | None = None
    notes: str = ""
    final_outcome: str | None = None


class ConsultationCaseCreateSchema(BaseSchema):
    case_id: str | None = None
    client_id: str
    category: str
    problem_text: str
    kundali_snapshot: dict[str, Any] = Field(default_factory=dict)
    system_prediction: dict[str, Any] = Field(default_factory=dict)
    applied_rules: list[str] = Field(default_factory=list)
    applied_remedies: list[str] = Field(default_factory=list)
    predicted_outcome: str
    final_outcome: str = "pending"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConsultationFromReportSchema(BaseSchema):
    client_id: str
    category: str
    problem_text: str
    unified_report: dict[str, Any]
    applied_rules: list[str] = Field(default_factory=list)
    applied_remedies: list[str] = Field(default_factory=list)
