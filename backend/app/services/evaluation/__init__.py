"""Intelligence evaluation and benchmark framework for AstroGuruAI Phase 8."""

from backend.app.services.evaluation.agreement import (
    compute_cross_engine_agreement,
    focus_signature,
    normalize_title,
)
from backend.app.services.evaluation.benchmark import (
    IntelligenceEvaluationBenchmark,
    evaluate_intelligence,
)
from backend.app.services.evaluation.confidence import compute_confidence_calibration
from backend.app.services.evaluation.drift import detect_output_drift
from backend.app.services.evaluation.metrics import (
    compute_fusion_consistency,
    compute_recommendation_consistency,
)
from backend.app.services.evaluation.models import (
    DriftReport,
    EngineObservationSnapshot,
    EvaluationInput,
    EvaluationResult,
    MetricRecord,
    RegressionReport,
    clamp_score,
    extract_engine_observations,
    observation_from_dict,
    resolve_fusion_payload,
)
from backend.app.services.evaluation.regression import compare_reports

__all__ = [
    "DriftReport",
    "EngineObservationSnapshot",
    "EvaluationInput",
    "EvaluationResult",
    "IntelligenceEvaluationBenchmark",
    "MetricRecord",
    "RegressionReport",
    "clamp_score",
    "compare_reports",
    "compute_confidence_calibration",
    "compute_cross_engine_agreement",
    "compute_fusion_consistency",
    "compute_recommendation_consistency",
    "detect_output_drift",
    "evaluate_intelligence",
    "extract_engine_observations",
    "focus_signature",
    "normalize_title",
    "observation_from_dict",
    "resolve_fusion_payload",
]
