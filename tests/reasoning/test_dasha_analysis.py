"""Comprehensive tests for the Dasha intelligence layer."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.app.services.reasoning.dasha import (
    DashaAnalysisResult,
    DashaIntelligenceAnalyzer,
    DashaObservationCategory,
    ReasoningObservation,
    analyze_antardasha,
    analyze_combined_effects,
    analyze_dignity_modifiers,
    analyze_domain_activation,
    analyze_event_windows,
    analyze_house_activation,
    analyze_mahadasha,
    analyze_pratyantardasha,
    build_dasha_context,
    event_windows_to_observations,
    lord_of_sign,
    make_observation,
    sign_index_from_name,
)
from backend.app.services.reasoning.fusion import DashaIntelligenceAdapter, FusionContext, normalize_dasha_observation
from backend.app.services.reasoning.fusion.models import FusionEngineId
from backend.app.services.reasoning.models import (
    DashaInput,
    DashaPeriodSnapshot,
    HouseSnapshot,
    HousesInput,
    PlanetPositionSnapshot,
    PlanetPositionsInput,
)
from tests.reasoning.conftest import FIXED_ANALYSIS_TIME, classical_chart, houses_for, p

DASHA_REFERENCE_TIME = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
PERIOD_START = datetime(2024, 1, 1, tzinfo=timezone.utc)
PERIOD_END = datetime(2026, 12, 31, tzinfo=timezone.utc)


def find_dasha_observation(
    observations: tuple[ReasoningObservation, ...],
    *,
    observation_id: str | None = None,
    title: str | None = None,
    category: DashaObservationCategory | None = None,
) -> ReasoningObservation:
    """Return the first Dasha observation matching filters."""
    for observation in observations:
        if observation_id is not None and observation.observation_id != observation_id:
            continue
        if title is not None and observation.title != title:
            continue
        if category is not None and observation.category != category:
            continue
        return observation
    raise AssertionError(f"No Dasha observation matched: id={observation_id}, title={title}")


def sample_dasha_input(
    *,
    md_lord: str = "Saturn",
    ad_lord: str = "Mercury",
    pr_lord: str | None = "Venus",
    with_dates: bool = True,
) -> DashaInput:
    """Build a representative dasha input for tests."""
    start = PERIOD_START if with_dates else None
    end = PERIOD_END if with_dates else None
    return DashaInput(
        system="vimshottari",
        current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord=md_lord, start=start, end=end),
        current_antardasha=DashaPeriodSnapshot(level="antardasha", lord=ad_lord, start=start, end=end),
        current_pratyantar=(
            DashaPeriodSnapshot(level="pratyantar", lord=pr_lord, start=start, end=end)
            if pr_lord is not None
            else None
        ),
    )


def dasha_chart(lagna: str = "Aries") -> tuple[PlanetPositionsInput, HousesInput]:
    """Build chart inputs for dasha intelligence tests."""
    return classical_chart(lagna)


def analyze_dasha(
    dasha: DashaInput,
    planet_positions: PlanetPositionsInput | None = None,
    houses: HousesInput | None = None,
    *,
    analyzer: DashaIntelligenceAnalyzer | None = None,
    reference_datetime: datetime | None = DASHA_REFERENCE_TIME,
) -> DashaAnalysisResult:
    """Run the Dasha analyzer."""
    engine = analyzer or DashaIntelligenceAnalyzer()
    return engine.analyze(
        dasha=dasha,
        planet_positions=planet_positions,
        houses=houses,
        reference_datetime=reference_datetime,
    )


@pytest.fixture
def standard_dasha_chart() -> tuple[PlanetPositionsInput, HousesInput, DashaInput]:
    """Default chart and dasha stack for integration tests."""
    planet_positions, houses = dasha_chart("Aries")
    return planet_positions, houses, sample_dasha_input()


@pytest.fixture
def frozen_dasha_analyzer(monkeypatch: pytest.MonkeyPatch) -> DashaIntelligenceAnalyzer:
    """Return an analyzer with a fixed analysis timestamp."""
    import backend.app.services.reasoning.dasha.analyzer as analyzer_module

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None) -> datetime:  # noqa: ANN001
            if tz is None:
                return FIXED_ANALYSIS_TIME.replace(tzinfo=None)
            return FIXED_ANALYSIS_TIME

    monkeypatch.setattr(analyzer_module, "datetime", FixedDateTime)
    return DashaIntelligenceAnalyzer()


class TestModelsAndHelpers:
    def test_make_observation_clamps_scores(self) -> None:
        observation = make_observation(
            observation_id="dasha-test",
            category=DashaObservationCategory.MAHADASHA,
            title="Test",
            explanation="Test explanation.",
            severity=1.5,
            confidence=-0.2,
        )
        assert observation.severity == 1.0
        assert observation.confidence == 0.0

    def test_sign_index_from_name(self) -> None:
        assert sign_index_from_name("aries") == 0
        assert lord_of_sign(0) == "Mars"
        with pytest.raises(ValueError):
            sign_index_from_name("NotASign")

    def test_build_dasha_context_from_first_house_cusp(self) -> None:
        houses = HousesInput(
            ascendant_sign=None,
            house_system="whole_sign",
            cusps=(HouseSnapshot(number=1, sign="Leo"),),
        )
        planet_positions = PlanetPositionsInput(
            ascendant_sign=None,
            planets=(p("Sun", "Leo", 1, 130.0),),
        )
        context = build_dasha_context(
            dasha=sample_dasha_input(),
            planet_positions=planet_positions,
            houses=houses,
        )
        assert context.lagna_sign_name == "Leo"

    def test_planet_without_explicit_house_uses_sign_offset(self) -> None:
        snapshot = PlanetPositionSnapshot(
            name="Sun",
            sign="Gemini",
            house=None,
            longitude=70.0,
        )
        context = build_dasha_context(
            dasha=sample_dasha_input(),
            planet_positions=PlanetPositionsInput(ascendant_sign="Aries", planets=(snapshot,)),
            houses=houses_for("Aries"),
        )
        assert context.get_planet("Sun").house == 3

    def test_unknown_sign_name_preserved(self) -> None:
        from backend.app.services.reasoning.dasha.analyzer import _normalize_sign_name

        assert _normalize_sign_name("CustomSign") == "CustomSign"
        assert _normalize_sign_name("aries") == "Aries"

    def test_build_dasha_context_without_chart(self) -> None:
        context = build_dasha_context(dasha=sample_dasha_input())
        assert context.planets == {}
        assert context.dasha.system == "vimshottari"

    def test_build_dasha_context_with_chart(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
            reference_datetime=DASHA_REFERENCE_TIME,
        )
        assert context.has_planet("Saturn")
        assert context.has_planet("Mercury")
        assert context.houses_ruled("Saturn") == (10, 11)

    def test_build_dasha_context_derives_ketu(self) -> None:
        planet_positions, houses = classical_chart(
            "Aries",
            overrides={"Ketu": p("Ketu", "Cancer", 4, 100.0)},
        )
        planet_positions = PlanetPositionsInput(
            ascendant_sign=planet_positions.ascendant_sign,
            moon_sign=planet_positions.moon_sign,
            planets=tuple(item for item in planet_positions.planets if item.name != "Ketu"),
        )
        context = build_dasha_context(
            dasha=sample_dasha_input(),
            planet_positions=planet_positions,
            houses=houses,
        )
        assert context.has_planet("Ketu")
        assert context.has_planet("Rahu")

    def test_chart_context_helpers(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        assert context.house_of("Saturn") == context.get_planet("Saturn").house
        assert context.active_period("mahadasha") is not None
        with pytest.raises(KeyError):
            context.get_planet("Pluto")
        with pytest.raises(ValueError):
            context.active_period("unknown")


class TestMahadashaModule:
    def test_mahadasha_observation(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_mahadasha(context)
        assert len(observations) == 1
        observation = observations[0]
        assert observation.category == DashaObservationCategory.MAHADASHA
        assert observation.affected_planets == ("Saturn",)
        assert "Saturn" in observation.title

    def test_mahadasha_missing_period(self) -> None:
        context = build_dasha_context(
            dasha=DashaInput(system="vimshottari"),
        )
        assert analyze_mahadasha(context) == ()


class TestAntardashaModule:
    def test_antardasha_observation(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_antardasha(context)
        assert len(observations) == 1
        assert observations[0].category == DashaObservationCategory.ANTARDASHA
        assert "Mercury" in observations[0].affected_planets

    def test_antardasha_without_mahadasha(self) -> None:
        context = build_dasha_context(
            dasha=DashaInput(
                system="vimshottari",
                current_antardasha=DashaPeriodSnapshot(level="antardasha", lord="Venus"),
            )
        )
        observations = analyze_antardasha(context)
        assert len(observations) == 1
        assert observations[0].affected_planets == ("Venus",)

    def test_antardasha_includes_occupied_house(self) -> None:
        context = build_dasha_context(
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Sun"),
                current_antardasha=DashaPeriodSnapshot(level="antardasha", lord="Jupiter"),
            ),
            planet_positions=PlanetPositionsInput(
                ascendant_sign="Aries",
                planets=(p("Sun", "Leo", 5, 130.0), p("Jupiter", "Libra", 7, 190.0)),
            ),
            houses=houses_for("Aries"),
        )
        observation = analyze_antardasha(context)[0]
        assert 7 in observation.affected_houses
        assert 9 in observation.affected_houses


class TestPratyantardashaModule:
    def test_pratyantar_observation(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_pratyantardasha(context)
        assert len(observations) == 1
        assert observations[0].category == DashaObservationCategory.PRATYANTAR

    def test_pratyantar_missing_period(self) -> None:
        context = build_dasha_context(dasha=sample_dasha_input(pr_lord=None))
        assert analyze_pratyantardasha(context) == ()


class TestCombinedEffects:
    def test_friendly_lords(self, standard_dasha_chart) -> None:
        planet_positions, houses, _ = standard_dasha_chart
        dasha = sample_dasha_input(md_lord="Saturn", ad_lord="Mercury")
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_combined_effects(context)
        assert len(observations) == 1
        assert observations[0].metadata["relationship"] == "friendly"

    def test_inimical_lords(self, standard_dasha_chart) -> None:
        planet_positions, houses, _ = standard_dasha_chart
        dasha = sample_dasha_input(md_lord="Saturn", ad_lord="Sun")
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_combined_effects(context)
        assert observations[0].metadata["relationship"] == "inimical"

    def test_same_lord(self, standard_dasha_chart) -> None:
        planet_positions, houses, _ = standard_dasha_chart
        dasha = sample_dasha_input(md_lord="Saturn", ad_lord="Saturn")
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_combined_effects(context)
        assert observations[0].metadata["relationship"] == "same_lord"

    def test_neutral_lords(self, standard_dasha_chart) -> None:
        planet_positions, houses, _ = standard_dasha_chart
        dasha = sample_dasha_input(md_lord="Mars", ad_lord="Venus")
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_combined_effects(context)
        assert observations[0].metadata["relationship"] == "neutral"

    def test_combined_effects_requires_both_periods(self) -> None:
        context = build_dasha_context(
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Jupiter"),
            )
        )
        assert analyze_combined_effects(context) == ()


class TestDignityModifiers:
    def test_dignity_observations_for_active_lords(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_dignity_modifiers(context)
        lords = {item.affected_planets[0] for item in observations}
        assert "Saturn" in lords
        assert "Mercury" in lords
        assert all(item.category == DashaObservationCategory.DIGNITY for item in observations)

    def test_dignity_skips_duplicate_lords(self, standard_dasha_chart) -> None:
        planet_positions, houses, _ = standard_dasha_chart
        dasha = sample_dasha_input(md_lord="Saturn", ad_lord="Saturn", pr_lord="Saturn")
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_dignity_modifiers(context)
        assert len(observations) == 1

    def test_dignity_without_chart(self) -> None:
        context = build_dasha_context(dasha=sample_dasha_input())
        assert analyze_dignity_modifiers(context) == ()

    def test_dignity_variants(self) -> None:
        sun_context = build_dasha_context(
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Sun"),
            ),
            planet_positions=PlanetPositionsInput(
                ascendant_sign="Aries",
                planets=(p("Sun", "Aries", 1, 10.0),),
            ),
            houses=houses_for("Aries"),
        )
        moon_context = build_dasha_context(
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Moon"),
            ),
            planet_positions=PlanetPositionsInput(
                ascendant_sign="Aries",
                planets=(p("Moon", "Scorpio", 8, 220.0),),
            ),
            houses=houses_for("Aries"),
        )
        assert analyze_dignity_modifiers(sun_context)[0].metadata["dignity"] == "exalted"
        assert analyze_dignity_modifiers(moon_context)[0].metadata["dignity"] == "debilitated"

        venus_context = build_dasha_context(
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Venus"),
            ),
            planet_positions=PlanetPositionsInput(
                ascendant_sign="Aries",
                planets=(p("Venus", "Taurus", 2, 45.0),),
            ),
            houses=houses_for("Aries"),
        )
        assert analyze_dignity_modifiers(venus_context)[0].metadata["dignity"] == "own"

        mars_context = build_dasha_context(
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Mars"),
            ),
            planet_positions=PlanetPositionsInput(
                ascendant_sign="Aries",
                planets=(p("Mars", "Aries", 1, 15.0),),
            ),
            houses=houses_for("Aries"),
        )
        assert analyze_dignity_modifiers(mars_context)[0].metadata["dignity"] == "moolatrikona"


class TestHouseActivation:
    def test_house_activation_observations(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_house_activation(context)
        assert len(observations) >= 3
        categories = {item.category for item in observations}
        assert categories == {DashaObservationCategory.HOUSE_ACTIVATION}
        house_types = {item.metadata["house_type"] for item in observations}
        assert any("kendra" in value or "trikona" in value or "dusthana" in value or "upachaya" in value for value in house_types)

    def test_house_activation_skips_duplicate_houses(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        dasha = sample_dasha_input(md_lord="Saturn", ad_lord="Saturn", pr_lord=None)
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        house_ids = [item.observation_id for item in analyze_house_activation(context)]
        assert len(house_ids) == len(set(house_ids))


class TestDomainActivation:
    def test_all_domain_templates_emit_observations(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_domain_activation(context)
        assert len(observations) == 7
        domain_ids = {item.metadata["domain_id"] for item in observations}
        assert domain_ids == {
            "marriage",
            "career",
            "finance",
            "health",
            "education",
            "foreign_settlement",
            "spirituality",
        }

    def test_domain_activation_without_active_lords(self) -> None:
        context = build_dasha_context(dasha=DashaInput(system="vimshottari"))
        assert analyze_domain_activation(context) == ()


class TestEventWindows:
    def test_event_window_records(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
            reference_datetime=DASHA_REFERENCE_TIME,
        )
        records = analyze_event_windows(context)
        assert len(records) == 21
        assert any(record.is_active for record in records)

    def test_event_window_observations(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
            reference_datetime=DASHA_REFERENCE_TIME,
        )
        records = analyze_event_windows(context)
        observations = event_windows_to_observations(records)
        assert len(observations) >= 1
        assert all(item.category == DashaObservationCategory.EVENT_WINDOW for item in observations)

    def test_event_window_inactive_period(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
            reference_datetime=datetime(2030, 1, 1, tzinfo=timezone.utc),
        )
        records = analyze_event_windows(context)
        assert all(record.is_active is False for record in records if record.end is not None)

    def test_event_window_without_dates(self, standard_dasha_chart) -> None:
        planet_positions, houses, _ = standard_dasha_chart
        dasha = sample_dasha_input(with_dates=False)
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        assert analyze_event_windows(context) == ()

    def test_event_window_range_formatting(self) -> None:
        from backend.app.services.reasoning.dasha.event_windows import _format_window_range, _period_is_active

        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2026, 1, 1, tzinfo=timezone.utc)
        assert "from" in _format_window_range(start, end)
        assert "from" in _format_window_range(start, None)
        assert "until" in _format_window_range(None, end)
        assert _format_window_range(None, None) == "within the current dasha segment"
        assert _period_is_active(start, end, datetime(2023, 1, 1, tzinfo=timezone.utc)) is False
        assert _period_is_active(None, None, datetime(2026, 1, 1, tzinfo=timezone.utc)) is True


class TestDashaAnalyzer:
    def test_full_analyzer_pipeline(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        result = analyze_dasha(dasha, planet_positions, houses)
        assert isinstance(result, DashaAnalysisResult)
        assert result.metadata["engine"] == "dasha_intelligence_v1"
        assert result.metadata["has_chart_context"] is True
        assert len(result.observations) > 10
        categories = {item.category for item in result.observations}
        assert DashaObservationCategory.MAHADASHA in categories
        assert DashaObservationCategory.ANTARDASHA in categories
        assert DashaObservationCategory.COMBINED_EFFECT in categories
        assert DashaObservationCategory.DOMAIN in categories

    def test_analyzer_without_chart(self) -> None:
        result = analyze_dasha(sample_dasha_input())
        assert result.metadata["has_chart_context"] is False
        assert len(result.observations) >= 3

    def test_frozen_analyzed_at_timestamp(
        self,
        standard_dasha_chart,
        frozen_dasha_analyzer: DashaIntelligenceAnalyzer,
    ) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        result = frozen_dasha_analyzer.analyze(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
        )
        assert result.analyzed_at == FIXED_ANALYSIS_TIME

    def test_modular_pipeline_matches_combined(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = build_dasha_context(
            dasha=dasha,
            planet_positions=planet_positions,
            houses=houses,
            reference_datetime=DASHA_REFERENCE_TIME,
        )
        modular_ids = {
            item.observation_id
            for module in (
                analyze_mahadasha(context),
                analyze_antardasha(context),
                analyze_pratyantardasha(context),
                analyze_combined_effects(context),
                analyze_dignity_modifiers(context),
                analyze_house_activation(context),
                analyze_domain_activation(context),
                event_windows_to_observations(analyze_event_windows(context)),
            )
            for item in module
        }
        combined = analyze_dasha(dasha, planet_positions, houses)
        assert modular_ids == {item.observation_id for item in combined.observations}


class TestFusionIntegration:
    def test_normalize_dasha_observation(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        result = analyze_dasha(dasha, planet_positions, houses)
        normalized = normalize_dasha_observation(result.observations[0])
        assert normalized.engine == FusionEngineId.DASHA
        assert normalized.category.startswith("dasha:")

    def test_dasha_adapter_emits_observations(self, standard_dasha_chart) -> None:
        planet_positions, houses, dasha = standard_dasha_chart
        context = FusionContext(
            planet_positions=planet_positions,
            houses=houses,
            dasha=dasha,
            reference_datetime=DASHA_REFERENCE_TIME,
        )
        observations = DashaIntelligenceAdapter().analyze(context)
        assert len(observations) > 2
        categories = {item.category for item in observations}
        assert "dasha:mahadasha" in categories
        assert "dasha:antardasha" in categories
        assert all(item.engine == FusionEngineId.DASHA for item in observations)

    def test_dasha_adapter_without_chart(self) -> None:
        context = FusionContext(
            planet_positions=PlanetPositionsInput(planets=()),
            houses=HousesInput(cusps=()),
            dasha=sample_dasha_input(),
        )
        observations = DashaIntelligenceAdapter().analyze(context)
        assert len(observations) >= 3

    def test_dasha_adapter_unavailable_without_periods(self) -> None:
        context = FusionContext(
            planet_positions=PlanetPositionsInput(planets=()),
            houses=HousesInput(cusps=()),
            dasha=DashaInput(system="vimshottari"),
        )
        adapter = DashaIntelligenceAdapter()
        assert adapter.is_available(context) is False
        assert adapter.analyze(context) == ()

    def test_build_context_requires_lagna_when_chart_partial(self) -> None:
        with pytest.raises(ValueError):
            build_dasha_context(
                dasha=sample_dasha_input(),
                planet_positions=PlanetPositionsInput(planets=()),
                houses=HousesInput(cusps=()),
            )
