"""Pydantic schemas for yoga detection JSON output."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class YogaConditionSchema(BaseSchema):
    name: str
    met: bool
    detail: str


class YogaDetectionSchema(BaseSchema):
    yoga_id: str
    yoga_name: str
    category: str
    is_present: bool
    strength: float = Field(..., ge=0, le=1)
    description: str
    planets_involved: list[str]
    houses_involved: list[int]
    conditions: list[YogaConditionSchema]
    evidence: list[str]


class YogaSummarySchema(BaseSchema):
    total_rules: int
    present_count: int
    absent_count: int
    average_strength: float


class YogaDetectionJSON(BaseSchema):
    """Top-level JSON output for yoga detection."""

    detected_at: datetime
    lagna_sign: str
    moon_sign: str
    yogas: list[YogaDetectionSchema]
    present_yogas: list[YogaDetectionSchema]
    summary: YogaSummarySchema
    metadata: dict[str, object]
