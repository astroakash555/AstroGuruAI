"""Typed models for the intelligence evaluation framework."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class EngineObservationSnapshot:
    """Normalized observation extracted from an intelligence engine section."""

    engine: str
    observation_id: str
    title: str
    category: str
    affected_planets: tuple[str, ...]
    affected_houses: tuple[int, ...]
    severity: float
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationInput:
    """Inputs required to evaluate intelligence output quality."""

    unified_report: dict[str, Any]
    fusion: dict[str, Any] | None = None
    observations: dict[str, tuple[EngineObservationSnapshot, ...]] | None = None
    baseline_report: dict[str, Any] | None = None
    comparison_report: dict[str, Any] | None = None


@dataclass(frozen=True)
class MetricRecord:
    """Single structured evaluation metric."""

    metric_id: str
    name: str
    score: float
    weight: float
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DriftReport:
    """Drift analysis between a baseline and current unified report."""

    drift_score: float
    is_drift_detected: bool
    changed_sections: tuple[str, ...]
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RegressionReport:
    """Regression analysis between two unified report payloads."""

    regression_score: float
    has_regression: bool
    regressions: tuple[dict[str, Any], ...]
    improvements: tuple[dict[str, Any], ...]
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationResult:
    """Complete structured output from intelligence evaluation."""

    evaluated_at: datetime
    cross_engine_agreement: float
    fusion_consistency: float
    recommendation_consistency: float
    confidence_calibration: float
    drift: DriftReport | None
    regression: RegressionReport | None
    intelligence_quality_score: float
    metrics: tuple[MetricRecord, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


def clamp_score(value: float) -> float:
    """Clamp a metric score to the inclusive 0-1 range."""
    return round(min(max(value, 0.0), 1.0), 4)


def observation_from_dict(engine: str, payload: dict[str, Any]) -> EngineObservationSnapshot:
    """Parse one observation dictionary into a normalized snapshot."""
    return EngineObservationSnapshot(
        engine=engine,
        observation_id=str(payload.get("observation_id") or payload.get("fusion_id") or ""),
        title=str(payload.get("title") or ""),
        category=str(payload.get("category") or ""),
        affected_planets=tuple(str(planet) for planet in payload.get("affected_planets", [])),
        affected_houses=tuple(int(house) for house in payload.get("affected_houses", [])),
        severity=float(payload.get("severity") or 0.0),
        confidence=float(payload.get("confidence") or 0.0),
        metadata=dict(payload.get("metadata") or {}),
    )


def extract_engine_observations(unified_report: dict[str, Any]) -> dict[str, tuple[EngineObservationSnapshot, ...]]:
    """Extract per-engine observations from a unified report payload."""
    sections = {
        "vedic": "vedic",
        "kp": "kp",
        "lal_kitab": "lal_kitab_intelligence",
    }
    extracted: dict[str, tuple[EngineObservationSnapshot, ...]] = {}

    for engine, section_key in sections.items():
        section = unified_report.get(section_key, {})
        observations = section.get("observations", [])
        extracted[engine] = tuple(
            observation_from_dict(engine, item)
            for item in observations
            if isinstance(item, dict)
        )

    return extracted


def resolve_fusion_payload(
    unified_report: dict[str, Any],
    fusion: dict[str, Any] | None,
) -> dict[str, Any]:
    """Resolve fusion output from explicit input or unified report section."""
    if fusion is not None:
        return fusion
    report_fusion = unified_report.get("fusion")
    if isinstance(report_fusion, dict):
        return report_fusion
    return {}
