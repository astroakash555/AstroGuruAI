"""Comprehensive tests for the Lal Kitab intelligence layer."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.app.services.reasoning.fusion import FusionContext, LalKitabIntelligenceAdapter, normalize_lal_kitab_observation
from backend.app.services.reasoning.fusion.models import FusionEngineId
from backend.app.services.reasoning.lal_kitab import (
    LalKitabAnalysisResult,
    LalKitabIntelligenceAnalyzer,
    LalKitabObservationCategory,
    LalKitabRemedy,
    ReasoningObservation,
    analyze_house_rules,
    analyze_planet_interpretations,
    analyze_planetary_combinations,
    analyze_remedy_observations,
    analyze_rin_debts,
    build_lal_kitab_context,
    generate_remedies,
    make_observation,
    sign_index_from_name,
)
from backend.app.services.reasoning.models import HouseSnapshot, HousesInput, PlanetPositionSnapshot, PlanetPositionsInput
from tests.reasoning.conftest import FIXED_ANALYSIS_TIME, classical_chart, houses_for, p

LK_REFERENCE_TIME = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


def find_lk_observation(
    observations: tuple[ReasoningObservation, ...],
    *,
    observation_id: str | None = None,
    title: str | None = None,
    category: LalKitabObservationCategory | None = None,
) -> ReasoningObservation:
    """Return the first Lal Kitab observation matching filters."""
    for observation in observations:
        if observation_id is not None and observation.observation_id != observation_id:
            continue
        if title is not None and observation.title != title:
            continue
        if category is not None and observation.category != category:
            continue
        return observation
    raise AssertionError(f"No Lal Kitab observation matched: id={observation_id}, title={title}")


def lk_chart(
    lagna: str,
    planets: tuple[PlanetPositionSnapshot, ...],
) -> tuple[PlanetPositionsInput, HousesInput]:
    """Build Lal Kitab chart inputs."""
    return (
        PlanetPositionsInput(ascendant_sign=lagna, planets=planets),
        houses_for(lagna),
    )


def analyze_lk(
    planet_positions: PlanetPositionsInput,
    houses: HousesInput,
    *,
    analyzer: LalKitabIntelligenceAnalyzer | None = None,
) -> LalKitabAnalysisResult:
    """Run the Lal Kitab analyzer."""
    engine = analyzer or LalKitabIntelligenceAnalyzer()
    return engine.analyze(planet_positions=planet_positions, houses=houses)


@pytest.fixture
def standard_lk_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Default Aries lagna chart for Lal Kitab integration tests."""
    return classical_chart("Aries")


@pytest.fixture
def pitra_rin_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    planets = (
        p("Sun", "Sagittarius", 9, 250.0),
        p("Saturn", "Pisces", 12, 350.0),
        p("Moon", "Cancer", 4, 100.0),
        p("Mars", "Aries", 1, 10.0),
        p("Mercury", "Virgo", 6, 165.0),
        p("Jupiter", "Libra", 7, 190.0),
        p("Venus", "Scorpio", 8, 220.0),
        p("Rahu", "Capricorn", 10, 280.0),
        p("Ketu", "Cancer", 4, 100.0),
    )
    return lk_chart("Aries", planets)


@pytest.fixture
def combination_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    planets = (
        p("Sun", "Aries", 1, 10.0),
        p("Moon", "Aries", 1, 11.0),
        p("Mars", "Scorpio", 8, 220.0),
        p("Saturn", "Scorpio", 8, 225.0),
        p("Rahu", "Scorpio", 8, 230.0),
        p("Mercury", "Virgo", 6, 165.0),
        p("Jupiter", "Libra", 7, 190.0),
        p("Venus", "Libra", 7, 195.0),
        p("Ketu", "Taurus", 2, 40.0),
    )
    return lk_chart("Aries", planets)


@pytest.fixture
def frozen_lk_analyzer(monkeypatch: pytest.MonkeyPatch) -> LalKitabIntelligenceAnalyzer:
    import backend.app.services.reasoning.lal_kitab.analyzer as analyzer_module

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None) -> datetime:  # noqa: ANN001
            if tz is None:
                return FIXED_ANALYSIS_TIME.replace(tzinfo=None)
            return FIXED_ANALYSIS_TIME

    monkeypatch.setattr(analyzer_module, "datetime", FixedDateTime)
    return LalKitabIntelligenceAnalyzer()


