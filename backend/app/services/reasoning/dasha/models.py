"""Typed models for the Dasha intelligence layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from backend.app.services.reasoning.dasha.constants import DashaObservationCategory
from backend.app.services.reasoning.models import DashaInput, DashaPeriodSnapshot


@dataclass(frozen=True)
class ReasoningObservation:
    """Structured observation emitted by Dasha intelligence modules."""

    category: DashaObservationCategory
    title: str
    explanation: str
    affected_planets: tuple[str, ...] = ()
    affected_houses: tuple[int, ...] = ()
    severity: float = 0.0
    confidence: float = 0.0
    observation_id: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class DashaPlanetRecord:
    """Normalized graha placement for dasha rule evaluation."""

    name: str
    longitude: float
    sign_name: str
    sign_index: int
    house: int
    dignity: str
    is_retrograde: bool = False


@dataclass(frozen=True)
class DashaChartContext:
    """Chart and dasha snapshot for dasha intelligence evaluation."""

    lagna_sign_index: int
    lagna_sign_name: str
    dasha: DashaInput
    reference_datetime: datetime | None
    planets: dict[str, DashaPlanetRecord]
    house_lords: dict[int, str]
    houses_ruled_by: dict[str, tuple[int, ...]]

    def get_planet(self, name: str) -> DashaPlanetRecord:
        """Return a planet record or raise when the graha is absent."""
        if name not in self.planets:
            raise KeyError(f"Planet {name!r} is not present in the dasha chart context.")
        return self.planets[name]

    def has_planet(self, name: str) -> bool:
        """Return True when the graha exists in the chart context."""
        return name in self.planets

    def house_of(self, name: str) -> int | None:
        """Return the whole-sign house occupied by a graha when present."""
        if name not in self.planets:
            return None
        return self.planets[name].house

    def houses_ruled(self, name: str) -> tuple[int, ...]:
        """Return bhavas ruled by a graha from the lagna."""
        return self.houses_ruled_by.get(name, ())

    def active_period(self, level: str) -> DashaPeriodSnapshot | None:
        """Return the active dasha period for a hierarchy level."""
        if level == "mahadasha":
            return self.dasha.current_mahadasha
        if level == "antardasha":
            return self.dasha.current_antardasha
        if level == "pratyantar":
            return self.dasha.current_pratyantar
        raise ValueError(f"Unknown dasha level: {level!r}")


@dataclass(frozen=True)
class EventWindowRecord:
    """Structured event window derived from dasha period boundaries."""

    window_id: str
    domain_id: str
    domain_name: str
    level: str
    lord: str
    start: datetime | None
    end: datetime | None
    activation_score: float
    target_houses: tuple[int, ...]
    is_active: bool
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class DashaAnalysisResult:
    """Complete output from the Dasha intelligence analyzer."""

    analyzed_at: datetime
    observations: tuple[ReasoningObservation, ...]
    event_windows: tuple[EventWindowRecord, ...]
    metadata: dict[str, object] = field(default_factory=dict)


def make_observation(
    *,
    observation_id: str,
    category: DashaObservationCategory,
    title: str,
    explanation: str,
    affected_planets: tuple[str, ...] = (),
    affected_houses: tuple[int, ...] = (),
    severity: float = 0.0,
    confidence: float = 0.0,
    metadata: dict[str, object] | None = None,
) -> ReasoningObservation:
    """Create a normalized Dasha reasoning observation with bounded scores."""
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
