"""Typed models for the Lal Kitab intelligence layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from backend.app.services.reasoning.lal_kitab.constants import LalKitabObservationCategory


@dataclass(frozen=True)
class ReasoningObservation:
    """Structured observation emitted by Lal Kitab intelligence modules."""

    category: LalKitabObservationCategory
    title: str
    explanation: str
    affected_planets: tuple[str, ...] = ()
    affected_houses: tuple[int, ...] = ()
    severity: float = 0.0
    confidence: float = 0.0
    observation_id: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class LalKitabPlanetRecord:
    """Normalized graha placement for Lal Kitab rule evaluation."""

    name: str
    longitude: float
    sign_name: str
    sign_index: int
    house: int
    is_retrograde: bool = False


@dataclass(frozen=True)
class LalKitabChartContext:
    """Whole-sign chart snapshot for Lal Kitab rule evaluation."""

    lagna_sign_index: int
    lagna_sign_name: str
    planets: dict[str, LalKitabPlanetRecord]
    planets_by_house: dict[int, tuple[str, ...]]
    house_lords: dict[int, str]

    def get_planet(self, name: str) -> LalKitabPlanetRecord:
        """Return a planet record or raise when the graha is absent."""
        if name not in self.planets:
            raise KeyError(f"Planet {name!r} is not present in the Lal Kitab chart context.")
        return self.planets[name]

    def has_planet(self, name: str) -> bool:
        """Return True when the graha exists in the chart context."""
        return name in self.planets

    def house_of(self, name: str) -> int:
        """Return the whole-sign house occupied by a graha."""
        return self.get_planet(name).house

    def planets_in_house(self, house: int) -> tuple[str, ...]:
        """Return grahas occupying a house."""
        return self.planets_by_house.get(house, ())

    def house_lord(self, house: int) -> str:
        """Return the lord of a bhava counted from lagna."""
        return self.house_lords[house]

    def is_dusthana(self, house: int) -> bool:
        """Return True when a house is a dusthana bhava."""
        from backend.app.services.reasoning.lal_kitab.constants import DUSTHANA_HOUSES

        return house in DUSTHANA_HOUSES

    def is_kendra(self, house: int) -> bool:
        """Return True when a house is a kendra bhava."""
        from backend.app.services.reasoning.lal_kitab.constants import KENDRA_HOUSES

        return house in KENDRA_HOUSES


@dataclass(frozen=True)
class LalKitabRemedy:
    """Structured Lal Kitab remedy recommendation."""

    remedy_id: str
    title: str
    explanation: str
    priority: str
    expected_duration: str
    affected_planets: tuple[str, ...]
    affected_houses: tuple[int, ...]
    confidence: float
    source_observation_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class LalKitabAnalysisResult:
    """Complete output from the Lal Kitab intelligence analyzer."""

    analyzed_at: datetime
    observations: tuple[ReasoningObservation, ...]
    remedies: tuple[LalKitabRemedy, ...]
    metadata: dict[str, object] = field(default_factory=dict)


def make_observation(
    *,
    observation_id: str,
    category: LalKitabObservationCategory,
    title: str,
    explanation: str,
    affected_planets: tuple[str, ...] = (),
    affected_houses: tuple[int, ...] = (),
    severity: float = 0.0,
    confidence: float = 0.0,
    metadata: dict[str, object] | None = None,
) -> ReasoningObservation:
    """Create a normalized Lal Kitab reasoning observation with bounded scores."""
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
