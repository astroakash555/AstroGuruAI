"""Comprehensive tests for the KP astrology intelligence layer."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.app.services.reasoning.kp import (
    EVENT_SUPPORT_THRESHOLD,
    EVENT_TEMPLATES,
    EventTimingAnalyzer,
    KPAnalysisResult,
    KPChartContext,
    KPIntelligenceAnalyzer,
    KPObservationCategory,
    ReasoningObservation,
    analyze_cusps,
    analyze_event_timing,
    analyze_ruling_planets,
    analyze_significators,
    analyze_star_lords,
    analyze_sub_lords,
    build_cusps,
    build_kp_context,
    build_significators,
    compute_ruling_planets,
    evaluate_event_templates,
    make_observation,
)
from backend.app.services.reasoning.kp.constants import (
    SIGN_NAMES,
    lord_of_sign,
    sign_index_from_name,
    sign_name_from_longitude,
)
from backend.app.services.reasoning.kp.event_timing import (
    _event_support_score,
    event_records_to_observations,
)
from backend.app.services.reasoning.kp.models import (
    EventTimingRecord,
    KPCuspRecord,
    KPPlanetRecord,
    KPSignificatorRecord,
    RulingPlanets,
)
from backend.app.services.reasoning.kp.ruling_planets import _day_lord, _repeated_components
from backend.app.services.reasoning.models import (
    HouseSnapshot,
    HousesInput,
    PlanetPositionSnapshot,
    PlanetPositionsInput,
)
from kp_engine.lords import get_sub_lord, get_star_lord
from tests.reasoning.conftest import FIXED_ANALYSIS_TIME, classical_chart, houses_for, p

KP_REFERENCE_TIME = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _titles(observations: tuple[ReasoningObservation, ...]) -> set[str]:
    return {item.title for item in observations}


def _by_id(observations: tuple[ReasoningObservation, ...]) -> dict[str, ReasoningObservation]:
    return {item.observation_id: item for item in observations}


def find_kp_observation(
    observations: tuple[ReasoningObservation, ...],
    *,
    title: str | None = None,
    observation_id: str | None = None,
    category: KPObservationCategory | None = None,
) -> ReasoningObservation:
    """Return the first KP observation matching the given filters."""
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
    raise AssertionError(f"No KP observation matched filters: {filters}")


def assert_kp_observation(
    observation: ReasoningObservation,
    *,
    category: KPObservationCategory,
    title: str,
    severity: float,
    confidence: float,
    affected_planets: tuple[str, ...],
    affected_houses: tuple[int, ...],
) -> None:
    """Assert the core structured fields of a KP observation."""
    assert observation.category == category
    assert observation.title == title
    assert observation.explanation
    assert observation.severity == severity
    assert observation.confidence == confidence
    assert observation.affected_planets == affected_planets
    assert observation.affected_houses == affected_houses
    assert 0.0 <= observation.severity <= 1.0
    assert 0.0 <= observation.confidence <= 1.0


def cusps_with_longitudes(
    lagna: str,
    longitudes: tuple[float, ...] | None = None,
) -> tuple[HouseSnapshot, ...]:
    """Build house cusps with optional explicit longitudes."""
    lagna_index = SIGN_NAMES.index(lagna)
    return tuple(
        HouseSnapshot(
            number=house,
            sign=SIGN_NAMES[(lagna_index + house - 1) % 12],
            longitude=longitudes[house - 1] if longitudes else None,
        )
        for house in range(1, 13)
    )


def kp_chart(
    lagna: str,
    planets: tuple[PlanetPositionSnapshot, ...],
    *,
    cusp_longitudes: tuple[float, ...] | None = None,
    moon_sign: str | None = None,
) -> tuple[PlanetPositionsInput, HousesInput]:
    """Build planet and house inputs for KP analysis."""
    return (
        PlanetPositionsInput(
            ascendant_sign=lagna,
            moon_sign=moon_sign,
            planets=planets,
        ),
        HousesInput(
            ascendant_sign=lagna,
            house_system="whole_sign",
            cusps=cusps_with_longitudes(lagna, cusp_longitudes),
        ),
    )


def analyze_kp(
    planet_positions: PlanetPositionsInput,
    houses: HousesInput,
    *,
    reference_datetime: datetime | None = KP_REFERENCE_TIME,
    analyzer: KPIntelligenceAnalyzer | None = None,
) -> KPAnalysisResult:
    """Run the KP analyzer and return the full result."""
    engine = analyzer or KPIntelligenceAnalyzer()
    return engine.analyze(
        planet_positions=planet_positions,
        houses=houses,
        reference_datetime=reference_datetime,
    )


@pytest.fixture
def frozen_kp_analyzer(monkeypatch: pytest.MonkeyPatch) -> KPIntelligenceAnalyzer:
    """Return a KP analyzer with a fixed analysis timestamp."""
    import backend.app.services.reasoning.kp.analyzer as analyzer_module

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None) -> datetime:  # noqa: ANN001
            if tz is None:
                return FIXED_ANALYSIS_TIME.replace(tzinfo=None)
            return FIXED_ANALYSIS_TIME

    monkeypatch.setattr(analyzer_module, "datetime", FixedDateTime)
    return KPIntelligenceAnalyzer()


@pytest.fixture
def standard_kp_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Aries lagna chart with explicit cusp longitudes for KP modules."""
    planets = (
        p("Sun", "Gemini", 3, 70.0),
        p("Moon", "Cancer", 4, 100.0),
        p("Mars", "Aries", 1, 10.0),
        p("Mercury", "Virgo", 6, 165.0),
        p("Jupiter", "Libra", 7, 190.0),
        p("Venus", "Scorpio", 8, 220.0),
        p("Saturn", "Sagittarius", 9, 250.0),
        p("Rahu", "Capricorn", 10, 280.0),
        p("Ketu", "Cancer", 4, 100.0),
    )
    return kp_chart("Aries", planets, moon_sign="Cancer")


