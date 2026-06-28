"""Typed models for the professional report engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReportLanguage(str, Enum):
    """Supported client report languages."""

    HINDI = "hi"
    ENGLISH = "en"
    HINGLISH = "hinglish"


@dataclass(frozen=True)
class ReportSection:
    """One structured report section derived from engine output."""

    section_id: str
    title: str
    narrative: str
    facts: dict[str, Any]
    confidence: float


@dataclass(frozen=True)
class ProfessionalReportInput:
    """Input for building a professional client report."""

    unified_report: dict[str, Any]
    remedy_generation: dict[str, Any] = field(default_factory=dict)
    problem_text: str | None = None
    language: ReportLanguage = ReportLanguage.HINDI


@dataclass(frozen=True)
class ProfessionalReportResult:
    """Structured professional report before serialization."""

    sections: tuple[ReportSection, ...]
    language: ReportLanguage
    overall_confidence: float
