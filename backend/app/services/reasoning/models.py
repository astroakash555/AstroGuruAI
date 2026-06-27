"""Typed input and output models for the horoscope reasoning engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any

from backend.app.services.reasoning.types import (
    EvidenceKind,
    ReasoningDomain,
    RecommendationPriority,
    RootCauseCategory,
)


@dataclass(frozen=True)
class BirthDetailsInput:
    """Normalized birth profile used to anchor horoscope reasoning."""

    date_of_birth: date
    birth_time: time
    birth_place: str
    timezone: str
    latitude: float
    longitude: float
    person_name: str | None = None
    client_id: str | None = None


@dataclass(frozen=True)
class PlanetPositionSnapshot:
    """Single graha placement supplied to the reasoning pipeline."""

    name: str
    longitude: float
    sign: str
    house: int | None = None
    nakshatra: str | None = None
    is_retrograde: bool = False


@dataclass(frozen=True)
class PlanetPositionsInput:
    """Collection of sidereal planetary positions for one chart."""

    planets: tuple[PlanetPositionSnapshot, ...]
    ascendant_sign: str | None = None
    moon_sign: str | None = None


@dataclass(frozen=True)
class HouseSnapshot:
    """House cusp or whole-sign house assignment."""

    number: int
    sign: str
    longitude: float | None = None


@dataclass(frozen=True)
class HousesInput:
    """House map for lagna-based reasoning."""

    cusps: tuple[HouseSnapshot, ...]
    ascendant_sign: str | None = None
    house_system: str | None = None


@dataclass(frozen=True)
class DashaPeriodSnapshot:
    """One dasha period at any hierarchical level."""

    level: str
    lord: str
    start: datetime | None = None
    end: datetime | None = None


@dataclass(frozen=True)
class DashaInput:
    """Dasha timeline context for temporal reasoning."""

    system: str
    current_mahadasha: DashaPeriodSnapshot | None = None
    current_antardasha: DashaPeriodSnapshot | None = None
    current_pratyantar: DashaPeriodSnapshot | None = None
    mahadashas: tuple[DashaPeriodSnapshot, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class TransitPlanetSnapshot:
    """Transiting graha snapshot relative to the natal chart."""

    planet: str
    sign: str
    house_from_lagna: int | None = None
    house_from_moon: int | None = None
    is_retrograde: bool = False


@dataclass(frozen=True)
class TransitInput:
    """Transit window data for timing-oriented reasoning."""

    reference_datetime: datetime | None = None
    planets: tuple[TransitPlanetSnapshot, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class KPSignificatorSnapshot:
    """KP significator set for one house."""

    house: int
    planets: tuple[str, ...]


@dataclass(frozen=True)
class KPDataInput:
    """Krishnamurti Paddhati analysis payload."""

    lagna_sign: str | None = None
    cusps: tuple[HouseSnapshot, ...] = ()
    significators: tuple[KPSignificatorSnapshot, ...] = ()
    supported_events: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class LalKitabFindingSnapshot:
    """Structured Lal Kitab rule evaluation record."""

    finding_id: str
    name: str
    category: str
    is_present: bool
    strength: float
    planets: tuple[str, ...] = ()
    houses: tuple[int, ...] = ()


@dataclass(frozen=True)
class LalKitabDataInput:
    """Lal Kitab analysis payload."""

    lagna_sign: str | None = None
    findings: tuple[LalKitabFindingSnapshot, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ReasoningEngineInput:
    """Complete multi-system input assembled for horoscope reasoning."""

    birth_details: BirthDetailsInput
    planet_positions: PlanetPositionsInput
    houses: HousesInput
    dasha: DashaInput
    transit: TransitInput
    kp_data: KPDataInput
    lal_kitab_data: LalKitabDataInput
    problem_text: str | None = None
    reference_date: date | None = None


@dataclass(frozen=True)
class Observation:
    """Factual statement derived from one input domain."""

    observation_id: str
    domain: ReasoningDomain
    summary: str
    source: str
    details: dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0


@dataclass(frozen=True)
class DetectedPattern:
    """Cross-cutting pattern identified from one or more observations."""

    pattern_id: str
    name: str
    domain: ReasoningDomain
    description: str
    supporting_observation_ids: tuple[str, ...]
    confidence: float


@dataclass(frozen=True)
class Strength:
    """Supportive astrological factor awaiting interpretive rules."""

    strength_id: str
    domain: ReasoningDomain
    label: str
    description: str
    score: float
    supporting_observation_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Weakness:
    """Challenging astrological factor awaiting interpretive rules."""

    weakness_id: str
    domain: ReasoningDomain
    label: str
    description: str
    score: float
    supporting_observation_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class RootCause:
    """Primary causal hypothesis synthesized from multi-system evidence."""

    cause_id: str
    category: RootCauseCategory
    primary_factor: str
    description: str
    severity: float
    supporting_evidence_ids: tuple[str, ...] = ()
    domains: tuple[ReasoningDomain, ...] = ()


@dataclass(frozen=True)
class Evidence:
    """Traceable evidence item linked to reasoning conclusions."""

    evidence_id: str
    kind: EvidenceKind
    domain: ReasoningDomain
    statement: str
    source: str
    reference_id: str | None = None
    weight: float = 1.0


@dataclass(frozen=True)
class Recommendation:
    """Actionable guidance derived from the reasoning output."""

    recommendation_id: str
    title: str
    description: str
    priority: RecommendationPriority
    domains: tuple[ReasoningDomain, ...]
    supporting_evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class DomainAnalysis:
    """Intermediate analysis artifact produced for one reasoning domain."""

    domain: ReasoningDomain
    observations: tuple[Observation, ...]
    detected_patterns: tuple[DetectedPattern, ...]
    strengths: tuple[Strength, ...]
    weaknesses: tuple[Weakness, ...]
    root_causes: tuple[RootCause, ...]
    evidence: tuple[Evidence, ...]
    recommendations: tuple[Recommendation, ...]
    coverage_score: float


@dataclass(frozen=True)
class AnalysisBundle:
    """Aggregated intermediate output from all domain analyzers."""

    domain_analyses: tuple[DomainAnalysis, ...]


@dataclass(frozen=True)
class ReasoningResult:
    """Final structured output from the horoscope reasoning engine."""

    analyzed_at: datetime
    observations: tuple[Observation, ...]
    detected_patterns: tuple[DetectedPattern, ...]
    strengths: tuple[Strength, ...]
    weaknesses: tuple[Weakness, ...]
    root_causes: tuple[RootCause, ...]
    confidence_score: float
    evidence: tuple[Evidence, ...]
    recommendations: tuple[Recommendation, ...]
    metadata: dict[str, object] = field(default_factory=dict)
