"""Tests for ConsultationBrain orchestrator."""

from backend.app.services.consultation_brain.brain import ConsultationBrain
from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource, PipelineStage
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationInput
from backend.app.services.consultation_brain.providers import YogaEvidenceProvider


class StubProvider:
    source = EvidenceSource.YOGAS

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        return (
            ConsultationEvidence(
                evidence_id="custom-evidence-1",
                source=EvidenceSource.YOGAS,
                title="Custom",
                summary="Injected provider evidence.",
                weight=0.9,
                confidence=0.8,
                category=EvidenceCategory.GENERAL,
            ),
        )


def test_brain_run_executes_all_pipeline_stages(sample_consultation_input):
    output = ConsultationBrain().run(sample_consultation_input)
    assert output.stage_trace == (
        PipelineStage.COLLECT_EVIDENCE,
        PipelineStage.NORMALIZE_EVIDENCE,
        PipelineStage.RESOLVE_CONFLICTS,
        PipelineStage.RANK_PRIORITIES,
        PipelineStage.GENERATE_RECOMMENDATIONS,
        PipelineStage.GENERATE_NARRATIVE,
        PipelineStage.PRODUCE_OUTPUT,
    )
    assert output.metadata["engine_version"] == ConsultationBrain.ENGINE_VERSION
    assert output.metadata["collection_metadata"]
    assert output.evidence
    assert output.executive_summary


def test_brain_accepts_injected_providers(sample_consultation_input):
    brain = ConsultationBrain(evidence_providers=[StubProvider()])
    output = brain.run(sample_consultation_input)
    assert len(output.evidence) == 1
    assert output.evidence[0].evidence_id == "custom-evidence-1"
    assert brain.evidence_providers[0].source == EvidenceSource.YOGAS


def test_brain_run_json_returns_serializable_dict(sample_consultation_input):
    payload = ConsultationBrain().run_json(sample_consultation_input)
    assert payload["overall_confidence"] >= 0.0
    assert payload["metadata"]["engine_version"]
    assert isinstance(payload["stage_trace"], list)
    assert payload["stage_trace"][0] == PipelineStage.COLLECT_EVIDENCE.value


def test_brain_with_empty_unified_report():
    output = ConsultationBrain().run(
        ConsultationInput(unified_report={}, problem_text=None, language="en")
    )
    assert output.evidence == ()
    assert output.priorities == ()
    assert output.recommendations == ()
    assert output.narrative is not None
    assert len(output.narrative.sections) == 10
