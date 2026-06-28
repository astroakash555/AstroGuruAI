"""Priority intelligence dataclasses."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any

from backend.app.services.consultation_brain.constants import EvidenceSource


class PriorityDomain(str, Enum):
    """Consultation topic domains ranked by the priority engine."""

    CAREER = "career"
    FINANCE = "finance"
    MARRIAGE = "marriage"
    RELATIONSHIP = "relationship"
    HEALTH = "health"
    EDUCATION = "education"
    CHILDREN = "children"
    PROPERTY = "property"
    BUSINESS = "business"
    SPIRITUALITY = "spirituality"
    FOREIGN_TRAVEL = "foreign_travel"
    LEGAL = "legal"
    MENTAL_WELLBEING = "mental_wellbeing"
    FAMILY = "family"


ALL_PRIORITY_DOMAINS: tuple[PriorityDomain, ...] = tuple(PriorityDomain)


def _freeze_mapping(value: Mapping[str, Any] | dict[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, MappingProxyType):
        return value
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class DomainPriority:
    """Ranked priority metrics for one consultation domain."""

    domain: PriorityDomain
    rank: int
    priority_score: float
    urgency: float
    importance: float
    evidence_count: int
    confidence: float
    supporting_sources: tuple[EvidenceSource, ...]
    evidence_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True)
class ConsultationPriorityResult:
    """Structured output of the priority intelligence engine."""

    priorities: tuple[DomainPriority, ...]
    highest_priority: DomainPriority | None
    secondary_priorities: tuple[DomainPriority, ...]
    suppressed_topics: tuple[PriorityDomain, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))
