"""Pydantic schemas for Lal Kitab JSON output."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LalKitabConditionSchema(BaseSchema):
    name: str
    met: bool
    detail: str


class LalKitabFindingSchema(BaseSchema):
    finding_id: str
    finding_name: str
    category: str
    is_present: bool
    strength: float = Field(..., ge=0, le=1)
    description: str
    planets_involved: list[str]
    houses_involved: list[int]
    conditions: list[LalKitabConditionSchema]
    evidence: list[str]
    recommendation_ids: list[str]


class PlanetHouseAnalysisSchema(BaseSchema):
    planet: str
    house: int
    sign: str
    effect_code: str
    strength: float = Field(..., ge=0, le=1)
    conditions: list[LalKitabConditionSchema]
    evidence: list[str]


class LalKitabSummarySchema(BaseSchema):
    total_rules: int = Field(..., ge=0)
    present_count: int = Field(..., ge=0)
    absent_count: int = Field(..., ge=0)
    average_strength: float = Field(..., ge=0, le=1)
    rin_count: int = Field(..., ge=0)
    dosh_count: int = Field(..., ge=0)


class LalKitabAnalysisJSON(BaseSchema):
    analyzed_at: datetime
    lagna_sign: str
    planet_by_house: list[PlanetHouseAnalysisSchema]
    rin_findings: list[LalKitabFindingSchema]
    dosh_findings: list[LalKitabFindingSchema]
    recommendations: list[LalKitabFindingSchema]
    summary: LalKitabSummarySchema
    metadata: dict[str, object]
