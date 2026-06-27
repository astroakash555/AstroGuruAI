"""Regression comparison between unified report JSON payloads."""

from __future__ import annotations

from typing import Any

from backend.app.services.evaluation.models import RegressionReport, clamp_score


REGRESSION_CHECKS: tuple[tuple[str, str, str], ...] = (
    ("fusion", "confidence", "max"),
    ("fusion", "observations", "count"),
    ("fusion", "root_causes", "count"),
    ("fusion", "recommendations", "count"),
    ("vedic", "observations", "count"),
    ("kp", "observations", "count"),
    ("lal_kitab_intelligence", "observations", "count"),
    ("summary", "reasoning_confidence_score", "max"),
)


def compare_reports(
    baseline_report: dict[str, Any],
    candidate_report: dict[str, Any],
    *,
    regression_tolerance: float = 0.05,
) -> RegressionReport:
    """
    Compare two unified report payloads and score intelligence regressions.

    Regressions are recorded when candidate intelligence outputs drop beyond
    tolerance relative to the baseline snapshot.
    """
    regressions: list[dict[str, Any]] = []
    improvements: list[dict[str, Any]] = []

    for section, field, mode in REGRESSION_CHECKS:
        baseline_value = _extract_metric(baseline_report, section, field, mode)
        candidate_value = _extract_metric(candidate_report, section, field, mode)
        delta = candidate_value - baseline_value

        entry = {
            "section": section,
            "field": field,
            "baseline": baseline_value,
            "candidate": candidate_value,
            "delta": round(delta, 4),
        }

        if mode == "max":
            if delta < -regression_tolerance:
                entry["severity"] = round(abs(delta), 4)
                regressions.append(entry)
            elif delta > regression_tolerance:
                improvements.append(entry)
        elif mode == "count":
            if baseline_value > 0 and candidate_value < baseline_value:
                drop_ratio = (baseline_value - candidate_value) / baseline_value
                if drop_ratio > regression_tolerance:
                    entry["severity"] = round(drop_ratio, 4)
                    regressions.append(entry)
            elif candidate_value > baseline_value:
                improvements.append(entry)

    conflict_regressions = _conflict_regressions(
        baseline_report.get("fusion", {}),
        candidate_report.get("fusion", {}),
    )
    regressions.extend(conflict_regressions)

    penalty = sum(float(item.get("severity", 0.1)) for item in regressions)
    max_penalty = max(len(REGRESSION_CHECKS) * 0.25, 1.0)
    regression_score = clamp_score(1.0 - min(penalty / max_penalty, 1.0))

    return RegressionReport(
        regression_score=regression_score,
        has_regression=bool(regressions),
        regressions=tuple(regressions),
        improvements=tuple(improvements),
        details={
            "regression_tolerance": regression_tolerance,
            "regression_count": len(regressions),
            "improvement_count": len(improvements),
            "penalty": round(penalty, 4),
        },
    )


def _extract_metric(
    report: dict[str, Any],
    section: str,
    field: str,
    mode: str,
) -> float:
    section_payload = report.get(section, {})
    if not isinstance(section_payload, dict):
        section_payload = {}

    if mode == "count":
        payload = section_payload.get(field, [])
        return float(len(payload)) if isinstance(payload, list) else 0.0

    value = section_payload.get(field)
    if value is None and section == "summary":
        summary_payload = report.get("summary", {})
        if isinstance(summary_payload, dict):
            value = summary_payload.get(field)
    if value is None:
        return 0.0

    numeric = float(value)
    if field == "reasoning_confidence_score" and numeric > 1.0:
        return numeric / 100.0
    return numeric


def _conflict_regressions(
    baseline_fusion: dict[str, Any],
    candidate_fusion: dict[str, Any],
) -> list[dict[str, Any]]:
    baseline_conflicts = len(baseline_fusion.get("conflicts", []))
    candidate_conflicts = len(candidate_fusion.get("conflicts", []))
    if candidate_conflicts <= baseline_conflicts:
        return []

    increase = candidate_conflicts - baseline_conflicts
    return [
        {
            "section": "fusion",
            "field": "conflicts",
            "baseline": baseline_conflicts,
            "candidate": candidate_conflicts,
            "delta": float(increase),
            "severity": round(min(increase * 0.12, 0.48), 4),
        }
    ]
