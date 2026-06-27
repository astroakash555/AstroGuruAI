"""Cross-engine agreement metrics for intelligence evaluation."""

from __future__ import annotations

import re

from backend.app.services.evaluation.models import (
    EngineObservationSnapshot,
    MetricRecord,
    clamp_score,
)

TITLE_NORMALIZER = re.compile(r"[^a-z0-9]+")


def compute_cross_engine_agreement(
    observations_by_engine: dict[str, tuple[EngineObservationSnapshot, ...]],
) -> MetricRecord:
    """
    Measure how often independent engines converge on the same astrological focus.

    Observations sharing affected planets, houses, and normalized title are
    treated as agreement clusters. The score is the fraction of unique focus
    clusters supported by more than one engine.
    """
    grouped: dict[tuple[frozenset[str], frozenset[int], str], set[str]] = {}

    for engine, observations in observations_by_engine.items():
        for observation in observations:
            signature = focus_signature(observation)
            grouped.setdefault(signature, set()).add(engine)

    if not grouped:
        return MetricRecord(
            metric_id="cross_engine_agreement",
            name="Cross-Engine Agreement",
            score=0.0,
            weight=0.20,
            details={
                "cluster_count": 0,
                "multi_engine_clusters": 0,
                "engines_evaluated": sorted(observations_by_engine.keys()),
            },
        )

    multi_engine_clusters = sum(1 for engines in grouped.values() if len(engines) > 1)
    score = multi_engine_clusters / len(grouped)

    engine_pair_counts: dict[str, int] = {}
    for engines in grouped.values():
        if len(engines) < 2:
            continue
        pair_key = "+".join(sorted(engines))
        engine_pair_counts[pair_key] = engine_pair_counts.get(pair_key, 0) + 1

    return MetricRecord(
        metric_id="cross_engine_agreement",
        name="Cross-Engine Agreement",
        score=clamp_score(score),
        weight=0.20,
        details={
            "cluster_count": len(grouped),
            "multi_engine_clusters": multi_engine_clusters,
            "engine_pair_counts": engine_pair_counts,
            "engines_evaluated": sorted(observations_by_engine.keys()),
        },
    )


def focus_signature(observation: EngineObservationSnapshot) -> tuple[frozenset[str], frozenset[int], str]:
    """Build a stable focus signature for agreement clustering."""
    return (
        frozenset(observation.affected_planets),
        frozenset(observation.affected_houses),
        normalize_title(observation.title),
    )


def normalize_title(title: str) -> str:
    """Normalize a title for agreement clustering."""
    return TITLE_NORMALIZER.sub("", title.strip().lower())
