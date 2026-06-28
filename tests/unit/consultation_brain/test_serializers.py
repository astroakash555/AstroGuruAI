"""Tests for consultation brain serializers."""

from datetime import UTC, datetime

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource, PipelineStage
from backend.app.services.consultation_brain.models import (
    ConsultationBrainOutput,
    ConsultationConflict,
    ConsultationEvidence,
    ConsultationPriority,
    ConsultationRecommendation,
)
from backend.app.services.consultation_brain.serializers import (
    conflict_to_dict,
    consultation_brain_output_to_dict,
    evidence_to_dict,
    priority_to_dict,
    recommendation_to_dict,
    stage_names,
)


def test_individual_entity_serializers(sample_evidence):
    assert evidence_to_dict(sample_evidence)["source"] == EvidenceSource.YOGAS.value
    conflict = ConsultationConflict(
        conflict_id="c1",
        evidence_ids=("a",),
        description="d",
        resolution="r",
        resolved_confidence=0.5,
    )
    assert conflict_to_dict(conflict)["conflict_id"] == "c1"
    priority = ConsultationPriority(
        rank=1,
        domain="general",
        title="Title",
        rationale="Why",
        confidence=0.5,
    )
    assert priority_to_dict(priority)["rank"] == 1
    recommendation = ConsultationRecommendation(
        recommendation_id="r1",
        title="Title",
        narrative="Text",
        priority_rank=1,
        confidence=0.5,
    )
    assert recommendation_to_dict(recommendation)["recommendation_id"] == "r1"


def test_consultation_brain_output_to_dict_serializes_enums():
    output = ConsultationBrainOutput(
        generated_at=datetime(2026, 6, 15, 12, 0, tzinfo=UTC),
        stage_trace=(PipelineStage.COLLECT_EVIDENCE,),
        evidence=(),
        conflicts=(),
        priorities=(),
        recommendations=(),
        overall_confidence=0.5,
        executive_summary="Summary",
        metadata={"language": "hi"},
    )
    payload = consultation_brain_output_to_dict(output)
    assert payload["stage_trace"] == ["collect_evidence"]
    assert payload["generated_at"].startswith("2026-06-15")
    assert payload["metadata"]["engine_version"]


def test_stage_names_helper():
    assert stage_names((PipelineStage.PRODUCE_OUTPUT,)) == ["produce_output"]
