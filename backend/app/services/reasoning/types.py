"""Shared type aliases and enumerations for the horoscope reasoning engine."""

from __future__ import annotations

from enum import Enum


class ReasoningDomain(str, Enum):
    """Astrology subsystems that contribute evidence to reasoning."""

    BIRTH_DETAILS = "birth_details"
    PLANET_POSITIONS = "planet_positions"
    HOUSES = "houses"
    DASHA = "dasha"
    TRANSIT = "transit"
    KP = "kp"
    LAL_KITAB = "lal_kitab"


class EvidenceKind(str, Enum):
    """Classification of evidentiary records produced during analysis."""

    OBSERVATION = "observation"
    PATTERN = "pattern"
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    ROOT_CAUSE = "root_cause"
    RECOMMENDATION = "recommendation"
    COVERAGE = "coverage"


class RecommendationPriority(str, Enum):
    """Relative urgency assigned to a recommendation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RootCauseCategory(str, Enum):
    """High-level grouping for root-cause findings."""

    PLANETARY = "planetary"
    HOUSE = "house"
    DASHA = "dasha"
    TRANSIT = "transit"
    KP = "kp"
    LAL_KITAB = "lal_kitab"
    MULTI_SYSTEM = "multi_system"


DOMAIN_WEIGHTS: dict[ReasoningDomain, float] = {
    ReasoningDomain.BIRTH_DETAILS: 0.10,
    ReasoningDomain.PLANET_POSITIONS: 0.20,
    ReasoningDomain.HOUSES: 0.15,
    ReasoningDomain.DASHA: 0.15,
    ReasoningDomain.TRANSIT: 0.15,
    ReasoningDomain.KP: 0.15,
    ReasoningDomain.LAL_KITAB: 0.10,
}