@pytest.fixture
def star_cluster_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Chart with two grahas sharing the same star lord."""
    planets = (
        p("Sun", "Aries", 1, 10.0),
        p("Moon", "Aries", 1, 11.0),
        p("Mars", "Leo", 5, 130.0),
        p("Mercury", "Virgo", 6, 165.0),
        p("Jupiter", "Libra", 7, 190.0),
        p("Venus", "Scorpio", 8, 220.0),
        p("Saturn", "Sagittarius", 9, 250.0),
        p("Rahu", "Capricorn", 10, 280.0),
        p("Ketu", "Cancer", 4, 100.0),
    )
    return kp_chart("Aries", planets)


@pytest.fixture
def own_star_sub_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Chart with a graha occupying its own star-lord sub segment."""
    planets = (
        p("Sun", "Aries", 1, 10.0),
        p("Moon", "Cancer", 4, 100.0),
        p("Mars", "Cancer", 4, 95.0),
        p("Mercury", "Virgo", 6, 165.0),
        p("Jupiter", "Libra", 7, 190.0),
        p("Venus", "Scorpio", 8, 220.0),
        p("Saturn", "Sagittarius", 9, 250.0),
        p("Rahu", "Capricorn", 10, 280.0),
        p("Ketu", "Cancer", 4, 100.0),
    )
    return kp_chart("Aries", planets)


@pytest.fixture
def marriage_event_chart() -> tuple[PlanetPositionsInput, HousesInput]:
    """Chart engineered for marriage event timing support."""
    cusp_longitudes = tuple(
        1.0 if house in (2, 7, 11) else float((house - 1) * 30)
        for house in range(1, 13)
    )
    planets = (
        p("Sun", "Gemini", 3, 70.0),
        p("Moon", "Cancer", 4, 100.0),
        p("Mars", "Aries", 1, 10.0),
        p("Mercury", "Virgo", 6, 165.0),
        p("Jupiter", "Libra", 7, 190.0),
        p("Venus", "Libra", 7, 195.0),
        p("Saturn", "Sagittarius", 9, 250.0),
        p("Rahu", "Capricorn", 10, 280.0),
    )
    return kp_chart("Aries", planets, cusp_longitudes=cusp_longitudes, moon_sign="Cancer")


