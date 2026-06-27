"""Pydantic schemas for fused intelligence sections in unified reports."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FusionRootCauseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    explanation: str
    supporting_observations: list[str] = Field(default_factory=list)
    supporting_engines: list[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class FusionConflictSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conflict_id: str
    title: str
    explanation: str
    engines: list[str] = Field(default_factory=list)
    observation_ids: list[str] = Field(default_factory=list)
    affected_planets: list[str] = Field(default_factory=list)
    affected_houses: list[int] = Field(default_factory=list)
    severity_spread: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)


class FusionRecommendationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: str
    title: str
    explanation: str
    priority: str
    supporting_root_causes: list[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class FusionReportSchema(BaseModel):
    """Fusion engine output embedded in unified reports."""

    model_config = ConfigDict(from_attributes=True)

    analyzed_at: str
    root_causes: list[FusionRootCauseSchema] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    conflicts: list[FusionConflictSchema] = Field(default_factory=list)
    recommendations: list[FusionRecommendationSchema] = Field(default_factory=list)
    observations: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
