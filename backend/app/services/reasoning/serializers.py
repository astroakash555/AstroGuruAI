"""JSON serializers for intelligence analyzer outputs."""

from __future__ import annotations

from typing import Any

from backend.app.services.reasoning.fusion.models import (
    FusionRecommendation,
    FusionResult,
    FusedObservation,
    InterpretationConflict,
    RootCauseAnalysis,
)
from backend.app.services.reasoning.kp.models import EventTimingRecord, KPAnalysisResult, ReasoningObservation as KPObservation
from backend.app.services.reasoning.lal_kitab.models import LalKitabAnalysisResult, LalKitabRemedy, ReasoningObservation as LKObservation
from backend.app.services.reasoning.vedic.analyzer import VedicAnalysisResult
from backend.app.services.reasoning.vedic.constants import VedicObservation


def _observation_dict(observation: VedicObservation | KPObservation | LKObservation) -> dict[str, Any]:
    category = (
        observation.category.value
        if hasattr(observation.category, "value")
        else str(observation.category)
    )
    return {
        "observation_id": observation.observation_id,
        "category": category,
        "title": observation.title,
        "explanation": observation.explanation,
        "affected_planets": list(observation.affected_planets),
        "affected_houses": list(observation.affected_houses),
        "severity": observation.severity,
        "confidence": observation.confidence,
        "metadata": dict(observation.metadata),
    }


def vedic_result_to_dict(result: VedicAnalysisResult) -> dict[str, Any]:
    """Serialize a Vedic intelligence result for unified report JSON."""
    return {
        "analyzed_at": result.analyzed_at.isoformat(),
        "observations": [_observation_dict(item) for item in result.observations],
        "metadata": dict(result.metadata),
    }


def _event_timing_dict(record: EventTimingRecord) -> dict[str, Any]:
    return {
        "event_id": record.event_id,
        "event_type": record.event_type,
        "target_houses": list(record.target_houses),
        "is_supported": record.is_supported,
        "support_score": record.support_score,
        "significators_matched": list(record.significators_matched),
        "cusp_sub_lords_matched": list(record.cusp_sub_lords_matched),
        "evidence": list(record.evidence),
    }


def kp_result_to_dict(result: KPAnalysisResult) -> dict[str, Any]:
    """Serialize a KP intelligence result for unified report JSON."""
    return {
        "analyzed_at": result.analyzed_at.isoformat(),
        "observations": [_observation_dict(item) for item in result.observations],
        "event_timing": [_event_timing_dict(item) for item in result.event_timing],
        "metadata": dict(result.metadata),
    }


def _remedy_dict(remedy: LalKitabRemedy) -> dict[str, Any]:
    return {
        "remedy_id": remedy.remedy_id,
        "title": remedy.title,
        "explanation": remedy.explanation,
        "priority": remedy.priority,
        "expected_duration": remedy.expected_duration,
        "affected_planets": list(remedy.affected_planets),
        "affected_houses": list(remedy.affected_houses),
        "confidence": remedy.confidence,
        "source_observation_ids": list(remedy.source_observation_ids),
    }


def lal_kitab_result_to_dict(result: LalKitabAnalysisResult) -> dict[str, Any]:
    """Serialize a Lal Kitab intelligence result for unified report JSON."""
    return {
        "analyzed_at": result.analyzed_at.isoformat(),
        "observations": [_observation_dict(item) for item in result.observations],
        "remedies": [_remedy_dict(item) for item in result.remedies],
        "metadata": dict(result.metadata),
    }


def _root_cause_dict(root_cause: RootCauseAnalysis) -> dict[str, Any]:
    return {
        "title": root_cause.title,
        "explanation": root_cause.explanation,
        "supporting_observations": list(root_cause.supporting_observations),
        "supporting_engines": [engine.value for engine in root_cause.supporting_engines],
        "confidence": root_cause.confidence,
    }


def _conflict_dict(conflict: InterpretationConflict) -> dict[str, Any]:
    return {
        "conflict_id": conflict.conflict_id,
        "title": conflict.title,
        "explanation": conflict.explanation,
        "engines": [engine.value for engine in conflict.engines],
        "observation_ids": list(conflict.observation_ids),
        "affected_planets": list(conflict.affected_planets),
        "affected_houses": list(conflict.affected_houses),
        "severity_spread": conflict.severity_spread,
        "confidence": conflict.confidence,
    }


def _recommendation_dict(recommendation: FusionRecommendation) -> dict[str, Any]:
    return {
        "recommendation_id": recommendation.recommendation_id,
        "title": recommendation.title,
        "explanation": recommendation.explanation,
        "priority": recommendation.priority,
        "supporting_root_causes": list(recommendation.supporting_root_causes),
        "confidence": recommendation.confidence,
    }


def _fused_observation_dict(observation: FusedObservation) -> dict[str, Any]:
    return {
        "fusion_id": observation.fusion_id,
        "title": observation.title,
        "explanation": observation.explanation,
        "category": observation.category,
        "affected_planets": list(observation.affected_planets),
        "affected_houses": list(observation.affected_houses),
        "severity": observation.severity,
        "confidence": observation.confidence,
        "supporting_engines": [engine.value for engine in observation.supporting_engines],
        "rank_score": observation.rank_score,
        "has_conflict": observation.has_conflict,
    }


def fusion_result_to_dict(result: FusionResult) -> dict[str, Any]:
    """Serialize fusion output for unified report JSON."""
    return {
        "analyzed_at": result.analyzed_at.isoformat(),
        "root_causes": [_root_cause_dict(item) for item in result.root_causes],
        "confidence": result.confidence_score,
        "conflicts": [_conflict_dict(item) for item in result.conflicts],
        "recommendations": [_recommendation_dict(item) for item in result.recommendations],
        "observations": [_fused_observation_dict(item) for item in result.observations],
        "metadata": dict(result.metadata),
    }
