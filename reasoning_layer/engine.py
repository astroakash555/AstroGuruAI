"""Main reasoning orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from knowledge_brain import KnowledgeQuery, KnowledgeRegistry, KnowledgeSearchEngine
from reasoning_layer.audit.trail import collect_audit_trail, validate_audit_coverage
from reasoning_layer.engines.confidence import compute_confidence
from reasoning_layer.engines.consensus import analyze_consensus
from reasoning_layer.engines.contradiction import analyze_contradictions
from reasoning_layer.engines.root_cause import analyze_root_causes
from reasoning_layer.history.analyzer import analyze_client_history
from reasoning_layer.history.store import ClientHistoryStore
from reasoning_layer.serializers.serializer import to_json_dict, to_json_string
from reasoning_layer.synthesizers.system_signals import extract_system_signals
from reasoning_layer.types import ReasoningInput, ReasoningResult


class ReasoningEngine:
    """
    Professional astrology reasoning layer.

    Synthesizes multi-system evidence into root causes, contradictions,
    confidence scores, and consensus — structured JSON only.
    """

    def __init__(
        self,
        *,
        history_store: ClientHistoryStore | None = None,
        knowledge_registry: KnowledgeRegistry | None = None,
    ) -> None:
        self._history_store = history_store or ClientHistoryStore()
        self._knowledge_search = KnowledgeSearchEngine(knowledge_registry or KnowledgeRegistry())

    @property
    def history_store(self) -> ClientHistoryStore:
        return self._history_store

    def analyze(self, reasoning_input: ReasoningInput) -> ReasoningResult:
        enriched = self._enrich_with_knowledge(reasoning_input)
        domain = _resolve_domain(enriched)
        signals = extract_system_signals(enriched)

        root_causes = analyze_root_causes(enriched, signals)
        contradictions = analyze_contradictions(signals, domain)
        confidence = compute_confidence(signals, contradictions)
        consensus = analyze_consensus(signals)
        client_history = analyze_client_history(self._history_store, enriched.client_id)

        result = ReasoningResult(
            analyzed_at=datetime.now(timezone.utc),
            problem_domain=domain,
            root_causes=root_causes,
            contradictions=contradictions,
            confidence=confidence,
            consensus=consensus,
            client_history=client_history,
            audit_trail=(),
            metadata={
                "engine": "reasoning_layer_v1",
                "ai_prediction": False,
                "ai_storytelling": False,
                "system_signals": {
                    name: {"stance": signal.stance, "strength": signal.strength}
                    for name, signal in signals.items()
                },
                "audit_validation_errors": list(validate_audit_coverage(
                    ReasoningResult(
                        analyzed_at=datetime.now(timezone.utc),
                        problem_domain=domain,
                        root_causes=root_causes,
                        contradictions=contradictions,
                        confidence=confidence,
                        consensus=consensus,
                        client_history=client_history,
                        audit_trail=(),
                    )
                )),
            },
        )

        audit_trail = collect_audit_trail(result)
        return ReasoningResult(
            analyzed_at=result.analyzed_at,
            problem_domain=result.problem_domain,
            root_causes=result.root_causes,
            contradictions=result.contradictions,
            confidence=result.confidence,
            consensus=result.consensus,
            client_history=result.client_history,
            audit_trail=audit_trail,
            metadata={**result.metadata, "audit_entry_count": len(audit_trail)},
        )

    def analyze_json(self, reasoning_input: ReasoningInput) -> dict[str, Any]:
        return to_json_dict(self.analyze(reasoning_input))

    def analyze_json_string(self, reasoning_input: ReasoningInput, *, indent: int | None = 2) -> str:
        return to_json_string(self.analyze(reasoning_input), indent=indent)

    def record_report(
        self,
        *,
        client_id: str,
        problem_domain: str | None,
        problem_text: str | None,
        outcome: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self._history_store.add_record(
            client_id=client_id,
            record_type="report",
            problem_domain=problem_domain,
            problem_text=problem_text,
            outcome=outcome,
            payload=payload,
        )

    def _enrich_with_knowledge(self, reasoning_input: ReasoningInput) -> ReasoningInput:
        if reasoning_input.knowledge_search:
            return reasoning_input
        if not reasoning_input.problem_text:
            return reasoning_input

        planets = ()
        houses = ()
        if reasoning_input.astro_intelligence:
            planets = tuple(reasoning_input.astro_intelligence.get("root_cause_planets", []))
            houses = tuple(reasoning_input.astro_intelligence.get("affected_houses", []))

        kb_result = self._knowledge_search.search_json(
            KnowledgeQuery(
                problem_text=reasoning_input.problem_text,
                planets=planets,
                houses=houses,
                max_results=15,
            )
        )
        return ReasoningInput(
            kundali=reasoning_input.kundali,
            navamsha=reasoning_input.navamsha,
            dasha=reasoning_input.dasha,
            yogas=reasoning_input.yogas,
            doshas=reasoning_input.doshas,
            transits=reasoning_input.transits,
            problem_analysis=reasoning_input.problem_analysis,
            lal_kitab=reasoning_input.lal_kitab,
            kp_analysis=reasoning_input.kp_analysis,
            astro_intelligence=reasoning_input.astro_intelligence,
            knowledge_search=kb_result,
            client_id=reasoning_input.client_id,
            problem_text=reasoning_input.problem_text,
        )


def _resolve_domain(reasoning_input: ReasoningInput) -> str | None:
    if reasoning_input.problem_analysis:
        category = reasoning_input.problem_analysis.get("category", {}).get("category")
        if category and category != "unknown":
            return category
    if reasoning_input.knowledge_search:
        return reasoning_input.knowledge_search.get("summary", {}).get("inferred_domain")
    return None


def reasoning_input_from_unified_report(
    unified_report: dict[str, Any],
    *,
    client_id: str | None = None,
    problem_text: str | None = None,
) -> ReasoningInput:
    """Build reasoning input from a unified report JSON payload."""
    return ReasoningInput(
        kundali=unified_report["kundali"],
        navamsha=unified_report["navamsha"],
        dasha=unified_report["dasha"],
        yogas=unified_report["yogas"],
        doshas=unified_report["doshas"],
        transits=unified_report["transits"],
        problem_analysis=unified_report.get("problem_analysis"),
        lal_kitab=unified_report.get("lal_kitab"),
        kp_analysis=unified_report.get("kp_analysis"),
        astro_intelligence=unified_report.get("astro_intelligence"),
        client_id=client_id or unified_report.get("subject", {}).get("client_id"),
        problem_text=problem_text,
    )
