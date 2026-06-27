"""Intelligence fusion layer for AstroGuruAI Phase 4."""

from backend.app.services.reasoning.fusion.conflict_resolver import (
    CONFLICT_CONFIDENCE_THRESHOLD,
    CONFLICT_SEVERITY_THRESHOLD,
    conflict_observation_ids,
    detect_conflicts,
)
from backend.app.services.reasoning.fusion.engine import (
    DashaIntelligenceAdapter,
    IntelligenceAnalyzerAdapter,
    IntelligenceFusionEngine,
    KPIntelligenceAdapter,
    LalKitabIntelligenceAdapter,
    TransitIntelligenceAdapter,
    VedicIntelligenceAdapter,
    default_adapters,
)
from backend.app.services.reasoning.fusion.evidence import (
    collect_observations,
    deduplicate_observations,
    merge_supporting_evidence,
    normalize_dasha_observation,
    normalize_kp_observation,
    normalize_lal_kitab_observation,
    normalize_title,
    normalize_vedic_observation,
    observation_signature,
)
from backend.app.services.reasoning.fusion.models import (
    FusionContext,
    FusionEngineId,
    FusionRecommendation,
    FusionResult,
    FusedObservation,
    InterpretationConflict,
    NormalizedObservation,
    RootCauseAnalysis,
)
from backend.app.services.reasoning.fusion.ranking import (
    CONFIDENCE_WEIGHT,
    ENGINE_SUPPORT_WEIGHT,
    SEVERITY_WEIGHT,
    compute_rank_score,
    rank_observations,
)
from backend.app.services.reasoning.fusion.recommendation import build_recommendations
from backend.app.services.reasoning.fusion.root_cause import ROOT_CAUSE_MAX_COUNT, ROOT_CAUSE_MIN_RANK, build_root_causes

__all__ = [
    "CONFIDENCE_WEIGHT",
    "CONFLICT_CONFIDENCE_THRESHOLD",
    "CONFLICT_SEVERITY_THRESHOLD",
    "DashaIntelligenceAdapter",
    "ENGINE_SUPPORT_WEIGHT",
    "FusionContext",
    "FusionEngineId",
    "FusionRecommendation",
    "FusionResult",
    "FusedObservation",
    "IntelligenceAnalyzerAdapter",
    "IntelligenceFusionEngine",
    "InterpretationConflict",
    "KPIntelligenceAdapter",
    "LalKitabIntelligenceAdapter",
    "NormalizedObservation",
    "ROOT_CAUSE_MAX_COUNT",
    "ROOT_CAUSE_MIN_RANK",
    "RootCauseAnalysis",
    "SEVERITY_WEIGHT",
    "TransitIntelligenceAdapter",
    "VedicIntelligenceAdapter",
    "build_recommendations",
    "build_root_causes",
    "collect_observations",
    "compute_rank_score",
    "conflict_observation_ids",
    "deduplicate_observations",
    "default_adapters",
    "detect_conflicts",
    "merge_supporting_evidence",
    "normalize_dasha_observation",
    "normalize_kp_observation",
    "normalize_lal_kitab_observation",
    "normalize_title",
    "normalize_vedic_observation",
    "observation_signature",
    "rank_observations",
]
