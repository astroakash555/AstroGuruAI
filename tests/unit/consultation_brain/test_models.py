"""Tests for consultation brain dataclasses."""

from dataclasses import is_dataclass
from datetime import UTC, datetime
from types import MappingProxyType

from backend.app.services.consultation_brain.models import (
    ConsultationBrainOutput,
    ConsultationConflict,
    ConsultationEvidence,
    ConsultationEvidenceBundle,
    ConsultationInput,
    ConsultationPriority,
    ConsultationRecommendation,
)


def test_models_are_frozen_dataclasses():
    for model in (
        ConsultationInput,
        ConsultationEvidence,
        ConsultationEvidenceBundle,
        ConsultationConflict,
        ConsultationPriority,
        ConsultationRecommendation,
        ConsultationBrainOutput,
    ):
        assert is_dataclass(model)
        assert model.__dataclass_params__.frozen is True


def test_output_metadata_is_read_only_mapping():
    output = ConsultationBrainOutput(
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        stage_trace=(),
        evidence=(),
        conflicts=(),
        priorities=(),
        recommendations=(),
        overall_confidence=0.5,
        executive_summary="Summary",
        metadata={"engine_version": "v0"},
    )
    assert isinstance(output.metadata, MappingProxyType)
