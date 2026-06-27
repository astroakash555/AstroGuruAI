"""Comprehensive tests for the Transit intelligence layer."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.app.services.reasoning.fusion import FusionContext, TransitIntelligenceAdapter, normalize_transit_observation
from backend.app.services.reasoning.fusion.models import FusionEngineId
from backend.app.services.reasoning.models import (
    DashaInput,
    DashaPeriodSnapshot,
    HouseSnapshot,
    HousesInput,
    PlanetPositionSnapshot,
    PlanetPositionsInput,
    TransitInput,
    TransitPlanetSnapshot,
)
from backend.app.services.reasoning.transit import (
    TransitAnalysisResult,
    TransitIntelligenceAnalyzer,
    TransitObservationCategory,
    ReasoningObservation,
    analyze_dasha_transit_interaction,
    analyze_dhaiya,
    analyze_domain_activation,
    analyze_event_windows,
    analyze_house_transits,
    analyze_jupiter_transits,
    analyze_natal_overlays,
    analyze_planet_transits,
    analyze_rahu_ketu_transits,
    analyze_sade_sati,
    analyze_transit_aspects,
    build_transit_context,
    event_windows_to_observations,
    make_observation,
    sign_index_from_name,
)
from tests.reasoning.conftest import FIXED_ANALYSIS_TIME, classical_chart, houses_for, p

TRANSIT_REFERENCE_TIME = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


def t(
    planet: str,
    sign: str,
    *,
    house_from_lagna: int | None = None,
    house_from_moon: int | None = None,
    is_retrograde: bool = False,
) -> TransitPlanetSnapshot:
    return TransitPlanetSnapshot(
        planet=planet,
        sign=sign,
        house_from_lagna=house_from_lagna,
        house_from_moon=house_from_moon,
        is_retrograde=is_retrograde,
    )


def sample_transit_input(**overrides) -> TransitInput:
    defaults = {
        "reference_datetime": TRANSIT_REFERENCE_TIME,
        "planets": (
            t("Saturn", "Cancer", house_from_lagna=4, house_from_moon=1),
            t("Jupiter", "Gemini", house_from_lagna=3, house_from_moon=12),
            t("Rahu", "Aquarius", house_from_lagna=11, house_from_moon=8),
            t("Ketu", "Leo", house_from_lagna=5, house_from_moon=2),
            t("Mars", "Aries", house_from_lagna=1, house_from_moon=10),
        ),
    }
    defaults.update(overrides)
    return TransitInput(**defaults)


def sample_dasha(lord: str = "Saturn") -> DashaInput:
    return DashaInput(
        system="vimshottari",
        current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord=lord),
        current_antardasha=DashaPeriodSnapshot(level="antardasha", lord="Mercury"),
    )


def analyze_transit(
    transit: TransitInput,
    planet_positions: PlanetPositionsInput | None = None,
    houses: HousesInput | None = None,
    *,
    dasha: DashaInput | None = None,
    analyzer: TransitIntelligenceAnalyzer | None = None,
) -> TransitAnalysisResult:
    engine = analyzer or TransitIntelligenceAnalyzer()
    return engine.analyze(
        transit=transit,
        planet_positions=planet_positions,
        houses=houses,
        dasha=dasha,
        reference_datetime=TRANSIT_REFERENCE_TIME,
    )


@pytest.fixture
def standard_transit_chart() -> tuple[PlanetPositionsInput, HousesInput, TransitInput]:
    planet_positions, houses = classical_chart("Aries", moon_sign="Cancer")
    return planet_positions, houses, sample_transit_input()


@pytest.fixture
def frozen_transit_analyzer(monkeypatch: pytest.MonkeyPatch) -> TransitIntelligenceAnalyzer:
    import backend.app.services.reasoning.transit.analyzer as analyzer_module

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None) -> datetime:  # noqa: ANN001
            if tz is None:
                return FIXED_ANALYSIS_TIME.replace(tzinfo=None)
            return FIXED_ANALYSIS_TIME

    monkeypatch.setattr(analyzer_module, "datetime", FixedDateTime)
    return TransitIntelligenceAnalyzer()


class TestModelHelpers:
    def test_make_observation_clamps_scores(self) -> None:
        observation = make_observation(
            observation_id="transit-test",
            category=TransitObservationCategory.PLANET_TRANSIT,
            title="Test",
            explanation="Test explanation.",
            severity=2.0,
            confidence=-1.0,
        )
        assert observation.severity == 1.0
        assert observation.confidence == 0.0

    def test_sign_index_from_name(self) -> None:
        assert sign_index_from_name("cancer") == 3
        with pytest.raises(ValueError):
            sign_index_from_name("Invalid")


class TestContextBuilder:
    def test_build_transit_context_with_chart(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
            dasha=sample_dasha(),
        )
        assert context.has_transit("Saturn")
        assert context.has_natal("Moon")
        assert context.active_dasha_lords() == ("Saturn", "Mercury")

    def test_build_transit_context_without_chart(self) -> None:
        context = build_transit_context(transit=sample_transit_input())
        assert context.natal_planets == {}
        assert context.has_transit("Saturn")

    def test_build_transit_context_derives_ketu(self) -> None:
        planet_positions, houses = classical_chart(
            "Aries",
            overrides={"Ketu": p("Ketu", "Cancer", 4, 100.0)},
        )
        planet_positions = PlanetPositionsInput(
            ascendant_sign=planet_positions.ascendant_sign,
            moon_sign="Cancer",
            planets=tuple(item for item in planet_positions.planets if item.name != "Ketu"),
        )
        context = build_transit_context(
            transit=sample_transit_input(),
            planet_positions=planet_positions,
            houses=houses,
        )
        assert context.has_natal("Ketu")

    def test_context_helpers(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
            dasha=sample_dasha(),
        )
        assert context.get_transit("Saturn").sign_name == "Cancer"
        with pytest.raises(KeyError):
            context.get_transit("Pluto")
        with pytest.raises(ValueError):
            context.active_period("unknown")


class TestPlanetTransits:
    def test_planet_transit_observations(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_planet_transits(context)
        assert len(observations) == len(transit.planets)
        assert observations[0].category == TransitObservationCategory.PLANET_TRANSIT


class TestHouseTransits:
    def test_house_and_natal_overlay(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
        )
        house_obs = analyze_house_transits(context)
        overlay_obs = analyze_natal_overlays(context)
        assert len(house_obs) >= 5
        assert all(item.category == TransitObservationCategory.HOUSE_TRANSIT for item in house_obs)
        assert any(item.category == TransitObservationCategory.NATAL_OVERLAY for item in overlay_obs)


class TestAspects:
    def test_transit_aspects(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_transit_aspects(context)
        assert len(observations) >= 1
        assert observations[0].category == TransitObservationCategory.ASPECT

    def test_aspects_skip_nodes_and_duplicates(self) -> None:
        planet_positions, houses = classical_chart(
            "Aries",
            overrides={
                "Rahu": p("Rahu", "Capricorn", 10, 280.0),
                "Ketu": p("Ketu", "Cancer", 4, 100.0),
            },
        )
        context = build_transit_context(
            transit=TransitInput(
                planets=(
                    t("Mars", "Aries", house_from_lagna=1, house_from_moon=10),
                    t("Sun", "Leo", house_from_lagna=5, house_from_moon=2),
                )
            ),
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_transit_aspects(context)
        assert all(item.metadata["natal_planet"] not in {"Rahu", "Ketu"} for item in observations)

    def test_house_transit_skips_missing_houses(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(t("Mars", "Aries", house_from_lagna=None, house_from_moon=None),)
            )
        )
        assert analyze_house_transits(context) == ()


class TestSadeSati:
    def test_sade_sati_peak_phase(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(t("Saturn", "Cancer", house_from_lagna=4, house_from_moon=1),)
            )
        )
        observations = analyze_sade_sati(context)
        assert len(observations) == 1
        assert observations[0].category == TransitObservationCategory.SADE_SATI
        assert observations[0].metadata["phase"] == "peak"

    def test_sade_sati_not_active(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(t("Saturn", "Capricorn", house_from_lagna=10, house_from_moon=7),)
            )
        )
        assert analyze_sade_sati(context) == ()


class TestDhaiya:
    def test_dhaiya_active(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(t("Saturn", "Libra", house_from_lagna=7, house_from_moon=4),)
            )
        )
        observations = analyze_dhaiya(context)
        assert len(observations) == 1
        assert observations[0].category == TransitObservationCategory.DHAIYA

    def test_dhaiya_not_active(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(t("Saturn", "Cancer", house_from_lagna=4, house_from_moon=1),)
            )
        )
        assert analyze_dhaiya(context) == ()


class TestJupiter:
    def test_jupiter_kendra_and_trikona(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(t("Jupiter", "Cancer", house_from_lagna=4, house_from_moon=1),)
            )
        )
        observations = analyze_jupiter_transits(context)
        categories = {item.metadata.get("effect") for item in observations}
        assert "kendra_blessing" in categories

    def test_jupiter_general_effect(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(t("Jupiter", "Taurus", house_from_lagna=2, house_from_moon=11),)
            )
        )
        observations = analyze_jupiter_transits(context)
        assert len(observations) == 1
        assert observations[0].metadata["effect"] == "general"


class TestRahuKetu:
    def test_rahu_ketu_axis(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_rahu_ketu_transits(context)
        assert any(item.observation_id == "transit-rahu-ketu-axis" for item in observations)


class TestDashaInteraction:
    def test_dasha_convergence_reactivates_natal_house(self) -> None:
        planet_positions, houses = classical_chart(
            "Aries",
            overrides={"Saturn": p("Saturn", "Cancer", 4, 250.0)},
            moon_sign="Cancer",
        )
        transit = TransitInput(
            planets=(t("Saturn", "Cancer", house_from_lagna=4, house_from_moon=1),)
        )
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
            dasha=sample_dasha("Saturn"),
        )
        observation = analyze_dasha_transit_interaction(context)[0]
        assert observation.metadata["is_supported"] is True
        assert "natal house" in observation.explanation

    def test_dasha_sign_overlay(self) -> None:
        planet_positions, houses = classical_chart("Aries", moon_sign="Cancer")
        transit = TransitInput(
            planets=(t("Saturn", "Libra", house_from_lagna=7, house_from_moon=4),)
        )
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Jupiter"),
            ),
        )
        observations = analyze_dasha_transit_interaction(context)
        assert any("Triggered by" in item.title for item in observations)

    def test_natal_house_missing_for_unknown_planet(self) -> None:
        context = build_transit_context(transit=sample_transit_input())
        assert context.natal_house("Saturn") is None

    def test_active_period_levels(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Saturn"),
                current_antardasha=DashaPeriodSnapshot(level="antardasha", lord="Mercury"),
                current_pratyantar=DashaPeriodSnapshot(level="pratyantar", lord="Venus"),
            ),
        )
        assert context.active_period("antardasha") is not None
        assert context.active_period("pratyantar") is not None

    def test_dasha_overlay_skips_missing_natal(self) -> None:
        context = build_transit_context(
            transit=TransitInput(planets=(t("Mars", "Aries", house_from_lagna=1, house_from_moon=10),)),
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Pluto"),
            ),
        )
        assert analyze_dasha_transit_interaction(context) == ()


class TestDomainAndEventWindows:
    def test_domain_activation_all_templates(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
        )
        observations = analyze_domain_activation(context)
        assert len(observations) == 7

    def test_event_windows(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
        )
        records = analyze_event_windows(context)
        observations = event_windows_to_observations(records)
        assert len(records) >= 1
        assert all(item.category == TransitObservationCategory.EVENT_WINDOW for item in observations)


class TestTransitAnalyzer:
    def test_full_pipeline(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        result = analyze_transit(
            transit,
            planet_positions,
            houses,
            dasha=sample_dasha(),
        )
        assert isinstance(result, TransitAnalysisResult)
        assert result.metadata["engine"] == "transit_intelligence_v1"
        assert len(result.observations) > 15
        categories = {item.category for item in result.observations}
        assert TransitObservationCategory.SADE_SATI in categories
        assert TransitObservationCategory.DOMAIN in categories

    def test_analyzer_without_chart(self) -> None:
        result = analyze_transit(sample_transit_input())
        assert result.metadata["has_chart_context"] is False
        assert len(result.observations) >= 5

    def test_frozen_timestamp(
        self,
        standard_transit_chart,
        frozen_transit_analyzer: TransitIntelligenceAnalyzer,
    ) -> None:
        planet_positions, houses, transit = standard_transit_chart
        result = frozen_transit_analyzer.analyze(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
        )
        assert result.analyzed_at == FIXED_ANALYSIS_TIME


class TestFusionIntegration:
    def test_normalize_transit_observation(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        result = analyze_transit(transit, planet_positions, houses)
        normalized = normalize_transit_observation(result.observations[0])
        assert normalized.engine == FusionEngineId.TRANSIT
        assert normalized.category.startswith("transit:")

    def test_transit_adapter(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = FusionContext(
            planet_positions=planet_positions,
            houses=houses,
            transit=transit,
            dasha=sample_dasha(),
            reference_datetime=TRANSIT_REFERENCE_TIME,
        )
        observations = TransitIntelligenceAdapter().analyze(context)
        assert len(observations) > 5
        assert all(item.engine == FusionEngineId.TRANSIT for item in observations)

    def test_adapter_unavailable_without_transits(self) -> None:
        context = FusionContext(
            planet_positions=PlanetPositionsInput(planets=()),
            houses=HousesInput(cusps=()),
            transit=TransitInput(planets=()),
        )
        adapter = TransitIntelligenceAdapter()
        assert adapter.is_available(context) is False
        assert adapter.analyze(context) == ()

    def test_build_context_requires_lagna_when_chart_partial(self) -> None:
        with pytest.raises(ValueError):
            build_transit_context(
                transit=sample_transit_input(),
                planet_positions=PlanetPositionsInput(planets=()),
                houses=HousesInput(cusps=()),
            )

    def test_build_context_from_first_house_cusp(self) -> None:
        houses = HousesInput(
            ascendant_sign=None,
            house_system="whole_sign",
            cusps=(HouseSnapshot(number=1, sign="Leo"),),
        )
        planet_positions = PlanetPositionsInput(
            ascendant_sign=None,
            planets=(p("Sun", "Leo", 1, 130.0),),
        )
        context = build_transit_context(
            transit=sample_transit_input(),
            planet_positions=planet_positions,
            houses=houses,
        )
        assert context.lagna_sign_name == "Leo"

    def test_planet_without_explicit_house(self) -> None:
        snapshot = PlanetPositionSnapshot(
            name="Sun",
            sign="Gemini",
            house=None,
            longitude=70.0,
        )
        context = build_transit_context(
            transit=sample_transit_input(),
            planet_positions=PlanetPositionsInput(ascendant_sign="Aries", planets=(snapshot,)),
            houses=houses_for("Aries"),
        )
        assert context.natal_planets["Sun"].house == 3

    def test_unknown_sign_name_preserved(self) -> None:
        from backend.app.services.reasoning.transit.analyzer import _normalize_sign_name

        assert _normalize_sign_name("CustomSign") == "CustomSign"

    def test_sade_sati_rising_and_setting(self) -> None:
        for house, phase in ((12, "rising"), (2, "setting")):
            context = build_transit_context(
                transit=TransitInput(
                    planets=(t("Saturn", "Gemini", house_from_lagna=3, house_from_moon=house),)
                )
            )
            observation = analyze_sade_sati(context)[0]
            assert observation.metadata["phase"] == phase

    def test_dhaiya_ashtama(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(t("Saturn", "Pisces", house_from_lagna=12, house_from_moon=8),)
            )
        )
        assert analyze_dhaiya(context)[0].metadata["phase"] == "ashtama"

    def test_jupiter_trikona_only(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(t("Jupiter", "Sagittarius", house_from_lagna=9, house_from_moon=6),)
            )
        )
        effects = {item.metadata.get("effect") for item in analyze_jupiter_transits(context)}
        assert "trikona_blessing" in effects

    def test_rahu_dusthana_effect(self) -> None:
        context = build_transit_context(
            transit=TransitInput(
                planets=(
                    t("Rahu", "Virgo", house_from_lagna=6, house_from_moon=3),
                    t("Ketu", "Pisces", house_from_lagna=12, house_from_moon=9),
                )
            )
        )
        observations = analyze_rahu_ketu_transits(context)
        assert any(item.metadata.get("effect") == "dusthana_nodal" for item in observations)

    def test_event_window_focus_planet_missing(self) -> None:
        from backend.app.services.reasoning.transit.event_windows import _domain_activation_score

        context = build_transit_context(transit=sample_transit_input())
        score, planets, houses, evidence = _domain_activation_score(
            context,
            (7,),
            ("Venus",),
            focus_planet="Pluto",
        )
        assert score == 0.0
        assert planets == ()
        assert evidence == ()

    def test_active_period_without_dasha(self) -> None:
        context = build_transit_context(transit=sample_transit_input())
        assert context.active_period("mahadasha") is None

    def test_modular_matches_combined(self, standard_transit_chart) -> None:
        planet_positions, houses, transit = standard_transit_chart
        context = build_transit_context(
            transit=transit,
            planet_positions=planet_positions,
            houses=houses,
            dasha=sample_dasha(),
        )
        modular_ids = {
            item.observation_id
            for module in (
                analyze_planet_transits(context),
                analyze_house_transits(context),
                analyze_natal_overlays(context),
                analyze_transit_aspects(context),
                analyze_sade_sati(context),
                analyze_dhaiya(context),
                analyze_jupiter_transits(context),
                analyze_rahu_ketu_transits(context),
                analyze_dasha_transit_interaction(context),
                analyze_domain_activation(context),
                event_windows_to_observations(analyze_event_windows(context)),
            )
            for item in module
        }
        combined = analyze_transit(transit, planet_positions, houses, dasha=sample_dasha())
        assert modular_ids == {item.observation_id for item in combined.observations}
