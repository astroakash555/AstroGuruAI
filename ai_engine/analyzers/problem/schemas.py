"""Pydantic schemas for problem analysis JSON output."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CategoryMatchSchema(BaseSchema):
    category: str
    label: str
    confidence: float = Field(..., ge=0, le=1)


class HouseMappingSchema(BaseSchema):
    primary: list[int]
    secondary: list[int]
    supporting: list[int]
    all_houses: list[int]


class PlanetMappingSchema(BaseSchema):
    primary: list[str]
    secondary: list[str]
    shadow: list[str]
    all_planets: list[str]


class SeveritySchema(BaseSchema):
    score: float = Field(..., ge=0, le=1)
    level: str
    signals: list[str]


class RootCauseIndicatorSchema(BaseSchema):
    indicator: str
    relevance: float = Field(..., ge=0, le=1)
    source: str


class ProblemAnalysisJSON(BaseSchema):
    """Structured JSON output for AI-ready problem context analysis."""

    original_text: str
    normalized_text: str
    category: CategoryMatchSchema
    alternative_categories: list[CategoryMatchSchema]
    houses: HouseMappingSchema
    planets: PlanetMappingSchema
    severity: SeveritySchema
    root_cause_indicators: list[RootCauseIndicatorSchema]
    analysis_notes: list[str]
    metadata: dict[str, object]
