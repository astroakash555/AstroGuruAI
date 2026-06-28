"""Recommendation intelligence dataclasses."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any

from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.priority_models import PriorityDomain


class RecommendationCategory(str, Enum):
    """Structured recommendation categories."""

    IMMEDIATE_ACTIONS = "immediate_actions"
    LIFESTYLE = "lifestyle"
    SPIRITUAL = "spiritual"
    MANTRA = "mantra"
    DONATION = "donation"
    GEMSTONE = "gemstone"
    BEHAVIOURAL = "behavioural"
    TIMING_ADVICE = "timing_advice"
    CAREER_ADVICE = "career_advice"
    MARRIAGE_ADVICE = "marriage_advice"
    EDUCATION_ADVICE = "education_advice"
    HEALTH_ADVICE = "health_advice"
    FINANCIAL_ADVICE = "financial_advice"
    GENERAL_GUIDANCE = "general_guidance"


class RecommendationTier(str, Enum):
    """Priority band for structured recommendations."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"


ALL_RECOMMENDATION_CATEGORIES: tuple[RecommendationCategory, ...] = tuple(RecommendationCategory)


def _freeze_mapping(value: Mapping[str, Any] | dict[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, MappingProxyType):
        return value
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class StructuredRecommendation:
    """Structured professional recommendation without narrative text."""

    recommendation_id: str
    category: RecommendationCategory
    priority: int
    confidence: float
    supporting_evidence_ids: tuple[str, ...]
    supporting_sources: tuple[EvidenceSource, ...]
    reason: str
    domain: PriorityDomain | None = None
    tier: RecommendationTier = RecommendationTier.MEDIUM
    metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True)
class ConsultationRecommendationResult:
    """Grouped recommendation output from the intelligence engine."""

    high_priority: tuple[StructuredRecommendation, ...]
    medium_priority: tuple[StructuredRecommendation, ...]
    low_priority: tuple[StructuredRecommendation, ...]
    deferred: tuple[StructuredRecommendation, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @property
    def all_recommendations(self) -> tuple[StructuredRecommendation, ...]:
        return self.high_priority + self.medium_priority + self.low_priority + self.deferred
