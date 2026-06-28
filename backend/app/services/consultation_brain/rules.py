"""Conflict detection rules for consultation brain evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence

STRONG_CONFIDENCE_THRESHOLD = 0.65
RARE_YOGA_CONFIDENCE_THRESHOLD = 0.70

CONFLICT_ELIGIBLE_SOURCES: frozenset[EvidenceSource] = frozenset(
    {
        EvidenceSource.DASHA,
        EvidenceSource.TRANSIT,
        EvidenceSource.YOGAS,
        EvidenceSource.KP,
        EvidenceSource.LAL_KITAB,
        EvidenceSource.RULE_STUDIO,
        EvidenceSource.CASE_LEARNING,
        EvidenceSource.FUSION,
    }
)


class ConflictType(str, Enum):
    """Structural conflict categories resolved by weighting."""

    POSITIVE_VS_NEGATIVE = "positive_vs_negative"
    STRONG_VS_WEAK = "strong_vs_weak"
    TIME_SENSITIVE_VS_PERMANENT = "time_sensitive_vs_permanent"
    RULE_BASED_VS_LEARNED = "rule_based_vs_learned"
    RARE_YOGA_VS_GENERAL_TRANSIT = "rare_yoga_vs_general_transit"


CONFLICT_TYPE_ORDER: tuple[ConflictType, ...] = (
    ConflictType.POSITIVE_VS_NEGATIVE,
    ConflictType.RARE_YOGA_VS_GENERAL_TRANSIT,
    ConflictType.TIME_SENSITIVE_VS_PERMANENT,
    ConflictType.RULE_BASED_VS_LEARNED,
    ConflictType.STRONG_VS_WEAK,
)


@dataclass(frozen=True)
class EvidenceSignals:
    """Derived structural signals used for conflict detection."""

    polarity: str
    strength: str
    timing: str
    origin: str
    specialty: str


def extract_signals(evidence: ConsultationEvidence) -> EvidenceSignals:
    """Extract deterministic structural signals without astrological inference."""
    metadata = evidence.metadata
    tags = set(evidence.tags)

    if metadata.get("is_supported") is False:
        polarity = "negative"
    elif metadata.get("is_supported") is True:
        polarity = "positive"
    elif tags.intersection({"negative", "unsupported", "affliction"}):
        polarity = "negative"
    elif tags.intersection({"positive", "supported"}):
        polarity = "positive"
    elif evidence.confidence >= 0.5:
        polarity = "positive"
    else:
        polarity = "negative"

    strength = "strong" if evidence.confidence >= STRONG_CONFIDENCE_THRESHOLD else "weak"

    if evidence.source in {EvidenceSource.DASHA, EvidenceSource.TRANSIT} or evidence.category == EvidenceCategory.TIMING:
        timing = "time_sensitive"
    else:
        timing = "permanent"

    if evidence.source in {EvidenceSource.RULE_STUDIO, EvidenceSource.GOLDEN_DATASET}:
        origin = "rule_based"
    elif evidence.source == EvidenceSource.CASE_LEARNING:
        origin = "learned"
    else:
        origin = "neutral"

    if evidence.source == EvidenceSource.YOGAS and evidence.confidence >= RARE_YOGA_CONFIDENCE_THRESHOLD:
        specialty = "rare_yoga"
    elif evidence.source == EvidenceSource.TRANSIT:
        specialty = "general_transit"
    else:
        specialty = "none"

    return EvidenceSignals(
        polarity=polarity,
        strength=strength,
        timing=timing,
        origin=origin,
        specialty=specialty,
    )


def _is_positive_vs_negative(left: EvidenceSignals, right: EvidenceSignals) -> bool:
    return (
        left.polarity != right.polarity
        and left.polarity != "neutral"
        and right.polarity != "neutral"
    )


def _is_strong_vs_weak(left: EvidenceSignals, right: EvidenceSignals, left_item: ConsultationEvidence, right_item: ConsultationEvidence) -> bool:
    return left.strength != right.strength and left_item.category == right_item.category


def _is_time_sensitive_vs_permanent(left: EvidenceSignals, right: EvidenceSignals) -> bool:
    return left.timing != right.timing


def _is_rule_based_vs_learned(left: EvidenceSignals, right: EvidenceSignals) -> bool:
    return (left.origin == "rule_based" and right.origin == "learned") or (
        left.origin == "learned" and right.origin == "rule_based"
    )


def _is_rare_yoga_vs_general_transit(left: EvidenceSignals, right: EvidenceSignals) -> bool:
    return (left.specialty == "rare_yoga" and right.specialty == "general_transit") or (
        left.specialty == "general_transit" and right.specialty == "rare_yoga"
    )


def detect_conflict_type(
    left_item: ConsultationEvidence,
    right_item: ConsultationEvidence,
) -> ConflictType | None:
    """Return the first matching conflict type for an evidence pair."""
    if left_item.source not in CONFLICT_ELIGIBLE_SOURCES or right_item.source not in CONFLICT_ELIGIBLE_SOURCES:
        return None
    if left_item.source == right_item.source:
        return None

    left = extract_signals(left_item)
    right = extract_signals(right_item)
    checks = {
        ConflictType.POSITIVE_VS_NEGATIVE: lambda: _is_positive_vs_negative(left, right),
        ConflictType.RARE_YOGA_VS_GENERAL_TRANSIT: lambda: _is_rare_yoga_vs_general_transit(left, right),
        ConflictType.TIME_SENSITIVE_VS_PERMANENT: lambda: _is_time_sensitive_vs_permanent(left, right),
        ConflictType.RULE_BASED_VS_LEARNED: lambda: _is_rule_based_vs_learned(left, right),
        ConflictType.STRONG_VS_WEAK: lambda: _is_strong_vs_weak(left, right, left_item, right_item),
    }
    for conflict_type in CONFLICT_TYPE_ORDER:
        if checks[conflict_type]():
            return conflict_type
    return None
