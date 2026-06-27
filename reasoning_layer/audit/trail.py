"""Audit trail aggregation engine."""

from __future__ import annotations

from reasoning_layer.types import (
    AuditEntry,
    ConsensusResult,
    ContradictionFinding,
    ReasoningResult,
    RootCauseFinding,
)


def collect_audit_trail(result: ReasoningResult) -> tuple[AuditEntry, ...]:
    """Ensure every conclusion has traceable audit entries."""
    entries: list[AuditEntry] = []

    for finding in result.root_causes:
        entries.extend(finding.audit)

    for contradiction in result.contradictions:
        entries.extend(contradiction.audit)

    entries.extend(result.consensus.audit)

    entries.extend(result.audit_trail)

    return _deduplicate(entries)


def validate_audit_coverage(result: ReasoningResult) -> tuple[str, ...]:
    """Return validation errors when conclusions lack audit metadata."""
    errors: list[str] = []

    if result.root_causes and not any(finding.audit for finding in result.root_causes):
        errors.append("root_causes_missing_audit")

    if result.contradictions and not any(item.audit for item in result.contradictions):
        errors.append("contradictions_missing_audit")

    if not result.consensus.audit:
        errors.append("consensus_missing_audit")

    for entry in collect_audit_trail(result):
        if not entry.rule_source or not entry.engine_source or not entry.reason_used:
            errors.append("incomplete_audit_entry")

    return tuple(dict.fromkeys(errors))


def _deduplicate(entries: list[AuditEntry]) -> tuple[AuditEntry, ...]:
    seen: set[tuple[str, str, str, str | None]] = set()
    unique: list[AuditEntry] = []
    for entry in entries:
        key = (entry.rule_source, entry.engine_source, entry.reason_used, entry.reference_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append(entry)
    return tuple(unique)
