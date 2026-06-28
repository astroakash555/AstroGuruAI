"""Human consultation narrative dataclasses."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any


class NarrativeLanguage(str, Enum):
    """Supported consultation narrative languages."""

    HINDI = "hi"
    HINGLISH = "hinglish"
    ENGLISH = "en"


class NarrativeSectionId(str, Enum):
    """Fixed consultation narrative section identifiers."""

    GREETING = "greeting"
    OVERALL_CHART_IMPRESSION = "overall_chart_impression"
    HIGHEST_PRIORITY_TOPIC = "highest_priority_topic"
    SUPPORTING_EVIDENCE = "supporting_evidence"
    DASHA_DISCUSSION = "dasha_discussion"
    TRANSIT_DISCUSSION = "transit_discussion"
    YOGAS = "yogas"
    PRACTICAL_GUIDANCE = "practical_guidance"
    RECOMMENDATIONS = "recommendations"
    CLOSING_SUMMARY = "closing_summary"


NARRATIVE_SECTION_ORDER: tuple[NarrativeSectionId, ...] = (
    NarrativeSectionId.GREETING,
    NarrativeSectionId.OVERALL_CHART_IMPRESSION,
    NarrativeSectionId.HIGHEST_PRIORITY_TOPIC,
    NarrativeSectionId.SUPPORTING_EVIDENCE,
    NarrativeSectionId.DASHA_DISCUSSION,
    NarrativeSectionId.TRANSIT_DISCUSSION,
    NarrativeSectionId.YOGAS,
    NarrativeSectionId.PRACTICAL_GUIDANCE,
    NarrativeSectionId.RECOMMENDATIONS,
    NarrativeSectionId.CLOSING_SUMMARY,
)


def _freeze_mapping(value: Mapping[str, Any] | dict[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, MappingProxyType):
        return value
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class NarrativeSection:
    """One section of the human consultation narrative."""

    section_id: NarrativeSectionId
    title: str
    paragraphs: tuple[str, ...]
    bullets: tuple[str, ...] = ()

    @property
    def body_text(self) -> str:
        parts: list[str] = list(self.paragraphs)
        if self.bullets:
            parts.extend(self.bullets)
        return "\n".join(parts)


@dataclass(frozen=True)
class ConsultationNarrative:
    """Structured human consultation narrative output."""

    language: NarrativeLanguage
    sections: tuple[NarrativeSection, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @property
    def section_titles(self) -> tuple[str, ...]:
        return tuple(section.title for section in self.sections)

    @property
    def full_text(self) -> str:
        blocks: list[str] = []
        for section in self.sections:
            blocks.append(section.title)
            blocks.append(section.body_text)
        return "\n\n".join(block for block in blocks if block)
