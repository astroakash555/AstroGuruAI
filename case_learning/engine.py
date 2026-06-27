"""Case learning orchestrator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from case_learning.analyzers.feedback import build_feedback_loops
from case_learning.analyzers.suggestions import generate_suggestions
from case_learning.metrics.calculator import compute_metrics
from case_learning.reports.generator import generate_learning_report
from case_learning.serializers.serializer import case_to_dict, learning_report_to_dict, metrics_to_dict
from case_learning.store.repository import CaseRepository


class CaseLearningEngine:
    """
    Case Learning Engine for AstroGuruAI.

    Learns from real client consultations, measures accuracy,
    suggests rule improvements, and generates learning reports.
    Output is structured JSON only.
    """

    def __init__(self, root: Path | str | None = None) -> None:
        self._repository = CaseRepository(root)

    @property
    def repository(self) -> CaseRepository:
        return self._repository

    def record_consultation_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            case = self._repository.create_case(payload)
        except ValueError as exc:
            return {"recorded": False, "error": str(exc), "metadata": {"engine": "case_learning_v1"}}
        return {"recorded": True, "case": case_to_dict(case), "metadata": {"engine": "case_learning_v1"}}

    def add_follow_up_json(self, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            case = self._repository.add_follow_up(case_id, payload)
        except KeyError as exc:
            return {"updated": False, "error": str(exc), "metadata": {"engine": "case_learning_v1"}}
        return {"updated": True, "case": case_to_dict(case), "metadata": {"engine": "case_learning_v1"}}

    def get_case_json(self, case_id: str) -> dict[str, Any]:
        case = self._repository.get_case(case_id)
        return {"case": case_to_dict(case), "metadata": {"engine": "case_learning_v1"}}

    def list_cases_json(self, *, category: str | None = None) -> dict[str, Any]:
        cases = self._repository.list_cases(category=category)
        return {
            "count": len(cases),
            "cases": [case_to_dict(case) for case in cases],
            "metadata": {"engine": "case_learning_v1"},
        }

    def learning_report_json(self, *, category: str | None = None) -> dict[str, Any]:
        cases = self._repository.list_cases(category=category)
        metrics = compute_metrics(cases)
        suggestions = generate_suggestions(cases)
        feedback_loops = build_feedback_loops(metrics, suggestions)
        report = generate_learning_report(
            cases=cases,
            metrics=metrics,
            suggestions=suggestions,
            feedback_loops=feedback_loops,
        )
        return learning_report_to_dict(report)

    def metrics_json(self, *, category: str | None = None) -> dict[str, Any]:
        cases = self._repository.list_cases(category=category)
        metrics = compute_metrics(cases)
        return {
            "metrics": metrics_to_dict(metrics),
            "metadata": {"engine": "case_learning_v1", "ai_prediction": False},
        }

    def suggestions_json(self, *, category: str | None = None) -> dict[str, Any]:
        cases = self._repository.list_cases(category=category)
        suggestions = generate_suggestions(cases)
        return {
            "count": len(suggestions),
            "suggestions": [
                {
                    "suggestion_id": item.suggestion_id,
                    "suggestion_type": item.suggestion_type,
                    "rule_id": item.rule_id,
                    "category": item.category,
                    "priority": item.priority,
                    "reason": item.reason,
                    "suggested_action": item.suggested_action,
                    "evidence": item.evidence,
                }
                for item in suggestions
            ],
            "metadata": {"engine": "case_learning_v1"},
        }

    def feedback_loops_json(self, *, category: str | None = None) -> dict[str, Any]:
        cases = self._repository.list_cases(category=category)
        metrics = compute_metrics(cases)
        suggestions = generate_suggestions(cases)
        loops = build_feedback_loops(metrics, suggestions)
        return {
            "count": len(loops),
            "feedback_loops": [
                {
                    "loop_id": loop.loop_id,
                    "category": loop.category,
                    "trigger": loop.trigger,
                    "metrics_snapshot": loop.metrics_snapshot,
                    "target_module": loop.target_module,
                    "suggestion_count": len(loop.suggestions),
                    "suggestions": [
                        {
                            "suggestion_type": item.suggestion_type,
                            "rule_id": item.rule_id,
                            "priority": item.priority,
                            "suggested_action": item.suggested_action,
                        }
                        for item in loop.suggestions
                    ],
                }
                for loop in loops
            ],
            "metadata": {"engine": "case_learning_v1"},
        }

    def manifest_json(self) -> dict[str, Any]:
        import json

        path = self._repository.root / "manifest.json"
        if not path.exists():
            return {"version": "1.0", "total_cases": 0}
        return json.loads(path.read_text(encoding="utf-8"))

    def record_from_consultation(
        self,
        *,
        client_id: str,
        category: str,
        problem_text: str,
        unified_report: dict[str, Any],
        applied_rules: tuple[str, ...] = (),
        applied_remedies: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        """Record a case from an existing consultation/unified report."""
        reasoning = unified_report.get("reasoning", {})
        consultation = unified_report.get("consultation", {})
        predicted = (
            reasoning.get("consensus", {}).get("final_consensus")
            or consultation.get("senior_guru", {}).get("final_conclusion", {}).get("consensus_outcome")
            or "unknown"
        )
        system_prediction = {
            "planets": unified_report.get("astro_intelligence", {}).get("root_cause_planets", []),
            "houses": unified_report.get("astro_intelligence", {}).get("affected_houses", []),
            "consensus_outcome": predicted,
            "confidence_score": reasoning.get("confidence", {}).get("overall_score"),
        }
        payload = {
            "client_id": client_id,
            "category": category,
            "problem_text": problem_text,
            "kundali_snapshot": unified_report.get("kundali", {}),
            "system_prediction": system_prediction,
            "applied_rules": list(applied_rules),
            "applied_remedies": list(applied_remedies),
            "predicted_outcome": predicted,
            "final_outcome": "pending",
        }
        return self.record_consultation_json(payload)
