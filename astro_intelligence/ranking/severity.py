"""Severity ranking for astro intelligence."""

from __future__ import annotations


def compute_severity_score(
    *,
    root_cause_count: int,
    affected_house_count: int,
    conflict_count: int,
    dosha_count: int,
    problem_severity: float | None,
) -> float:
    """Compute aggregate severity score (0-1)."""
    score = 0.0
    score += min(0.3, root_cause_count * 0.08)
    score += min(0.2, affected_house_count * 0.04)
    score += min(0.25, conflict_count * 0.1)
    score += min(0.15, dosha_count * 0.05)
    if problem_severity is not None:
        score += problem_severity * 0.25
    return round(min(score, 1.0), 3)


def compute_confidence_score(
    *,
    sections_present: int,
    root_cause_count: int,
    remedy_count: int,
) -> float:
    """Compute confidence score based on available evidence."""
    score = 0.35
    score += min(0.35, sections_present * 0.05)
    score += min(0.2, root_cause_count * 0.05)
    score += min(0.1, remedy_count * 0.02)
    return round(min(score, 1.0), 3)
