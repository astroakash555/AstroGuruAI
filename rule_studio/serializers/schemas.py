"""Pydantic schemas for rule studio JSON."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RuleConditionsSchema(BaseSchema):
    planets: list[str] = Field(default_factory=list)
    houses: list[int] = Field(default_factory=list)
    signs: list[str] = Field(default_factory=list)
    nakshatras: list[str] = Field(default_factory=list)
    dasha_lords: list[str] = Field(default_factory=list)
    transits: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    remedy_type: str | None = None
    severity: str | None = None


class ExpertRuleSchema(BaseSchema):
    rule_id: str
    rule_name: str
    system: str
    description: str
    conditions: RuleConditionsSchema
    weight: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    outcome: str
    source_book: str
    notes: str = ""
    domain: str | None = None
    category: str | None = None
    version: int = Field(..., ge=1)
    status: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    approval_history: list[dict[str, Any]] = Field(default_factory=list)
    performance_summary: dict[str, Any] = Field(default_factory=dict)


class RuleCreateSchema(BaseSchema):
    rule_id: str | None = None
    rule_name: str
    system: str
    description: str
    conditions: RuleConditionsSchema
    weight: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    outcome: str
    source_book: str
    notes: str = ""
    domain: str | None = None
    category: str | None = None


class RuleUpdateSchema(BaseSchema):
    rule_name: str | None = None
    description: str | None = None
    conditions: RuleConditionsSchema | None = None
    weight: float | None = Field(default=None, ge=0, le=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    outcome: str | None = None
    source_book: str | None = None
    notes: str | None = None
    domain: str | None = None
    category: str | None = None


class WorkflowActionSchema(BaseSchema):
    actor: str = "expert"
    notes: str = ""


class SandboxTestRequestSchema(BaseSchema):
    sample_context: dict[str, Any] | None = None
