"""Rule studio API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from backend.app.schemas.common import BaseSchema
from rule_studio.serializers.schemas import (
    RuleCreateSchema,
    RuleUpdateSchema,
    SandboxTestRequestSchema,
    WorkflowActionSchema,
)


class RuleListResponse(BaseSchema):
    count: int
    rules: list[dict[str, Any]]
    metadata: dict[str, Any]


class RuleDetailResponse(BaseSchema):
    rule: dict[str, Any]
    versions: list[dict[str, Any]]
    performance: dict[str, Any]
    metadata: dict[str, Any]


class RuleMutationResponse(BaseSchema):
    created: bool | None = None
    updated: bool | None = None
    success: bool | None = None
    rule: dict[str, Any] | None = None
    validation_errors: list[str] = Field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConflictListResponse(BaseSchema):
    conflict_count: int
    conflicts: list[dict[str, Any]]
    metadata: dict[str, Any]


class SandboxTestResponse(BaseSchema):
    sandbox: dict[str, Any]
    performance_run: dict[str, Any]
    metadata: dict[str, Any]


class StudioReportResponse(BaseSchema):
    generated_at: str
    total_rules: int
    active_rules: int
    pending_review: int
    conflicts: list[dict[str, Any]]
    performance_summary: dict[str, Any]
    metadata: dict[str, Any]
