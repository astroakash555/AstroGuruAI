"""Rule studio service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rule_studio import RuleStudioEngine


class RuleStudioService:
    """Service layer for expert rule authoring APIs."""

    def __init__(self, *, data_root: str | None = None) -> None:
        root = Path(data_root) if data_root else None
        self._engine = RuleStudioEngine(root)

    def list_rules(
        self,
        *,
        system: str | None = None,
        status: str | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        return self._engine.list_rules_json(system=system, status=status, is_active=is_active)

    def get_rule(self, rule_id: str) -> dict[str, Any]:
        return self._engine.get_rule_json(rule_id)

    def create_rule(self, payload: dict[str, Any], *, actor: str = "expert") -> dict[str, Any]:
        return self._engine.create_rule_json(payload, actor=actor)

    def update_rule(
        self,
        rule_id: str,
        payload: dict[str, Any],
        *,
        actor: str = "expert",
    ) -> dict[str, Any]:
        return self._engine.update_rule_json(rule_id, payload, actor=actor)

    def submit_for_review(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._engine.submit_for_review_json(rule_id, actor=actor, notes=notes)

    def approve(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._engine.approve_json(rule_id, actor=actor, notes=notes)

    def reject(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._engine.reject_json(rule_id, actor=actor, notes=notes)

    def activate(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._engine.activate_json(rule_id, actor=actor, notes=notes)

    def deactivate(self, rule_id: str, *, actor: str, notes: str = "") -> dict[str, Any]:
        return self._engine.deactivate_json(rule_id, actor=actor, notes=notes)

    def detect_conflicts(self) -> dict[str, Any]:
        return self._engine.detect_conflicts_json()

    def sandbox_test(
        self,
        rule_id: str,
        sample_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._engine.sandbox_test_json(rule_id, sample_context)

    def studio_report(self) -> dict[str, Any]:
        return self._engine.studio_report_json()

    def manifest(self) -> dict[str, Any]:
        return self._engine.get_manifest_json()
