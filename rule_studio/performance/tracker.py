"""Rule performance tracking."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from rule_studio.constants import PERFORMANCE_TRACKING_WINDOW
from rule_studio.sandbox.tester import test_rule_in_sandbox
from rule_studio.store.repository import RuleRepository
from rule_studio.types import ExpertRule, RulePerformanceRecord


class PerformanceTracker:
    """Track sandbox and benchmark performance for authored rules."""

    def __init__(
        self,
        repository: RuleRepository,
        storage_path: Path | str | None = None,
    ) -> None:
        self._repository = repository
        self._path = Path(storage_path) if storage_path else repository.root / "performance" / "records.json"
        self._records: list[RulePerformanceRecord] = []
        if self._path.exists():
            self._load()

    def record_sandbox_run(
        self,
        rule: ExpertRule,
        *,
        match_score: float,
        passed: bool,
    ) -> RulePerformanceRecord:
        record = RulePerformanceRecord(
            rule_id=rule.rule_id,
            run_id=str(uuid4()),
            recorded_at=datetime.now(timezone.utc),
            match_score=match_score,
            cases_tested=1,
            cases_passed=1 if passed else 0,
            sandbox_score=match_score,
        )
        self._records.append(record)
        self._persist()
        self._update_rule_summary(rule.rule_id)
        return record

    def run_and_track(
        self,
        rule: ExpertRule,
        sample_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result = test_rule_in_sandbox(rule, sample_context)
        record = self.record_sandbox_run(
            rule,
            match_score=result.match_score,
            passed=result.passed,
        )
        return {
            "run_id": record.run_id,
            "match_score": result.match_score,
            "passed": result.passed,
            "matched_conditions": list(result.matched_conditions),
            "unmatched_conditions": list(result.unmatched_conditions),
        }

    def get_rule_performance(self, rule_id: str) -> dict[str, Any]:
        records = [record for record in self._records if record.rule_id == rule_id][
            -PERFORMANCE_TRACKING_WINDOW:
        ]
        if not records:
            return {"rule_id": rule_id, "runs": 0, "average_match_score": 0.0, "pass_rate": 0.0}

        avg_score = sum(record.match_score for record in records) / len(records)
        pass_rate = sum(record.cases_passed for record in records) / sum(
            record.cases_tested for record in records
        )
        return {
            "rule_id": rule_id,
            "runs": len(records),
            "average_match_score": round(avg_score, 4),
            "pass_rate": round(pass_rate, 4),
            "last_run_at": records[-1].recorded_at.isoformat(),
        }

    def _update_rule_summary(self, rule_id: str) -> None:
        summary = self.get_rule_performance(rule_id)
        self._repository.update_performance(rule_id, summary)

    def _persist(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "rule_id": record.rule_id,
                "run_id": record.run_id,
                "recorded_at": record.recorded_at.isoformat(),
                "match_score": record.match_score,
                "cases_tested": record.cases_tested,
                "cases_passed": record.cases_passed,
                "sandbox_score": record.sandbox_score,
            }
            for record in self._records[-500:]
        ]
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load(self) -> None:
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        self._records = [
            RulePerformanceRecord(
                rule_id=item["rule_id"],
                run_id=item["run_id"],
                recorded_at=datetime.fromisoformat(item["recorded_at"]),
                match_score=item["match_score"],
                cases_tested=item["cases_tested"],
                cases_passed=item["cases_passed"],
                sandbox_score=item.get("sandbox_score"),
            )
            for item in raw
        ]
