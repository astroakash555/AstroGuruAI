"""Remedy matching engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from remedy_engine.knowledge.registry import RemedyKnowledgeRegistry
from remedy_engine.models.remedy import RemedyMatch, RemedyMatchResult, RemedyRecord
from remedy_engine.serializers.serializer import remedies_to_json_dict, to_json_dict, to_json_string

SEVERITY_RANK = {"low": 1, "moderate": 2, "high": 3, "critical": 4}


@dataclass(frozen=True)
class RemedyMatchContext:
    """Context for matching remedies against chart intelligence."""

    root_cause_planets: tuple[str, ...] = ()
    affected_houses: tuple[int, ...] = ()
    categories: tuple[str, ...] = ()
    severity_level: str = "moderate"
    astrology_systems: tuple[str, ...] = ("vedic", "lal_kitab", "kp")
    max_results: int = 10


class RemedyEngine:
    """Match structured remedies from the knowledge base to analysis context."""

    def __init__(self, registry: RemedyKnowledgeRegistry | None = None) -> None:
        self._registry = registry or RemedyKnowledgeRegistry()

    @property
    def registry(self) -> RemedyKnowledgeRegistry:
        return self._registry

    def list_knowledge_json(self) -> dict[str, Any]:
        return remedies_to_json_dict(self._registry.remedies)

    def match(self, context: RemedyMatchContext) -> RemedyMatchResult:
        matches: list[RemedyMatch] = []
        target_severity = SEVERITY_RANK.get(context.severity_level, 2)

        for remedy in self._registry.remedies:
            if remedy.astrology_system not in context.astrology_systems:
                continue

            score, reasons = _score_remedy(remedy, context, target_severity)
            if score <= 0:
                continue

            matches.append(
                RemedyMatch(
                    remedy=remedy,
                    match_score=round(min(score, 1.0), 3),
                    match_reasons=tuple(reasons),
                )
            )

        matches.sort(key=lambda item: (-item.match_score, item.remedy.priority))
        limited = tuple(matches[: context.max_results])

        return RemedyMatchResult(
            matched_remedies=limited,
            metadata={
                "engine": "remedy_engine_v1",
                "ai_interpretation": False,
                "matched_count": len(limited),
            },
        )

    def match_json(self, context: RemedyMatchContext) -> dict[str, Any]:
        return to_json_dict(self.match(context))

    def match_json_string(self, context: RemedyMatchContext, *, indent: int | None = 2) -> str:
        return to_json_string(self.match(context), indent=indent)


def _score_remedy(
    remedy: RemedyRecord,
    context: RemedyMatchContext,
    target_severity: int,
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if remedy.planet and remedy.planet in context.root_cause_planets:
        score += 0.35
        reasons.append(f"Targets root cause planet {remedy.planet}.")

    if remedy.house and remedy.house in context.affected_houses:
        score += 0.25
        reasons.append(f"Targets affected house {remedy.house}.")

    if context.categories and remedy.category in context.categories:
        score += 0.2
        reasons.append(f"Matches category {remedy.category}.")

    remedy_severity = SEVERITY_RANK.get(remedy.severity, 2)
    if remedy_severity >= target_severity:
        score += 0.1
        reasons.append(f"Severity band {remedy.severity} aligns with context.")

    score += remedy.confidence_score * 0.1
    score += max(0.0, (6 - remedy.priority) * 0.02)

    if score == 0 and remedy.planet is None and not context.categories:
        return 0.0, reasons

    if score == 0 and context.root_cause_planets and remedy.planet in context.root_cause_planets:
        score = 0.2
        reasons.append(f"General support for planet {remedy.planet}.")

    return score, reasons
