"""Historical output drift detection for intelligence evaluation."""

from __future__ import annotations

from typing import Any

from backend.app.services.evaluation.models import DriftReport, clamp_score


INTELLIGENCE_SECTIONS: tuple[str, ...] = (
    "vedic",
    "kp",
    "lal_kitab_intelligence",
    "fusion",
    "astro_intelligence",
)


def detect_output_drift(
    current_report: dict[str, Any],
    baseline_report: dict[str, Any],
    *,
    drift_threshold: float = 0.18,
) -> DriftReport:
    """
    Detect drift in intelligence outputs between two unified report payloads.

    Compares observation counts, fusion confidence, recommendation counts, and
    category distributions across intelligence sections.
    """
    deltas: list[float] = []
    changed_sections: list[str] = []
    section_details: dict[str, Any] = {}

    for section in INTELLIGENCE_SECTIONS:
        current_section = current_report.get(section, {})
        baseline_section = baseline_report.get(section, {})
        if not isinstance(current_section, dict) or not isinstance(baseline_section, dict):
            continue

        section_delta = _section_drift_delta(current_section, baseline_section)
        section_details[section] = section_delta
        deltas.append(section_delta["composite_delta"])
        if section_delta["composite_delta"] >= drift_threshold:
            changed_sections.append(section)

    summary_delta = _summary_drift_delta(
        current_report.get("summary", {}),
        baseline_report.get("summary", {}),
    )
    if summary_delta:
        section_details["summary"] = summary_delta
        deltas.append(summary_delta["composite_delta"])
        if summary_delta["composite_delta"] >= drift_threshold:
            changed_sections.append("summary")

    drift_score = clamp_score(sum(deltas) / len(deltas)) if deltas else 0.0

    return DriftReport(
        drift_score=drift_score,
        is_drift_detected=drift_score >= drift_threshold,
        changed_sections=tuple(changed_sections),
        details={
            "drift_threshold": drift_threshold,
            "sections_compared": list(section_details.keys()),
            "section_details": section_details,
        },
    )


def _section_drift_delta(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    current_obs = len(current.get("observations", []))
    baseline_obs = len(baseline.get("observations", []))
    observation_delta = _relative_delta(current_obs, baseline_obs)

    current_conf = float(current.get("confidence") or 0.0)
    baseline_conf = float(baseline.get("confidence") or 0.0)
    confidence_delta = abs(current_conf - baseline_conf)

    current_recs = len(current.get("recommendations", []))
    baseline_recs = len(baseline.get("recommendations", []))
    recommendation_delta = _relative_delta(current_recs, baseline_recs)

    current_categories = _category_distribution(current.get("observations", []))
    baseline_categories = _category_distribution(baseline.get("observations", []))
    category_delta = _distribution_delta(current_categories, baseline_categories)

    composite_delta = clamp_score(
        (0.30 * observation_delta)
        + (0.25 * confidence_delta)
        + (0.20 * recommendation_delta)
        + (0.25 * category_delta)
    )

    return {
        "observation_delta": round(observation_delta, 4),
        "confidence_delta": round(confidence_delta, 4),
        "recommendation_delta": round(recommendation_delta, 4),
        "category_delta": round(category_delta, 4),
        "composite_delta": composite_delta,
    }


def _summary_drift_delta(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any] | None:
    if not current and not baseline:
        return None

    current_conf = _normalize_summary_confidence(current.get("reasoning_confidence_score"))
    baseline_conf = _normalize_summary_confidence(baseline.get("reasoning_confidence_score"))
    confidence_delta = abs(current_conf - baseline_conf)

    current_severity = float(current.get("intelligence_severity_score") or 0.0)
    baseline_severity = float(baseline.get("intelligence_severity_score") or 0.0)
    severity_delta = abs(current_severity - baseline_severity)

    composite_delta = clamp_score((0.55 * confidence_delta) + (0.45 * severity_delta))
    return {
        "confidence_delta": round(confidence_delta, 4),
        "severity_delta": round(severity_delta, 4),
        "composite_delta": composite_delta,
    }


def _relative_delta(current: int, baseline: int) -> float:
    if baseline == 0:
        return 1.0 if current > 0 else 0.0
    return clamp_score(abs(current - baseline) / baseline)


def _category_distribution(observations: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in observations:
        if not isinstance(item, dict):
            continue
        category = str(item.get("category") or "unknown")
        counts[category] = counts.get(category, 0) + 1
    return counts


def _distribution_delta(current: dict[str, int], baseline: dict[str, int]) -> float:
    categories = set(current) | set(baseline)
    if not categories:
        return 0.0
    total_current = sum(current.values()) or 1
    total_baseline = sum(baseline.values()) or 1
    delta = 0.0
    for category in categories:
        current_ratio = current.get(category, 0) / total_current
        baseline_ratio = baseline.get(category, 0) / total_baseline
        delta += abs(current_ratio - baseline_ratio)
    return clamp_score(delta / 2.0)


def _normalize_summary_confidence(value: Any) -> float:
    if value is None:
        return 0.0
    numeric = float(value)
    if numeric > 1.0:
        return clamp_score(numeric / 100.0)
    return clamp_score(numeric)
