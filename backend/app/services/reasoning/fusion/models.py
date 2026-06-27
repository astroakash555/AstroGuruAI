"""Typed models for the intelligence fusion layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from backend.app.services.reasoning.models import (
    DashaInput,
    HousesInput,
    LalKitabDataInput,
    PlanetPositionsInput,
    TransitInput,
)


class FusionEngineId(str, Enum):
    """Registered intelligence engines participating in fusion."""

    VEDIC = "vedic"
    KP = "kp"
    LAL_KITAB = "lal_kitab"
    DASHA = "dasha"
    TRANSIT = "transit"


@dataclass(frozen=True)
class FusionContext:
    """Shared chart context passed to all intelligence analyzers."""

    planet_positions: PlanetPositionsInput
    houses: HousesInput
    reference_datetime: datetime | None = None
    dasha: DashaInput | None = None
    transit: TransitInput | None = None
    lal_kitab_data: LalKitabDataInput | None = None


@dataclass(frozen=True)
class NormalizedObservation:
    """Engine observation normalized into a common fusion shape."""

    observation_id: str
    engine: FusionEngineId
    category: str
    title: str
    explanation: str
    affected_planets: tuple[str, ...] = ()
    affected_houses: tuple[int, ...] = ()
    severity: float = 0.0
    confidence: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class FusedObservation:
    """Observation after deduplication, evidence merge, and ranking."""

    fusion_id: str
    title: str
    explanation: str
    category: str
    affected_planets: tuple[str, ...]
    affected_houses: tuple[int, ...]
    severity: float
    confidence: float
    supporting_engines: tuple[FusionEngineId, ...]
    source_observation_ids: tuple[str, ...]
    rank_score: float
    has_conflict: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class InterpretationConflict:
    """Conflicting interpretations detected across intelligence engines."""

    conflict_id: str
    title: str
    explanation: str
    engines: tuple[FusionEngineId, ...]
    observation_ids: tuple[str, ...]
    affected_planets: tuple[str, ...]
    affected_houses: tuple[int, ...]
    severity_spread: float
    confidence: float


@dataclass(frozen=True)
class RootCauseAnalysis:
    """Primary causal hypothesis synthesized from fused observations."""

    title: str
    explanation: str
    supporting_observations: tuple[str, ...]
    supporting_engines: tuple[FusionEngineId, ...]
    confidence: float


@dataclass(frozen=True)
class FusionRecommendation:
    """Actionable guidance derived from fused root-cause analysis."""

    recommendation_id: str
    title: str
    explanation: str
    priority: str
    supporting_root_causes: tuple[str, ...]
    confidence: float


@dataclass(frozen=True)
class FusionResult:
    """Complete output from the intelligence fusion engine."""

    analyzed_at: datetime
    observations: tuple[FusedObservation, ...]
    root_causes: tuple[RootCauseAnalysis, ...]
    recommendations: tuple[FusionRecommendation, ...]
    confidence_score: float
    conflicts: tuple[InterpretationConflict, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)
