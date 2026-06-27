"""Consultation layer typed models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from reasoning_layer.types import AuditEntry


@dataclass(frozen=True)
class AgentFinding:
    agent_id: str
    agent_role: str
    findings: dict[str, Any]
    evidence: tuple[str, ...]
    confidence: float
    audit: tuple[AuditEntry, ...]


@dataclass(frozen=True)
class SeniorGuruConclusion:
    compared_findings: dict[str, Any]
    resolved_conflicts: tuple[dict[str, Any], ...]
    strongest_causes: tuple[dict[str, Any], ...]
    strongest_remedies: tuple[dict[str, Any], ...]
    final_conclusion: dict[str, Any]
    audit: tuple[AuditEntry, ...]


@dataclass(frozen=True)
class SelfReviewResult:
    contradictions_found: tuple[dict[str, Any], ...]
    missing_evidence: tuple[str, ...]
    weak_remedies: tuple[dict[str, Any], ...]
    unsupported_conclusions: tuple[str, ...]
    review_score: int
    audit: tuple[AuditEntry, ...]


@dataclass(frozen=True)
class ConsultationInput:
    unified_report: dict[str, Any]
    problem_text: str | None = None
    client_id: str | None = None


@dataclass(frozen=True)
class ConsultationResult:
    consultation_id: str
    analyzed_at: datetime
    problem_text: str | None
    specialist_agents: tuple[AgentFinding, ...]
    senior_guru: SeniorGuruConclusion
    self_review: SelfReviewResult
    audit_trail: tuple[AuditEntry, ...]
    metadata: dict[str, object] = field(default_factory=dict)
