"""Multi-agent consultation orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from knowledge_brain import KnowledgeQuery, KnowledgeRegistry, KnowledgeSearchEngine
from consultation_layer.agents.kp import analyze_kp
from consultation_layer.agents.lal_kitab import analyze_lal_kitab
from consultation_layer.agents.problem_specialist import analyze_problem
from consultation_layer.agents.self_review import review_consultation
from consultation_layer.agents.senior_guru import synthesize_conclusion
from consultation_layer.agents.vedic import analyze_vedic
from consultation_layer.serializers.serializer import to_json_dict, to_json_string
from consultation_layer.types import ConsultationInput, ConsultationResult
from reasoning_layer.history.store import ClientHistoryStore
from reasoning_layer.types import AuditEntry


class ConsultationEngine:
    """
    Multi-agent senior astrologer consultation system.

    Coordinates specialist agents, senior guru synthesis, and self-review.
    Output is structured JSON only — no marketing text or unsupported claims.
    """

    def __init__(
        self,
        history_store: ClientHistoryStore | None = None,
        knowledge_registry: KnowledgeRegistry | None = None,
    ) -> None:
        self._history_store = history_store or ClientHistoryStore()
        self._knowledge_search = KnowledgeSearchEngine(knowledge_registry or KnowledgeRegistry())

    def consult(self, consultation_input: ConsultationInput) -> ConsultationResult:
        problem_text = consultation_input.problem_text
        report = self._enrich_report(consultation_input.unified_report, problem_text)

        specialists = (
            analyze_vedic(report),
            analyze_kp(report),
            analyze_lal_kitab(report),
            analyze_problem(report, problem_text),
        )

        senior_guru = synthesize_conclusion(specialists, report)
        self_review = review_consultation(specialists, senior_guru)

        audit_trail = _collect_audit(specialists, senior_guru, self_review)

        result = ConsultationResult(
            consultation_id=str(uuid4()),
            analyzed_at=datetime.now(timezone.utc),
            problem_text=problem_text,
            specialist_agents=specialists,
            senior_guru=senior_guru,
            self_review=self_review,
            audit_trail=audit_trail,
            metadata={
                "engine": "consultation_layer_v1",
                "ai_prediction": False,
                "marketing_text": False,
                "agent_count": len(specialists) + 2,
                "review_score": self_review.review_score,
            },
        )

        if consultation_input.client_id:
            self._history_store.add_record(
                client_id=consultation_input.client_id,
                record_type="consultation",
                problem_domain=senior_guru.final_conclusion.get("problem_domain"),
                problem_text=problem_text,
                outcome=senior_guru.final_conclusion.get("consensus_outcome"),
                payload={
                    "consultation_id": result.consultation_id,
                    "review_score": self_review.review_score,
                },
            )

        return result

    def consult_json(self, consultation_input: ConsultationInput) -> dict[str, Any]:
        return to_json_dict(self.consult(consultation_input))

    def consult_json_string(
        self,
        consultation_input: ConsultationInput,
        *,
        indent: int | None = 2,
    ) -> str:
        return to_json_string(self.consult(consultation_input), indent=indent)

    def _enrich_report(
        self,
        report: dict[str, Any],
        problem_text: str | None,
    ) -> dict[str, Any]:
        if report.get("knowledge_search") or not problem_text:
            return report

        intelligence = report.get("astro_intelligence", {})
        kb_result = self._knowledge_search.search_json(
            KnowledgeQuery(
                problem_text=problem_text,
                planets=tuple(intelligence.get("root_cause_planets", [])),
                houses=tuple(intelligence.get("affected_houses", [])),
                max_results=15,
            )
        )
        enriched = dict(report)
        enriched["knowledge_search"] = kb_result
        return enriched


def consultation_input_from_unified_report(
    unified_report: dict[str, Any],
    *,
    problem_text: str | None = None,
    client_id: str | None = None,
) -> ConsultationInput:
    """Build consultation input from unified report JSON."""
    subject = unified_report.get("subject", {})
    return ConsultationInput(
        unified_report=unified_report,
        problem_text=problem_text,
        client_id=client_id or subject.get("client_id"),
    )


def _collect_audit(specialists, senior_guru, self_review) -> tuple[AuditEntry, ...]:
    entries: list[AuditEntry] = []
    for agent in specialists:
        entries.extend(agent.audit)
    entries.extend(senior_guru.audit)
    entries.extend(self_review.audit)

    seen: set[tuple[str, str, str, str | None]] = set()
    unique: list[AuditEntry] = []
    for entry in entries:
        key = (entry.rule_source, entry.engine_source, entry.reason_used, entry.reference_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append(entry)
    return tuple(unique)
