"""Observation ranking for the intelligence fusion layer."""

from __future__ import annotations

from dataclasses import replace

from backend.app.services.reasoning.fusion.models import FusedObservation

CONFIDENCE_WEIGHT = 0.40
SEVERITY_WEIGHT = 0.35
ENGINE_SUPPORT_WEIGHT = 0.25


def compute_rank_score(
    observation: FusedObservation,
    *,
    active_engine_count: int,
) -> float:
    """
    Rank fused observations using confidence, severity, and engine support.

    The score prioritizes high-confidence, high-severity observations that are
    corroborated by multiple intelligence engines.
    """
    engine_factor = len(observation.supporting_engines) / max(active_engine_count, 1)
    score = (
        CONFIDENCE_WEIGHT * observation.confidence
        + SEVERITY_WEIGHT * observation.severity
        + ENGINE_SUPPORT_WEIGHT * engine_factor
    )
    return round(min(max(score, 0.0), 1.0), 4)


def rank_observations(
    observations: tuple[FusedObservation, ...],
    *,
    active_engine_count: int,
) -> tuple[FusedObservation, ...]:
    """Apply ranking scores and return observations in descending rank order."""
    ranked = [
        replace(
            observation,
            rank_score=compute_rank_score(
                observation,
                active_engine_count=active_engine_count,
            ),
        )
        for observation in observations
    ]
    ranked.sort(
        key=lambda item: (
            item.rank_score,
            item.confidence,
            item.severity,
            len(item.supporting_engines),
        ),
        reverse=True,
    )
    return tuple(ranked)
