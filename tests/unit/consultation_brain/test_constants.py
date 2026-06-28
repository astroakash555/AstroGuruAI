"""Tests for consultation brain constants."""

from backend.app.services.consultation_brain.constants import (
    ENGINE_VERSION,
    EvidenceCategory,
    EvidenceSource,
    PipelineStage,
    SOURCE_WEIGHTS,
)


def test_enums_contain_expected_sources():
    assert EvidenceSource.FUSION.value == "fusion"
    assert EvidenceSource.RULE_STUDIO.value == "rule_studio"
    assert EvidenceCategory.TIMING.value == "timing"


def test_pipeline_stage_order_names():
    assert PipelineStage.COLLECT_EVIDENCE.value == "collect_evidence"
    assert PipelineStage.PRODUCE_OUTPUT.value == "produce_output"


def test_source_weights_include_all_sources():
    for source in EvidenceSource:
        assert source in SOURCE_WEIGHTS


def test_engine_version_present():
    assert ENGINE_VERSION.startswith("consultation_brain")
