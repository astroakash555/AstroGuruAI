"""Shared constants for the consultation brain foundation."""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from types import MappingProxyType


class EvidenceSource(str, Enum):
    """Originating intelligence subsystem for a piece of evidence."""

    YOGAS = "yogas"
    DASHA = "dasha"
    TRANSIT = "transit"
    KP = "kp"
    LAL_KITAB = "lal_kitab"
    RULE_STUDIO = "rule_studio"
    CASE_LEARNING = "case_learning"
    FUSION = "fusion"
    PROFESSIONAL_REPORT = "professional_report"
    GOLDEN_DATASET = "golden_dataset"


class EvidenceCategory(str, Enum):
    """High-level life domain or signal type."""

    GENERAL = "general"
    RELATIONSHIP = "relationship"
    CAREER = "career"
    HEALTH = "health"
    FINANCE = "finance"
    SPIRITUAL = "spiritual"
    TIMING = "timing"
    REMEDY = "remedy"


class PipelineStage(str, Enum):
    """Named stages in the consultation brain pipeline."""

    COLLECT_EVIDENCE = "collect_evidence"
    NORMALIZE_EVIDENCE = "normalize_evidence"
    RESOLVE_CONFLICTS = "resolve_conflicts"
    RANK_PRIORITIES = "rank_priorities"
    GENERATE_RECOMMENDATIONS = "generate_recommendations"
    GENERATE_NARRATIVE = "generate_narrative"
    PRODUCE_OUTPUT = "produce_output"


ENGINE_VERSION = "consultation_brain_narrative_v0.6"

# Relative weights used by the placeholder weighted reasoning engine (read-only).
SOURCE_WEIGHTS: Mapping[EvidenceSource, float] = MappingProxyType(
    {
        EvidenceSource.FUSION: 1.0,
        EvidenceSource.PROFESSIONAL_REPORT: 0.95,
        EvidenceSource.GOLDEN_DATASET: 0.9,
        EvidenceSource.RULE_STUDIO: 0.85,
        EvidenceSource.CASE_LEARNING: 0.8,
        EvidenceSource.KP: 0.75,
        EvidenceSource.LAL_KITAB: 0.75,
        EvidenceSource.DASHA: 0.7,
        EvidenceSource.TRANSIT: 0.65,
        EvidenceSource.YOGAS: 0.6,
    }
)

MIN_EVIDENCE_CONFIDENCE = 0.0
MAX_EVIDENCE_CONFIDENCE = 1.0
CONFLICT_CONFIDENCE_PENALTY = 0.08
DEFAULT_OVERALL_CONFIDENCE = 0.5
MAX_PRIORITIES = 8
MAX_RECOMMENDATIONS = 5
