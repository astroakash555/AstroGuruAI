"""Knowledge search models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from knowledge_brain.models.rules import AstrologyRule


@dataclass(frozen=True)
class KnowledgeQuery:
    problem_text: str = ""
    domain: str | None = None
    category: str | None = None
    systems: tuple[str, ...] = ("vedic", "lal_kitab", "kp")
    planets: tuple[str, ...] = ()
    houses: tuple[int, ...] = ()
    signs: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    max_results: int = 25


@dataclass(frozen=True)
class RankedRule:
    rule: AstrologyRule
    score: float
    match_reasons: tuple[str, ...]


@dataclass(frozen=True)
class KnowledgeSearchResult:
    queried_at: datetime
    query: KnowledgeQuery
    ranked_rules: tuple[RankedRule, ...]
    matched_entities: tuple[dict[str, Any], ...]
    summary: dict[str, object]
    metadata: dict[str, object] = field(default_factory=dict)
