"""Delivery-layer models for the human astrologer rewrite engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HumanAstrologerSectionId(str, Enum):
    """Ten-part client consultation flow."""

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


HUMAN_ASTROLOGER_SECTION_ORDER: tuple[HumanAstrologerSectionId, ...] = (
    HumanAstrologerSectionId.GREETING,
    HumanAstrologerSectionId.UNDERSTANDING_PROBLEM,
    HumanAstrologerSectionId.WHY_PROBLEM_EXISTS,
    HumanAstrologerSectionId.CURRENT_SITUATION,
    HumanAstrologerSectionId.POSITIVE_FACTORS,
    HumanAstrologerSectionId.NEGATIVE_FACTORS,
    HumanAstrologerSectionId.FUTURE_OUTLOOK,
    HumanAstrologerSectionId.REMEDIES,
    HumanAstrologerSectionId.PRACTICAL_ADVICE,
    HumanAstrologerSectionId.FINAL_BLESSING,
)

DELIVERY_MODE = "human_astrologer_rewrite_v1"


@dataclass(frozen=True)
class HumanAstrologerSection:
    section_id: HumanAstrologerSectionId
    title: str
    paragraphs: tuple[str, ...]

    @property
    def body(self) -> str:
        return "\n\n".join(self.paragraphs)


@dataclass(frozen=True)
class HumanAstrologerConsultation:
    language: str
    sections: tuple[HumanAstrologerSection, ...]
