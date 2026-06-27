"""Rule-based problem category classifier."""

from __future__ import annotations

import re

from ai_engine.analyzers.problem.constants import CATEGORY_LABELS, ProblemCategory
from ai_engine.analyzers.problem.keywords import CATEGORY_KEYWORDS, UNKNOWN_PHRASES
from ai_engine.analyzers.problem.types import CategoryMatch


def normalize_text(text: str) -> str:
    """Normalize free text for keyword matching."""
    cleaned = text.strip().lower()
    cleaned = re.sub(r"[^\w\s'-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def classify_problem(text: str) -> tuple[CategoryMatch, tuple[CategoryMatch, ...]]:
    """
    Classify problem text into Vedic problem categories.

    Returns the top match and ranked alternatives.
    """
    normalized = normalize_text(text)
    if not normalized:
        unknown = _category_match(ProblemCategory.UNKNOWN, 0.0)
        return unknown, ()

    if _is_unknown_problem(normalized):
        unknown = _category_match(ProblemCategory.UNKNOWN, 0.55)
        return unknown, ()

    scores = _score_categories(normalized)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_category, top_score = ranked[0]

    if top_score < 0.2:
        unknown = _category_match(ProblemCategory.UNKNOWN, max(top_score, 0.35))
        alternatives = tuple(
            _category_match(category, score)
            for category, score in ranked[:3]
            if score > 0
        )
        return unknown, alternatives

    primary = _category_match(top_category, top_score)
    alternatives = tuple(
        _category_match(category, score)
        for category, score in ranked[1:4]
        if score >= 0.15 and category != top_category
    )
    return primary, alternatives


def _score_categories(normalized: str) -> dict[ProblemCategory, float]:
    scores: dict[ProblemCategory, float] = {}
    tokens = set(normalized.split())

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0.0
        for keyword in keywords:
            if " " in keyword:
                if keyword in normalized:
                    score += 1.5
            elif keyword in tokens or keyword in normalized:
                score += 1.0
        if score > 0:
            scores[category] = score

    if not scores:
        return {ProblemCategory.UNKNOWN: 0.0}

    max_score = max(scores.values())
    return {category: min(score / max_score, 1.0) for category, score in scores.items()}


def _is_unknown_problem(normalized: str) -> bool:
    if len(normalized.split()) <= 2 and normalized in {"problem", "help", "issue"}:
        return True
    return any(phrase in normalized for phrase in UNKNOWN_PHRASES)


def _category_match(category: ProblemCategory, confidence: float) -> CategoryMatch:
    return CategoryMatch(
        category=category,
        label=CATEGORY_LABELS[category],
        confidence=round(min(max(confidence, 0.0), 1.0), 3),
    )
