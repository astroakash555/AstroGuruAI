"""Case learning service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from case_learning import CaseLearningEngine


class CaseLearningService:
    """Service layer for case learning APIs."""

    def __init__(self, *, data_root: str | None = None) -> None:
        root = Path(data_root) if data_root else None
        self._engine = CaseLearningEngine(root)

    def record_consultation(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._engine.record_consultation_json(payload)

    def record_from_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._engine.record_from_consultation(
            client_id=payload["client_id"],
            category=payload["category"],
            problem_text=payload["problem_text"],
            unified_report=payload["unified_report"],
            applied_rules=tuple(payload.get("applied_rules", [])),
            applied_remedies=tuple(payload.get("applied_remedies", [])),
        )

    def add_follow_up(self, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._engine.add_follow_up_json(case_id, payload)

    def get_case(self, case_id: str) -> dict[str, Any]:
        return self._engine.get_case_json(case_id)

    def list_cases(self, *, category: str | None = None) -> dict[str, Any]:
        return self._engine.list_cases_json(category=category)

    def learning_report(self, *, category: str | None = None) -> dict[str, Any]:
        return self._engine.learning_report_json(category=category)

    def metrics(self, *, category: str | None = None) -> dict[str, Any]:
        return self._engine.metrics_json(category=category)

    def suggestions(self, *, category: str | None = None) -> dict[str, Any]:
        return self._engine.suggestions_json(category=category)

    def feedback_loops(self, *, category: str | None = None) -> dict[str, Any]:
        return self._engine.feedback_loops_json(category=category)

    def manifest(self) -> dict[str, Any]:
        return self._engine.manifest_json()
