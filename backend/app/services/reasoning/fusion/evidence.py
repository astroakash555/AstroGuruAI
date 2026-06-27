"""Evidence normalization, deduplication, and merge helpers."""

from __future__ import annotations

import re

from backend.app.services.reasoning.fusion.models import (
    FusionEngineId,
    FusedObservation,
    NormalizedObservation,
)
from backend.app.services.reasoning.dasha.models import ReasoningObservation as DashaObservation
from backend.app.services.reasoning.kp.models import ReasoningObservation as KPObservation
from backend.app.services.reasoning.lal_kitab.models import ReasoningObservation as LalKitabObservation
from backend.app.services.reasoning.vedic.constants import VedicObservation

TITLE_NORMALIZER = re.compile(r"[^a-z0-9]+")


def normalize_vedic_observation(observation: VedicObservation) -> NormalizedObservation:
    """Convert a Vedic observation into the fusion-normalized shape."""
    return NormalizedObservation(
        observation_id=observation.observation_id,
        engine=FusionEngineId.VEDIC,
        category=f"vedic:{observation.category.value}",
        title=observation.title,
        explanation=observation.explanation,
        affected_planets=observation.affected_planets,
        affected_houses=observation.affected_houses,
        severity=observation.severity,
        confidence=observation.confidence,
        metadata=dict(observation.metadata),
    )


def normalize_kp_observation(observation: KPObservation) -> NormalizedObservation:
    """Convert a KP observation into the fusion-normalized shape."""
    return NormalizedObservation(
        observation_id=observation.observation_id,
        engine=FusionEngineId.KP,
        category=f"kp:{observation.category.value}",
        title=observation.title,
        explanation=observation.explanation,
        affected_planets=observation.affected_planets,
        affected_houses=observation.affected_houses,
        severity=observation.severity,
        confidence=observation.confidence,
        metadata=dict(observation.metadata),
    )


def normalize_lal_kitab_observation(observation: LalKitabObservation) -> NormalizedObservation:
    """Convert a Lal Kitab observation into the fusion-normalized shape."""
    return NormalizedObservation(
        observation_id=observation.observation_id,
        engine=FusionEngineId.LAL_KITAB,
        category=f"lal_kitab:{observation.category.value}",
        title=observation.title,
        explanation=observation.explanation,
        affected_planets=observation.affected_planets,
        affected_houses=observation.affected_houses,
        severity=observation.severity,
        confidence=observation.confidence,
        metadata=dict(observation.metadata),
    )


def normalize_dasha_observation(observation: DashaObservation) -> NormalizedObservation:
    """Convert a Dasha observation into the fusion-normalized shape."""
    return NormalizedObservation(
        observation_id=observation.observation_id,
        engine=FusionEngineId.DASHA,
        category=f"dasha:{observation.category.value}",
        title=observation.title,
        explanation=observation.explanation,
        affected_planets=observation.affected_planets,
        affected_houses=observation.affected_houses,
        severity=observation.severity,
        confidence=observation.confidence,
        metadata=dict(observation.metadata),
    )


def collect_observations(
    observations: tuple[NormalizedObservation, ...],
) -> tuple[NormalizedObservation, ...]:
    """Return observations in stable engine and identifier order."""
    return tuple(
        sorted(
            observations,
            key=lambda item: (item.engine.value, item.observation_id, item.title),
        )
    )


def deduplicate_observations(
    observations: tuple[NormalizedObservation, ...],
) -> tuple[NormalizedObservation, ...]:
    """Remove duplicate observations within the same intelligence engine."""
    seen: set[tuple[str, str]] = set()
    unique: list[NormalizedObservation] = []

    for observation in observations:
        key = (observation.engine.value, observation.observation_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append(observation)

    return tuple(unique)


def observation_signature(observation: NormalizedObservation) -> tuple[frozenset[str], frozenset[int], str]:
    """Build a merge signature for cross-engine evidence grouping."""
    return (
        frozenset(observation.affected_planets),
        frozenset(observation.affected_houses),
        normalize_title(observation.title),
    )


def normalize_title(title: str) -> str:
    """Normalize a title for duplicate and merge detection."""
    return TITLE_NORMALIZER.sub("", title.strip().lower())


def merge_supporting_evidence(
    observations: tuple[NormalizedObservation, ...],
    *,
    conflict_ids: frozenset[str] | None = None,
) -> tuple[FusedObservation, ...]:
    """
    Merge cross-engine observations that describe the same astrological focus.

    Observations sharing affected planets, houses, and normalized title are
    combined into one fused record with multi-engine support metadata.
    """
    conflict_ids = conflict_ids or frozenset()
    grouped: dict[tuple[frozenset[str], frozenset[int], str], list[NormalizedObservation]] = {}

    for observation in observations:
        grouped.setdefault(observation_signature(observation), []).append(observation)

    fused: list[FusedObservation] = []
    for index, group in enumerate(grouped.values()):
        primary = _select_primary_observation(group)
        engines = tuple(dict.fromkeys(item.engine for item in group))
        source_ids = tuple(dict.fromkeys(item.observation_id for item in group))
        severity = max(item.severity for item in group)
        confidence = _merged_confidence(group)
        explanation = _merged_explanation(primary, group)
        category = primary.category if len(group) == 1 else "fusion:multi_engine"
        fusion_id = f"fusion-{index + 1:04d}-{normalize_title(primary.title) or 'observation'}"

        fused.append(
            FusedObservation(
                fusion_id=fusion_id[:80],
                title=primary.title,
                explanation=explanation,
                category=category,
                affected_planets=primary.affected_planets,
                affected_houses=primary.affected_houses,
                severity=round(severity, 4),
                confidence=round(confidence, 4),
                supporting_engines=engines,
                source_observation_ids=source_ids,
                rank_score=0.0,
                has_conflict=any(item.observation_id in conflict_ids for item in group),
                metadata={
                    "engine_count": len(engines),
                    "source_count": len(group),
                    "categories": tuple(dict.fromkeys(item.category for item in group)),
                },
            )
        )

    return tuple(fused)


def _select_primary_observation(
    group: list[NormalizedObservation],
) -> NormalizedObservation:
    """Select the strongest observation to represent a merged group."""
    return max(
        group,
        key=lambda item: (item.confidence, item.severity, len(item.explanation)),
    )


def _merged_confidence(group: list[NormalizedObservation]) -> float:
    """Boost confidence when multiple engines independently agree."""
    base = max(item.confidence for item in group)
    if len(group) == 1:
        return base
    agreement_bonus = min(0.08 * (len(group) - 1), 0.16)
    engine_bonus = min(0.05 * (len({item.engine for item in group}) - 1), 0.10)
    return min(base + agreement_bonus + engine_bonus, 1.0)


def _merged_explanation(
    primary: NormalizedObservation,
    group: list[NormalizedObservation],
) -> str:
    """Combine explanations while preserving the primary interpretation."""
    if len(group) == 1:
        return primary.explanation

    supporting_engines = sorted(
        {item.engine.value for item in group if item.engine != primary.engine}
    )
    if not supporting_engines:
        return primary.explanation

    engine_list = ", ".join(supporting_engines)
    return (
        f"{primary.explanation} Corroborated by {engine_list} intelligence "
        f"({len(group)} supporting observations)."
    )
