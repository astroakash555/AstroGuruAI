"""Typed models for the KP astrology intelligence layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from backend.app.services.reasoning.kp.constants import KPObservationCategory


@dataclass(frozen=True)
class ReasoningObservation:
    """Structured observation emitted by reasoning intelligence modules."""

    category: KPObservationCategory
    title: str
    explanation: str
    affected_planets: tuple[str, ...] = ()
    affected_houses: tuple[int, ...] = ()
    severity: float = 0.0
    confidence: float = 0.0
    observation_id: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class KPPlanetRecord:
    """Normalized graha placement with KP lord assignments."""

    name: str
    longitude: float
    sign_name: str
    sign_index: int
    house: int
    nakshatra: str | None
    star_lord: str
    sub_lord: str


@dataclass(frozen=True)
class KPCuspRecord:
    """Bhava cusp with KP star and sub lords."""

    house: int
    longitude: float
    sign_name: str
    star_lord: str
    sub_lord: str


@dataclass(frozen=True)
class KPSignificatorRecord:
    """KP significator levels A-D for one house."""

    house: int
    level_a: tuple[str, ...]
    level_b: tuple[str, ...]
    level_c: tuple[str, ...]
    level_d: tuple[str, ...]
    combined: tuple[str, ...]


@dataclass(frozen=True)
class RulingPlanets:
    """Classical KP ruling planets for a judgement moment."""

    day_lord: str
    moon_sign_lord: str
    moon_star_lord: str
    moon_sub_lord: str
    lagna_sign_lord: str
    lagna_star_lord: str
    lagna_sub_lord: str
    components: tuple[str, ...]
    ruling_set: tuple[str, ...]


@dataclass(frozen=True)
class KPChartContext:
    """Normalized chart snapshot for KP rule evaluation."""

    lagna_sign_index: int
    lagna_sign_name: str
    lagna_longitude: float
    reference_datetime: datetime | None
    planets: dict[str, KPPlanetRecord]
    cusps: tuple[KPCuspRecord, ...]
    significators: tuple[KPSignificatorRecord, ...]
    ruling_planets: RulingPlanets | None

    def get_planet(self, name: str) -> KPPlanetRecord:
        """Return a planet record or raise when the graha is absent."""
        if name not in self.planets:
            raise KeyError(f"Planet {name!r} is not present in the KP chart context.")
        return self.planets[name]

    def has_planet(self, name: str) -> bool:
        """Return True when the graha exists in the chart context."""
        return name in self.planets

    def cusp_for_house(self, house: int) -> KPCuspRecord | None:
        """Return the cusp record for a house when available."""
        for cusp in self.cusps:
            if cusp.house == house:
                return cusp
        return None

    def significators_for_house(self, house: int) -> KPSignificatorRecord | None:
        """Return significator levels for a house when available."""
        for record in self.significators:
            if record.house == house:
                return record
        return None


@dataclass(frozen=True)
class EventTimingRecord:
    """Structured event timing evaluation for future prediction extensions."""

    event_id: str
    event_type: str
    target_houses: tuple[int, ...]
    is_supported: bool
    support_score: float
    significators_matched: tuple[str, ...]
    cusp_sub_lords_matched: tuple[str, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class KPAnalysisResult:
    """Complete output from the KP intelligence analyzer."""

    analyzed_at: datetime
    observations: tuple[ReasoningObservation, ...]
    event_timing: tuple[EventTimingRecord, ...]
    metadata: dict[str, object] = field(default_factory=dict)


def make_observation(
    *,
    observation_id: str,
    category: KPObservationCategory,
    title: str,
    explanation: str,
    affected_planets: tuple[str, ...] = (),
    affected_houses: tuple[int, ...] = (),
    severity: float = 0.0,
    confidence: float = 0.0,
    metadata: dict[str, object] | None = None,
) -> ReasoningObservation:
    """Create a normalized KP reasoning observation with bounded scores."""
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
