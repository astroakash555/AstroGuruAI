"""Rule approval workflow."""

from __future__ import annotations

from rule_studio.store.repository import RuleRepository
from rule_studio.types import ExpertRule


class ApprovalWorkflow:
    """Manage rule lifecycle: draft → review → approved → active."""

    def __init__(self, repository: RuleRepository) -> None:
        self._repository = repository

    def submit_for_review(self, rule_id: str, *, actor: str, notes: str = "") -> ExpertRule:
        rule = self._repository.get_rule(rule_id)
        if rule.status not in {"draft", "rejected"}:
            raise ValueError(f"Rule {rule_id} cannot be submitted from status {rule.status}")
        return self._repository.set_status(
            rule_id,
            status="pending_review",
            is_active=False,
            action="submit",
            actor=actor,
            notes=notes,
        )

    def approve(self, rule_id: str, *, actor: str, notes: str = "") -> ExpertRule:
        rule = self._repository.get_rule(rule_id)
        if rule.status != "pending_review":
            raise ValueError(f"Rule {rule_id} is not pending review")
        return self._repository.set_status(
            rule_id,
            status="approved",
            is_active=False,
            action="approve",
            actor=actor,
            notes=notes,
        )

    def reject(self, rule_id: str, *, actor: str, notes: str = "") -> ExpertRule:
        rule = self._repository.get_rule(rule_id)
        if rule.status != "pending_review":
            raise ValueError(f"Rule {rule_id} is not pending review")
        return self._repository.set_status(
            rule_id,
            status="rejected",
            is_active=False,
            action="reject",
            actor=actor,
            notes=notes,
        )

    def activate(self, rule_id: str, *, actor: str, notes: str = "") -> ExpertRule:
        rule = self._repository.get_rule(rule_id)
        if rule.status not in {"approved", "inactive"}:
            raise ValueError(f"Rule {rule_id} must be approved before activation")
        return self._repository.set_status(
            rule_id,
            status="active",
            is_active=True,
            action="activate",
            actor=actor,
            notes=notes,
        )

    def deactivate(self, rule_id: str, *, actor: str, notes: str = "") -> ExpertRule:
        rule = self._repository.get_rule(rule_id)
        if not rule.is_active:
            raise ValueError(f"Rule {rule_id} is not active")
        return self._repository.set_status(
            rule_id,
            status="inactive",
            is_active=False,
            action="deactivate",
            actor=actor,
            notes=notes,
        )
