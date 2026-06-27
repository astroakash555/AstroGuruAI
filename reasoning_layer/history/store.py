"""Client history storage."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from reasoning_layer.types import ClientHistoryRecord


class ClientHistoryStore:
    """JSON-backed store for client reports, remedies, and consultations."""

    def __init__(self, storage_path: Path | str | None = None) -> None:
        self._path = Path(storage_path) if storage_path else None
        self._records: list[ClientHistoryRecord] = []
        if self._path and self._path.exists():
            self._load()

    def add_record(
        self,
        *,
        client_id: str,
        record_type: str,
        problem_domain: str | None = None,
        problem_text: str | None = None,
        remedies_applied: tuple[str, ...] = (),
        outcome: str | None = None,
        payload: dict[str, Any] | None = None,
        recorded_at: datetime | None = None,
    ) -> ClientHistoryRecord:
        record = ClientHistoryRecord(
            record_id=str(uuid4()),
            client_id=client_id,
            recorded_at=recorded_at or datetime.now(timezone.utc),
            record_type=record_type,
            problem_domain=problem_domain,
            problem_text=problem_text,
            remedies_applied=remedies_applied,
            outcome=outcome,
            payload=payload or {},
        )
        self._records.append(record)
        self._persist()
        return record

    def records_for_client(self, client_id: str) -> tuple[ClientHistoryRecord, ...]:
        return tuple(record for record in self._records if record.client_id == client_id)

    def reports_for_client(self, client_id: str) -> tuple[ClientHistoryRecord, ...]:
        return tuple(
            record
            for record in self.records_for_client(client_id)
            if record.record_type == "report"
        )

    def remedies_for_client(self, client_id: str) -> tuple[ClientHistoryRecord, ...]:
        return tuple(
            record
            for record in self.records_for_client(client_id)
            if record.record_type == "remedy"
        )

    def consultations_for_client(self, client_id: str) -> tuple[ClientHistoryRecord, ...]:
        return tuple(
            record
            for record in self.records_for_client(client_id)
            if record.record_type == "consultation"
        )

    def _persist(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "record_id": record.record_id,
                "client_id": record.client_id,
                "recorded_at": record.recorded_at.isoformat(),
                "record_type": record.record_type,
                "problem_domain": record.problem_domain,
                "problem_text": record.problem_text,
                "remedies_applied": list(record.remedies_applied),
                "outcome": record.outcome,
                "payload": record.payload,
            }
            for record in self._records
        ]
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._path:
            return
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        self._records = [
            ClientHistoryRecord(
                record_id=item["record_id"],
                client_id=item["client_id"],
                recorded_at=datetime.fromisoformat(item["recorded_at"]),
                record_type=item["record_type"],
                problem_domain=item.get("problem_domain"),
                problem_text=item.get("problem_text"),
                remedies_applied=tuple(item.get("remedies_applied", [])),
                outcome=item.get("outcome"),
                payload=item.get("payload", {}),
            )
            for item in raw
        ]
