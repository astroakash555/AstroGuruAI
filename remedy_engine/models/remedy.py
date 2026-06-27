"""Remedy record models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RemedyRecord:
    """Machine-readable remedy entry from the knowledge base."""

    remedy_id: str
    remedy_name: str
    remedy_type: str
    astrology_system: str
    planet: str | None
    house: int | None
    severity: str
    category: str
    description: str
    expected_effect: str
    confidence_score: float
    priority: int


@dataclass(frozen=True)
class RemedyMatch:
    """A remedy matched to chart or intelligence context."""

    remedy: RemedyRecord
    match_score: float
    match_reasons: tuple[str, ...]


@dataclass(frozen=True)
class RemedyMatchResult:
    """Output of remedy matching."""

    matched_remedies: tuple[RemedyMatch, ...]
    metadata: dict[str, object]
