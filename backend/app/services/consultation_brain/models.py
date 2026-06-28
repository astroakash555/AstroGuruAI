"""Frozen dataclasses for consultation brain inputs and outputs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource, PipelineStage
from backend.app.services.consultation_brain.narrative_models import ConsultationNarrative


def _freeze_mapping(value: Mapping[str, Any] | dict[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, MappingProxyType):
        return value
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class ConsultationInput:
    """Inputs required to run the consultation brain pipeline."""

    unified_report: dict[str, Any]
    professional_report: dict[str, Any] | None = None
    problem_text: str | None = None
    language: str = "hi"
    reference_time: datetime | None = None


@dataclass(frozen=True)
class ConsultationEvidence:
    """Normalized astrological signal collected from one subsystem."""

    evidence_id: str
    source: EvidenceSource
    category: EvidenceCategory
    title: str
    summary: str
    weight: float
    confidence: float
    raw_reference: str = ""
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True)
class ConsultationEvidenceBundle:
    """Normalized evidence grouped by subsystem source."""

    yogas: tuple[ConsultationEvidence, ...] = ()
    dasha: tuple[ConsultationEvidence, ...] = ()
    transit: tuple[ConsultationEvidence, ...] = ()
    kp: tuple[ConsultationEvidence, ...] = ()
    lal_kitab: tuple[ConsultationEvidence, ...] = ()
    rule_studio: tuple[ConsultationEvidence, ...] = ()
    case_learning: tuple[ConsultationEvidence, ...] = ()
    fusion: tuple[ConsultationEvidence, ...] = ()
    golden_dataset: tuple[ConsultationEvidence, ...] = ()
    professional_report: tuple[ConsultationEvidence, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @property
    def evidence_count(self) -> int:
        return len(self.all_evidence)

    @property
    def all_evidence(self) -> tuple[ConsultationEvidence, ...]:
        return (
            self.yogas
            + self.dasha
            + self.transit
            + self.kp
            + self.lal_kitab
            + self.rule_studio
            + self.case_learning
            + self.fusion
            + self.golden_dataset
            + self.professional_report
        )


@dataclass(frozen=True)
class ConsultationConflictResolution:
    """Weighted resolution for a detected evidence conflict."""

    resolution_id: str
    conflict_type: str
    resolved_signal: ConsultationEvidence
    winning_sources: tuple[EvidenceSource, ...]
    losing_sources: tuple[EvidenceSource, ...]
    resolution_reason: str
    confidence: float
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConsultationConflict:
    """Contradictory evidence cluster and its resolution summary."""

    conflict_id: str
    evidence_ids: tuple[str, ...]
    description: str
    resolution: str
    resolved_confidence: float


@dataclass(frozen=True)
class ConsultationPriority:
    """Ranked focus area derived from weighted evidence."""

    rank: int
    domain: str
    title: str
    rationale: str
    confidence: float
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConsultationRecommendation:
    """Client-facing recommendation derived from ranked priorities."""

    recommendation_id: str
    title: str
    narrative: str
    priority_rank: int
    confidence: float
    evidence_ids: tuple[str, ...] = ()
    action_items: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConsultationBrainOutput:
    """Structured result of the full consultation brain pipeline."""

    generated_at: datetime
    stage_trace: tuple[PipelineStage, ...]
    evidence: tuple[ConsultationEvidence, ...]
    conflicts: tuple[ConsultationConflict, ...]
    priorities: tuple[ConsultationPriority, ...]
    recommendations: tuple[ConsultationRecommendation, ...]
    overall_confidence: float
    executive_summary: str
    narrative: ConsultationNarrative | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))