# ---------------------------------------------------------------------------
# Constants and models
# ---------------------------------------------------------------------------


class TestConstantsAndModels:
    def test_sign_helpers(self) -> None:
        assert sign_index_from_name("aries") == 0
        assert lord_of_sign(0) == "Mars"
        assert sign_name_from_longitude(95.0) == "Cancer"

        with pytest.raises(ValueError, match="Unknown sign name"):
            sign_index_from_name("NotASign")

    def test_make_observation_clamps_scores(self) -> None:
        observation = make_observation(
            observation_id="kp-test-clamp",
            category=KPObservationCategory.STAR_LORD,
            title="Clamp Test",
            explanation="Scores should be bounded.",
            severity=1.5,
            confidence=-0.2,
        )
        assert observation.severity == 1.0
        assert observation.confidence == 0.0

    def test_chart_context_accessors(self) -> None:
        planet = KPPlanetRecord(
            name="Sun",
            longitude=10.0,
            sign_name="Aries",
            sign_index=0,
            house=1,
            nakshatra="Ashwini",
            star_lord="Ketu",
            sub_lord="Ketu",
        )
        cusp = KPCuspRecord(
            house=1,
            longitude=0.0,
            sign_name="Aries",
            star_lord="Ketu",
            sub_lord="Ketu",
        )
        significator = KPSignificatorRecord(
            house=1,
            level_a=("Sun",),
            level_b=(),
            level_c=(),
            level_d=("Mars",),
            combined=("Sun", "Mars"),
        )
        context = KPChartContext(
            lagna_sign_index=0,
            lagna_sign_name="Aries",
            lagna_longitude=0.0,
            reference_datetime=KP_REFERENCE_TIME,
            planets={"Sun": planet},
            cusps=(cusp,),
            significators=(significator,),
            ruling_planets=None,
        )
        assert context.get_planet("Sun") == planet
        assert context.has_planet("Sun") is True
        assert context.has_planet("Moon") is False
        assert context.cusp_for_house(1) == cusp
        assert context.cusp_for_house(2) is None
        assert context.significators_for_house(1) == significator
        assert context.significators_for_house(2) is None

        with pytest.raises(KeyError, match="Planet 'Moon'"):
            context.get_planet("Moon")


# ---------------------------------------------------------------------------
# Context building
# ---------------------------------------------------------------------------


class TestContextBuilding:
    def test_build_kp_context_derives_ketu_from_rahu(self) -> None:
        planets = (
            p("Sun", "Aries", 1, 10.0),
            p("Moon", "Cancer", 4, 100.0),
            p("Rahu", "Capricorn", 10, 280.0),
        )
        planet_positions, houses = kp_chart("Aries", planets)
        context = build_kp_context(planet_positions, houses)

        assert "Ketu" in context.planets
        assert context.planets["Ketu"].longitude == pytest.approx(100.0)
        assert context.planets["Ketu"].sign_name == "Cancer"

    def test_build_kp_context_resolves_lagna_from_first_house_cusp(self) -> None:
        cusps = (
            HouseSnapshot(number=1, sign="Leo"),
            HouseSnapshot(number=2, sign="Virgo"),
        )
        planet_positions = PlanetPositionsInput(
            ascendant_sign=None,
            planets=(p("Sun", "Leo", 1, 130.0),),
        )
        houses = HousesInput(ascendant_sign=None, cusps=cusps)
        context = build_kp_context(planet_positions, houses)
        assert context.lagna_sign_name == "Leo"

    def test_build_kp_context_requires_lagna_sign(self) -> None:
        planet_positions = PlanetPositionsInput(
            ascendant_sign=None,
            planets=(p("Sun", "Aries", 1, 10.0),),
        )
        houses = HousesInput(ascendant_sign=None, cusps=())

        with pytest.raises(ValueError, match="Lagna sign is required"):
            build_kp_context(planet_positions, houses)

    def test_build_cusps_from_lagna_when_no_cusp_input(self) -> None:
        context = KPChartContext(
            lagna_sign_index=0,
            lagna_sign_name="Aries",
            lagna_longitude=5.0,
            reference_datetime=None,
            planets={},
            cusps=(),
            significators=(),
            ruling_planets=None,
        )
        records = build_cusps(context)
        assert len(records) == 12
        assert records[0].house == 1
        assert records[0].longitude == pytest.approx(5.0)
        assert records[1].longitude == pytest.approx(35.0)

    def test_cusp_records_use_whole_sign_fallback_longitude(self) -> None:
        planet_positions, houses = kp_chart(
            "Aries",
            (p("Sun", "Aries", 1, 10.0),),
        )
        context = build_kp_context(planet_positions, houses)
        first_cusp = context.cusp_for_house(1)
        assert first_cusp is not None
        assert first_cusp.longitude == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Star lord analysis
