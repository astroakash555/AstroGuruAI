"""Typed models for the transit intelligence layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from backend.app.services.reasoning.models import DashaInput, DashaPeriodSnapshot
from backend.app.services.reasoning.transit.constants import TransitObservationCategory


@dataclass(frozen=True)
class ReasoningObservation:
    """Structured observation emitted by transit intelligence modules."""

    category: TransitObservationCategory
    title: str
    explanation: str
    affected_planets: tuple[str, ...] = ()
    affected_houses: tuple[int, ...] = ()
    severity: float = 0.0
    confidence: float = 0.0
    observation_id: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class TransitPlanetRecord:
    """Normalized transiting graha snapshot."""

    planet: str
    sign_name: str
    sign_index: int
    house_from_lagna: int | None
    house_from_moon: int | None
    is_retrograde: bool = False


@dataclass(frozen=True)
class NatalPlanetRecord:
    """Normalized natal graha placement for transit overlays."""

    name: str
    sign_name: str
    sign_index: int
    house: int


@dataclass(frozen=True)
class TransitChartContext:
    """Chart, transit, and optional dasha snapshot for transit evaluation."""

    lagna_sign_index: int
    lagna_sign_name: str
    moon_sign_index: int
    moon_sign_name: str
    reference_datetime: datetime | None
    transits: dict[str, TransitPlanetRecord]
    natal_planets: dict[str, NatalPlanetRecord]
    house_lords: dict[int, str]
    dasha: DashaInput | None = None

    def get_transit(self, planet: str) -> TransitPlanetRecord:
        """Return a transit record or raise when absent."""
        if planet not in self.transits:
            raise KeyError(f"Transit planet {planet!r} is not present in the context.")
        return self.transits[planet]

    def has_transit(self, planet: str) -> bool:
        """Return True when a transiting graha is present."""
        return planet in self.transits

    def has_natal(self, name: str) -> bool:
        """Return True when a natal graha is present."""
        return name in self.natal_planets

    def natal_house(self, name: str) -> int | None:
        """Return the natal house of a graha when present."""
        if name not in self.natal_planets:
            return None
        return self.natal_planets[name].house

    def active_dasha_lords(self) -> tuple[str, ...]:
        """Return active dasha lords across hierarchy levels."""
        if self.dasha is None:
            return ()
        lords: list[str] = []
        for period in (
            self.dasha.current_mahadasha,
            self.dasha.current_antardasha,
            self.dasha.current_pratyantar,
        ):
            if period is not None and period.lord not in lords:
                lords.append(period.lord)
        return tuple(lords)

    def active_period(self, level: str) -> DashaPeriodSnapshot | None:
        """Return the active dasha period for a hierarchy level."""
        if self.dasha is None:
            return None
        if level == "mahadasha":
            return self.dasha.current_mahadasha
        if level == "antardasha":
            return self.dasha.current_antardasha
        if level == "pratyantar":
            return self.dasha.current_pratyantar
        raise ValueError(f"Unknown dasha level: {level!r}")


@dataclass(frozen=True)
class TransitEventWindowRecord:
    """Structured event window derived from transit activation."""

    window_id: str
    domain_id: str
    domain_name: str
    planet: str
    activation_score: float
    target_houses: tuple[int, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class TransitAnalysisResult:
    """Complete output from the transit intelligence analyzer."""

    analyzed_at: datetime
    observations: tuple[ReasoningObservation, ...]
    event_windows: tuple[TransitEventWindowRecord, ...]
    metadata: dict[str, object] = field(default_factory=dict)


def make_observation(
    *,
    observation_id: str,
    category: TransitObservationCategory,
    title: str,
    explanation: str,
    affected_planets: tuple[str, ...] = (),
    affected_houses: tuple[int, ...] = (),
    severity: float = 0.0,
    confidence: float = 0.0,
    metadata: dict[str, object] | None = None,
) -> ReasoningObservation:
    """Create a normalized transit reasoning observation with bounded scores."""
    return ReasoningObservation(
        observation_id=observation_id,
        category=category,
        title=title,
        explanation=explanation,
        affected_planets=affected_planets,
        affected_houses=affected_houses,
        severity=round(min(max(severity, 0.0), 1.0), 4),
        confidence=round(min(max(confidence, 0.0), 1.0), 4),
        metadata=metadata or {},
    )
