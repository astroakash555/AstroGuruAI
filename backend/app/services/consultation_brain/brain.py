"""Main orchestrator for the consultation brain foundation pipeline."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.app.services.consultation_brain.confidence import compute_overall_confidence
from backend.app.services.consultation_brain.config import ConsultationBrainConfig
from backend.app.services.consultation_brain.conflict_engine import ConflictEngine
from backend.app.services.consultation_brain.constants import ENGINE_VERSION, PipelineStage
from backend.app.services.consultation_brain.models import (
    ConsultationBrainOutput,
    ConsultationEvidence,
    ConsultationEvidenceBundle,
    ConsultationInput,
)
from backend.app.services.consultation_brain.priority_engine import PriorityEngine, to_legacy_priorities
from backend.app.services.consultation_brain.protocols import Clock, EvidenceProvider
from backend.app.services.consultation_brain.collectors import EvidenceCollector, provider_sources
from backend.app.services.consultation_brain.reasoning import normalize_evidence
from backend.app.services.consultation_brain.recommendation_engine import RecommendationEngine, to_legacy_recommendations
from backend.app.services.consultation_brain.narrative_engine import NarrativeEngine
from backend.app.services.consultation_brain.serializers import consultation_brain_output_to_dict


class ConsultationBrain:
    """Foundation orchestrator wiring evidence through recommendation stages."""

    ENGINE_VERSION = ENGINE_VERSION

    def __init__(
        self,
        *,
        evidence_providers: Sequence[EvidenceProvider] | None = None,
        clock: Clock | None = None,
        config: ConsultationBrainConfig | None = None,
        evidence_collector: EvidenceCollector | None = None,
        conflict_engine: ConflictEngine | None = None,
        priority_engine: PriorityEngine | None = None,
        recommendation_engine: RecommendationEngine | None = None,
        narrative_engine: NarrativeEngine | None = None,
    ) -> None:
        resolved = config or ConsultationBrainConfig()
        self._evidence_providers: tuple[EvidenceProvider, ...] = tuple(
            evidence_providers if evidence_providers is not None else resolved.evidence_providers
        )
        self._clock: Clock = clock if clock is not None else resolved.clock
        self._evidence_collector = evidence_collector or EvidenceCollector(
            providers=self._evidence_providers,
            clock=self._clock,
        )
        self._conflict_engine = conflict_engine or ConflictEngine()
        self._priority_engine = priority_engine or PriorityEngine()
        self._recommendation_engine = recommendation_engine or RecommendationEngine()
        self._narrative_engine = narrative_engine or NarrativeEngine()

    @property
    def narrative_engine(self) -> NarrativeEngine:
        """Registered narrative engine used during narrative generation."""
        return self._narrative_engine

    @property
    def recommendation_engine(self) -> RecommendationEngine:
        """Registered recommendation engine used during recommendation generation."""
        return self._recommendation_engine

    @property
    def priority_engine(self) -> PriorityEngine:
        """Registered priority engine used during ranking."""
        return self._priority_engine

    @property
    def conflict_engine(self) -> ConflictEngine:
        """Registered conflict engine used during resolution."""
        return self._conflict_engine

    @property
    def evidence_collector(self) -> EvidenceCollector:
        """Registered evidence collector used during collection."""
        return self._evidence_collector

    @property
    def evidence_providers(self) -> tuple[EvidenceProvider, ...]:
        """Registered evidence providers used during collection."""
        return self._evidence_providers

    @property
    def clock(self) -> Clock:
        """Injectable clock used when reference_time is absent."""
        return self._clock

    def run(self, consultation_input: ConsultationInput) -> ConsultationBrainOutput:
        """Execute all six pipeline stages and return structured output."""
        bundle = self._evidence_collector.collect(consultation_input)
        return self._build_output(consultation_input, bundle.all_evidence, evidence_bundle=bundle)

    async def run_async(self, consultation_input: ConsultationInput) -> ConsultationBrainOutput:
        """Execute the pipeline with async evidence collection."""
        bundle = await self._evidence_collector.collect_async(consultation_input)
        return self._build_output(consultation_input, bundle.all_evidence, evidence_bundle=bundle)

    def run_json(self, consultation_input: ConsultationInput) -> dict[str, Any]:
        """Run pipeline and return JSON-serializable dict."""
        return consultation_brain_output_to_dict(self.run(consultation_input))

    async def run_json_async(self, consultation_input: ConsultationInput) -> dict[str, Any]:
        """Run async pipeline and return JSON-serializable dict."""
        return consultation_brain_output_to_dict(await self.run_async(consultation_input))

    def _build_output(
        self,
        consultation_input: ConsultationInput,
        raw_evidence: tuple[ConsultationEvidence, ...],
        *,
        evidence_bundle: ConsultationEvidenceBundle | None = None,
    ) -> ConsultationBrainOutput:
        stage_trace: list[PipelineStage] = [PipelineStage.COLLECT_EVIDENCE]

        stage_trace.append(PipelineStage.NORMALIZE_EVIDENCE)

        stage_trace.append(PipelineStage.RESOLVE_CONFLICTS)
        conflict_result = self._conflict_engine.resolve(
            evidence_bundle or ConsultationEvidenceBundle()
        )
        conflicts = conflict_result.legacy_conflicts
        resolved_evidence = conflict_result.resolved_evidence
        normalized_evidence = normalize_evidence(resolved_evidence)

        stage_trace.append(PipelineStage.RANK_PRIORITIES)
        priority_result = self._priority_engine.rank(conflict_result, normalized_evidence)
        priorities = to_legacy_priorities(priority_result)

        stage_trace.append(PipelineStage.GENERATE_RECOMMENDATIONS)
        recommendation_result = self._recommendation_engine.generate(
            priority_result,
            conflict_result,
            evidence_bundle or ConsultationEvidenceBundle(),
        )
        recommendations = to_legacy_recommendations(recommendation_result)

        stage_trace.append(PipelineStage.GENERATE_NARRATIVE)
        narrative = self._narrative_engine.generate(
            recommendation_result,
            priority_result,
            conflict_result,
            evidence_bundle or ConsultationEvidenceBundle(),
            consultation_input.professional_report,
            language=consultation_input.language,
            problem_text=consultation_input.problem_text,
        )

        overall_confidence = compute_overall_confidence(
            evidence=normalized_evidence,
            conflicts=conflicts,
            priorities=priorities,
        )

        stage_trace.append(PipelineStage.PRODUCE_OUTPUT)
        generated_at = consultation_input.reference_time or self._clock.now_utc()
        executive_summary = _executive_summary(
            problem_text=consultation_input.problem_text,
            priority_count=len(priorities),
            evidence_count=len(resolved_evidence),
        )

        return ConsultationBrainOutput(
            generated_at=generated_at,
            stage_trace=tuple(stage_trace),
            evidence=normalized_evidence,
            conflicts=conflicts,
            priorities=priorities,
            recommendations=recommendations,
            overall_confidence=overall_confidence,
            executive_summary=executive_summary,
            narrative=narrative,
            metadata={
                "engine_version": self.ENGINE_VERSION,
                "language": consultation_input.language,
                "evidence_count": len(normalized_evidence),
                "conflict_count": len(conflicts),
                "conflict_resolution_count": len(conflict_result.resolutions),
                "priority_domain_count": len(priority_result.priorities),
                "suppressed_topic_count": len(priority_result.suppressed_topics),
                "recommendation_high_count": len(recommendation_result.high_priority),
                "recommendation_medium_count": len(recommendation_result.medium_priority),
                "recommendation_low_count": len(recommendation_result.low_priority),
                "recommendation_deferred_count": len(recommendation_result.deferred),
                "narrative_section_count": len(narrative.sections),
                "narrative_language": narrative.language.value,
                "provider_sources": provider_sources(self._evidence_providers),
                "collection_metadata": dict((evidence_bundle or ConsultationEvidenceBundle()).metadata),
            },
        )


def _executive_summary(*, problem_text: str | None, priority_count: int, evidence_count: int) -> str:
    concern = problem_text or "the native's chart"
    return (
        f"Consultation brain foundation summary for {concern}. "
        f"{evidence_count} evidence placeholders collected; {priority_count} priorities ranked. "
        "Detailed reasoning will be enabled in a future phase."
    )
