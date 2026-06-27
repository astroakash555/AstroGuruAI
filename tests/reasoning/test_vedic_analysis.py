"""Comprehensive tests for the Vedic horoscope intelligence layer."""

from __future__ import annotations

import pytest

from backend.app.services.reasoning.models import (
    HousesInput,
    PlanetPositionSnapshot,
    PlanetPositionsInput,
)
from backend.app.services.reasoning.vedic import (
    ObservationCategory,
    VedicChartContext,
    VedicIntelligenceAnalyzer,
    analyze_aspects,
    analyze_houses,
    analyze_planet_strengths,
    build_vedic_context,
    detect_doshas,
    detect_yogas,
    make_observation,
)
from backend.app.services.reasoning.vedic.constants import (
    DignityState,
    VedicPlanetRecord,
    angular_separation,
    house_distance,
    lord_of_sign,
    sign_index_from_name,
)
from backend.app.services.reasoning.vedic.planet_strength import (
    analyze_planet_strengths as planet_strength_module,
    classify_dignity,
    detect_combustion,
)
from tests.reasoning.conftest import (
    FIXED_ANALYSIS_TIME,
    all_classical_planets,
    analyze,
    assert_observation,
    chart,
    classical_chart,
    find_observation,
    houses_for,
    p,
    whole_sign_cusps,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _titles(observations: tuple) -> set[str]:
    return {item.title for item in observations}


def _by_id(observations: tuple) -> dict[str, object]:
    return {item.observation_id: item for item in observations}


# ---------------------------------------------------------------------------
# Realistic chart fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def dignity_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Aries lagna chart isolating dignity, combustion, and retrograde states."""
    planets = (
        p("Sun", "Aries", 1, 10.0),
        p("Mercury", "Aries", 1, 12.0),
        p("Moon", "Scorpio", 8, 220.0),
        p("Mars", "Cancer", 4, 100.0),
        p("Jupiter", "Capricorn", 10, 280.0),
        p("Venus", "Virgo", 6, 165.0),
        p("Saturn", "Libra", 7, 195.0, is_retrograde=True),
        p("Rahu", "Gemini", 3, 70.0),
        p("Ketu", "Sagittarius", 9, 250.0),
    )
    return chart("Aries", planets, moon_sign="Scorpio")


@pytest.fixture
def house_analysis_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Taurus lagna chart with empty, benefic, and malefic house occupancy."""
    planets = (
        p("Sun", "Gemini", 2, 70.0),
        p("Moon", "Leo", 4, 130.0),
        p("Mars", "Cancer", 3, 100.0),
        p("Mercury", "Gemini", 2, 72.0),
        p("Jupiter", "Pisces", 11, 340.0),
        p("Venus", "Cancer", 3, 102.0),
        p("Saturn", "Aquarius", 10, 310.0),
        p("Rahu", "Virgo", 5, 160.0),
        p("Ketu", "Pisces", 11, 340.0),
    )
    return chart("Taurus", planets, moon_sign="Leo")


@pytest.fixture
def yoga_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Aries lagna chart engineered for multiple wealth and status yogas."""
    planets = (
        p("Sun", "Leo", 5, 130.0),
        p("Mercury", "Leo", 5, 145.0),
        p("Moon", "Cancer", 4, 100.0),
        p("Jupiter", "Libra", 7, 190.0),
        p("Mars", "Capricorn", 10, 280.0),
        p("Venus", "Aquarius", 11, 300.0),
        p("Saturn", "Aquarius", 11, 305.0),
        p("Rahu", "Taurus", 2, 45.0),
        p("Ketu", "Scorpio", 8, 220.0),
    )
    return chart("Aries", planets, moon_sign="Cancer")


@pytest.fixture
def dosha_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Cancer lagna chart with multiple classical dosha combinations."""
    planets = (
        p("Sun", "Gemini", 12, 70.0),
        p("Moon", "Scorpio", 5, 220.0),
        p("Mars", "Libra", 4, 190.0),
        p("Mercury", "Gemini", 12, 75.0),
        p("Jupiter", "Gemini", 12, 80.0),
        p("Venus", "Taurus", 11, 40.0),
        p("Saturn", "Taurus", 11, 42.0),
        p("Rahu", "Gemini", 12, 78.0),
        p("Ketu", "Sagittarius", 6, 260.0),
    )
    return chart("Cancer", planets, moon_sign="Scorpio")


@pytest.fixture
def aspect_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Leo lagna chart highlighting classical and special graha aspects."""
    planets = (
        p("Sun", "Leo", 1, 120.0),
        p("Moon", "Aquarius", 7, 300.0),
        p("Mars", "Leo", 1, 125.0),
        p("Mercury", "Sagittarius", 5, 255.0),
        p("Jupiter", "Leo", 1, 128.0),
        p("Venus", "Scorpio", 4, 220.0),
        p("Saturn", "Libra", 3, 190.0),
        p("Rahu", "Leo", 1, 130.0),
        p("Ketu", "Aquarius", 7, 310.0),
    )
    return chart("Leo", planets, moon_sign="Aquarius")


@pytest.fixture
def kaal_sarp_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Virgo lagna chart with all classical grahas enclosed by the nodal axis."""
    planets = all_classical_planets(
        "Virgo",
        {
            "Sun": ("Gemini", 10, 70.0),
            "Moon": ("Cancer", 11, 100.0),
            "Mars": ("Cancer", 11, 105.0),
            "Mercury": ("Leo", 12, 130.0),
            "Jupiter": ("Leo", 12, 135.0),
            "Venus": ("Virgo", 1, 150.0),
            "Saturn": ("Libra", 2, 190.0),
        },
        nodes={
            "Rahu": ("Gemini", 10, 60.0),
            "Ketu": ("Sagittarius", 4, 240.0),
        },
    )
    return chart("Virgo", planets)


@pytest.fixture
def kemadruma_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Scorpio lagna chart with an isolated Moon and no qualifying support."""
    planets = (
        p("Sun", "Aries", 6, 20.0),
        p("Moon", "Aquarius", 4, 300.0),
        p("Mars", "Gemini", 8, 70.0),
        p("Mercury", "Gemini", 8, 75.0),
        p("Jupiter", "Cancer", 9, 100.0),
        p("Venus", "Gemini", 8, 78.0),
        p("Saturn", "Cancer", 9, 105.0),
        p("Rahu", "Gemini", 8, 80.0),
        p("Ketu", "Sagittarius", 2, 250.0),
    )
    return chart("Scorpio", planets, moon_sign="Aquarius")


# ---------------------------------------------------------------------------
# Constants and context edge cases
# ---------------------------------------------------------------------------


class TestConstantsAndContext:
    def test_sign_index_from_name_normalizes_case(self) -> None:
        assert sign_index_from_name("aries") == 0
        assert sign_index_from_name("PISCES") == 11

    def test_sign_index_from_name_rejects_unknown_sign(self) -> None:
        with pytest.raises(ValueError, match="Unknown sign name"):
            sign_index_from_name("NotASign")

    def test_house_distance_and_angular_separation(self) -> None:
        assert house_distance(1, 7) == 7
        assert house_distance(11, 2) == 4
        assert angular_separation(350.0, 10.0) == 20.0
        assert angular_separation(10.0, 350.0) == 20.0

    def test_lord_of_sign(self) -> None:
        assert lord_of_sign(0) == "Mars"
        assert lord_of_sign(4) == "Sun"

    def test_build_context_derives_ketu_from_rahu(self) -> None:
        planet_positions = PlanetPositionsInput(
            ascendant_sign="Aries",
            planets=(p("Rahu", "Gemini", 3, 70.0),),
        )
        context = build_vedic_context(planet_positions, houses_for("Aries"))
        assert context.has_planet("Ketu")
        assert context.get_planet("Ketu").sign_name == "Sagittarius"
        assert context.get_planet("Ketu").longitude == pytest.approx(250.0)

    def test_build_context_infers_house_from_sign_when_missing(self) -> None:
        snapshot = PlanetPositionSnapshot(
            name="Sun",
            sign="Aries",
            house=None,
            longitude=10.0,
        )
        context = build_vedic_context(
            PlanetPositionsInput(planets=(snapshot,)),
            houses_for("Aries"),
        )
        assert context.get_planet("Sun").house == 1

    def test_build_context_requires_lagna(self) -> None:
        with pytest.raises(ValueError, match="Lagna sign is required"):
            build_vedic_context(
                PlanetPositionsInput(planets=()),
                HousesInput(cusps=()),
            )

    def test_context_get_planet_raises_for_missing_graha(self) -> None:
        planet_positions, houses = chart("Aries", (p("Sun", "Aries", 1, 10.0),))
        context = build_vedic_context(planet_positions, houses)
        with pytest.raises(KeyError, match="Planet 'Mars'"):
            context.get_planet("Mars")

    def test_context_aspect_distances(self, aspect_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_vedic_context(*aspect_chart)
        assert context.aspect_distances("Jupiter", "Moon") == (7,)
        assert context.aspect_distances("Sun", "Mercury") == ()

    def test_build_context_uses_first_house_cusp_without_ascendant_field(self) -> None:
        houses = HousesInput(
            house_system="whole_sign",
            cusps=whole_sign_cusps("Aries"),
        )
        context = build_vedic_context(
            PlanetPositionsInput(planets=(p("Sun", "Aries", 1, 10.0),)),
            houses,
        )
        assert context.lagna_sign_name == "Aries"

    def test_normalize_sign_name_returns_unknown_sign_unchanged(self) -> None:
        from backend.app.services.reasoning.vedic.analyzer import _normalize_sign_name

        assert _normalize_sign_name("Unknown") == "Unknown"

    def test_make_observation_clamps_scores(self) -> None:
        observation = make_observation(
            observation_id="test",
            category=ObservationCategory.PLANET_STRENGTH,
            title="Clamp Test",
            explanation="Values should be bounded.",
            severity=1.5,
            confidence=-0.2,
        )
        assert observation.severity == 1.0
        assert observation.confidence == 0.0


# ---------------------------------------------------------------------------
# Planet strength
# ---------------------------------------------------------------------------


class TestPlanetStrength:
    @pytest.mark.parametrize(
        ("planet_name", "sign", "house", "longitude", "expected_title", "severity", "confidence"),
        [
            ("Sun", "Aries", 1, 10.0, "Sun in Exaltation", 0.85, 0.95),
            ("Moon", "Scorpio", 8, 220.0, "Moon in Debilitation", 0.8, 0.93),
            ("Mars", "Aries", 1, 12.0, "Mars in Own Sign", 0.75, 0.9),
            ("Venus", "Capricorn", 10, 280.0, "Venus in Friendly Sign", 0.55, 0.82),
            ("Venus", "Leo", 5, 128.0, "Venus in Enemy Sign", 0.65, 0.85),
        ],
        ids=["exaltation", "debilitation", "own_sign", "friendly_sign", "enemy_sign"],
    )
    def test_dignity_observations(
        self,
        planet_name: str,
        sign: str,
        house: int,
        longitude: float,
        expected_title: str,
        severity: float,
        confidence: float,
    ) -> None:
        observations = analyze(
            *classical_chart(
                "Aries",
                {
                    planet_name: p(
                        planet_name,
                        sign,
                        house,
                        longitude,
                    )
                },
            )
        )
        observation = find_observation(observations, title=expected_title)
        assert_observation(
            observation,
            category=ObservationCategory.PLANET_STRENGTH,
            title=expected_title,
            severity=severity,
            confidence=confidence,
            affected_planets=(planet_name,),
            affected_houses=(house,),
        )

    def test_classify_dignity_neutral_for_nodes(self) -> None:
        assert classify_dignity("Rahu", 3) == DignityState.NEUTRAL_SIGN

    def test_combustion_observation(self, dignity_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*dignity_chart)
        observation = find_observation(observations, title="Mercury Combust")
        assert observation.category == ObservationCategory.PLANET_STRENGTH
        assert observation.affected_planets == ("Mercury", "Sun")
        assert observation.affected_houses == (1, 1)
        assert observation.confidence == 0.9
        assert observation.severity > 0.45
        assert "combustion orb 14" in observation.explanation

    def test_detect_combustion_returns_none_outside_orb(self) -> None:
        planet_positions, houses = chart(
            "Aries",
            (
                p("Sun", "Aries", 1, 10.0),
                p("Mercury", "Pisces", 12, 350.0),
            ),
        )
        context = build_vedic_context(planet_positions, houses)
        assert detect_combustion(context, "Mercury") is None

    def test_retrograde_observation(self, dignity_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*dignity_chart)
        observation = find_observation(observations, title="Saturn Retrograde")
        assert_observation(
            observation,
            category=ObservationCategory.PLANET_STRENGTH,
            title="Saturn Retrograde",
            severity=0.55,
            confidence=0.95,
            affected_planets=("Saturn",),
            affected_houses=(7,),
        )


# ---------------------------------------------------------------------------
# House analysis
# ---------------------------------------------------------------------------


class TestHouseAnalysis:
    def test_empty_house_observation(self, house_analysis_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*house_analysis_chart)
        observation = find_observation(observations, observation_id="house-01-empty")
        assert observation.category == ObservationCategory.HOUSE
        assert observation.title == "House 1 Unoccupied"
        assert observation.affected_houses[0] == 1
        assert observation.metadata["is_empty"] is True
        assert observation.confidence == 0.95

    def test_house_lord_placement_observation(
        self,
        house_analysis_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        observations = analyze(*house_analysis_chart)
        observation = find_observation(observations, observation_id="house-02-lord-placement")
        assert observation.category == ObservationCategory.HOUSE
        assert observation.title == "House 2 Lord Placement"
        assert "Mercury" in observation.explanation
        assert observation.affected_houses == (2, 2)
        assert observation.confidence == 0.84

    def test_benefic_influence_observation(
        self,
        house_analysis_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        observations = analyze(*house_analysis_chart)
        observation = find_observation(observations, observation_id="house-02-benefic-influence")
        assert observation.title == "Benefic Influence on House 2"
        assert set(observation.affected_planets) == {"Mercury"}
        assert observation.affected_houses == (2,)
        assert observation.severity == pytest.approx(0.45, abs=0.01)

    def test_malefic_influence_observation(
        self,
        house_analysis_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        observations = analyze(*house_analysis_chart)
        observation = find_observation(observations, observation_id="house-03-malefic-influence")
        assert observation.title == "Malefic Influence on House 3"
        assert "Mars" in observation.affected_planets
        assert observation.affected_houses == (3,)
        assert observation.severity > 0.45

    def test_house_strength_scores_are_deterministic(
        self,
        house_analysis_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        first = analyze(*house_analysis_chart)
        second = analyze(*house_analysis_chart)
        first_scores = {
            obs.observation_id: obs.severity
            for obs in first
            if obs.observation_id.endswith("-strength")
        }
        second_scores = {
            obs.observation_id: obs.severity
            for obs in second
            if obs.observation_id.endswith("-strength")
        }
        assert first_scores == second_scores


# ---------------------------------------------------------------------------
# Yoga detection
# ---------------------------------------------------------------------------


class TestYogaDetection:
    def test_gaj_kesari_yoga(self, yoga_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*yoga_chart)
        observation = find_observation(observations, title="Gaj Kesari Yoga")
        assert_observation(
            observation,
            category=ObservationCategory.YOGA,
            title="Gaj Kesari Yoga",
            severity=0.78,
            confidence=0.92,
            affected_planets=("Moon", "Jupiter"),
            affected_houses=(4, 7),
        )

    def test_budhaditya_yoga(self, yoga_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*yoga_chart)
        observation = find_observation(observations, title="Budhaditya Yoga")
        assert observation.affected_planets == ("Sun", "Mercury")
        assert observation.affected_houses == (5, 5)
        assert observation.severity == 0.72
        assert observation.confidence == 0.9

    def test_raj_yoga(self, yoga_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*yoga_chart)
        observation = find_observation(observations, title="Raj Yoga")
        assert observation.category == ObservationCategory.YOGA
        assert "Kendra and trikona lords are connected" in observation.explanation
        assert observation.confidence == 0.87
        assert len(observation.affected_planets) >= 2

    def test_dhana_yoga(self, yoga_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*yoga_chart)
        observation = find_observation(observations, title="Dhana Yoga")
        assert observation.affected_planets == ("Venus", "Saturn")
        assert 11 in observation.affected_houses
        assert observation.confidence == 0.84

    def test_panch_mahapurusha_yoga(self, yoga_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*yoga_chart)
        observation = find_observation(observations, title="Panch Mahapurusha Yoga")
        assert "Ruchaka Yoga" in observation.explanation
        assert "Mars" in observation.affected_planets
        assert 10 in observation.affected_houses
        assert observation.confidence == 0.9

    def test_neecha_bhanga_yoga_when_debilitation_is_cancelled(self) -> None:
        planets = (
            p("Sun", "Aries", 1, 10.0),
            p("Moon", "Scorpio", 8, 220.0),
            p("Mars", "Cancer", 4, 100.0),
            p("Mercury", "Pisces", 12, 350.0),
            p("Jupiter", "Cancer", 4, 102.0),
            p("Venus", "Virgo", 6, 165.0),
            p("Saturn", "Libra", 7, 195.0),
            p("Rahu", "Gemini", 3, 70.0),
            p("Ketu", "Sagittarius", 9, 250.0),
        )
        observations = analyze(*chart("Aries", planets))
        observation = find_observation(observations, title="Neecha Bhanga Raj Yoga")
        assert "Mercury" in observation.affected_planets
        assert observation.confidence == 0.88

    def test_vipreet_raj_yoga(self) -> None:
        planets = (
            p("Sun", "Aries", 1, 10.0),
            p("Moon", "Aries", 1, 12.0),
            p("Mars", "Scorpio", 8, 220.0),
            p("Mercury", "Virgo", 6, 165.0),
            p("Jupiter", "Pisces", 12, 350.0),
            p("Venus", "Libra", 7, 190.0),
            p("Saturn", "Taurus", 2, 45.0),
            p("Rahu", "Gemini", 3, 70.0),
            p("Ketu", "Sagittarius", 9, 250.0),
        )
        observations = analyze(*chart("Aries", planets))
        observation = find_observation(observations, title="Vipreet Raj Yoga")
        assert "Harsha Yoga" in observation.explanation
        assert observation.confidence == 0.86


# ---------------------------------------------------------------------------
# Dosha detection
# ---------------------------------------------------------------------------


class TestDoshaDetection:
    def test_manglik_dosha(self, dosha_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*dosha_chart)
        observation = find_observation(observations, title="Manglik Dosha")
        assert observation.affected_planets == ("Mars",)
        assert observation.affected_houses == (4,)
        assert observation.confidence in {0.88, 0.78}
        assert observation.severity > 0.0

    def test_manglik_mitigation_lowers_severity(self) -> None:
        planets = (
            p("Sun", "Gemini", 3, 70.0),
            p("Moon", "Cancer", 4, 100.0),
            p("Mars", "Aries", 7, 10.0),
            p("Mercury", "Gemini", 3, 72.0),
            p("Jupiter", "Aries", 7, 12.0),
            p("Venus", "Taurus", 8, 45.0),
            p("Saturn", "Aquarius", 5, 310.0),
            p("Rahu", "Gemini", 3, 74.0),
            p("Ketu", "Sagittarius", 11, 250.0),
        )
        observations = analyze(*chart("Libra", planets))
        observation = find_observation(observations, title="Manglik Dosha")
        assert observation.metadata["mitigating_factors"]
        assert observation.confidence == 0.78
        assert observation.severity < 0.65

    def test_kaal_sarp_dosha(self, kaal_sarp_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*kaal_sarp_chart)
        observation = find_observation(observations, title="Kaal Sarp Dosha")
        assert observation.severity == 0.9
        assert observation.confidence == 0.92
        assert "Rahu" in observation.affected_planets
        assert "Ketu" in observation.affected_planets
        assert observation.metadata["subtype"] == "Ghatak"

    def test_kaal_sarp_not_present_when_planet_outside_axis(self) -> None:
        planets = all_classical_planets(
            "Aries",
            {
                "Sun": ("Gemini", 3, 70.0),
                "Moon": ("Cancer", 4, 100.0),
                "Mars": ("Cancer", 4, 105.0),
                "Mercury": ("Leo", 5, 130.0),
                "Jupiter": ("Leo", 5, 135.0),
                "Venus": ("Virgo", 6, 165.0),
                "Saturn": ("Pisces", 12, 350.0),
            },
            nodes={
                "Rahu": ("Gemini", 3, 60.0),
                "Ketu": ("Sagittarius", 9, 240.0),
            },
        )
        observations = analyze(*chart("Aries", planets))
        assert "Kaal Sarp Dosha" not in _titles(observations)

    def test_guru_chandal_dosha(self, dosha_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*dosha_chart)
        observation = find_observation(observations, title="Guru Chandal Yoga")
        assert observation.affected_planets == ("Jupiter", "Rahu")
        assert observation.affected_houses == (12,)
        assert observation.severity == 0.74
        assert observation.confidence == 0.9

    def test_kemadruma_dosha(self, kemadruma_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*kemadruma_chart)
        observation = find_observation(observations, title="Kemadruma Yoga")
        assert observation.affected_planets == ("Moon",)
        assert observation.affected_houses == (4, 5, 3)
        assert observation.severity == 0.7
        assert observation.confidence == 0.86

    def test_kemadruma_not_present_when_moon_is_supported(self) -> None:
        planets = (
            p("Sun", "Aries", 6, 20.0),
            p("Moon", "Aquarius", 4, 300.0),
            p("Mars", "Taurus", 7, 45.0),
            p("Mercury", "Gemini", 8, 70.0),
            p("Jupiter", "Pisces", 5, 350.0),
            p("Venus", "Gemini", 8, 75.0),
            p("Saturn", "Cancer", 9, 100.0),
            p("Rahu", "Gemini", 8, 80.0),
            p("Ketu", "Sagittarius", 2, 250.0),
        )
        observations = analyze(*chart("Scorpio", planets))
        assert "Kemadruma Yoga" not in _titles(observations)

    def test_guru_chandal_with_ketu(self) -> None:
        planets = (
            p("Sun", "Aries", 1, 10.0),
            p("Moon", "Taurus", 2, 40.0),
            p("Mars", "Gemini", 3, 70.0),
            p("Mercury", "Cancer", 4, 100.0),
            p("Jupiter", "Sagittarius", 9, 260.0),
            p("Venus", "Capricorn", 10, 280.0),
            p("Saturn", "Aquarius", 11, 310.0),
            p("Rahu", "Gemini", 3, 72.0),
            p("Ketu", "Sagittarius", 9, 262.0),
        )
        observations = analyze(*chart("Aries", planets))
        observation = find_observation(observations, title="Guru Chandal Yoga")
        assert observation.affected_planets == ("Jupiter", "Ketu")
        assert observation.metadata["node"] == "Ketu"

    def test_individual_detectors_return_none_when_prerequisites_are_missing(self) -> None:
        from backend.app.services.reasoning.vedic.doshas import _detect_kaal_sarp, _detect_manglik
        from backend.app.services.reasoning.vedic.yogas import _detect_budhaditya, _detect_gaj_kesari

        planet_positions, houses = chart("Aries", (p("Sun", "Aries", 1, 10.0),))
        context = build_vedic_context(planet_positions, houses)
        assert _detect_gaj_kesari(context) is None
        assert _detect_budhaditya(context) is None
        assert _detect_manglik(context) is None
        assert _detect_kaal_sarp(context) is None
        assert analyze_aspects(context) == ()

    def test_pitra_dosha(self, dosha_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observations = analyze(*dosha_chart)
        observation = find_observation(observations, title="Pitra Dosha")
        assert "Sun" in observation.affected_planets
        assert 9 in observation.affected_houses or 12 in observation.affected_houses
        assert observation.confidence == 0.85
        assert observation.metadata["active_triggers"]


# ---------------------------------------------------------------------------
# Aspect analysis
# ---------------------------------------------------------------------------


class TestAspectAnalysis:
    def test_standard_seventh_aspect(self, aspect_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_vedic_context(*aspect_chart)
        observations = analyze_aspects(context)
        observation = find_observation(observations, title="Jupiter Aspects Moon")
        assert observation.affected_planets == ("Jupiter", "Moon")
        assert observation.affected_houses == (1, 7)
        assert observation.metadata["aspect_distance"] == 7
        assert observation.confidence == 0.88

    def test_mars_special_fourth_aspect(self, aspect_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_vedic_context(*aspect_chart)
        observations = analyze_aspects(context)
        observation = find_observation(
            observations,
            title="Mars Special 4th Aspect on Venus",
        )
        assert observation.affected_planets == ("Mars", "Venus")
        assert observation.affected_houses == (1, 4)
        assert observation.metadata["aspect_type"] == "mars_special"
        assert observation.confidence == 0.9

    def test_jupiter_special_fifth_aspect(self, aspect_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_vedic_context(*aspect_chart)
        observations = analyze_aspects(context)
        observation = find_observation(
            observations,
            title="Jupiter Special 5th Aspect on Mercury",
        )
        assert observation.metadata["aspect_distance"] == 5
        assert observation.metadata["aspect_type"] == "jupiter_special"

    def test_saturn_special_third_aspect(self, aspect_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_vedic_context(*aspect_chart)
        observations = analyze_aspects(context)
        observation = find_observation(
            observations,
            title="Saturn Special 3rd Aspect on Mercury",
        )
        assert observation.metadata["aspect_distance"] == 3
        assert observation.metadata["aspect_type"] == "saturn_special"

    def test_rahu_ketu_influences(self, aspect_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_vedic_context(*aspect_chart)
        observations = analyze_aspects(context)
        placement = find_observation(observations, title="Rahu Axis Influence")
        conjunction = find_observation(observations, title="Rahu Conjoins Sun")
        assert placement.affected_planets == ("Rahu",)
        assert conjunction.affected_planets == ("Rahu", "Sun")
        assert placement.confidence == 0.87
        assert conjunction.confidence == 0.89


# ---------------------------------------------------------------------------
# Analyzer integration and determinism
# ---------------------------------------------------------------------------


class TestAnalyzerIntegration:
    def test_full_analysis_metadata(self, yoga_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        analyzer = VedicIntelligenceAnalyzer()
        result = analyzer.analyze(planet_positions=yoga_chart[0], houses=yoga_chart[1])
        assert result.metadata["engine"] == "vedic_intelligence_v1"
        assert result.metadata["lagna_sign"] == "Aries"
        assert result.metadata["planet_count"] == 9
        assert result.metadata["observation_count"] == len(result.observations)
        assert sum(result.metadata["category_counts"].values()) == len(result.observations)

    def test_deterministic_observation_snapshot(
        self,
        yoga_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        first = analyze(*yoga_chart)
        second = analyze(*yoga_chart)
        assert [(item.observation_id, item.severity, item.confidence) for item in first] == [
            (item.observation_id, item.severity, item.confidence) for item in second
        ]

    def test_frozen_analyzed_at_timestamp(
        self,
        frozen_analyzer: VedicIntelligenceAnalyzer,
        yoga_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        result = frozen_analyzer.analyze(planet_positions=yoga_chart[0], houses=yoga_chart[1])
        assert result.analyzed_at == FIXED_ANALYSIS_TIME

    def test_modular_pipeline_matches_combined_analyzer(
        self,
        yoga_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_vedic_context(*yoga_chart)
        modular_ids = [
            item.observation_id
            for item in (
                *analyze_planet_strengths(context),
                *analyze_houses(context),
                *detect_yogas(context),
                *detect_doshas(context),
                *analyze_aspects(context),
            )
        ]
        combined_ids = [item.observation_id for item in analyze(*yoga_chart)]
        assert modular_ids == combined_ids

    def test_budhaditya_combust_branch(self) -> None:
        planets = (
            p("Sun", "Leo", 5, 130.0),
            p("Mercury", "Leo", 5, 131.0),
            p("Moon", "Cancer", 4, 100.0),
            p("Mars", "Aries", 1, 10.0),
            p("Jupiter", "Libra", 7, 190.0),
            p("Venus", "Virgo", 6, 165.0),
            p("Saturn", "Aquarius", 11, 305.0),
            p("Rahu", "Gemini", 3, 70.0),
            p("Ketu", "Sagittarius", 9, 250.0),
        )
        observations = analyze(*chart("Aries", planets))
        observation = find_observation(observations, title="Budhaditya Yoga")
        assert observation.severity == 0.58
        assert observation.confidence == 0.75
        assert observation.metadata["mercury_combust"] is True

    def test_context_methods_used_by_rules(self) -> None:
        record = VedicPlanetRecord(
            name="Sun",
            longitude=10.0,
            sign_index=0,
            sign_name="Aries",
            house=1,
            is_retrograde=False,
        )
        context = VedicChartContext(
            lagna_sign_index=0,
            lagna_sign_name="Aries",
            planets={"Sun": record},
            house_lords={house: "Mars" for house in range(1, 13)},
            planets_by_house={house: ("Sun",) if house == 1 else () for house in range(1, 13)},
        )
        assert context.house_lord(1) == "Mars"
        assert context.planets_in_house(1) == ("Sun",)
        assert context.is_in_kendra_from("Sun", 1) is True

    def test_planet_strength_skips_nodes_for_dignity_only(self) -> None:
        planet_positions, houses = chart(
            "Aries",
            (
                p("Sun", "Aries", 1, 10.0),
                p("Rahu", "Gemini", 3, 70.0),
            ),
        )
        context = build_vedic_context(planet_positions, houses)
        titles = {item.title for item in planet_strength_module(context)}
        assert not any(title.startswith("Rahu in") for title in titles)