class TestConstantsAndModels:
    def test_sign_index_from_name(self) -> None:
        assert sign_index_from_name("aries") == 0
        with pytest.raises(ValueError, match="Unknown sign name"):
            sign_index_from_name("Invalid")

    def test_make_observation_clamps_scores(self) -> None:
        observation = make_observation(
            observation_id="lk-test",
            category=LalKitabObservationCategory.PLANET,
            title="Clamp",
            explanation="Test clamp.",
            severity=2.0,
            confidence=-1.0,
        )
        assert observation.severity == 1.0
        assert observation.confidence == 0.0

    def test_chart_context_accessors(self, standard_lk_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_lal_kitab_context(*standard_lk_chart)
        assert context.lagna_sign_name == "Aries"
        assert context.has_planet("Sun")
        assert context.house_of("Sun") == context.get_planet("Sun").house
        assert context.house_lord(1) == "Mars"
        assert context.is_kendra(1) is True
        assert context.is_dusthana(6) is True

        with pytest.raises(KeyError, match="Planet 'Pluto'"):
            context.get_planet("Pluto")


class TestContextBuilding:
    def test_build_context_derives_ketu_from_rahu(self) -> None:
        planet_positions, houses = lk_chart(
            "Aries",
            (
                p("Sun", "Aries", 1, 10.0),
                p("Rahu", "Capricorn", 10, 280.0),
            ),
        )
        context = build_lal_kitab_context(planet_positions, houses)
        assert "Ketu" in context.planets
        assert context.planets["Ketu"].sign_name == "Cancer"

    def test_build_context_requires_lagna(self) -> None:
        with pytest.raises(ValueError, match="Lagna sign is required"):
            build_lal_kitab_context(
                PlanetPositionsInput(planets=(p("Sun", "Aries", 1, 10.0),)),
                HousesInput(cusps=()),
            )


class TestPlanetAnalysis:
    def test_planet_interpretations_for_all_grahas(
        self,
        standard_lk_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_lal_kitab_context(*standard_lk_chart)
        observations = analyze_planet_interpretations(context)
        assert len(observations) == len(context.planets)
        sample = find_lk_observation(
            observations,
            observation_id="lk-planet-sun-h03",
        )
        assert sample.category == LalKitabObservationCategory.PLANET
        assert sample.affected_planets == ("Sun",)
        assert 0.0 <= sample.severity <= 1.0


class TestHouseAnalysis:
    def test_house_profiles_generated_for_all_houses(
        self,
        standard_lk_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_lal_kitab_context(*standard_lk_chart)
        observations = analyze_house_rules(context)
        profiles = [
            item for item in observations if item.observation_id.startswith("lk-house-") and item.observation_id.endswith("-profile")
        ]
        assert len(profiles) == 12

    def test_crowded_house_observation(self, combination_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_lal_kitab_context(*combination_chart)
        crowded = find_lk_observation(
            analyze_house_rules(context),
            observation_id="lk-house-08-crowded",
        )
        assert crowded.category == LalKitabObservationCategory.HOUSE
        assert crowded.metadata["occupant_count"] >= 3

    def test_dusthana_activation(self, combination_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_lal_kitab_context(*combination_chart)
        dusthana = find_lk_observation(
            analyze_house_rules(context),
            observation_id="lk-house-08-dusthana-activation",
        )
        assert dusthana.metadata["dusthana"] is True


class TestRinDebts:
    def test_all_five_rin_types_emitted(
        self,
        standard_lk_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        observations = analyze_rin_debts(build_lal_kitab_context(*standard_lk_chart))
        rin_ids = {item.metadata["rin_id"] for item in observations}
        assert rin_ids == {"pitra_rin", "matra_rin", "stri_rin", "guru_rin", "dev_rin"}

    def test_pitra_rin_present(self, pitra_rin_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observation = find_lk_observation(
            analyze_rin_debts(build_lal_kitab_context(*pitra_rin_chart)),
            observation_id="lk-rin-pitra_rin",
        )
        assert observation.metadata["is_present"] is True
        assert observation.title == "Pitra Rin Present"
        assert observation.severity >= 0.80

    def test_rin_display_names(self, standard_lk_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        matra = find_lk_observation(
            analyze_rin_debts(build_lal_kitab_context(*standard_lk_chart)),
            observation_id="lk-rin-matra_rin",
        )
        assert matra.metadata["rin_name"] == "Matra Rin"


class TestCombinations:
    def test_saturn_rahu_combination(self, combination_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observation = find_lk_observation(
            analyze_planetary_combinations(build_lal_kitab_context(*combination_chart)),
            observation_id="lk-combination-saturn_rahu",
        )
        assert observation.category == LalKitabObservationCategory.COMBINATION
        assert "Saturn" in observation.affected_planets
        assert "Rahu" in observation.affected_planets

    def test_sun_moon_combination(self, combination_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        observation = find_lk_observation(
            analyze_planetary_combinations(build_lal_kitab_context(*combination_chart)),
            observation_id="lk-combination-sun_moon",
        )
        assert observation.affected_houses == (1,)


class TestRemedies:
    def test_generate_remedies_from_pitra_rin(self, pitra_rin_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = build_lal_kitab_context(*pitra_rin_chart)
        rin_observations = analyze_rin_debts(context)
        remedies = generate_remedies(context, rin_observations)
        assert len(remedies) >= 1
        remedy = remedies[0]
        assert isinstance(remedy, LalKitabRemedy)
        assert remedy.title
        assert remedy.explanation
        assert remedy.priority in {"high", "medium", "low"}
        assert remedy.expected_duration
        assert remedy.affected_planets
        assert 0.0 <= remedy.confidence <= 1.0

    def test_remedy_observations_compatible_with_fusion(self, pitra_rin_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        result = analyze_lk(*pitra_rin_chart)
        remedy_observations = [item for item in result.observations if item.category == LalKitabObservationCategory.REMEDY]
        assert remedy_observations
        normalized = normalize_lal_kitab_observation(remedy_observations[0])
        assert normalized.engine == FusionEngineId.LAL_KITAB
        assert normalized.category.startswith("lal_kitab:")

    def test_analyze_remedy_observations_wrapper(self) -> None:
        remedies = (
            LalKitabRemedy(
                remedy_id="test",
                title="Test Remedy",
                explanation="Test explanation.",
                priority="medium",
                expected_duration="40 days",
                affected_planets=("Sun",),
                affected_houses=(1,),
                confidence=0.8,
            ),
        )
        observations = analyze_remedy_observations(remedies)
        assert len(observations) == 1
        assert observations[0].metadata["expected_duration"] == "40 days"


class TestAnalyzerIntegration:
    def test_full_analysis_metadata(self, standard_lk_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        result = analyze_lk(*standard_lk_chart)
        assert result.metadata["engine"] == "lal_kitab_intelligence_v1"
        assert result.metadata["planet_count"] == 9
        assert result.metadata["observation_count"] == len(result.observations)
        assert result.metadata["remedy_count"] == len(result.remedies)
        assert sum(result.metadata["category_counts"].values()) == len(result.observations)

    def test_deterministic_output(self, standard_lk_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        first = analyze_lk(*standard_lk_chart)
        second = analyze_lk(*standard_lk_chart)
        assert [(item.observation_id, item.severity, item.confidence) for item in first.observations] == [
            (item.observation_id, item.severity, item.confidence) for item in second.observations
        ]

    def test_frozen_analyzed_at_timestamp(
        self,
        frozen_lk_analyzer: LalKitabIntelligenceAnalyzer,
        standard_lk_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        result = frozen_lk_analyzer.analyze(
            planet_positions=standard_lk_chart[0],
            houses=standard_lk_chart[1],
        )
        assert result.analyzed_at == FIXED_ANALYSIS_TIME

    def test_modular_pipeline_matches_combined_analyzer(
        self,
        standard_lk_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_lal_kitab_context(*standard_lk_chart)
        base_observations = (
            *analyze_planet_interpretations(context),
            *analyze_house_rules(context),
            *analyze_rin_debts(context),
            *analyze_planetary_combinations(context),
        )
        remedies = generate_remedies(context, base_observations)
        modular_ids = [
            * [item.observation_id for item in base_observations],
            *[item.observation_id for item in analyze_remedy_observations(remedies)],
        ]
        combined_ids = [item.observation_id for item in analyze_lk(*standard_lk_chart).observations]
        assert modular_ids == combined_ids

    def test_fusion_adapter_integration(self, standard_lk_chart: tuple[PlanetPositionsInput, HousesInput]) -> None:
        context = FusionContext(
            planet_positions=standard_lk_chart[0],
            houses=standard_lk_chart[1],
            reference_datetime=LK_REFERENCE_TIME,
        )
        observations = LalKitabIntelligenceAdapter().analyze(context)
        assert len(observations) > 0
        assert all(item.engine == FusionEngineId.LAL_KITAB for item in observations)

    def test_planet_house_fallback_from_sign(self) -> None:
        planet_positions = PlanetPositionsInput(
            ascendant_sign="Aries",
            planets=(p("Sun", "Gemini", None, 70.0),),
        )
        context = build_lal_kitab_context(planet_positions, houses_for("Aries"))
        assert context.get_planet("Sun").house == 3

    def test_invalid_sign_raises(self) -> None:
        planet_positions = PlanetPositionsInput(
            ascendant_sign="Aries",
            planets=(p("Sun", "NotASign", 1, 10.0),),
        )
        with pytest.raises(ValueError, match="Unknown sign name"):
            build_lal_kitab_context(planet_positions, houses_for("Aries"))

    def test_resolve_lagna_from_first_house_cusp(self) -> None:
        planet_positions = PlanetPositionsInput(
            ascendant_sign=None,
            planets=(p("Sun", "Leo", 1, 130.0),),
        )
        houses = HousesInput(
            ascendant_sign=None,
            cusps=(HouseSnapshot(number=1, sign="Leo"),),
        )
        context = build_lal_kitab_context(planet_positions, houses)
        assert context.lagna_sign_name == "Leo"

    def test_house_lord_dusthana_observation(self) -> None:
        planets = (
            p("Sun", "Aries", 1, 10.0),
            p("Moon", "Cancer", 4, 100.0),
            p("Mars", "Aries", 1, 11.0),
            p("Mercury", "Gemini", 3, 70.0),
            p("Jupiter", "Sagittarius", 9, 250.0),
            p("Venus", "Scorpio", 8, 220.0),
            p("Saturn", "Capricorn", 10, 280.0),
            p("Rahu", "Capricorn", 10, 285.0),
            p("Ketu", "Cancer", 4, 100.0),
        )
        context = build_lal_kitab_context(*lk_chart("Aries", planets))
        observation = find_lk_observation(
            analyze_house_rules(context),
            observation_id="lk-house-07-lord-dusthana",
        )
        assert "dusthana" in observation.explanation.lower()
