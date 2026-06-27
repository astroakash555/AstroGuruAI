"""Recommendation generation from fused root-cause analysis."""

from __future__ import annotations

from backend.app.services.reasoning.fusion.models import FusionRecommendation, RootCauseAnalysis

HIGH_PRIORITY_CONFIDENCE = 0.80
MEDIUM_PRIORITY_CONFIDENCE = 0.65


def build_recommendations(
    root_causes: tuple[RootCauseAnalysis, ...],
) -> tuple[FusionRecommendation, ...]:
    """Derive actionable recommendations from synthesized root causes."""
    recommendations: list[FusionRecommendation] = []

    for index, root_cause in enumerate(root_causes, start=1):
        priority = _priority_for_confidence(root_cause.confidence)
        recommendations.append(
            FusionRecommendation(
                recommendation_id=f"fusion-recommendation-{index:04d}",
                title=_recommendation_title(root_cause, priority),
                explanation=_recommendation_explanation(root_cause, priority),
                priority=priority,
                supporting_root_causes=(root_cause.title,),
                confidence=root_cause.confidence,
            )
        )

    return tuple(recommendations)


def _priority_for_confidence(confidence: float) -> str:
    """Map root-cause confidence to recommendation priority."""
    if confidence >= HIGH_PRIORITY_CONFIDENCE:
        return "high"
    if confidence >= MEDIUM_PRIORITY_CONFIDENCE:
        return "medium"
    return "low"


def _recommendation_title(root_cause: RootCauseAnalysis, priority: str) -> str:
    """Build a concise recommendation title."""
    return f"{priority.title()} Priority: Address {root_cause.title}"


def _recommendation_explanation(root_cause: RootCauseAnalysis, priority: str) -> str:
    """Build a recommendation explanation tied to fused evidence."""
    engine_list = ", ".join(engine.value for engine in root_cause.supporting_engines)
    return (
        f"{root_cause.explanation} Recommended action ({priority} priority): "
        f"review this factor in consultation, supported by {engine_list or 'fusion'} "
        f"analysis with confidence {root_cause.confidence:.2f}."
    )
