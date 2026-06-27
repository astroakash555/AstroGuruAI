"""Serialize rule studio objects to JSON."""

from __future__ import annotations

from typing import Any

from rule_studio.store.repository import _rule_to_dict
from rule_studio.types import ExpertRule, RuleStudioReport, SandboxTestResult


def rule_to_dict(rule: ExpertRule) -> dict[str, Any]:
    return _rule_to_dict(rule)


def sandbox_to_dict(result: SandboxTestResult) -> dict[str, Any]:
    return {
        "rule_id": result.rule_id,
        "passed": result.passed,
        "match_score": result.match_score,
        "matched_conditions": list(result.matched_conditions),
        "unmatched_conditions": list(result.unmatched_conditions),
        "sample_context": result.sample_context,
        "audit": list(result.audit),
    }


def to_json_dict(report: RuleStudioReport) -> dict[str, Any]:
    return {
        "generated_at": report.generated_at.isoformat(),
        "total_rules": report.total_rules,
        "active_rules": report.active_rules,
        "pending_review": report.pending_review,
        "conflicts": [
            {
                "rule_id_a": item.rule_id_a,
                "rule_id_b": item.rule_id_b,
                "conflict_type": item.conflict_type,
                "overlap_score": item.overlap_score,
                "details": item.details,
            }
            for item in report.conflicts
        ],
        "performance_summary": report.performance_summary,
        "metadata": dict(report.metadata),
    }
