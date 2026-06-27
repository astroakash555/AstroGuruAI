"""Pydantic schemas for Astro Intelligence JSON output."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PlanetaryConflictSchema(BaseSchema):
    planets: list[str]
    conflict_type: str
    severity: float = Field(..., ge=0, le=1)
    evidence: list[str]


class RankedCauseSchema(BaseSchema):
    planet: str
    severity: float = Field(..., ge=0, le=1)
    reasons: list[str]


class RecommendedRemedySchema(BaseSchema):
    remedy_id: str
    remedy_name: str
    astrology_system: str
    match_score: float = Field(..., ge=0, le=1)
    match_reasons: list[str]
    priority: int = Field(..., ge=1)


class AstroIntelligenceJSON(BaseSchema):
    analyzed_at: datetime
    root_cause_planets: list[str]
    supportive_planets: list[str]
    affected_houses: list[int]
    planetary_conflicts: list[PlanetaryConflictSchema]
    severity_score: float = Field(..., ge=0, le=1)
    recommended_remedies: list[RecommendedRemedySchema | dict[str, Any]]
    confidence_score: float = Field(..., ge=0, le=1)
    ranked_causes: list[RankedCauseSchema]
    metadata: dict[str, object]
