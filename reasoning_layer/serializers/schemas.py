"""Pydantic schemas for reasoning layer JSON output."""

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


class RootCauseFindingSchema(BaseSchema):
    cause_type: str
    primary_factor: str
    triggering_planet: str | None = None
    supporting_planet: str | None = None
    dasha_influence: dict[str, Any]
    transit_influence: dict[str, Any]
    severity: float = Field(..., ge=0, le=1)
    audit: list[AuditEntrySchema]


class ContradictionFindingSchema(BaseSchema):
    topic: str
    supporting_evidence: list[dict[str, Any]]
    opposing_evidence: list[dict[str, Any]]
    confidence_score: float = Field(..., ge=0, le=100)
    audit: list[AuditEntrySchema]


class ConfidenceBreakdownSchema(BaseSchema):
    vedic_agreement: float = Field(..., ge=0, le=1)
    kp_agreement: float = Field(..., ge=0, le=1)
    lal_kitab_agreement: float = Field(..., ge=0, le=1)
    dasha_agreement: float = Field(..., ge=0, le=1)
    transit_agreement: float = Field(..., ge=0, le=1)
    overall_score: int = Field(..., ge=0, le=100)


class ConsensusResultSchema(BaseSchema):
    agreement_areas: list[str]
    disagreement_areas: list[str]
    final_consensus: str
    system_stances: dict[str, str]
    audit: list[AuditEntrySchema]


class ClientHistoryInsightSchema(BaseSchema):
    repeated_problems: list[str]
    remedy_effectiveness: list[dict[str, Any]]
    detected_patterns: list[dict[str, Any]]
    consultation_count: int = Field(..., ge=0)
    report_count: int = Field(..., ge=0)


class ReasoningJSON(BaseSchema):
    analyzed_at: datetime
    problem_domain: str | None = None
    root_causes: list[RootCauseFindingSchema]
    contradictions: list[ContradictionFindingSchema]
    confidence: ConfidenceBreakdownSchema
    consensus: ConsensusResultSchema
    client_history: ClientHistoryInsightSchema | None = None
    audit_trail: list[AuditEntrySchema]
    metadata: dict[str, object]
