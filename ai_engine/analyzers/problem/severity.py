"""Severity scoring for client problem statements."""

from __future__ import annotations

import re

from ai_engine.analyzers.problem.constants import ProblemCategory
from ai_engine.analyzers.problem.keywords import SEVERITY_KEYWORDS
from ai_engine.analyzers.problem.types import SeverityAssessment

CATEGORY_BASE_SEVERITY: dict[ProblemCategory, float] = {
    ProblemCategory.MARRIAGE: 0.55,
    ProblemCategory.BUSINESS_FINANCE: 0.6,
    ProblemCategory.CAREER: 0.5,
    ProblemCategory.HEALTH: 0.65,
    ProblemCategory.LEGAL: 0.7,
    ProblemCategory.EDUCATION: 0.4,
    ProblemCategory.FAMILY: 0.5,
    ProblemCategory.PROPERTY: 0.45,
    ProblemCategory.SPIRITUAL: 0.4,
    ProblemCategory.UNKNOWN: 0.35,
}

SEVERITY_LEVELS: tuple[tuple[str, float], ...] = (
    ("critical", 0.85),
    ("high", 0.7),
    ("moderate", 0.5),
    ("low", 0.3),
    ("minimal", 0.0),
)


def assess_severity(normalized_text: str, category: ProblemCategory) -> SeverityAssessment:
    """Compute severity score from language signals and category baseline."""
    base = CATEGORY_BASE_SEVERITY[category]
    signals: list[str] = []
    boosts: list[float] = []

    for keyword, weight in SEVERITY_KEYWORDS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", normalized_text):
            signals.append(keyword)
            boosts.append(weight)

    keyword_boost = sum(boosts) / len(boosts) if boosts else 0.0
    exclamation_boost = min(normalized_text.count("!") * 0.03, 0.1)
    urgency_boost = 0.08 if any(word in normalized_text for word in ("please help", "asap", "urgent")) else 0.0

    score = base
    if keyword_boost:
        score = (base * 0.4) + (keyword_boost * 0.6)
    score += exclamation_boost + urgency_boost

    if category == ProblemCategory.UNKNOWN:
        score = min(score, 0.45)

    score = round(min(max(score, 0.0), 1.0), 3)
    level = _severity_level(score)
    return SeverityAssessment(score=score, level=level, signals=tuple(dict.fromkeys(signals)))


def _severity_level(score: float) -> str:
    for label, threshold in SEVERITY_LEVELS:
        if score >= threshold:
            return label
    return "minimal"
