"""Typed models for problem analysis."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_engine.analyzers.problem.constants import ProblemCategory


@dataclass(frozen=True)
class ProblemAnalyzerInput:
    """Input payload for problem context analysis."""

    problem_text: str
    client_id: str | None = None
    locale: str = "en"


@dataclass(frozen=True)
class CategoryMatch:
    """Detected category with confidence."""

    category: ProblemCategory
    label: str
    confidence: float


@dataclass(frozen=True)
class HouseMapping:
    """Houses related to the detected problem."""

    primary: tuple[int, ...]
    secondary: tuple[int, ...]
    supporting: tuple[int, ...]
    all_houses: tuple[int, ...]


@dataclass(frozen=True)
class PlanetMapping:
    """Planets related to the detected problem."""

    primary: tuple[str, ...]
    secondary: tuple[str, ...]
    shadow: tuple[str, ...]
    all_planets: tuple[str, ...]


@dataclass(frozen=True)
class SeverityAssessment:
    """Severity scoring for the stated problem."""

    score: float
    level: str
    signals: tuple[str, ...]


@dataclass(frozen=True)
class RootCauseIndicator:
    """Astrological root cause indicator (analysis only, not a remedy)."""

    indicator: str
    relevance: float
    source: str


@dataclass(frozen=True)
class ProblemAnalysisResult:
    """Complete problem context analysis."""

    original_text: str
    normalized_text: str
    category: CategoryMatch
    alternative_categories: tuple[CategoryMatch, ...]
    houses: HouseMapping
    planets: PlanetMapping
    severity: SeverityAssessment
    root_cause_indicators: tuple[RootCauseIndicator, ...]
    analysis_notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, object] = field(default_factory=dict)
