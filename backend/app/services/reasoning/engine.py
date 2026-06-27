"""Horoscope reasoning engine orchestrator."""

from __future__ import annotations

from typing import Any

from backend.app.services.reasoning.aggregator import ReasoningAggregator
from backend.app.services.reasoning.analyzer import ReasoningAnalyzer
from backend.app.services.reasoning.confidence import ConfidenceBreakdown, ConfidenceScorer
from backend.app.services.reasoning.models import ReasoningEngineInput, ReasoningResult


class ReasoningEngine:
    """
    Modular horoscope reasoning engine for AstroGuruAI Phase 2.

    Accepts structured birth, chart, dasha, transit, KP, and Lal Kitab inputs,
    runs them through independent analysis, confidence, and aggregation stages,
    and returns a fully typed ``ReasoningResult``.
    """

    def __init__(
        self,
        *,
        analyzer: ReasoningAnalyzer | None = None,
        confidence_scorer: ConfidenceScorer | None = None,
        aggregator: ReasoningAggregator | None = None,
    ) -> None:
        self._analyzer = analyzer or ReasoningAnalyzer()
        self._confidence_scorer = confidence_scorer or ConfidenceScorer()
        self._aggregator = aggregator or ReasoningAggregator()

    @property
    def analyzer(self) -> ReasoningAnalyzer:
        """Domain analyzer used by this engine instance."""
        return self._analyzer

    @property
    def confidence_scorer(self) -> ConfidenceScorer:
        """Confidence scorer used by this engine instance."""
        return self._confidence_scorer

    @property
    def aggregator(self) -> ReasoningAggregator:
        """Result aggregator used by this engine instance."""
        return self._aggregator

    def analyze(self, reasoning_input: ReasoningEngineInput) -> ReasoningResult:
        """Execute the full reasoning pipeline and return a structured result."""
        bundle = self._analyzer.analyze(reasoning_input)
        confidence_score = self._confidence_scorer.score(
            reasoning_input=reasoning_input,
            bundle=bundle,
        )
        return self._aggregator.aggregate(
            reasoning_input=reasoning_input,
            bundle=bundle,
            confidence_score=confidence_score,
        )

    def analyze_with_breakdown(
        self,
        reasoning_input: ReasoningEngineInput,
    ) -> tuple[ReasoningResult, ConfidenceBreakdown]:
        """Execute the pipeline and return both the result and confidence metrics."""
        bundle = self._analyzer.analyze(reasoning_input)
        breakdown = self._confidence_scorer.breakdown(
            reasoning_input=reasoning_input,
            bundle=bundle,
        )
        result = self._aggregator.aggregate(
            reasoning_input=reasoning_input,
            bundle=bundle,
            confidence_score=breakdown.weighted_score,
        )
        return result, breakdown

    def analyze_json(self, reasoning_input: ReasoningEngineInput) -> dict[str, Any]:
        """Return the reasoning result as a JSON-serializable dictionary."""
        return reasoning_result_to_dict(self.analyze(reasoning_input))


def reasoning_result_to_dict(result: ReasoningResult) -> dict[str, Any]:
    """Serialize a reasoning result for API or logging consumers."""
    return {
        "analyzed_at": result.analyzed_at.isoformat(),
        "observations": [
            {
                "observation_id": item.observation_id,
                "domain": item.domain.value,
                "summary": item.summary,
                "source": item.source,
                "details": item.details,
                "weight": item.weight,
            }
            for item in result.observations
        ],
        "detected_patterns": [
            {
                "pattern_id": item.pattern_id,
                "name": item.name,
                "domain": item.domain.value,
                "description": item.description,
                "supporting_observation_ids": item.supporting_observation_ids,
                "confidence": item.confidence,
            }
            for item in result.detected_patterns
        ],
        "strengths": [
            {
                "strength_id": item.strength_id,
                "domain": item.domain.value,
                "label": item.label,
                "description": item.description,
                "score": item.score,
                "supporting_observation_ids": item.supporting_observation_ids,
            }
            for item in result.strengths
        ],
        "weaknesses": [
            {
                "weakness_id": item.weakness_id,
                "domain": item.domain.value,
                "label": item.label,
                "description": item.description,
                "score": item.score,
                "supporting_observation_ids": item.supporting_observation_ids,
            }
            for item in result.weaknesses
        ],
        "root_causes": [
            {
                "cause_id": item.cause_id,
                "category": item.category.value,
                "primary_factor": item.primary_factor,
                "description": item.description,
                "severity": item.severity,
                "supporting_evidence_ids": item.supporting_evidence_ids,
                "domains": [domain.value for domain in item.domains],
            }
            for item in result.root_causes
        ],
        "confidence_score": result.confidence_score,
        "evidence": [
            {
                "evidence_id": item.evidence_id,
                "kind": item.kind.value,
                "domain": item.domain.value,
                "statement": item.statement,
                "source": item.source,
                "reference_id": item.reference_id,
                "weight": item.weight,
            }
            for item in result.evidence
        ],
        "recommendations": [
            {
                "recommendation_id": item.recommendation_id,
                "title": item.title,
                "description": item.description,
                "priority": item.priority.value,
                "domains": [domain.value for domain in item.domains],
                "supporting_evidence_ids": item.supporting_evidence_ids,
            }
            for item in result.recommendations
        ],
        "metadata": result.metadata,
    }
