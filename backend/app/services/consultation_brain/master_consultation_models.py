"""Master astrologer consultation dataclasses."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any


class MasterConsultationLanguage(str, Enum):
    """Supported master consultation languages."""

    HINDI = "hi"
    HINGLISH = "hinglish"
    ENGLISH = "en"


class MasterConsultationSectionId(str, Enum):
    """Ten-part master astrologer consultation flow."""

    GREETING = "greeting"
    UNDERSTANDING_PROBLEM = "understanding_problem"
    WHY_PROBLEM_EXISTS = "why_problem_exists"
    CURRENT_SITUATION = "current_situation"
    POSITIVE_FACTORS = "positive_factors"
    NEGATIVE_FACTORS = "negative_factors"
    FUTURE_OUTLOOK = "future_outlook"
    REMEDIES = "remedies"
    PRACTICAL_ADVICE = "practical_advice"
    FINAL_BLESSING = "final_blessing"


MASTER_CONSULTATION_SECTION_ORDER: tuple[MasterConsultationSectionId, ...] = (
    MasterConsultationSectionId.GREETING,
    MasterConsultationSectionId.UNDERSTANDING_PROBLEM,
    MasterConsultationSectionId.WHY_PROBLEM_EXISTS,
    MasterConsultationSectionId.CURRENT_SITUATION,
    MasterConsultationSectionId.POSITIVE_FACTORS,
    MasterConsultationSectionId.NEGATIVE_FACTORS,
    MasterConsultationSectionId.FUTURE_OUTLOOK,
    MasterConsultationSectionId.REMEDIES,
    MasterConsultationSectionId.PRACTICAL_ADVICE,
    MasterConsultationSectionId.FINAL_BLESSING,
)


def _freeze_mapping(value: Mapping[str, Any] | dict[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, MappingProxyType):
        return value
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class MasterConsultationSection:
    """One emotionally intelligent consultation section."""

    section_id: MasterConsultationSectionId
    title: str
    paragraphs: tuple[str, ...]

    @property
    def body_text(self) -> str:
        return "\n\n".join(self.paragraphs)


@dataclass(frozen=True)
class MasterConsultation:
    """Full master astrologer conversation output."""

    language: MasterConsultationLanguage
    sections: tuple[MasterConsultationSection, ...]
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
            blocks.extend(section.paragraphs)
        return "\n\n".join(block for block in blocks if block)