# ---------------------------------------------------------------------------


class TestStarLordAnalysis:
    def test_per_planet_star_lord_observations(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart)
        observations = analyze_star_lords(context)

        sun_observation = find_kp_observation(observations, observation_id="kp-star-lord-sun")
        sun = context.get_planet("Sun")
        assert sun_observation.category == KPObservationCategory.STAR_LORD
        assert sun_observation.affected_planets == ("Sun", sun.star_lord)
        assert sun_observation.affected_houses == (sun.house,)
        assert sun_observation.metadata["star_lord"] == sun.star_lord

    def test_star_lord_cluster_observation(
        self,
        star_cluster_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*star_cluster_chart)
        observations = analyze_star_lords(context)
        cluster = find_kp_observation(observations, title="Ketu Star Lord Cluster")
        clustered_planets = cluster.metadata["planets"]

        assert cluster.category == KPObservationCategory.STAR_LORD
        assert "Sun" in cluster.affected_planets
        assert "Moon" in cluster.affected_planets
        assert cluster.severity == pytest.approx(min(0.5 + (0.08 * len(clustered_planets)), 0.85))
        assert cluster.confidence == 0.88


# ---------------------------------------------------------------------------
# Sub lord analysis
# ---------------------------------------------------------------------------


class TestSubLordAnalysis:
    def test_per_planet_sub_lord_observations(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart)
        observations = analyze_sub_lords(context)
        mars_observation = find_kp_observation(observations, observation_id="kp-sub-lord-mars")
        mars = context.get_planet("Mars")

        assert mars_observation.category == KPObservationCategory.SUB_LORD
        assert mars_observation.affected_planets == ("Mars", mars.star_lord, mars.sub_lord)
        assert "shared_sub_lord_planets" in mars_observation.metadata

    def test_own_star_sub_lord_observation(
        self,
        own_star_sub_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*own_star_sub_chart)
        mars = context.get_planet("Mars")
        assert mars.star_lord == mars.sub_lord

        observations = analyze_sub_lords(context)
        own_star = find_kp_observation(
            observations,
            observation_id="kp-sub-lord-own-star-mars",
        )
        assert own_star.title == "Mars Own-Star Sub Lord"
        assert own_star.severity == 0.72


# ---------------------------------------------------------------------------
# Significators
# ---------------------------------------------------------------------------


class TestSignificatorAnalysis:
    def test_build_significators_levels(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart)
        house_one = context.significators_for_house(1)
        assert house_one is not None
        assert "Mars" in house_one.level_a
        assert "Mars" in house_one.combined

    def test_house_significator_observations(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart)
        observations = analyze_significators(context)
        house_one = find_kp_observation(
            observations,
            observation_id="kp-significator-house-01",
        )
        record = context.significators_for_house(1)
        assert record is not None
        assert house_one.affected_planets == record.combined
        assert house_one.category == KPObservationCategory.SIGNIFICATOR

    def test_empty_significator_chain_observation(self) -> None:
        planets = (
            p("Sun", "Aries", 1, 10.0),
            p("Moon", "Cancer", 4, 100.0),
            p("Mars", "Aries", 1, 11.0),
            p("Mercury", "Virgo", 6, 165.0),
            p("Jupiter", "Libra", 7, 190.0),
            p("Venus", "Scorpio", 8, 220.0),
            p("Rahu", "Capricorn", 10, 280.0),
            p("Ketu", "Cancer", 4, 100.0),
        )
        context = build_kp_context(*kp_chart("Aries", planets))
        empty_record = context.significators_for_house(11)
        assert empty_record is not None
        assert empty_record.combined == ()

        observations = analyze_significators(context)
        empty_observation = find_kp_observation(
            observations,
            observation_id="kp-significator-house-11-empty",
        )
        assert empty_observation.title == "House 11 Weak Significator Chain"
        assert empty_observation.severity == 0.62


