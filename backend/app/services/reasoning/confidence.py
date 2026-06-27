"""Confidence scoring for horoscope reasoning outputs."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.services.reasoning.models import AnalysisBundle, ReasoningEngineInput
from backend.app.services.reasoning.types import DOMAIN_WEIGHTS, ReasoningDomain


@dataclass(frozen=True)
class ConfidenceBreakdown:
    """Per-domain and aggregate confidence metrics."""

    domain_scores: dict[ReasoningDomain, float]
    weighted_score: float
    evidence_weight_total: float


class ConfidenceScorer:
    """
    Computes confidence from input coverage and emitted evidence weights.

    The scorer is intentionally domain-agnostic and does not apply astrology
    rules. It measures how completely each subsystem contributed data.
    """

    def score(
        self,
        *,
        reasoning_input: ReasoningEngineInput,
        bundle: AnalysisBundle,
    ) -> float:
        """Return the final confidence score in the range [0.0, 1.0]."""
        return self.breakdown(
            reasoning_input=reasoning_input,
            bundle=bundle,
        ).weighted_score

    def breakdown(
        self,
        *,
        reasoning_input: ReasoningEngineInput,
        bundle: AnalysisBundle,
    ) -> ConfidenceBreakdown:
        """Return detailed confidence metrics for observability and testing."""
        domain_scores = {
            analysis.domain: analysis.coverage_score
            for analysis in bundle.domain_analyses
        }
        weighted_score = sum(
            domain_scores.get(domain, 0.0) * weight
            for domain, weight in DOMAIN_WEIGHTS.items()
        )
        evidence_weight_total = sum(
            evidence.weight for analysis in bundle.domain_analyses for evidence in analysis.evidence
        )

        if reasoning_input.problem_text:
            weighted_score = min(1.0, weighted_score + 0.05)

        return ConfidenceBreakdown(
            domain_scores=domain_scores,
            weighted_score=round(min(max(weighted_score, 0.0), 1.0), 4),
            evidence_weight_total=round(evidence_weight_total, 4),
        )
