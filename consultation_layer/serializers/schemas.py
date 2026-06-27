"""Pydantic schemas for consultation JSON output."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AuditEntrySchema(BaseSchema):
    rule_source: str
    engine_source: str
    reason_used: str
    reference_id: str | None = None


class AgentFindingSchema(BaseSchema):
    agent_id: str
    agent_role: str
    findings: dict[str, Any]
    evidence: list[str]
    confidence: float = Field(..., ge=0, le=1)
    audit: list[AuditEntrySchema]


class SeniorGuruConclusionSchema(BaseSchema):
    compared_findings: dict[str, Any]
    resolved_conflicts: list[dict[str, Any]]
    strongest_causes: list[dict[str, Any]]
    strongest_remedies: list[dict[str, Any]]
    final_conclusion: dict[str, Any]
    audit: list[AuditEntrySchema]


class SelfReviewResultSchema(BaseSchema):
    contradictions_found: list[dict[str, Any]]
    missing_evidence: list[str]
    weak_remedies: list[dict[str, Any]]
    unsupported_conclusions: list[str]
    review_score: int = Field(..., ge=0, le=100)
    audit: list[AuditEntrySchema]


class ConsultationJSON(BaseSchema):
    consultation_id: str
    analyzed_at: datetime
    problem_text: str | None = None
    specialist_agents: list[AgentFindingSchema]
    senior_guru: SeniorGuruConclusionSchema
    self_review: SelfReviewResultSchema
    audit_trail: list[AuditEntrySchema]
    metadata: dict[str, object]
