"""Unit tests for the Vedic horoscope intelligence layer."""

from __future__ import annotations

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
    classify_dignity,
)
from backend.app.services.reasoning.vedic.constants import DignityState


def _sample_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    planet_positions = PlanetPositionsInput(
        ascendant_sign="Taurus",
        moon_sign="Leo",
        planets=(
            PlanetPositionSnapshot(name="Sun", longitude=280.0, sign="Capricorn", house=9),
            PlanetPositionSnapshot(name="Moon", longitude=130.0, sign="Leo", house=4),
            PlanetPositionSnapshot(name="Mars", longitude=100.0, sign="Cancer", house=3, is_retrograde=True),
            PlanetPositionSnapshot(name="Mercury", longitude=282.0, sign="Capricorn", house=9),
            PlanetPositionSnapshot(name="Jupiter", longitude=220.0, sign="Scorpio", house=7),
            PlanetPositionSnapshot(name="Venus", longitude=310.0, sign="Aquarius", house=10),
            PlanetPositionSnapshot(name="Saturn", longitude=20.0, sign="Aries", house=12),
            PlanetPositionSnapshot(name="Rahu", longitude=150.0, sign="Virgo", house=5),
            PlanetPositionSnapshot(name="Ketu", longitude=330.0, sign="Pisces", house=11),
        ),
    )
    houses = HousesInput(
        ascendant_sign="Taurus",
        house_system="whole_sign",
        cusps=tuple(
            HouseSnapshot(number=house, sign=sign)
            for house, sign in (
                (1, "Taurus"),
                (2, "Gemini"),
                (3, "Cancer"),
                (4, "Leo"),
                (5, "Virgo"),
                (6, "Libra"),
                (7, "Scorpio"),
                (8, "Sagittarius"),
                (9, "Capricorn"),
                (10, "Aquarius"),
                (11, "Pisces"),
                (12, "Aries"),
            )
        ),
    )
    return planet_positions, houses


def test_classify_dignity_exaltation_and_debilitation():
    assert classify_dignity("Sun", 0) == DignityState.EXALTATION
    assert classify_dignity("Sun", 6) == DignityState.DEBILITATION
    assert classify_dignity("Mars", 0) == DignityState.OWN_SIGN


def test_vedic_analyzer_returns_structured_observations():
    planet_positions, houses = _sample_chart()
    result = VedicIntelligenceAnalyzer().analyze(
        planet_positions=planet_positions,
        houses=houses,
    )

    assert result.observations
    assert result.metadata["engine"] == "vedic_intelligence_v1"
    assert result.metadata["observation_count"] == len(result.observations)

    sample = result.observations[0]
    assert sample.category in ObservationCategory
    assert sample.title
    assert sample.explanation
    assert 0.0 <= sample.severity <= 1.0
    assert 0.0 <= sample.confidence <= 1.0


def test_vedic_analyzer_detects_gaj_kesari_yoga():
    planet_positions, houses = _sample_chart()
    result = VedicIntelligenceAnalyzer().analyze(
        planet_positions=planet_positions,
        houses=houses,
    )
    yoga_titles = {
        observation.title
        for observation in result.observations
        if observation.category == ObservationCategory.YOGA
    }
    assert "Gaj Kesari Yoga" in yoga_titles


def test_vedic_analyzer_detects_manglik_and_retrograde():
    planet_positions, houses = _sample_chart()
    result = VedicIntelligenceAnalyzer().analyze(
        planet_positions=planet_positions,
        houses=houses,
    )
    titles = {observation.title for observation in result.observations}
    assert "Manglik Dosha" in titles
    assert "Mars Retrograde" in titles


def test_vedic_analyzer_requires_lagna_sign():
    with pytest.raises(ValueError, match="Lagna sign is required"):
        VedicIntelligenceAnalyzer().analyze(
            planet_positions=PlanetPositionsInput(planets=()),
            houses=HousesInput(cusps=()),
        )
