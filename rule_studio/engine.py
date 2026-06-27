"""Rule studio orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rule_studio.performance.tracker import PerformanceTracker
from rule_studio.sandbox.tester import test_rule_in_sandbox
from rule_studio.serializers.serializer import rule_to_dict, sandbox_to_dict, to_json_dict
from rule_studio.store.repository import RuleRepository
from rule_studio.types import ExpertRule, RuleStudioReport
from rule_studio.validators.conflict_detector import detect_conflicts
from rule_studio.validators.schema_validator import validate_rule_payload
from rule_studio.workflow.approval import ApprovalWorkflow


class RuleStudioEngine:
    """
    Expert Rule Authoring Studio for AstroGuruAI.

    Manages custom astrology rules without coding — versioning, approval,
    conflict detection, sandbox testing, and performance tracking.
    Output is structured JSON only.
    """

    def __init__(self, root: Path | str | None = None) -> None:
        self._repository = RuleRepository(root)
        self._workflow = ApprovalWorkflow(self._repository)
        self._performance = PerformanceTracker(self._repository)

    @property
    def repository(self) -> RuleRepository:
        return self._repository

    def list_rules_json(
        self,
        *,
        system: str | None = None,
        status: str | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        rules = self._repository.list_rules(system=system, status=status, is_active=is_active)
        return {
            "count": len(rules),
            "rules": [rule_to_dict(rule) for rule in rules],
            "metadata": {"engine": "rule_studio_v1", "ai_prediction": False},
        }

    def get_rule_json(self, rule_id: str) -> dict[str, Any]:
        rule = self._repository.get_rule(rule_id)
        versions = self._repository.list_versions(rule_id)
        return {
            "rule": rule_to_dict(rule),
            "versions": [
                {
                    "version": item.version,
                    "changed_at": item.changed_at.isoformat(),
                    "changed_by": item.changed_by,
                }
                for item in versions
            ],
            "performance": self._performance.get_rule_performance(rule_id),
            "metadata": {"engine": "rule_studio_v1"},
        }

    def create_rule_json(self, payload: dict[str, Any], *, actor: str = "expert") -> dict[str, Any]:
        errors = validate_rule_payload(payload)
        if errors:
            return {"created": False, "validation_errors": list(errors), "metadata": {"engine": "rule_studio_v1"}}
        rule = self._repository.create_rule(payload, actor=actor)
        return {"created": True, "rule": rule_to_dict(rule), "metadata": {"engine": "rule_studio_v1"}}

    def update_rule_json(
        self,
        rule_id: str,
        payload: dict[str, Any],
        *,
        actor: str = "expert",
    ) -> dict[str, Any]:
        errors = validate_rule_payload(payload, partial=True)
        if errors:
            return {"updated": False, "validation_errors": list(errors), "metadata": {"engine": "rule_studio_v1"}}
        try:
            rule = self._repository.update_rule(rule_id, payload, actor=actor)
        except (KeyError, ValueError) as exc:
            return {"updated": False, "error": str(exc), "metadata": {"engine": "rule_studio_v1"}}
        return {"updated": True, "rule": rule_to_dict(rule), "metadata": {"engine": "rule_studio_v1"}}

    def submit_for_review_json(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._workflow_action("submit", rule_id, actor=actor, notes=notes)

    def approve_json(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._workflow_action("approve", rule_id, actor=actor, notes=notes)

    def reject_json(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._workflow_action("reject", rule_id, actor=actor, notes=notes)

    def activate_json(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._workflow_action("activate", rule_id, actor=actor, notes=notes)

    def deactivate_json(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._workflow_action("deactivate", rule_id, actor=actor, notes=notes)

    def detect_conflicts_json(self) -> dict[str, Any]:
        rules = self._repository.list_rules()
        conflicts = detect_conflicts(rules)
        return {
            "conflict_count": len(conflicts),
            "conflicts": [
                {
                    "rule_id_a": item.rule_id_a,
                    "rule_id_b": item.rule_id_b,
                    "conflict_type": item.conflict_type,
                    "overlap_score": item.overlap_score,
                    "details": item.details,
                }
                for item in conflicts
            ],
            "metadata": {"engine": "rule_studio_v1"},
        }

    def sandbox_test_json(
        self,
        rule_id: str,
        sample_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        rule = self._repository.get_rule(rule_id)
        result = test_rule_in_sandbox(rule, sample_context)
        performance = self._performance.run_and_track(rule, sample_context)
        return {
            "sandbox": sandbox_to_dict(result),
            "performance_run": performance,
            "metadata": {"engine": "rule_studio_v1"},
        }

    def studio_report_json(self) -> dict[str, Any]:
        rules = self._repository.list_rules()
        conflicts = detect_conflicts(rules)
        report = RuleStudioReport(
            generated_at=datetime.now(timezone.utc),
            total_rules=len(rules),
            active_rules=sum(1 for rule in rules if rule.is_active),
            pending_review=sum(1 for rule in rules if rule.status == "pending_review"),
            conflicts=conflicts,
            performance_summary={
                "tracked_rules": sum(1 for rule in rules if rule.performance_summary),
                "average_pass_rate": _average_pass_rate(rules),
            },
            metadata={"engine": "rule_studio_v1", "ai_prediction": False},
        )
        return to_json_dict(report)

    def get_manifest_json(self) -> dict[str, Any]:
        path = self._repository.root / "manifest.json"
        if not path.exists():
            return {"version": "1.0", "total_rules": 0}
        import json

        return json.loads(path.read_text(encoding="utf-8"))

    def _workflow_action(self, action: str, rule_id: str, *, actor: str, notes: str) -> dict[str, Any]:
        handlers = {
            "submit": self._workflow.submit_for_review,
            "approve": self._workflow.approve,
            "reject": self._workflow.reject,
            "activate": self._workflow.activate,
            "deactivate": self._workflow.deactivate,
        }
        try:
            rule = handlers[action](rule_id, actor=actor, notes=notes)
        except ValueError as exc:
            return {"success": False, "error": str(exc), "metadata": {"engine": "rule_studio_v1"}}
        return {"success": True, "rule": rule_to_dict(rule), "metadata": {"engine": "rule_studio_v1"}}


def _average_pass_rate(rules: tuple[ExpertRule, ...]) -> float:
    rates = [
        rule.performance_summary.get("pass_rate", 0.0)
        for rule in rules
        if rule.performance_summary
    ]
    if not rates:
        return 0.0
    return round(sum(rates) / len(rates), 4)
