"""Confidence calibration metrics for intelligence evaluation."""

from __future__ import annotations

from typing import Any

from backend.app.services.evaluation.agreement import focus_signature
from backend.app.services.evaluation.models import (
    EngineObservationSnapshot,
    MetricRecord,
    clamp_score,
)


def compute_confidence_calibration(
    fusion: dict[str, Any],
    observations_by_engine: dict[str, tuple[EngineObservationSnapshot, ...]],
) -> MetricRecord:
    """
    Measure how well declared confidence scores match empirical support.

    Empirical support blends severity with cross-engine agreement density for
    each fused observation and per-engine observations when fusion is sparse.
    """
    fused_observations = fusion.get("observations", [])
    calibration_errors: list[float] = []
    samples: list[dict[str, float | str]] = []

    cluster_support = _cluster_support_map(observations_by_engine)

    for item in fused_observations:
        declared = float(item.get("confidence") or 0.0)
        severity = float(item.get("severity") or 0.0)
        engine_count = len(item.get("supporting_engines", []))
        empirical = clamp_score(
            (0.55 * severity)
            + (0.25 * min(engine_count / 3.0, 1.0))
            + (0.20 * (0.5 if item.get("has_conflict") else 1.0))
        )
        error = abs(declared - empirical)
        calibration_errors.append(error)
        samples.append(
            {
                "source": "fusion",
                "declared": declared,
                "empirical": empirical,
                "error": round(error, 4),
            }
        )

    if not calibration_errors:
        for engine, observations in observations_by_engine.items():
            for observation in observations:
                declared = observation.confidence
                signature = focus_signature(observation)
                support = cluster_support.get(signature, 1)
                empirical = clamp_score(
                    (0.60 * observation.severity)
                    + (0.40 * min(support / 3.0, 1.0))
                )
                error = abs(declared - empirical)
                calibration_errors.append(error)
                samples.append(
                    {
                        "source": engine,
                        "declared": declared,
                        "empirical": empirical,
                        "error": round(error, 4),
                    }
                )

    if not calibration_errors:
        return MetricRecord(
            metric_id="confidence_calibration",
            name="Confidence Calibration",
            score=0.0,
            weight=0.15,
            details={"sample_count": 0, "mean_absolute_error": 0.0},
        )

    mean_absolute_error = sum(calibration_errors) / len(calibration_errors)
    score = clamp_score(1.0 - mean_absolute_error)

    return MetricRecord(
        metric_id="confidence_calibration",
        name="Confidence Calibration",
        score=score,
        weight=0.15,
        details={
            "sample_count": len(calibration_errors),
            "mean_absolute_error": round(mean_absolute_error, 4),
            "samples": samples[:10],
        },
    )


def _cluster_support_map(
    observations_by_engine: dict[str, tuple[EngineObservationSnapshot, ...]],
) -> dict[tuple[frozenset[str], frozenset[int], str], int]:
    """Count engine support per focus cluster."""
    counts: dict[tuple[frozenset[str], frozenset[int], str], set[str]] = {}
    for engine, observations in observations_by_engine.items():
        for observation in observations:
            signature = focus_signature(observation)
            counts.setdefault(signature, set()).add(engine)
    return {signature: len(engines) for signature, engines in counts.items()}