# ---------------------------------------------------------------------------
# Ruling planets
# ---------------------------------------------------------------------------


class TestRulingPlanets:
    def test_ruling_planets_unavailable_without_reference_time(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart, reference_datetime=None)
        assert context.ruling_planets is None

        observations = analyze_ruling_planets(context)
        unavailable = find_kp_observation(
            observations,
            observation_id="kp-ruling-planets-unavailable",
        )
        assert unavailable.category == KPObservationCategory.RULING_PLANET
        assert unavailable.metadata["available"] is False

    def test_ruling_planets_available_with_reference_time(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart, reference_datetime=KP_REFERENCE_TIME)
        ruling = context.ruling_planets
        assert ruling is not None
        assert ruling.day_lord == _day_lord(KP_REFERENCE_TIME)
        assert ruling.moon_sign_lord == lord_of_sign(context.get_planet("Moon").sign_index)
        assert ruling.lagna_sign_lord == "Mars"

        observations = analyze_ruling_planets(context)
        ruling_set = find_kp_observation(
            observations,
            observation_id="kp-ruling-planets-set",
        )
        assert ruling_set.affected_planets == ruling.ruling_set

    def test_reinforced_ruling_planet_emphasis(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart, reference_datetime=KP_REFERENCE_TIME)
        ruling = context.ruling_planets
        assert ruling is not None

        repeated = _repeated_components(ruling.components)
        assert repeated

        observations = analyze_ruling_planets(context)
        reinforced = find_kp_observation(
            observations,
            observation_id="kp-ruling-planets-reinforced",
        )
        assert reinforced.affected_planets == repeated
        assert reinforced.severity == pytest.approx(min(0.65 + (0.08 * len(repeated)), 0.9))

    def test_compute_ruling_planets_requires_moon(self) -> None:
        context = build_kp_context(
            *kp_chart("Aries", (p("Sun", "Aries", 1, 10.0),)),
            reference_datetime=KP_REFERENCE_TIME,
        )
        assert compute_ruling_planets(
            KPChartContext(
                lagna_sign_index=context.lagna_sign_index,
                lagna_sign_name=context.lagna_sign_name,
                lagna_longitude=context.lagna_longitude,
                reference_datetime=KP_REFERENCE_TIME,
                planets={"Sun": context.get_planet("Sun")},
                cusps=context.cusps,
                significators=context.significators,
                ruling_planets=None,
            )
        ) is None


# ---------------------------------------------------------------------------
# Cuspal analysis
# ---------------------------------------------------------------------------


class TestCuspalAnalysis:
    def test_cuspal_sub_lord_observations(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart)
        observations = analyze_cusps(context)
        first_cusp = context.cusp_for_house(1)
        assert first_cusp is not None

        cusp_observation = find_kp_observation(
            observations,
            observation_id="kp-cusp-house-01",
        )
        assert cusp_observation.affected_planets == (first_cusp.star_lord, first_cusp.sub_lord)
        assert cusp_observation.category == KPObservationCategory.CUSP

    def test_repeated_cuspal_sub_lord_pattern(self) -> None:
        cusp_longitudes = tuple(1.0 if house in (2, 7) else float((house - 1) * 30) for house in range(1, 13))
        context = build_kp_context(
            *kp_chart("Aries", (p("Sun", "Aries", 1, 10.0),), cusp_longitudes=cusp_longitudes)
        )
        _, _, sub_lord = get_sub_lord(1.0)
        observations = analyze_cusps(context)
        pattern = find_kp_observation(
            observations,
            observation_id=f"kp-cusp-sub-lord-{sub_lord.lower()}",
        )
        assert pattern.affected_houses == (2, 7)
        assert pattern.category == KPObservationCategory.CUSP


