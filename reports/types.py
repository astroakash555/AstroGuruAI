"""Typed models for unified report orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from astrology_engine.core.base import BirthData


@dataclass(frozen=True)
class ReportInput:
    """Input for generating a unified astrology report."""

    birth_data: BirthData
    birth_place: str
    problem_text: str | None = None
    client_id: str | None = None
    locale: str = "en"
    target_date: date | None = None
    reference_datetime: datetime | None = None
    include_problem_analysis: bool = True


@dataclass(frozen=True)
class ReportSummary:
    """Cross-section summary for quick report overview."""

    lagna_sign: str
    moon_sign: str
    moon_nakshatra: str
    present_yogas_count: int
    present_doshas_count: int
    highest_dosha_severity: str | None
    current_mahadasha: str | None
    current_antardasha: str | None
    problem_category: str | None
    problem_severity: str | None
    lal_kitab_findings_count: int = 0
    kp_supported_events: int = 0
    intelligence_severity_score: float | None = None
    recommended_remedies_count: int = 0
    reasoning_confidence_score: int | None = None


@dataclass(frozen=True)
class UnifiedReportResult:
    """Complete unified report before JSON serialization."""

    generated_at: datetime
    subject: dict[str, Any]
    kundali: dict[str, Any]
    navamsha: dict[str, Any]
    dasha: dict[str, Any]
    yogas: dict[str, Any]
    doshas: dict[str, Any]
    transits: dict[str, Any]
    problem_analysis: dict[str, Any] | None
    lal_kitab: dict[str, Any]
    kp_analysis: dict[str, Any]
    astro_intelligence: dict[str, Any]
    remedy_recommendations: dict[str, Any]
    vedic: dict[str, Any]
    kp: dict[str, Any]
    lal_kitab_intelligence: dict[str, Any]
    fusion: dict[str, Any]
    summary: ReportSummary
    metadata: dict[str, Any] = field(default_factory=dict)
