"""Pydantic schema for unified report JSON output."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ReportSummarySchema(BaseSchema):
    lagna_sign: str
    moon_sign: str
    moon_nakshatra: str
    present_yogas_count: int = Field(..., ge=0)
    present_doshas_count: int = Field(..., ge=0)
    highest_dosha_severity: str | None = None
    current_mahadasha: str | None = None
    current_antardasha: str | None = None
    problem_category: str | None = None
    problem_severity: str | None = None
    lal_kitab_findings_count: int = Field(default=0, ge=0)
    kp_supported_events: int = Field(default=0, ge=0)
    intelligence_severity_score: float | None = Field(default=None, ge=0, le=1)
    recommended_remedies_count: int = Field(default=0, ge=0)
    reasoning_confidence_score: int | None = Field(default=None, ge=0, le=100)


class UnifiedReportJSON(BaseSchema):
    """Top-level unified report contract."""

    generated_at: datetime
    version: str = "unified_report_v2"
    subject: dict[str, Any]
    kundali: dict[str, Any]
    navamsha: dict[str, Any]
    dasha: dict[str, Any]
    yogas: dict[str, Any]
    doshas: dict[str, Any]
    transits: dict[str, Any]
    problem_analysis: dict[str, Any] | None = None
    lal_kitab: dict[str, Any]
    kp_analysis: dict[str, Any]
    astro_intelligence: dict[str, Any]
    remedy_recommendations: dict[str, Any]
    vedic: dict[str, Any]
    kp: dict[str, Any]
    lal_kitab_intelligence: dict[str, Any]
    fusion: dict[str, Any]
    summary: ReportSummarySchema
    metadata: dict[str, Any]
