"""Typed models for the AI consultation brain."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ConsultationSection:
    """Structured consultation narrative for one life domain."""

    section_id: str
    title: str
    current_situation: str
    root_cause: str
    positive_factors: tuple[str, ...]
    challenges: tuple[str, ...]
    timeline: str
    actionable_advice: tuple[str, ...]
    confidence: float
    supporting_observation_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConsultationPriorityItem:
    """Ranked priority derived from fused intelligence."""

    rank: int
    title: str
    explanation: str
    domain: str
    confidence: float


@dataclass(frozen=True)
class ConsultationStrengthItem:
    """Ranked strength indicator from fused intelligence."""

    rank: int
    title: str
    explanation: str
    confidence: float
    supporting_engines: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConsultationRiskItem:
    """Ranked risk indicator from fused intelligence."""

    rank: int
    title: str
    explanation: str
    severity: float
    confidence: float
    has_conflict: bool = False


@dataclass(frozen=True)
class ConsultationResult:
    """Complete consultation brain output."""

    generated_at: datetime
    executive_summary: str
    sections: tuple[ConsultationSection, ...]
    priorities: tuple[ConsultationPriorityItem, ...]
    strengths: tuple[ConsultationStrengthItem, ...]
    risks: tuple[ConsultationRiskItem, ...]
    overall_confidence: float
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class DomainConsultationConfig:
    """Configuration for mapping fusion evidence to a consultation section."""

    section_id: str
    title: str
    keywords: tuple[str, ...]
    primary_planets: tuple[str, ...]
    target_houses: tuple[int, ...]
    timeline_hint: str = "Active dasha and transit cycles modulate timing over the coming months."


def consultation_section_to_dict(section: ConsultationSection) -> dict[str, Any]:
    """Serialize one consultation section to JSON-compatible dict."""
    payload = asdict(section)
    return payload


def consultation_result_to_dict(result: ConsultationResult) -> dict[str, Any]:
    """Serialize consultation brain output to JSON-compatible dict."""
    return {
        "generated_at": result.generated_at.isoformat(),
        "executive_summary": result.executive_summary,
        "sections": [consultation_section_to_dict(section) for section in result.sections],
        "priorities": [asdict(item) for item in result.priorities],
        "strengths": [asdict(item) for item in result.strengths],
        "risks": [asdict(item) for item in result.risks],
        "overall_confidence": result.overall_confidence,
        "metadata": dict(result.metadata),
    }
