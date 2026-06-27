"""Reasoning layer typed models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class AuditEntry:
    """Traceable source for every reasoning conclusion."""

    rule_source: str
    engine_source: str
    reason_used: str
    reference_id: str | None = None


@dataclass(frozen=True)
class SystemSignal:
    """Normalized signal from one astrology system."""

    system: str
    stance: str
    strength: float
    factors: tuple[str, ...]
    audit: tuple[AuditEntry, ...]


@dataclass(frozen=True)
class RootCauseFinding:
    cause_type: str
    primary_factor: str
    triggering_planet: str | None
    supporting_planet: str | None
    dasha_influence: dict[str, Any]
    transit_influence: dict[str, Any]
    severity: float
    audit: tuple[AuditEntry, ...]


@dataclass(frozen=True)
class ContradictionFinding:
    topic: str
    supporting_evidence: tuple[dict[str, Any], ...]
    opposing_evidence: tuple[dict[str, Any], ...]
    confidence_score: float
    audit: tuple[AuditEntry, ...]


@dataclass(frozen=True)
class ConfidenceBreakdown:
    vedic_agreement: float
    kp_agreement: float
    lal_kitab_agreement: float
    dasha_agreement: float
    transit_agreement: float
    overall_score: int


@dataclass(frozen=True)
class ConsensusResult:
    agreement_areas: tuple[str, ...]
    disagreement_areas: tuple[str, ...]
    final_consensus: str
    system_stances: dict[str, str]
    audit: tuple[AuditEntry, ...]


@dataclass(frozen=True)
class ClientHistoryRecord:
    record_id: str
    client_id: str
    recorded_at: datetime
    record_type: str
    problem_domain: str | None
    problem_text: str | None
    remedies_applied: tuple[str, ...]
    outcome: str | None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ClientHistoryInsight:
    repeated_problems: tuple[str, ...]
    remedy_effectiveness: tuple[dict[str, Any], ...]
    detected_patterns: tuple[dict[str, Any], ...]
    consultation_count: int
    report_count: int


@dataclass(frozen=True)
class ReasoningInput:
    """Structured input assembled from unified report sections."""

    kundali: dict[str, Any]
    navamsha: dict[str, Any]
    dasha: dict[str, Any]
    yogas: dict[str, Any]
    doshas: dict[str, Any]
    transits: dict[str, Any]
    problem_analysis: dict[str, Any] | None = None
    lal_kitab: dict[str, Any] | None = None
    kp_analysis: dict[str, Any] | None = None
    astro_intelligence: dict[str, Any] | None = None
    knowledge_search: dict[str, Any] | None = None
    client_id: str | None = None
    problem_text: str | None = None


@dataclass(frozen=True)
class ReasoningResult:
    analyzed_at: datetime
    problem_domain: str | None
    root_causes: tuple[RootCauseFinding, ...]
    contradictions: tuple[ContradictionFinding, ...]
    confidence: ConfidenceBreakdown
    consensus: ConsensusResult
    client_history: ClientHistoryInsight | None
    audit_trail: tuple[AuditEntry, ...]
    metadata: dict[str, object] = field(default_factory=dict)
