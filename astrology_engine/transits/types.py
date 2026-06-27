"""Typed models for transit analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from astrology_engine.core.types import NakshatraInfo, ZodiacSign


@dataclass(frozen=True)
class TransitInput:
    """Input for transit computation relative to a natal chart."""

    natal_lagna_sign_index: int
    natal_moon_sign_index: int
    natal_planets: dict[str, int]  # planet name -> sign index
    latitude: float
    longitude: float
    timezone: str


@dataclass(frozen=True)
class TransitPlanetSnapshot:
    """Sidereal snapshot of a transiting graha at a moment."""

    planet: str
    datetime: datetime
    longitude: float
    sign: ZodiacSign
    house_from_lagna: int
    house_from_moon: int
    is_retrograde: bool
    nakshatra: NakshatraInfo
    speed: float


@dataclass(frozen=True)
class SignChangeEvent:
    """Sign ingress during an observation window."""

    planet: str
    datetime: datetime
    from_sign: str
    to_sign: str
    from_house_lagna: int
    to_house_lagna: int


@dataclass(frozen=True)
class NatalImpact:
    """Natal chart impact from a transiting graha."""

    impact_type: str
    description: str
    strength: float
    target: str | None = None
    house_from_lagna: int | None = None
    house_from_moon: int | None = None


@dataclass(frozen=True)
class TransitPlanetAnalysis:
    """Analysis bundle for one transiting graha."""

    planet: str
    theme: str
    current: TransitPlanetSnapshot | None
    sign_changes: tuple[SignChangeEvent, ...]
    natal_impacts: tuple[NatalImpact, ...]
    highlights: tuple[str, ...]
    retrograde_periods: tuple[tuple[datetime, datetime], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DailyTransitResult:
    """Single-day transit snapshot."""

    date: date
    snapshots: tuple[TransitPlanetSnapshot, ...]
    analyses: tuple[TransitPlanetAnalysis, ...]


@dataclass(frozen=True)
class MonthlyTransitResult:
    """Monthly transit summary."""

    year: int
    month: int
    period_start: date
    period_end: date
    sign_changes: tuple[SignChangeEvent, ...]
    daily_snapshots: tuple[TransitPlanetSnapshot, ...]
    analyses: tuple[TransitPlanetAnalysis, ...]
    highlights: tuple[str, ...]


@dataclass(frozen=True)
class YearlyTransitResult:
    """Yearly transit summary."""

    year: int
    period_start: date
    period_end: date
    sign_changes: tuple[SignChangeEvent, ...]
    monthly_highlights: tuple[str, ...]
    analyses: tuple[TransitPlanetAnalysis, ...]
    highlights: tuple[str, ...]


@dataclass(frozen=True)
class TransitAnalysisResult:
    """Complete transit analysis output."""

    computed_at: datetime
    natal_lagna_sign: str
    natal_moon_sign: str
    daily: DailyTransitResult | None
    monthly: MonthlyTransitResult | None
    yearly: YearlyTransitResult | None
    saturn: TransitPlanetAnalysis
    jupiter: TransitPlanetAnalysis
    rahu: TransitPlanetAnalysis
    ketu: TransitPlanetAnalysis
    metadata: dict[str, object] = field(default_factory=dict)
