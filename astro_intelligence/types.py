"""Astro Intelligence typed models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class PlanetaryConflict:
    planets: tuple[str, ...]
    conflict_type: str
    severity: float
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class RankedCause:
    planet: str
    severity: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class AstroIntelligenceInput:
    """Structured analysis input assembled from report sections."""

    kundali: dict[str, Any]
    navamsha: dict[str, Any]
    dasha: dict[str, Any]
    yogas: dict[str, Any]
    doshas: dict[str, Any]
    transits: dict[str, Any]
    problem_analysis: dict[str, Any] | None = None
    lal_kitab: dict[str, Any] | None = None
    kp_analysis: dict[str, Any] | None = None


@dataclass(frozen=True)
class AstroIntelligenceResult:
    analyzed_at: datetime
    root_cause_planets: tuple[str, ...]
    supportive_planets: tuple[str, ...]
    affected_houses: tuple[int, ...]
    planetary_conflicts: tuple[PlanetaryConflict, ...]
    severity_score: float
    recommended_remedies: tuple[dict[str, Any], ...]
    confidence_score: float
    ranked_causes: tuple[RankedCause, ...]
    metadata: dict[str, object] = field(default_factory=dict)
