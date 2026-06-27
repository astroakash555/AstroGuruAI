"""Lal Kitab analysis types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class LalKitabCondition:
    name: str
    met: bool
    detail: str


@dataclass(frozen=True)
class LalKitabFinding:
    finding_id: str
    finding_name: str
    category: str
    is_present: bool
    strength: float
    description: str
    planets_involved: tuple[str, ...]
    houses_involved: tuple[int, ...]
    conditions: tuple[LalKitabCondition, ...]
    evidence: tuple[str, ...]
    recommendation_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PlanetHouseAnalysis:
    planet: str
    house: int
    sign: str
    effect_code: str
    strength: float
    conditions: tuple[LalKitabCondition, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class LalKitabSummary:
    total_rules: int
    present_count: int
    absent_count: int
    average_strength: float
    rin_count: int
    dosh_count: int


@dataclass(frozen=True)
class LalKitabAnalysisResult:
    analyzed_at: datetime
    lagna_sign: str
    planet_by_house: tuple[PlanetHouseAnalysis, ...]
    rin_findings: tuple[LalKitabFinding, ...]
    dosh_findings: tuple[LalKitabFinding, ...]
    recommendations: tuple[LalKitabFinding, ...]
    summary: LalKitabSummary
    metadata: dict[str, object] = field(default_factory=dict)
