"""Aggregation of domain analyses into a final reasoning result."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.services.reasoning.models import (
    AnalysisBundle,
    DetectedPattern,
    DomainAnalysis,
    Evidence,
    Observation,
    ReasoningEngineInput,
    ReasoningResult,
    Recommendation,
    RootCause,
    Strength,
    Weakness,
)


class ReasoningAggregator:
    """
    Combines domain-level analysis artifacts into a single reasoning result.

    Interpretive sections remain empty until dedicated rule modules populate
    them. The aggregator preserves ordering by domain declaration sequence.
    """

    ENGINE_VERSION = "horoscope_reasoning_v1"

    def aggregate(
        self,
        *,
        reasoning_input: ReasoningEngineInput,
        bundle: AnalysisBundle,
        confidence_score: float,
    ) -> ReasoningResult:
        """Merge all domain artifacts and attach engine metadata."""
        observations = self._merge_field(bundle.domain_analyses, "observations")
        detected_patterns = self._merge_field(bundle.domain_analyses, "detected_patterns")
        strengths = self._merge_field(bundle.domain_analyses, "strengths")
        weaknesses = self._merge_field(bundle.domain_analyses, "weaknesses")
        root_causes = self._merge_field(bundle.domain_analyses, "root_causes")
        evidence = self._merge_field(bundle.domain_analyses, "evidence")
        recommendations = self._merge_field(bundle.domain_analyses, "recommendations")

        return ReasoningResult(
            analyzed_at=datetime.now(timezone.utc),
            observations=observations,
            detected_patterns=detected_patterns,
            strengths=strengths,
            weaknesses=weaknesses,
            root_causes=root_causes,
            confidence_score=confidence_score,
            evidence=evidence,
            recommendations=recommendations,
            metadata={
                "engine": self.ENGINE_VERSION,
                "domain_count": len(bundle.domain_analyses),
                "observation_count": len(observations),
                "evidence_count": len(evidence),
                "problem_text_provided": reasoning_input.problem_text is not None,
                "reference_date": (
                    reasoning_input.reference_date.isoformat()
                    if reasoning_input.reference_date is not None
                    else None
                ),
            },
        )

    @staticmethod
    def _merge_field(
        domain_analyses: tuple[DomainAnalysis, ...],
        field_name: str,
    ) -> tuple[
        Observation
        | DetectedPattern
        | Strength
        | Weakness
        | RootCause
        | Evidence
        | Recommendation,
        ...,
    ]:
        """Concatenate one artifact type from all domain analyses."""
        merged: list[
            Observation
            | DetectedPattern
            | Strength
            | Weakness
            | RootCause
            | Evidence
            | Recommendation
        ] = []
        for analysis in domain_analyses:
            merged.extend(getattr(analysis, field_name))
        return tuple(merged)
