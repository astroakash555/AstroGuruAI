"""Pydantic schemas for dosha detection JSON output."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DoshaConditionSchema(BaseSchema):
    name: str
    met: bool
    detail: str


class DoshaDetectionSchema(BaseSchema):
    dosha_id: str
    dosha_name: str
    category: str
    is_present: bool
    severity: float = Field(..., ge=0, le=1)
    severity_level: str
    subtype: str | None = None
    description: str
    planets_involved: list[str]
    houses_involved: list[int]
    conditions: list[DoshaConditionSchema]
    mitigating_factors: list[str]
    evidence: list[str]


class DoshaSummarySchema(BaseSchema):
    total_rules: int
    present_count: int
    absent_count: int
    average_severity: float
    highest_severity: float


class DoshaDetectionJSON(BaseSchema):
    """Top-level JSON output for dosha detection."""

    detected_at: datetime
    lagna_sign: str
    moon_sign: str
    doshas: list[DoshaDetectionSchema]
    present_doshas: list[DoshaDetectionSchema]
    summary: DoshaSummarySchema
    metadata: dict[str, object]