# ---------------------------------------------------------------------------
# Event timing
# ---------------------------------------------------------------------------


class TestEventTiming:
    def test_event_support_score_helpers(self) -> None:
        assert _event_support_score(set(), set(), ("Venus",), (2, 7)) == 0.0
        assert _event_support_score({"Venus"}, set(), ("Venus", "Jupiter"), (2, 7, 11)) == pytest.approx(0.175)
        assert _event_support_score(
            {"Venus", "Jupiter"},
            {"Venus"},
            ("Venus", "Jupiter"),
            (2, 7, 11),
        ) == pytest.approx(0.6167, rel=1e-3)

    def test_evaluate_event_templates_supported_marriage(
        self,
        marriage_event_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*marriage_event_chart, reference_datetime=KP_REFERENCE_TIME)
        records = evaluate_event_templates(context)
        marriage = next(record for record in records if record.event_type == "marriage")

        assert marriage.is_supported is True
        assert marriage.support_score >= EVENT_SUPPORT_THRESHOLD
        assert "Venus" in marriage.significators_matched
        assert "Venus" in marriage.cusp_sub_lords_matched

    def test_event_timing_observations(
        self,
        marriage_event_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*marriage_event_chart)
        records = evaluate_event_templates(context)
        observations = event_records_to_observations(records)
        marriage = find_kp_observation(observations, observation_id="kp-event-marriage_event")

        assert marriage.category == KPObservationCategory.EVENT_TIMING
        assert "supported" in marriage.explanation
        assert marriage.confidence == 0.9

    def test_unsupported_event_timing_observation(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart)
        observations = analyze_event_timing(context)
        marriage = find_kp_observation(observations, observation_id="kp-event-marriage_event")
        assert "not supported" in marriage.explanation
        assert marriage.confidence == 0.82

    def test_event_timing_analyzer_wrapper(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart)
        analyzer = EventTimingAnalyzer()
        assert len(analyzer.analyze(context)) == len(EVENT_TEMPLATES)
        assert len(analyzer.analyze_observations(context)) == len(EVENT_TEMPLATES)

    def test_event_record_to_observation_fields(self) -> None:
        record = EventTimingRecord(
            event_id="test_event",
            event_type="career",
            target_houses=(10,),
            is_supported=False,
            support_score=0.2,
            significators_matched=("Sun",),
            cusp_sub_lords_matched=(),
            evidence=("Sun is significator for house 10.",),
        )
        observation = event_records_to_observations((record,))[0]
        assert observation.affected_planets == ("Sun",)
        assert observation.affected_houses == (10,)
        assert observation.metadata["evidence"] == record.evidence


# ---------------------------------------------------------------------------
# Analyzer integration and determinism
# ---------------------------------------------------------------------------


