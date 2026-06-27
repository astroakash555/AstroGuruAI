"""Shared fixtures and chart builders for Vedic reasoning tests."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from backend.app.services.reasoning.models import (
    HouseSnapshot,
    HousesInput,
    PlanetPositionSnapshot,
    PlanetPositionsInput,
)
from backend.app.services.reasoning.vedic import (
    ObservationCategory,
    VedicIntelligenceAnalyzer,
    VedicObservation,
)
from backend.app.services.reasoning.vedic.constants import SIGN_NAMES

FIXED_ANALYSIS_TIME = datetime(2026, 6, 20, 12, 0, 0, tzinfo=timezone.utc)


def whole_sign_cusps(lagna: str) -> tuple[HouseSnapshot, ...]:
    """Build whole-sign house cusps for a given lagna."""
    lagna_index = SIGN_NAMES.index(lagna)
    return tuple(
        HouseSnapshot(number=house, sign=SIGN_NAMES[(lagna_index + house - 1) % 12])
        for house in range(1, 13)
    )


def houses_for(lagna: str) -> HousesInput:
    """Return a whole-sign house map anchored to the lagna."""
    return HousesInput(
        ascendant_sign=lagna,
        house_system="whole_sign",
        cusps=whole_sign_cusps(lagna),
    )


def p(
    name: str,
    sign: str,
    house: int,
    longitude: float,
    *,
    is_retrograde: bool = False,
    nakshatra: str | None = None,
) -> PlanetPositionSnapshot:
    """Create a planet snapshot with explicit whole-sign house placement."""
    return PlanetPositionSnapshot(
        name=name,
        sign=sign,
        house=house,
        longitude=longitude,
        is_retrograde=is_retrograde,
        nakshatra=nakshatra,
    )


def chart(
    lagna: str,
    planets: tuple[PlanetPositionSnapshot, ...],
    *,
    moon_sign: str | None = None,
) -> tuple[PlanetPositionsInput, HousesInput]:
    """Build planet and house inputs for a whole-sign chart."""
    return (
        PlanetPositionsInput(
            ascendant_sign=lagna,
            moon_sign=moon_sign,
            planets=planets,
        ),
        houses_for(lagna),
    )


def all_classical_planets(
    lagna: str,
    placements: dict[str, tuple[str, int, float]],
    *,
    nodes: dict[str, tuple[str, int, float]] | None = None,
    retrograde: frozenset[str] = frozenset(),
) -> tuple[PlanetPositionSnapshot, ...]:
    """Build a full classical graha set with optional node overrides."""
    snapshots: list[PlanetPositionSnapshot] = []
    for name, (sign, house, longitude) in placements.items():
        snapshots.append(
            p(name, sign, house, longitude, is_retrograde=name in retrograde)
        )
    if nodes:
        for name, (sign, house, longitude) in nodes.items():
            snapshots.append(
                p(name, sign, house, longitude, is_retrograde=name in retrograde)
            )
    return tuple(snapshots)


def classical_chart(
    lagna: str,
    overrides: dict[str, PlanetPositionSnapshot] | None = None,
    *,
    moon_sign: str | None = None,
) -> tuple[PlanetPositionsInput, HousesInput]:
    """Build a complete nine-graha chart with optional planet overrides."""
    lagna_index = SIGN_NAMES.index(lagna)

    def _house(sign: str) -> int:
        sign_index = SIGN_NAMES.index(sign)
        return (sign_index - lagna_index + 12) % 12 + 1

    defaults: dict[str, PlanetPositionSnapshot] = {
        "Sun": p("Sun", "Gemini", _house("Gemini"), 70.0),
        "Moon": p("Moon", "Cancer", _house("Cancer"), 100.0),
        "Mars": p("Mars", "Leo", _house("Leo"), 130.0),
        "Mercury": p("Mercury", "Virgo", _house("Virgo"), 165.0),
        "Jupiter": p("Jupiter", "Libra", _house("Libra"), 190.0),
        "Venus": p("Venus", "Scorpio", _house("Scorpio"), 220.0),
        "Saturn": p("Saturn", "Sagittarius", _house("Sagittarius"), 250.0),
        "Rahu": p("Rahu", "Capricorn", _house("Capricorn"), 280.0),
        "Ketu": p("Ketu", "Cancer", _house("Cancer"), 100.0),
    }
    if overrides:
        defaults.update(overrides)
    return chart(lagna, tuple(defaults[name] for name in (
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
    )), moon_sign=moon_sign)


def analyze(
    planet_positions: PlanetPositionsInput,
    houses: HousesInput,
    *,
    analyzer: VedicIntelligenceAnalyzer | None = None,
) -> tuple[VedicObservation, ...]:
    """Run the Vedic analyzer and return observations only."""
    engine = analyzer or VedicIntelligenceAnalyzer()
    return engine.analyze(planet_positions=planet_positions, houses=houses).observations


def find_observation(
    observations: tuple[VedicObservation, ...],
    *,
    title: str | None = None,
    observation_id: str | None = None,
    category: ObservationCategory | None = None,
) -> VedicObservation:
    """Return the first observation matching the given filters."""
    for observation in observations:
        if title is not None and observation.title != title:
            continue
        if observation_id is not None and observation.observation_id != observation_id:
            continue
        if category is not None and observation.category != category:
            continue
        return observation
    filters = {
        key: value
        for key, value in {
            "title": title,
            "observation_id": observation_id,
            "category": category,
        }.items()
        if value is not None
    }
    raise AssertionError(f"No observation matched filters: {filters}")


def assert_observation(
    observation: VedicObservation,
    *,
    category: ObservationCategory,
    title: str,
    severity: float,
    confidence: float,
    affected_planets: tuple[str, ...],
    affected_houses: tuple[int, ...],
) -> None:
    """Assert the core structured fields of a Vedic observation."""
    assert observation.category == category
    assert observation.title == title
    assert observation.explanation
    assert observation.severity == severity
    assert observation.confidence == confidence
    assert observation.affected_planets == affected_planets
    assert observation.affected_houses == affected_houses
    assert 0.0 <= observation.severity <= 1.0
    assert 0.0 <= observation.confidence <= 1.0


@pytest.fixture
def frozen_analyzer(monkeypatch: pytest.MonkeyPatch) -> VedicIntelligenceAnalyzer:
    """Return an analyzer with a fixed analysis timestamp."""
    import backend.app.services.reasoning.vedic.analyzer as analyzer_module

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz: Any = None) -> datetime:
            if tz is None:
                return FIXED_ANALYSIS_TIME.replace(tzinfo=None)
            return FIXED_ANALYSIS_TIME

    monkeypatch.setattr(analyzer_module, "datetime", FixedDateTime)
    return VedicIntelligenceAnalyzer()
