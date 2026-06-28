"""JSON serialization helpers for consultation brain output."""

from __future__ import annotations

from dataclasses import fields
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any

from backend.app.services.consultation_brain.constants import ENGINE_VERSION, PipelineStage
from backend.app.services.consultation_brain.models import (
    ConsultationBrainOutput,
    ConsultationConflict,
    ConsultationEvidence,
    ConsultationEvidenceBundle,
    ConsultationPriority,
    ConsultationRecommendation,
)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, MappingProxyType):
        return {key: _serialize_value(item) for key, item in value.items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    return value


def _dataclass_payload(instance: object) -> dict[str, Any]:
    return {field.name: getattr(instance, field.name) for field in fields(instance)}  # type: ignore[arg-type]


def evidence_to_dict(evidence: ConsultationEvidence) -> dict[str, Any]:
    return _serialize_value(_dataclass_payload(evidence))


def conflict_to_dict(conflict: ConsultationConflict) -> dict[str, Any]:
    return _serialize_value(_dataclass_payload(conflict))


def priority_to_dict(priority: ConsultationPriority) -> dict[str, Any]:
    return _serialize_value(_dataclass_payload(priority))


def recommendation_to_dict(recommendation: ConsultationRecommendation) -> dict[str, Any]:
    return _serialize_value(_dataclass_payload(recommendation))


def evidence_bundle_to_dict(bundle: ConsultationEvidenceBundle) -> dict[str, Any]:
    """Serialize grouped evidence bundle to JSON-compatible dict."""
    payload = _serialize_value(_dataclass_payload(bundle))
    payload["all_evidence"] = [evidence_to_dict(item) for item in bundle.all_evidence]
    payload["evidence_count"] = bundle.evidence_count
    return payload


def consultation_brain_output_to_dict(output: ConsultationBrainOutput) -> dict[str, Any]:
    """Serialize full consultation brain output to JSON-compatible dict."""
    payload = _serialize_value(_dataclass_payload(output))
    payload["stage_trace"] = [stage.value for stage in output.stage_trace]
    payload["metadata"] = {
        **output.metadata,
        "engine_version": ENGINE_VERSION,
    }
    return payload


def stage_names(stages: tuple[PipelineStage, ...]) -> list[str]:
    return [stage.value for stage in stages]
