"""Pydantic schemas for KP JSON output."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CuspalPointSchema(BaseSchema):
    house: int = Field(..., ge=1, le=12)
    longitude: float
    sign: str
    star_lord: str
    sub_lord: str


class SignificatorSetSchema(BaseSchema):
    house: int = Field(..., ge=1, le=12)
    level_a: list[str]
    level_b: list[str]
    level_c: list[str]
    level_d: list[str]
    combined: list[str]


class StarLordAnalysisSchema(BaseSchema):
    planet: str
    longitude: float
    nakshatra: str
    star_lord: str
    house: int | None = Field(default=None, ge=1, le=12)


class SubLordAnalysisSchema(BaseSchema):
    planet: str
    longitude: float
    nakshatra: str
    star_lord: str
    sub_lord: str
    house: int | None = Field(default=None, ge=1, le=12)


class EventAnalysisSchema(BaseSchema):
    event_id: str
    event_type: str
    target_houses: list[int]
    is_supported: bool
    support_score: float = Field(..., ge=0, le=1)
    significators_matched: list[str]
    cusp_sub_lords_matched: list[str]
    evidence: list[str]


class KPAnalysisSummarySchema(BaseSchema):
    total_cusps: int = Field(..., ge=0)
    total_significator_sets: int = Field(..., ge=0)
    supported_events: int = Field(..., ge=0)
    total_events: int = Field(..., ge=0)


class KPAnalysisJSON(BaseSchema):
    analyzed_at: datetime
    lagna_sign: str
    cusps: list[CuspalPointSchema]
    significators: list[SignificatorSetSchema]
    star_lords: list[StarLordAnalysisSchema]
    sub_lords: list[SubLordAnalysisSchema]
    events: list[EventAnalysisSchema]
    summary: KPAnalysisSummarySchema
    metadata: dict[str, object]