class TestAnalyzerIntegration:
    def test_full_analysis_metadata(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        result = analyze_kp(*standard_kp_chart)
        assert result.metadata["engine"] == "kp_intelligence_v1"
        assert result.metadata["lagna_sign"] == "Aries"
        assert result.metadata["planet_count"] == 9
        assert result.metadata["observation_count"] == len(result.observations)
        assert result.metadata["ruling_planets_available"] is True
        assert sum(result.metadata["category_counts"].values()) == len(result.observations)
        assert len(result.event_timing) == len(EVENT_TEMPLATES)

    def test_deterministic_observation_snapshot(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        first = analyze_kp(*standard_kp_chart).observations
        second = analyze_kp(*standard_kp_chart).observations
        assert [(item.observation_id, item.severity, item.confidence) for item in first] == [
            (item.observation_id, item.severity, item.confidence) for item in second
        ]

    def test_frozen_analyzed_at_timestamp(
        self,
        frozen_kp_analyzer: KPIntelligenceAnalyzer,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        result = frozen_kp_analyzer.analyze(
            planet_positions=standard_kp_chart[0],
            houses=standard_kp_chart[1],
            reference_datetime=KP_REFERENCE_TIME,
        )
        assert result.analyzed_at == FIXED_ANALYSIS_TIME

    def test_modular_pipeline_matches_combined_analyzer(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        context = build_kp_context(*standard_kp_chart, reference_datetime=KP_REFERENCE_TIME)
        timing = EventTimingAnalyzer()
        modular_ids = [
            item.observation_id
            for item in (
                *analyze_star_lords(context),
                *analyze_sub_lords(context),
                *analyze_significators(context),
                *analyze_ruling_planets(context),
                *analyze_cusps(context),
                *timing.analyze_observations(context),
            )
        ]
        combined_ids = [
            item.observation_id for item in analyze_kp(*standard_kp_chart).observations
        ]
        assert modular_ids == combined_ids

    def test_classical_chart_integration(self) -> None:
        planet_positions, houses = classical_chart("Aries")
        result = analyze_kp(planet_positions, houses)
        assert result.metadata["planet_count"] == 9
        assert _titles(result.observations)

    def test_custom_event_timing_dependency(
        self,
        standard_kp_chart: tuple[PlanetPositionsInput, HousesInput],
    ) -> None:
        class StubTiming(EventTimingAnalyzer):
            def analyze(self, context: KPChartContext) -> tuple[EventTimingRecord, ...]:
                return (
                    EventTimingRecord(
                        event_id="stub_event",
                        event_type="stub",
                        target_houses=(1,),
                        is_supported=True,
                        support_score=0.9,
                        significators_matched=("Sun",),
                        cusp_sub_lords_matched=(),
                        evidence=("stub evidence",),
                    ),
                )

            def analyze_observations(
                self,
                context: KPChartContext,
            ) -> tuple[ReasoningObservation, ...]:
                return event_records_to_observations(self.analyze(context))

        analyzer = KPIntelligenceAnalyzer(event_timing=StubTiming())
        result = analyzer.analyze(
            planet_positions=standard_kp_chart[0],
            houses=standard_kp_chart[1],
            reference_datetime=KP_REFERENCE_TIME,
        )
        assert result.event_timing[0].event_id == "stub_event"
        assert find_kp_observation(result.observations, observation_id="kp-event-stub_event")

    def test_planet_house_fallback_from_sign(
        self,
    ) -> None:
        planet_positions = PlanetPositionsInput(
            ascendant_sign="Aries",
            planets=(p("Sun", "Gemini", None, 70.0),),
        )
        houses = houses_for("Aries")
        context = build_kp_context(planet_positions, houses)
        assert context.get_planet("Sun").house == 3

    def test_invalid_sign_name_passthrough_in_normalization(self) -> None:
        planet_positions = PlanetPositionsInput(
            ascendant_sign="Aries",
            planets=(p("Sun", "UnknownSign", 1, 10.0),),
        )
        houses = houses_for("Aries")
        with pytest.raises(ValueError, match="Unknown sign name"):
            build_kp_context(planet_positions, houses)

    def test_ruling_planets_metadata_when_unavailable(self) -> None:
        planet_positions, houses = standard_kp_chart_fixture()
        result = analyze_kp(planet_positions, houses, reference_datetime=None)
        assert result.metadata["ruling_planets_available"] is False
        assert find_kp_observation(
            result.observations,
            observation_id="kp-ruling-planets-unavailable",
        )


def standard_kp_chart_fixture() -> tuple[PlanetPositionsInput, HousesInput]:
    """Local helper mirroring the standard chart fixture."""
    planets = (
        p("Sun", "Gemini", 3, 70.0),
        p("Moon", "Cancer", 4, 100.0),
        p("Mars", "Aries", 1, 10.0),
        p("Mercury", "Virgo", 6, 165.0),
        p("Jupiter", "Libra", 7, 190.0),
        p("Venus", "Scorpio", 8, 220.0),
        p("Saturn", "Sagittarius", 9, 250.0),
        p("Rahu", "Capricorn", 10, 280.0),
        p("Ketu", "Cancer", 4, 100.0),
    )
    return kp_chart("Aries", planets, moon_sign="Cancer")
