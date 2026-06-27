"""Rule studio typed models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ExpertRuleConditions:
    planets: tuple[str, ...] = ()
    houses: tuple[int, ...] = ()
    signs: tuple[str, ...] = ()
    nakshatras: tuple[str, ...] = ()
    dasha_lords: tuple[str, ...] = ()
    transits: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    remedy_type: str | None = None
    severity: str | None = None


@dataclass(frozen=True)
class ApprovalRecord:
    action: str
    actor: str
    recorded_at: datetime
    notes: str = ""


@dataclass(frozen=True)
class RulePerformanceRecord:
    rule_id: str
    run_id: str
    recorded_at: datetime
    match_score: float
    cases_tested: int
    cases_passed: int
    sandbox_score: float | None = None


@dataclass(frozen=True)
class ExpertRule:
    rule_id: str
    rule_name: str
    system: str
    description: str
    conditions: ExpertRuleConditions
    weight: float
    confidence: float
    outcome: str
    source_book: str
    notes: str
    domain: str | None = None
    category: str | None = None
    version: int = 1
    status: str = "draft"
    is_active: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    approval_history: tuple[ApprovalRecord, ...] = ()
    performance_summary: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuleVersionSnapshot:
    rule_id: str
    version: int
    snapshot: dict[str, Any]
    changed_at: datetime
    changed_by: str


@dataclass(frozen=True)
class RuleConflict:
    rule_id_a: str
    rule_id_b: str
    conflict_type: str
    overlap_score: float
    details: dict[str, Any]


@dataclass(frozen=True)
class SandboxTestResult:
    rule_id: str
    passed: bool
    match_score: float
    matched_conditions: tuple[str, ...]
    unmatched_conditions: tuple[str, ...]
    sample_context: dict[str, Any]
    audit: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class RuleStudioReport:
    generated_at: datetime
    total_rules: int
    active_rules: int
    pending_review: int
    conflicts: tuple[RuleConflict, ...]
    performance_summary: dict[str, Any]
    metadata: dict[str, object] = field(default_factory=dict)
