"""Typed models for the professional report engine."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any

from backend.app.services.consultation_brain.models import ConsultationBrainOutput
from backend.app.services.consultation_brain.master_consultation_models import MasterConsultation


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
    consultation_brain_output: ConsultationBrainOutput | None = None
    master_consultation: MasterConsultation | None = None


def _freeze_mapping(value: Mapping[str, Any] | dict[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, MappingProxyType):
        return value
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class ProfessionalReportResult:
    """Structured professional report before serialization."""

    sections: tuple[ReportSection, ...]
    language: ReportLanguage
    overall_confidence: float
    delivery_metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "delivery_metadata", _freeze_mapping(self.delivery_metadata))
