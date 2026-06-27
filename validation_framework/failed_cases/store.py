"""Failed case storage."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from validation_framework.metrics.accuracy import failed_metric_names
from validation_framework.types import CaseValidationResult, FailedCaseRecord


class FailedCaseStore:
    """JSON-backed store for benchmark validation failures."""

    def __init__(self, storage_path: Path | str | None = None) -> None:
        self._path = Path(storage_path) if storage_path else None
        self._records: list[FailedCaseRecord] = []
        if self._path and self._path.exists():
            self._load()

    def record_failure(
        self,
        result: CaseValidationResult,
        *,
        case_snapshot: dict | None = None,
    ) -> FailedCaseRecord:
        record = FailedCaseRecord(
            case_id=result.case_id,
            category=result.category,
            match_percentage=result.match_percentage,
            failed_metrics=failed_metric_names(result.accuracy_metrics, threshold=0.4),
            recorded_at=datetime.now(timezone.utc),
            case_snapshot=case_snapshot or validation_snapshot(result),
        )
        self._records.append(record)
        self._persist()
        return record

    def all_failures(self) -> tuple[FailedCaseRecord, ...]:
        return tuple(self._records)

    def failures_by_category(self, category: str) -> tuple[FailedCaseRecord, ...]:
        return tuple(record for record in self._records if record.category == category)

    def _persist(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "case_id": record.case_id,
                "category": record.category,
                "match_percentage": record.match_percentage,
                "failed_metrics": list(record.failed_metrics),
                "recorded_at": record.recorded_at.isoformat(),
                "case_snapshot": record.case_snapshot,
            }
            for record in self._records
        ]
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._path:
            return
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        self._records = [
            FailedCaseRecord(
                case_id=item["case_id"],
                category=item["category"],
                match_percentage=item["match_percentage"],
                failed_metrics=tuple(item.get("failed_metrics", [])),
                recorded_at=datetime.fromisoformat(item["recorded_at"]),
                case_snapshot=item.get("case_snapshot", {}),
            )
            for item in raw
        ]


def validation_snapshot(result: CaseValidationResult) -> dict:
    return {
        "case_id": result.case_id,
        "category": result.category,
        "match_percentage": result.match_percentage,
        "actual_outcome": result.actual_outcome,
        "system_prediction": result.system_prediction,
        "comparison_details": result.comparison_details,
    }
