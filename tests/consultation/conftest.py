"""Shared fixtures for consultation brain tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.app.services.reasoning.fusion.models import (
    FusedObservation,
    FusionEngineId,
    FusionRecommendation,
    FusionResult,
    InterpretationConflict,
    RootCauseAnalysis,
)

CONSULTATION_REFERENCE_TIME = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


def fused_observation(
    *,
    fusion_id: str,
    title: str,
    severity: float = 0.5,
    confidence: float = 0.8,
    planets: tuple[str, ...] = ("Venus",),
    houses: tuple[int, ...] = (7,),
    category: str = "vedic:relationship",
    rank_score: float = 0.55,
    has_conflict: bool = False,
) -> FusedObservation:
    return FusedObservation(
        fusion_id=fusion_id,
        title=title,
        explanation=f"{title} detailed explanation.",
        category=category,
        affected_planets=planets,
        affected_houses=houses,
        severity=severity,
        confidence=confidence,
        supporting_engines=(FusionEngineId.VEDIC,),
        source_observation_ids=(fusion_id,),
        rank_score=rank_score,
        has_conflict=has_conflict,
    )


@pytest.fixture
def rich_fusion_result() -> FusionResult:
    observations = (
        fused_observation(
            fusion_id="obs-rel",
            title="Venus relationship pressure",
            severity=0.75,
            planets=("Venus", "Moon"),
            houses=(2, 7),
            category="vedic:relationship",
        ),
        fused_observation(
            fusion_id="obs-career",
            title="Saturn career discipline",
            severity=0.45,
            confidence=0.9,
            planets=("Saturn", "Sun"),
            houses=(10,),
            category="dasha:career",
            rank_score=0.62,
        ),
        fused_observation(
            fusion_id="obs-finance",
            title="Jupiter wealth support",
            severity=0.3,
            confidence=0.85,
            planets=("Jupiter",),
            houses=(2, 11),
            category="transit:finance",
            rank_score=0.58,
        ),
        fused_observation(
            fusion_id="obs-health",
            title="Mars health sensitivity",
            severity=0.8,
            confidence=0.7,
            planets=("Mars",),
            houses=(6, 8),
            category="transit:health",
            has_conflict=True,
            rank_score=0.66,
        ),
    )
    root_causes = (
        RootCauseAnalysis(
            title="Venus relationship pressure",
            explanation="Venus affliction drives relationship delay.",
            supporting_observations=("obs-rel",),
            supporting_engines=(FusionEngineId.VEDIC, FusionEngineId.KP),
            confidence=0.82,
        ),
        RootCauseAnalysis(
            title="Saturn career discipline",
            explanation="Saturn pressure on 10th house shapes career timing.",
            supporting_observations=("obs-career",),
            supporting_engines=(FusionEngineId.VEDIC,),
            confidence=0.78,
        ),
    )
    recommendations = (
        FusionRecommendation(
            recommendation_id="rec-1",
            title="Strengthen Venus remedies",
            explanation="Perform Venus pacification during relationship dasha windows.",
            priority="high",
            supporting_root_causes=("Venus relationship pressure",),
            confidence=0.84,
        ),
        FusionRecommendation(
            recommendation_id="rec-2",
            title="Career patience protocol",
            explanation="Avoid impulsive job changes while Saturn transits the 10th house.",
            priority="medium",
            supporting_root_causes=("Saturn career discipline",),
            confidence=0.76,
        ),
    )
    conflicts = (
        InterpretationConflict(
            conflict_id="conf-1",
            title="Health interpretation split",
            explanation="Vedic and KP disagree on Mars health severity.",
            engines=(FusionEngineId.VEDIC, FusionEngineId.KP),
            observation_ids=("obs-health",),
            affected_planets=("Mars",),
            affected_houses=(6,),
            severity_spread=0.25,
            confidence=0.71,
        ),
    )
    return FusionResult(
        analyzed_at=CONSULTATION_REFERENCE_TIME,
        observations=observations,
        root_causes=root_causes,
        recommendations=recommendations,
        confidence_score=0.79,
        conflicts=conflicts,
        metadata={"active_engines": ("vedic", "kp", "lal_kitab")},
    )


@pytest.fixture
def empty_fusion_result() -> FusionResult:
    return FusionResult(
        analyzed_at=CONSULTATION_REFERENCE_TIME,
        observations=(),
        root_causes=(),
        recommendations=(),
        confidence_score=0.4,
        conflicts=(),
        metadata={"active_engines": ()},
    )
