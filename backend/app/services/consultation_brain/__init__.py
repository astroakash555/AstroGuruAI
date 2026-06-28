"""Consultation brain foundation package."""

from backend.app.services.consultation_brain.brain import ConsultationBrain
from backend.app.services.consultation_brain.clock import FixedClock, UtcClock
from backend.app.services.consultation_brain.collectors import (
    EvidenceCollector,
    as_async_provider,
    collect_evidence,
    collect_evidence_async,
    default_evidence_providers,
    provider_sources,
)
from backend.app.services.consultation_brain.config import ConsultationBrainConfig
from backend.app.services.consultation_brain.constants import (
    ENGINE_VERSION,
    EvidenceCategory,
    EvidenceSource,
    PipelineStage,
)
from backend.app.services.consultation_brain.conflict_engine import ConflictEngine, ConflictEngineResult
from backend.app.services.consultation_brain.models import (
    ConsultationBrainOutput,
    ConsultationConflict,
    ConsultationConflictResolution,
    ConsultationEvidence,
    ConsultationEvidenceBundle,
    ConsultationInput,
    ConsultationPriority,
    ConsultationRecommendation,
)
from backend.app.services.consultation_brain.master_consultation_engine import MasterConsultationEngine
from backend.app.services.consultation_brain.master_consultation_models import (
    MasterConsultation,
    MasterConsultationLanguage,
    MasterConsultationSection,
    MasterConsultationSectionId,
)
from backend.app.services.consultation_brain.narrative_engine import NarrativeEngine
from backend.app.services.consultation_brain.narrative_models import (
    ConsultationNarrative,
    NarrativeLanguage,
    NarrativeSection,
    NarrativeSectionId,
)
from backend.app.services.consultation_brain.priority_engine import PriorityEngine, to_legacy_priorities
from backend.app.services.consultation_brain.priority_models import (
    ALL_PRIORITY_DOMAINS,
    ConsultationPriorityResult,
    DomainPriority,
    PriorityDomain,
)
from backend.app.services.consultation_brain.recommendation_models import (
    ALL_RECOMMENDATION_CATEGORIES,
    ConsultationRecommendationResult,
    RecommendationCategory,
    RecommendationTier,
    StructuredRecommendation,
)
from backend.app.services.consultation_brain.recommendation_engine import RecommendationEngine, to_legacy_recommendations
from backend.app.services.consultation_brain.normalizer import EvidenceNormalizer
from backend.app.services.consultation_brain.protocols import AsyncEvidenceProvider, Clock, EvidenceProvider
from backend.app.services.consultation_brain.providers import (
    CaseLearningEvidenceProvider,
    DashaEvidenceProvider,
    FusionEvidenceProvider,
    GoldenDatasetEvidenceProvider,
    KPEvidenceProvider,
    LalKitabEvidenceProvider,
    ProfessionalReportEvidenceProvider,
    RuleStudioEvidenceProvider,
    TransitEvidenceProvider,
    YogaEvidenceProvider,
    default_collection_providers,
)
from backend.app.services.consultation_brain.serializers import (
    consultation_brain_output_to_dict,
    evidence_bundle_to_dict,
)

__all__ = [
    "ALL_RECOMMENDATION_CATEGORIES",
    "ALL_PRIORITY_DOMAINS",
    "AsyncEvidenceProvider",
    "CaseLearningEvidenceProvider",
    "Clock",
    "ConflictEngine",
    "ConflictEngineResult",
    "ConflictType",
    "ConsultationBrain",
    "ConsultationBrainConfig",
    "ConsultationBrainOutput",
    "ConsultationConflict",
    "ConsultationConflictResolution",
    "ConsultationEvidence",
    "ConsultationEvidenceBundle",
    "ConsultationInput",
    "ConsultationNarrative",
    "ConsultationPriority",
    "ConsultationPriorityResult",
    "ConsultationRecommendation",
    "ConsultationRecommendationResult",
    "RecommendationCategory",
    "RecommendationEngine",
    "RecommendationTier",
    "StructuredRecommendation",
    "DomainPriority",
    "DashaEvidenceProvider",
    "ENGINE_VERSION",
    "EvidenceCategory",
    "EvidenceCollector",
    "EvidenceNormalizer",
    "EvidenceProvider",
    "EvidenceSource",
    "FixedClock",
    "FusionEvidenceProvider",
    "GoldenDatasetEvidenceProvider",
    "KPEvidenceProvider",
    "LalKitabEvidenceProvider",
    "MasterConsultation",
    "MasterConsultationEngine",
    "MasterConsultationLanguage",
    "MasterConsultationSection",
    "MasterConsultationSectionId",
    "NarrativeEngine",
    "NarrativeLanguage",
    "NarrativeSection",
    "NarrativeSectionId",
    "PriorityDomain",
    "PriorityEngine",
    "ProfessionalReportEvidenceProvider",
    "RuleStudioEvidenceProvider",
    "TransitEvidenceProvider",
    "UtcClock",
    "YogaEvidenceProvider",
    "as_async_provider",
    "collect_evidence",
    "collect_evidence_async",
    "consultation_brain_output_to_dict",
    "default_collection_providers",
    "default_evidence_providers",
    "evidence_bundle_to_dict",
    "PipelineStage",
    "provider_sources",
    "to_legacy_priorities",
    "to_legacy_recommendations",
]
