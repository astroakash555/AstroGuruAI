"""KP astrology analysis types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class CuspalPoint:
    house: int
    longitude: float
    sign: str
    star_lord: str
    sub_lord: str


@dataclass(frozen=True)
class SignificatorSet:
    house: int
    level_a: tuple[str, ...]
    level_b: tuple[str, ...]
    level_c: tuple[str, ...]
    level_d: tuple[str, ...]
    combined: tuple[str, ...]


@dataclass(frozen=True)
class StarLordAnalysis:
    planet: str
    longitude: float
    nakshatra: str
    star_lord: str
    house: int | None


@dataclass(frozen=True)
class SubLordAnalysis:
    planet: str
    longitude: float
    nakshatra: str
    star_lord: str
    sub_lord: str
    house: int | None


@dataclass(frozen=True)
class EventAnalysis:
    event_id: str
    event_type: str
    target_houses: tuple[int, ...]
    is_supported: bool
    support_score: float
    significators_matched: tuple[str, ...]
    cusp_sub_lords_matched: tuple[str, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class KPAnalysisSummary:
    total_cusps: int
    total_significator_sets: int
    supported_events: int
    total_events: int


@dataclass(frozen=True)
class KPAnalysisResult:
    analyzed_at: datetime
    lagna_sign: str
    cusps: tuple[CuspalPoint, ...]
    significators: tuple[SignificatorSet, ...]
    star_lords: tuple[StarLordAnalysis, ...]
    sub_lords: tuple[SubLordAnalysis, ...]
    events: tuple[EventAnalysis, ...]
    summary: KPAnalysisSummary
    metadata: dict[str, object] = field(default_factory=dict)
