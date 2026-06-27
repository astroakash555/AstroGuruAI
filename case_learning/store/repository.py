"""Consultation case repository."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from case_learning.constants import TRACKED_CATEGORIES
from case_learning.types import ConsultationCase, FollowUpResult


class CaseRepository:
    """JSON-backed store for real client consultation learning cases."""

    def __init__(self, root: Path | str | None = None) -> None:
        self._root = Path(root or Path(__file__).resolve().parents[2] / "case_learning_data")
        self._cases_dir = self._root / "cases"
        self._cases_dir.mkdir(parents=True, exist_ok=True)
        if not (self._root / "manifest.json").exists():
            self._write_manifest()

    @property
    def root(self) -> Path:
        return self._root

    def list_cases(self, *, category: str | None = None) -> tuple[ConsultationCase, ...]:
        cases: list[ConsultationCase] = []
        for path in sorted(self._cases_dir.glob("*.json")):
            case = self._load_file(path)
            if category and case.category != category:
                continue
            cases.append(case)
        return tuple(cases)

    def get_case(self, case_id: str) -> ConsultationCase:
        path = self._cases_dir / f"{case_id}.json"
        if not path.exists():
            raise KeyError(f"Case not found: {case_id}")
        return self._load_file(path)

    def create_case(self, payload: dict[str, Any]) -> ConsultationCase:
        case_id = payload.get("case_id") or f"case_{uuid4().hex[:10]}"
        if (self._cases_dir / f"{case_id}.json").exists():
            raise ValueError(f"Case already exists: {case_id}")

        category = payload.get("category", "general")
        if category not in TRACKED_CATEGORIES:
            raise ValueError(f"Unsupported category: {category}")

        now = datetime.now(timezone.utc)
        case = _case_from_dict(
            {
                **payload,
                "case_id": case_id,
                "recorded_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "follow_up_results": payload.get("follow_up_results", []),
            }
        )
        self._save(case)
        self._write_manifest()
        return case

    def add_follow_up(self, case_id: str, payload: dict[str, Any]) -> ConsultationCase:
        case = self.get_case(case_id)
        now = datetime.now(timezone.utc)
        follow_up = FollowUpResult(
            follow_up_id=payload.get("follow_up_id") or str(uuid4()),
            recorded_at=now,
            outcome_type=payload["outcome_type"],
            description=payload.get("description", ""),
            remedy_effectiveness=payload.get("remedy_effectiveness"),
            notes=payload.get("notes", ""),
        )
        updated = ConsultationCase(
            case_id=case.case_id,
            client_id=case.client_id,
            category=case.category,
            problem_text=case.problem_text,
            kundali_snapshot=case.kundali_snapshot,
            system_prediction=case.system_prediction,
            applied_rules=case.applied_rules,
            applied_remedies=case.applied_remedies,
            predicted_outcome=case.predicted_outcome,
            final_outcome=payload.get("final_outcome", case.final_outcome),
            follow_up_results=case.follow_up_results + (follow_up,),
            recorded_at=case.recorded_at,
            updated_at=now,
            metadata=case.metadata,
        )
        self._save(updated)
        return updated

    def update_final_outcome(self, case_id: str, final_outcome: str) -> ConsultationCase:
        case = self.get_case(case_id)
        updated = ConsultationCase(
            case_id=case.case_id,
            client_id=case.client_id,
            category=case.category,
            problem_text=case.problem_text,
            kundali_snapshot=case.kundali_snapshot,
            system_prediction=case.system_prediction,
            applied_rules=case.applied_rules,
            applied_remedies=case.applied_remedies,
            predicted_outcome=case.predicted_outcome,
            final_outcome=final_outcome,
            follow_up_results=case.follow_up_results,
            recorded_at=case.recorded_at,
            updated_at=datetime.now(timezone.utc),
            metadata=case.metadata,
        )
        self._save(updated)
        return updated

    def _save(self, case: ConsultationCase) -> None:
        path = self._cases_dir / f"{case.case_id}.json"
        path.write_text(json.dumps(_case_to_dict(case), indent=2), encoding="utf-8")

    def _load_file(self, path: Path) -> ConsultationCase:
        return _case_from_dict(json.loads(path.read_text(encoding="utf-8")))

    def _write_manifest(self) -> None:
        cases = self.list_cases()
        manifest = {
            "version": "1.0",
            "name": "AstroGuruAI Case Learning",
            "total_cases": len(cases),
            "categories": {
                category: sum(1 for case in cases if case.category == category)
                for category in TRACKED_CATEGORIES
            },
        }
        (self._root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _case_from_dict(data: dict[str, Any]) -> ConsultationCase:
    follow_ups = tuple(
        FollowUpResult(
            follow_up_id=item["follow_up_id"],
            recorded_at=datetime.fromisoformat(item["recorded_at"]),
            outcome_type=item["outcome_type"],
            description=item.get("description", ""),
            remedy_effectiveness=item.get("remedy_effectiveness"),
            notes=item.get("notes", ""),
        )
        for item in data.get("follow_up_results", [])
    )
    return ConsultationCase(
        case_id=data["case_id"],
        client_id=data["client_id"],
        category=data["category"],
        problem_text=data["problem_text"],
        kundali_snapshot=data.get("kundali_snapshot", {}),
        system_prediction=data.get("system_prediction", {}),
        applied_rules=tuple(data.get("applied_rules", [])),
        applied_remedies=tuple(data.get("applied_remedies", [])),
        predicted_outcome=data.get("predicted_outcome", ""),
        final_outcome=data.get("final_outcome", ""),
        follow_up_results=follow_ups,
        recorded_at=datetime.fromisoformat(data["recorded_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
        metadata=data.get("metadata", {}),
    )


def _case_to_dict(case: ConsultationCase) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "client_id": case.client_id,
        "category": case.category,
        "problem_text": case.problem_text,
        "kundali_snapshot": case.kundali_snapshot,
        "system_prediction": case.system_prediction,
        "applied_rules": list(case.applied_rules),
        "applied_remedies": list(case.applied_remedies),
        "predicted_outcome": case.predicted_outcome,
        "final_outcome": case.final_outcome,
        "follow_up_results": [
            {
                "follow_up_id": item.follow_up_id,
                "recorded_at": item.recorded_at.isoformat(),
                "outcome_type": item.outcome_type,
                "description": item.description,
                "remedy_effectiveness": item.remedy_effectiveness,
                "notes": item.notes,
            }
            for item in case.follow_up_results
        ],
        "recorded_at": case.recorded_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
        "metadata": case.metadata,
    }
