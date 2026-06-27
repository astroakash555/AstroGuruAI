"""Comprehensive tests for the intelligence fusion layer."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.app.services.reasoning.fusion import (
    FusionContext,
    FusionEngineId,
    FusionResult,
    IntelligenceFusionEngine,
    NormalizedObservation,
    build_recommendations,
    build_root_causes,
    collect_observations,
    compute_rank_score,
    conflict_observation_ids,
    deduplicate_observations,
    detect_conflicts,
    merge_supporting_evidence,
    normalize_kp_observation,
    normalize_title,
    normalize_vedic_observation,
    observation_signature,
    rank_observations,
)
from backend.app.services.reasoning.fusion.engine import (
    DashaIntelligenceAdapter,
    LalKitabIntelligenceAdapter,
    TransitIntelligenceAdapter,
    VedicIntelligenceAdapter,
)
from backend.app.services.reasoning.fusion.models import FusedObservation
from backend.app.services.reasoning.kp.constants import KPObservationCategory
from backend.app.services.reasoning.kp.models import ReasoningObservation as KPObservation
from backend.app.services.reasoning.models import (
    DashaInput,
    DashaPeriodSnapshot,
    HousesInput,
    LalKitabDataInput,
    LalKitabFindingSnapshot,
    PlanetPositionsInput,
    TransitInput,
    TransitPlanetSnapshot,
)
from backend.app.services.reasoning.vedic.constants import ObservationCategory, VedicObservation
from tests.reasoning.conftest import FIXED_ANALYSIS_TIME, classical_chart

FUSION_REFERENCE_TIME = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


def _normalized(
    *,
    observation_id: str,
    engine: FusionEngineId,
    title: str,
    severity: float,
    confidence: float,
    planets: tuple[str, ...] = (),
    houses: tuple[int, ...] = (),
) -> NormalizedObservation:
    return NormalizedObservation(
        observation_id=observation_id,
        engine=engine,
        category=f"{engine.value}:test",
        title=title,
        explanation=f"{title} explanation.",
        affected_planets=planets,
        affected_houses=houses,
        severity=severity,
        confidence=confidence,
    )


def _fused(
    *,
    fusion_id: str,
    title: str,
    severity: float,
    confidence: float,
    engines: tuple[FusionEngineId, ...],
    planets: tuple[str, ...] = ("Mars",),
    houses: tuple[int, ...] = (1,),
    rank_score: float = 0.0,
) -> FusedObservation:
    return FusedObservation(
        fusion_id=fusion_id,
        title=title,
        explanation=f"{title} explanation.",
        category="fusion:test",
        affected_planets=planets,
        affected_houses=houses,
        severity=severity,
        confidence=confidence,
        supporting_engines=engines,
        source_observation_ids=(fusion_id,),
        rank_score=rank_score,
    )


def fusion_context(**kwargs) -> FusionContext:
    planet_positions, houses = classical_chart("Aries")
    defaults = {
        "planet_positions": planet_positions,
        "houses": houses,
        "reference_datetime": FUSION_REFERENCE_TIME,
    }
    defaults.update(kwargs)
    return FusionContext(**defaults)


@pytest.fixture
def frozen_fusion_engine(monkeypatch: pytest.MonkeyPatch) -> IntelligenceFusionEngine:
    import backend.app.services.reasoning.fusion.engine as engine_module

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None) -> datetime:  # noqa: ANN001
            if tz is None:
                return FIXED_ANALYSIS_TIME.replace(tzinfo=None)
            return FIXED_ANALYSIS_TIME

    monkeypatch.setattr(engine_module, "datetime", FixedDateTime)
    return IntelligenceFusionEngine()


class TestEvidenceNormalization:
    def test_normalize_vedic_observation(self) -> None:
        source = VedicObservation(
            observation_id="vedic-test",
            category=ObservationCategory.DOSHA,
            title="Manglik Dosha",
            explanation="Mars influences marriage houses.",
            affected_planets=("Mars",),
            affected_houses=(1, 4, 7, 8, 12),
            severity=0.72,
            confidence=0.88,
        )
        normalized = normalize_vedic_observation(source)
        assert normalized.engine == FusionEngineId.VEDIC
        assert normalized.category == "vedic:dosha"
        assert normalized.title == "Manglik Dosha"

    def test_normalize_kp_observation(self) -> None:
        source = KPObservation(
            observation_id="kp-test",
            category=KPObservationCategory.STAR_LORD,
            title="Mars Star Lord",
            explanation="Mars star lord detail.",
            affected_planets=("Mars", "Ketu"),
            affected_houses=(1,),
            severity=0.55,
            confidence=0.92,
        )
        normalized = normalize_kp_observation(source)
        assert normalized.engine == FusionEngineId.KP
        assert normalized.category == "kp:star_lord"

    def test_deduplicate_within_engine(self) -> None:
        observations = (
            _normalized(
                observation_id="dup",
                engine=FusionEngineId.VEDIC,
                title="One",
                severity=0.5,
                confidence=0.8,
            ),
            _normalized(
                observation_id="dup",
                engine=FusionEngineId.VEDIC,
                title="One duplicate",
                severity=0.6,
                confidence=0.9,
            ),
        )
        deduplicated = deduplicate_observations(observations)
        assert len(deduplicated) == 1

    def test_merge_supporting_evidence_across_engines(self) -> None:
        observations = (
            _normalized(
                observation_id="vedic-mars",
                engine=FusionEngineId.VEDIC,
                title="Mars Factor",
                severity=0.70,
                confidence=0.85,
                planets=("Mars",),
                houses=(1,),
            ),
            _normalized(
                observation_id="kp-mars",
                engine=FusionEngineId.KP,
                title="Mars Factor",
                severity=0.60,
                confidence=0.90,
                planets=("Mars",),
                houses=(1,),
            ),
        )
        fused = merge_supporting_evidence(observations)
        assert len(fused) == 1
        assert fused[0].supporting_engines == (FusionEngineId.VEDIC, FusionEngineId.KP)
        assert fused[0].severity == 0.70
        assert "Corroborated by" in fused[0].explanation

    def test_observation_signature_and_title_normalization(self) -> None:
        observation = _normalized(
            observation_id="sig",
            engine=FusionEngineId.KP,
            title="Mars Star Lord",
            severity=0.5,
            confidence=0.8,
            planets=("Mars",),
            houses=(1,),
        )
        assert normalize_title("Mars Star Lord") == "marsstarlord"
        assert observation_signature(observation)[2] == "marsstarlord"


class TestConflictResolver:
    def test_detect_conflicts_for_same_focus(self) -> None:
        observations = (
            _normalized(
                observation_id="vedic-conflict",
                engine=FusionEngineId.VEDIC,
                title="Strong Mars",
                severity=0.90,
                confidence=0.92,
                planets=("Mars",),
                houses=(1,),
            ),
            _normalized(
                observation_id="kp-conflict",
                engine=FusionEngineId.KP,
                title="Weak Mars",
                severity=0.40,
                confidence=0.91,
                planets=("Mars",),
                houses=(1,),
            ),
        )
        conflicts = detect_conflicts(observations)
        assert len(conflicts) == 1
        assert conflicts[0].severity_spread == pytest.approx(0.50)
        assert set(conflicts[0].engines) == {FusionEngineId.VEDIC, FusionEngineId.KP}

    def test_no_conflict_when_severity_is_aligned(self) -> None:
        observations = (
            _normalized(
                observation_id="vedic-aligned",
                engine=FusionEngineId.VEDIC,
                title="Mars Factor",
                severity=0.70,
                confidence=0.90,
                planets=("Mars",),
                houses=(1,),
            ),
            _normalized(
                observation_id="kp-aligned",
                engine=FusionEngineId.KP,
                title="Mars Factor",
                severity=0.68,
                confidence=0.88,
                planets=("Mars",),
                houses=(1,),
            ),
        )
        assert detect_conflicts(observations) == ()


class TestRanking:
    def test_rank_score_prefers_multi_engine_support(self) -> None:
        single = _fused(
            fusion_id="single",
            title="Single Engine",
            severity=0.70,
            confidence=0.90,
            engines=(FusionEngineId.VEDIC,),
        )
        multi = _fused(
            fusion_id="multi",
            title="Multi Engine",
            severity=0.70,
            confidence=0.90,
            engines=(FusionEngineId.VEDIC, FusionEngineId.KP),
        )
        single_score = compute_rank_score(single, active_engine_count=2)
        multi_score = compute_rank_score(multi, active_engine_count=2)
        assert multi_score > single_score

    def test_rank_observations_orders_descending(self) -> None:
        low = _fused(
            fusion_id="low",
            title="Low",
            severity=0.40,
            confidence=0.50,
            engines=(FusionEngineId.VEDIC,),
        )
        high = _fused(
            fusion_id="high",
            title="High",
            severity=0.90,
            confidence=0.95,
            engines=(FusionEngineId.VEDIC, FusionEngineId.KP),
        )
        ranked = rank_observations((low, high), active_engine_count=2)
        assert ranked[0].fusion_id == "high"
        assert ranked[0].rank_score >= ranked[1].rank_score


class TestRootCauseAndRecommendations:
    def test_build_root_causes_from_ranked_observations(self) -> None:
        ranked = rank_observations(
            (
                _fused(
                    fusion_id="cause-1",
                    title="Primary Factor",
                    severity=0.85,
                    confidence=0.92,
                    engines=(FusionEngineId.VEDIC, FusionEngineId.KP),
                ),
            ),
            active_engine_count=2,
        )
        root_causes = build_root_causes(ranked)
        assert len(root_causes) == 1
        assert root_causes[0].supporting_observations == ("cause-1",)
        assert set(root_causes[0].supporting_engines) == {
            FusionEngineId.VEDIC,
            FusionEngineId.KP,
        }

    def test_build_recommendations_from_root_causes(self) -> None:
        root_causes = build_root_causes(
            rank_observations(
                (
                    _fused(
                        fusion_id="cause-1",
                        title="Primary Factor",
                        severity=0.85,
                        confidence=0.92,
                        engines=(FusionEngineId.VEDIC, FusionEngineId.KP),
                    ),
                ),
                active_engine_count=2,
            )
        )
        recommendations = build_recommendations(root_causes)
        assert len(recommendations) == 1
        assert recommendations[0].priority == "high"
        assert recommendations[0].supporting_root_causes == (root_causes[0].title,)


class TestFutureAdapters:
    def test_lal_kitab_adapter_emits_chart_observations(self) -> None:
        context = fusion_context()
        observations = LalKitabIntelligenceAdapter().analyze(context)
        assert len(observations) > 0
        assert observations[0].engine == FusionEngineId.LAL_KITAB
        assert all(item.observation_id for item in observations)

    def test_dasha_adapter_emits_active_periods(self) -> None:
        context = fusion_context(
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Saturn"),
                current_antardasha=DashaPeriodSnapshot(level="antardasha", lord="Mercury"),
            )
        )
        observations = DashaIntelligenceAdapter().analyze(context)
        assert len(observations) > 2
        categories = {item.category for item in observations}
        assert "dasha:mahadasha" in categories
        assert "dasha:antardasha" in categories
        assert {item.affected_planets[0] for item in observations if item.category == "dasha:mahadasha"} == {"Saturn"}

    def test_transit_adapter_emits_transiting_planets(self) -> None:
        context = fusion_context(
            transit=TransitInput(
                reference_datetime=FUSION_REFERENCE_TIME,
                planets=(
                    TransitPlanetSnapshot(
                        planet="Saturn",
                        sign="Pisces",
                        house_from_lagna=12,
                        house_from_moon=9,
                    ),
                ),
            )
        )
        observations = TransitIntelligenceAdapter().analyze(context)
        assert len(observations) > 1
        categories = {item.category for item in observations}
        assert "transit:planet_transit" in categories
        assert observations[0].affected_planets[0] == "Saturn"


class TestFusionEngineIntegration:
    def test_fuses_vedic_and_kp_observations(self) -> None:
        result = IntelligenceFusionEngine().fuse(fusion_context())
        assert isinstance(result, FusionResult)
        assert result.metadata["engine"] == "intelligence_fusion_v1"
        assert "vedic" in result.metadata["active_engines"]
        assert "kp" in result.metadata["active_engines"]
        assert "lal_kitab" in result.metadata["active_engines"]
        assert len(result.observations) > 0
        assert len(result.root_causes) > 0
        assert len(result.recommendations) == len(result.root_causes)
        assert 0.0 <= result.confidence_score <= 1.0

    def test_observations_are_ranked_descending(self) -> None:
        result = IntelligenceFusionEngine().fuse(fusion_context())
        scores = [item.rank_score for item in result.observations]
        assert scores == sorted(scores, reverse=True)

    def test_deterministic_fusion_snapshot(self) -> None:
        context = fusion_context()
        first = IntelligenceFusionEngine().fuse(context)
        second = IntelligenceFusionEngine().fuse(context)
        assert [
            (item.fusion_id, item.rank_score, item.confidence, item.severity)
            for item in first.observations
        ] == [
            (item.fusion_id, item.rank_score, item.confidence, item.severity)
            for item in second.observations
        ]

    def test_frozen_analyzed_at_timestamp(
        self,
        frozen_fusion_engine: IntelligenceFusionEngine,
    ) -> None:
        result = frozen_fusion_engine.fuse(fusion_context())
        assert result.analyzed_at == FIXED_ANALYSIS_TIME

    def test_custom_adapter_registry(self) -> None:
        class StubAdapter:
            @property
            def engine_id(self) -> FusionEngineId:
                return FusionEngineId.TRANSIT

            def is_available(self, context: FusionContext) -> bool:
                return True

            def analyze(self, context: FusionContext) -> tuple[NormalizedObservation, ...]:
                return (
                    _normalized(
                        observation_id="stub-transit",
                        engine=FusionEngineId.TRANSIT,
                        title="Stub Transit",
                        severity=0.77,
                        confidence=0.80,
                        planets=("Jupiter",),
                        houses=(9,),
                    ),
                )

        engine = IntelligenceFusionEngine(adapters=(StubAdapter(),))
        result = engine.fuse(fusion_context())
        assert result.metadata["active_engines"] == ("transit",)
        assert any(item.supporting_engines == (FusionEngineId.TRANSIT,) for item in result.observations)

    def test_collect_observations_stable_order(self) -> None:
        observations = collect_observations(
            (
                _normalized(
                    observation_id="b",
                    engine=FusionEngineId.KP,
                    title="B",
                    severity=0.5,
                    confidence=0.5,
                ),
                _normalized(
                    observation_id="a",
                    engine=FusionEngineId.VEDIC,
                    title="A",
                    severity=0.5,
                    confidence=0.5,
                ),
            )
        )
        assert observations[0].engine == FusionEngineId.KP

    def test_conflict_ids_mark_fused_observations(self) -> None:
        observations = (
            _normalized(
                observation_id="vedic-conflict",
                engine=FusionEngineId.VEDIC,
                title="Strong Mars",
                severity=0.90,
                confidence=0.92,
                planets=("Mars",),
                houses=(1,),
            ),
            _normalized(
                observation_id="kp-conflict",
                engine=FusionEngineId.KP,
                title="Weak Mars",
                severity=0.40,
                confidence=0.91,
                planets=("Mars",),
                houses=(1,),
            ),
        )
        conflicts = detect_conflicts(observations)
        fused = merge_supporting_evidence(
            observations,
            conflict_ids=conflict_observation_ids(conflicts),
        )
        assert any(item.has_conflict for item in fused)

    def test_future_engines_included_when_data_present(self) -> None:
        context = fusion_context(
            dasha=DashaInput(
                system="vimshottari",
                current_mahadasha=DashaPeriodSnapshot(level="mahadasha", lord="Saturn"),
            ),
            transit=TransitInput(
                reference_datetime=FUSION_REFERENCE_TIME,
                planets=(TransitPlanetSnapshot(planet="Jupiter", sign="Gemini", house_from_lagna=3),),
            ),
            lal_kitab_data=LalKitabDataInput(
                findings=(
                    LalKitabFindingSnapshot(
                        finding_id="lk-1",
                        name="Sample Finding",
                        category="debt",
                        is_present=True,
                        strength=0.7,
                    ),
                )
            ),
        )
        result = IntelligenceFusionEngine().fuse(context)
        assert "dasha" in result.metadata["active_engines"]
        assert "transit" in result.metadata["active_engines"]
        assert "lal_kitab" in result.metadata["active_engines"]

    def test_vedic_adapter_availability_requires_chart_data(self) -> None:
        adapter = VedicIntelligenceAdapter()
        empty_context = FusionContext(
            planet_positions=PlanetPositionsInput(planets=()),
            houses=HousesInput(cusps=()),
        )
        assert adapter.is_available(empty_context) is False
