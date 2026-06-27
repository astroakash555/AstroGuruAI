"""Intelligence fusion engine orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

from backend.app.services.reasoning.fusion.conflict_resolver import (
    conflict_observation_ids,
    detect_conflicts,
)
from backend.app.services.reasoning.dasha.analyzer import DashaIntelligenceAnalyzer
from backend.app.services.reasoning.fusion.evidence import (
    collect_observations,
    deduplicate_observations,
    merge_supporting_evidence,
    normalize_dasha_observation,
    normalize_kp_observation,
    normalize_lal_kitab_observation,
    normalize_vedic_observation,
)
from backend.app.services.reasoning.fusion.models import (
    FusionContext,
    FusionEngineId,
    FusionResult,
    NormalizedObservation,
)
from backend.app.services.reasoning.fusion.ranking import rank_observations
from backend.app.services.reasoning.fusion.recommendation import build_recommendations
from backend.app.services.reasoning.fusion.root_cause import build_root_causes
from backend.app.services.reasoning.kp.analyzer import KPIntelligenceAnalyzer
from backend.app.services.reasoning.lal_kitab.analyzer import LalKitabIntelligenceAnalyzer
from backend.app.services.reasoning.vedic.analyzer import VedicIntelligenceAnalyzer


class IntelligenceAnalyzerAdapter(Protocol):
    """Contract for pluggable intelligence engines in the fusion layer."""

    @property
    def engine_id(self) -> FusionEngineId:
        """Unique engine identifier."""
        ...

    def is_available(self, context: FusionContext) -> bool:
        """Return True when the adapter can analyze the supplied context."""
        ...

    def analyze(self, context: FusionContext) -> tuple[NormalizedObservation, ...]:
        """Run the engine and return normalized observations."""
        ...


class VedicIntelligenceAdapter:
    """Adapter wrapping the Vedic intelligence analyzer."""

    def __init__(self, analyzer: VedicIntelligenceAnalyzer | None = None) -> None:
        self._analyzer = analyzer or VedicIntelligenceAnalyzer()

    @property
    def engine_id(self) -> FusionEngineId:
        return FusionEngineId.VEDIC

    def is_available(self, context: FusionContext) -> bool:
        return bool(context.planet_positions.planets and context.houses.cusps)

    def analyze(self, context: FusionContext) -> tuple[NormalizedObservation, ...]:
        result = self._analyzer.analyze(
            planet_positions=context.planet_positions,
            houses=context.houses,
        )
        return tuple(normalize_vedic_observation(item) for item in result.observations)


class KPIntelligenceAdapter:
    """Adapter wrapping the KP intelligence analyzer."""

    def __init__(self, analyzer: KPIntelligenceAnalyzer | None = None) -> None:
        self._analyzer = analyzer or KPIntelligenceAnalyzer()

    @property
    def engine_id(self) -> FusionEngineId:
        return FusionEngineId.KP

    def is_available(self, context: FusionContext) -> bool:
        return bool(context.planet_positions.planets and context.houses.cusps)

    def analyze(self, context: FusionContext) -> tuple[NormalizedObservation, ...]:
        result = self._analyzer.analyze(
            planet_positions=context.planet_positions,
            houses=context.houses,
            reference_datetime=context.reference_datetime,
        )
        return tuple(normalize_kp_observation(item) for item in result.observations)


class LalKitabIntelligenceAdapter:
    """Adapter wrapping the Lal Kitab intelligence analyzer."""

    def __init__(self, analyzer: LalKitabIntelligenceAnalyzer | None = None) -> None:
        self._analyzer = analyzer or LalKitabIntelligenceAnalyzer()

    @property
    def engine_id(self) -> FusionEngineId:
        return FusionEngineId.LAL_KITAB

    def is_available(self, context: FusionContext) -> bool:
        return bool(context.planet_positions.planets and context.houses.cusps)

    def analyze(self, context: FusionContext) -> tuple[NormalizedObservation, ...]:
        result = self._analyzer.analyze(
            planet_positions=context.planet_positions,
            houses=context.houses,
        )
        return tuple(normalize_lal_kitab_observation(item) for item in result.observations)


class DashaIntelligenceAdapter:
    """Adapter wrapping the Dasha intelligence analyzer."""

    def __init__(self, analyzer: DashaIntelligenceAnalyzer | None = None) -> None:
        self._analyzer = analyzer or DashaIntelligenceAnalyzer()

    @property
    def engine_id(self) -> FusionEngineId:
        return FusionEngineId.DASHA

    def is_available(self, context: FusionContext) -> bool:
        dasha = context.dasha
        if dasha is None:
            return False
        return bool(
            dasha.current_mahadasha
            or dasha.current_antardasha
            or dasha.current_pratyantar
            or dasha.mahadashas
        )

    def analyze(self, context: FusionContext) -> tuple[NormalizedObservation, ...]:
        dasha = context.dasha
        if dasha is None:
            return ()

        has_chart = bool(context.planet_positions.planets and context.houses.cusps)
        result = self._analyzer.analyze(
            dasha=dasha,
            planet_positions=context.planet_positions if has_chart else None,
            houses=context.houses if has_chart else None,
            reference_datetime=context.reference_datetime,
        )
        return tuple(normalize_dasha_observation(item) for item in result.observations)


class TransitIntelligenceAdapter:
    """Placeholder adapter for future transit intelligence integration."""

    @property
    def engine_id(self) -> FusionEngineId:
        return FusionEngineId.TRANSIT

    def is_available(self, context: FusionContext) -> bool:
        transit = context.transit
        return transit is not None and len(transit.planets) > 0

    def analyze(self, context: FusionContext) -> tuple[NormalizedObservation, ...]:
        transit = context.transit
        if transit is None:
            return ()

        observations: list[NormalizedObservation] = []
        for snapshot in transit.planets:
            houses = tuple(
                house
                for house in (snapshot.house_from_lagna, snapshot.house_from_moon)
                if house is not None
            )
            observations.append(
                NormalizedObservation(
                    observation_id=f"transit-{snapshot.planet.lower()}",
                    engine=FusionEngineId.TRANSIT,
                    category="transit:placement",
                    title=f"Transiting {snapshot.planet} in {snapshot.sign}",
                    explanation=(
                        f"Transiting {snapshot.planet} occupies {snapshot.sign}"
                        + (
                            f" influencing houses {', '.join(str(house) for house in houses)}."
                            if houses
                            else "."
                        )
                    ),
                    affected_planets=(snapshot.planet,),
                    affected_houses=houses,
                    severity=0.60,
                    confidence=0.84,
                    metadata={
                        "sign": snapshot.sign,
                        "is_retrograde": snapshot.is_retrograde,
                        "reference_datetime": (
                            transit.reference_datetime.isoformat()
                            if transit.reference_datetime is not None
                            else None
                        ),
                    },
                )
            )
        return tuple(observations)


class IntelligenceFusionEngine:
    """
    Executes available intelligence analyzers and fuses their observations.

    The engine deduplicates evidence, resolves conflicts, ranks observations,
    and synthesizes root causes and recommendations without API coupling.
    """

    ENGINE_VERSION = "intelligence_fusion_v1"

    def __init__(
        self,
        *,
        adapters: tuple[IntelligenceAnalyzerAdapter, ...] | None = None,
    ) -> None:
        self._adapters = adapters or default_adapters()

    @property
    def adapters(self) -> tuple[IntelligenceAnalyzerAdapter, ...]:
        """Registered intelligence analyzer adapters."""
        return self._adapters

    def fuse(self, context: FusionContext) -> FusionResult:
        """Execute all available analyzers and return a fused intelligence result."""
        active_adapters = tuple(adapter for adapter in self._adapters if adapter.is_available(context))
        raw_observations: list[NormalizedObservation] = []

        for adapter in active_adapters:
            raw_observations.extend(adapter.analyze(context))

        collected = collect_observations(tuple(raw_observations))
        deduplicated = deduplicate_observations(collected)
        conflicts = detect_conflicts(deduplicated)
        conflict_ids = conflict_observation_ids(conflicts)
        fused = merge_supporting_evidence(deduplicated, conflict_ids=conflict_ids)
        ranked = rank_observations(
            fused,
            active_engine_count=max(len(active_adapters), 1),
        )
        root_causes = build_root_causes(ranked)
        recommendations = build_recommendations(root_causes)
        confidence_score = _compute_confidence_score(
            root_causes,
            ranked,
            active_engine_count=len(active_adapters),
            registered_engine_count=len(self._adapters),
        )

        return FusionResult(
            analyzed_at=datetime.now(timezone.utc),
            observations=ranked,
            root_causes=root_causes,
            recommendations=recommendations,
            confidence_score=confidence_score,
            conflicts=conflicts,
            metadata={
                "engine": self.ENGINE_VERSION,
                "active_engines": tuple(adapter.engine_id.value for adapter in active_adapters),
                "registered_engines": tuple(adapter.engine_id.value for adapter in self._adapters),
                "raw_observation_count": len(collected),
                "fused_observation_count": len(ranked),
                "conflict_count": len(conflicts),
                "root_cause_count": len(root_causes),
                "recommendation_count": len(recommendations),
            },
        )


def default_adapters() -> tuple[IntelligenceAnalyzerAdapter, ...]:
    """Return the default set of intelligence analyzer adapters."""
    return (
        VedicIntelligenceAdapter(),
        KPIntelligenceAdapter(),
        LalKitabIntelligenceAdapter(),
        DashaIntelligenceAdapter(),
        TransitIntelligenceAdapter(),
    )


def _compute_confidence_score(
    root_causes: tuple,
    observations: tuple,
    *,
    active_engine_count: int,
    registered_engine_count: int,
) -> float:
    """Compute an overall fusion confidence score."""
    if root_causes:
        root_component = sum(item.confidence for item in root_causes) / len(root_causes)
    elif observations:
        root_component = sum(item.confidence for item in observations[:5]) / min(len(observations), 5)
    else:
        root_component = 0.0

    engine_coverage = active_engine_count / max(registered_engine_count, 1)
    score = (0.75 * root_component) + (0.25 * engine_coverage)
    return round(min(max(score, 0.0), 1.0), 4)
