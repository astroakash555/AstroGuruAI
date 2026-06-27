"""Expert rule repository with versioning."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from rule_studio.constants import RULE_STATUSES, RULE_SYSTEMS
from rule_studio.types import ApprovalRecord, ExpertRule, ExpertRuleConditions, RuleVersionSnapshot


class RuleRepository:
    """JSON-backed store for expert-authored rules."""

    def __init__(self, root: Path | str | None = None) -> None:
        self._root = Path(root or Path(__file__).resolve().parents[2] / "rule_studio_data")
        self._rules_dir = self._root / "rules"
        self._versions_dir = self._root / "versions"
        self._rules_dir.mkdir(parents=True, exist_ok=True)
        self._versions_dir.mkdir(parents=True, exist_ok=True)
        if not (self._root / "manifest.json").exists():
            self._write_manifest()

    @property
    def root(self) -> Path:
        return self._root

    def list_rules(
        self,
        *,
        system: str | None = None,
        status: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[ExpertRule, ...]:
        rules: list[ExpertRule] = []
        for path in sorted(self._rules_dir.glob("*.json")):
            rule = self._load_rule_file(path)
            if system and rule.system != system:
                continue
            if status and rule.status != status:
                continue
            if is_active is not None and rule.is_active != is_active:
                continue
            rules.append(rule)
        return tuple(rules)

    def get_rule(self, rule_id: str) -> ExpertRule:
        path = self._rules_dir / f"{rule_id}.json"
        if not path.exists():
            raise KeyError(f"Rule not found: {rule_id}")
        return self._load_rule_file(path)

    def create_rule(self, payload: dict[str, Any], *, actor: str = "expert") -> ExpertRule:
        rule_id = payload.get("rule_id") or f"{payload['system']}_{uuid4().hex[:8]}"
        if (self._rules_dir / f"{rule_id}.json").exists():
            raise ValueError(f"Rule already exists: {rule_id}")

        now = datetime.now(timezone.utc)
        rule = _rule_from_dict(
            {
                **payload,
                "rule_id": rule_id,
                "version": 1,
                "status": payload.get("status", "draft"),
                "is_active": False,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "approval_history": [],
                "performance_summary": {},
            }
        )
        self._save_rule(rule)
        self._save_version_snapshot(rule, changed_by=actor)
        self._write_manifest()
        return rule

    def update_rule(
        self,
        rule_id: str,
        payload: dict[str, Any],
        *,
        actor: str = "expert",
    ) -> ExpertRule:
        existing = self.get_rule(rule_id)
        if existing.status == "active":
            raise ValueError("Active rules must be deactivated before editing.")

        now = datetime.now(timezone.utc)
        merged = _rule_to_dict(existing)
        merged.update(payload)
        merged["rule_id"] = rule_id
        merged["version"] = existing.version + 1
        merged["updated_at"] = now.isoformat()
        merged["status"] = payload.get("status", "draft")
        merged["is_active"] = False

        rule = _rule_from_dict(merged)
        self._save_rule(rule)
        self._save_version_snapshot(rule, changed_by=actor)
        self._write_manifest()
        return rule

    def set_status(
        self,
        rule_id: str,
        *,
        status: str,
        is_active: bool,
        action: str,
        actor: str,
        notes: str = "",
    ) -> ExpertRule:
        if status not in RULE_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        rule = self.get_rule(rule_id)
        now = datetime.now(timezone.utc)
        history = list(rule.approval_history)
        history.append(
            ApprovalRecord(action=action, actor=actor, recorded_at=now, notes=notes)
        )

        updated = ExpertRule(
            rule_id=rule.rule_id,
            rule_name=rule.rule_name,
            system=rule.system,
            description=rule.description,
            conditions=rule.conditions,
            weight=rule.weight,
            confidence=rule.confidence,
            outcome=rule.outcome,
            source_book=rule.source_book,
            notes=rule.notes,
            domain=rule.domain,
            category=rule.category,
            version=rule.version,
            status=status,
            is_active=is_active,
            created_at=rule.created_at,
            updated_at=now,
            approval_history=tuple(history),
            performance_summary=rule.performance_summary,
        )
        self._save_rule(updated)
        self._write_manifest()
        return updated

    def list_versions(self, rule_id: str) -> tuple[RuleVersionSnapshot, ...]:
        path = self._versions_dir / f"{rule_id}.json"
        if not path.exists():
            return ()
        raw = json.loads(path.read_text(encoding="utf-8"))
        return tuple(
            RuleVersionSnapshot(
                rule_id=rule_id,
                version=item["version"],
                snapshot=item["snapshot"],
                changed_at=datetime.fromisoformat(item["changed_at"]),
                changed_by=item["changed_by"],
            )
            for item in raw
        )

    def update_performance(self, rule_id: str, performance: dict[str, Any]) -> ExpertRule:
        rule = self.get_rule(rule_id)
        updated = ExpertRule(
            rule_id=rule.rule_id,
            rule_name=rule.rule_name,
            system=rule.system,
            description=rule.description,
            conditions=rule.conditions,
            weight=rule.weight,
            confidence=rule.confidence,
            outcome=rule.outcome,
            source_book=rule.source_book,
            notes=rule.notes,
            domain=rule.domain,
            category=rule.category,
            version=rule.version,
            status=rule.status,
            is_active=rule.is_active,
            created_at=rule.created_at,
            updated_at=datetime.now(timezone.utc),
            approval_history=rule.approval_history,
            performance_summary=performance,
        )
        self._save_rule(updated)
        return updated

    def _save_rule(self, rule: ExpertRule) -> None:
        path = self._rules_dir / f"{rule.rule_id}.json"
        path.write_text(json.dumps(_rule_to_dict(rule), indent=2), encoding="utf-8")

    def _save_version_snapshot(self, rule: ExpertRule, *, changed_by: str) -> None:
        path = self._versions_dir / f"{rule.rule_id}.json"
        existing: list[dict[str, Any]] = []
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
        existing.append(
            {
                "version": rule.version,
                "snapshot": _rule_to_dict(rule),
                "changed_at": (rule.updated_at or datetime.now(timezone.utc)).isoformat(),
                "changed_by": changed_by,
            }
        )
        path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    def _load_rule_file(self, path: Path) -> ExpertRule:
        return _rule_from_dict(json.loads(path.read_text(encoding="utf-8")))

    def _write_manifest(self) -> None:
        rules = self.list_rules()
        manifest = {
            "version": "1.0",
            "name": "AstroGuruAI Rule Studio",
            "total_rules": len(rules),
            "active_rules": sum(1 for rule in rules if rule.is_active),
            "systems": {system: sum(1 for rule in rules if rule.system == system) for system in RULE_SYSTEMS},
            "status_counts": {
                status: sum(1 for rule in rules if rule.status == status) for status in RULE_STATUSES
            },
        }
        (self._root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _rule_from_dict(data: dict[str, Any]) -> ExpertRule:
    conditions_data = data.get("conditions", {})
    history = tuple(
        ApprovalRecord(
            action=item["action"],
            actor=item["actor"],
            recorded_at=datetime.fromisoformat(item["recorded_at"]),
            notes=item.get("notes", ""),
        )
        for item in data.get("approval_history", [])
    )
    return ExpertRule(
        rule_id=data["rule_id"],
        rule_name=data["rule_name"],
        system=data["system"],
        description=data.get("description", ""),
        conditions=ExpertRuleConditions(
            planets=tuple(conditions_data.get("planets", [])),
            houses=tuple(conditions_data.get("houses", [])),
            signs=tuple(conditions_data.get("signs", [])),
            nakshatras=tuple(conditions_data.get("nakshatras", [])),
            dasha_lords=tuple(conditions_data.get("dasha_lords", [])),
            transits=tuple(conditions_data.get("transits", [])),
            tags=tuple(conditions_data.get("tags", [])),
            remedy_type=conditions_data.get("remedy_type"),
            severity=conditions_data.get("severity"),
        ),
        weight=float(data.get("weight", 0.5)),
        confidence=float(data.get("confidence", 0.5)),
        outcome=data.get("outcome", ""),
        source_book=data.get("source_book", ""),
        notes=data.get("notes", ""),
        domain=data.get("domain"),
        category=data.get("category"),
        version=int(data.get("version", 1)),
        status=data.get("status", "draft"),
        is_active=bool(data.get("is_active", False)),
        created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        approval_history=history,
        performance_summary=data.get("performance_summary", {}),
    )


def _rule_to_dict(rule: ExpertRule) -> dict[str, Any]:
    return {
        "rule_id": rule.rule_id,
        "rule_name": rule.rule_name,
        "system": rule.system,
        "description": rule.description,
        "conditions": {
            "planets": list(rule.conditions.planets),
            "houses": list(rule.conditions.houses),
            "signs": list(rule.conditions.signs),
            "nakshatras": list(rule.conditions.nakshatras),
            "dasha_lords": list(rule.conditions.dasha_lords),
            "transits": list(rule.conditions.transits),
            "tags": list(rule.conditions.tags),
            "remedy_type": rule.conditions.remedy_type,
            "severity": rule.conditions.severity,
        },
        "weight": rule.weight,
        "confidence": rule.confidence,
        "outcome": rule.outcome,
        "source_book": rule.source_book,
        "notes": rule.notes,
        "domain": rule.domain,
        "category": rule.category,
        "version": rule.version,
        "status": rule.status,
        "is_active": rule.is_active,
        "created_at": rule.created_at.isoformat() if rule.created_at else None,
        "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
        "approval_history": [
            {
                "action": item.action,
                "actor": item.actor,
                "recorded_at": item.recorded_at.isoformat(),
                "notes": item.notes,
            }
            for item in rule.approval_history
        ],
        "performance_summary": rule.performance_summary,
    }
