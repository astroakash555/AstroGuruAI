"""Tests for subsystem evidence providers."""

from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationInput
from backend.app.services.consultation_brain.protocols import EvidenceProvider
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


def test_default_collection_providers_register_all_ten_sources():
    providers = default_collection_providers()
    sources = {provider.source for provider in providers}
    assert sources == {
        EvidenceSource.YOGAS,
        EvidenceSource.DASHA,
        EvidenceSource.TRANSIT,
        EvidenceSource.KP,
        EvidenceSource.LAL_KITAB,
        EvidenceSource.RULE_STUDIO,
        EvidenceSource.CASE_LEARNING,
        EvidenceSource.FUSION,
        EvidenceSource.GOLDEN_DATASET,
        EvidenceSource.PROFESSIONAL_REPORT,
    }


def test_providers_implement_protocol():
    for provider in default_collection_providers():
        assert isinstance(provider, EvidenceProvider)


def test_yoga_provider_extracts_present_yogas(sample_unified_report):
    evidence = YogaEvidenceProvider().collect(ConsultationInput(unified_report=sample_unified_report))
    assert any(item.evidence_id == "yoga-gaj_kesari" for item in evidence)
    assert any(item.evidence_id == "yoga-summary" for item in evidence)


def test_dasha_provider_extracts_active_periods(sample_unified_report):
    evidence = DashaEvidenceProvider().collect(ConsultationInput(unified_report=sample_unified_report))
    ids = {item.evidence_id for item in evidence}
    assert "dasha-mahadasha-saturn" in ids
    assert "dasha-antardasha-venus" in ids


def test_transit_provider_extracts_planet_signals(sample_unified_report):
    evidence = TransitEvidenceProvider().collect(ConsultationInput(unified_report=sample_unified_report))
    assert evidence[0].source == EvidenceSource.TRANSIT
    assert "sade_sati_phase" in evidence[0].summary


def test_kp_provider_extracts_events_and_observations(sample_unified_report):
    evidence = KPEvidenceProvider().collect(ConsultationInput(unified_report=sample_unified_report))
    assert any(item.evidence_id == "kp-event-marriage_event" for item in evidence)
    assert any(item.evidence_id == "kp-observation-kp-obs-1" for item in evidence)


def test_lal_kitab_provider_extracts_findings(sample_unified_report):
    evidence = LalKitabEvidenceProvider().collect(ConsultationInput(unified_report=sample_unified_report))
    assert any("saturn_rahu_dosh" in item.evidence_id for item in evidence)


def test_rule_studio_provider_extracts_rules(sample_unified_report):
    evidence = RuleStudioEvidenceProvider().collect(ConsultationInput(unified_report=sample_unified_report))
    assert evidence[0].evidence_id == "rule-studio-marriage_delay_rule"


def test_case_learning_provider_extracts_patterns(sample_unified_report):
    evidence = CaseLearningEvidenceProvider().collect(ConsultationInput(unified_report=sample_unified_report))
    assert evidence[0].evidence_id == "case-learning-late_marriage_case"


def test_fusion_provider_extracts_confidence_and_signals(sample_unified_report):
    evidence = FusionEvidenceProvider().collect(ConsultationInput(unified_report=sample_unified_report))
    assert any(item.evidence_id == "fusion-confidence" for item in evidence)
    assert any(item.evidence_id == "fusion-root-seventh_house" for item in evidence)


def test_golden_dataset_provider_extracts_matches(sample_unified_report):
    evidence = GoldenDatasetEvidenceProvider().collect(ConsultationInput(unified_report=sample_unified_report))
    assert evidence[0].evidence_id == "golden-dataset-benchmark_marriage_001"


def test_professional_report_provider_extracts_sections(sample_consultation_input):
    evidence = ProfessionalReportEvidenceProvider().collect(sample_consultation_input)
    assert evidence[0].source == EvidenceSource.PROFESSIONAL_REPORT
    assert "Marriage delay indicated." in evidence[0].summary


def test_providers_return_empty_when_section_missing():
    empty_input = ConsultationInput(unified_report={})
    assert YogaEvidenceProvider().collect(empty_input) == ()
    assert FusionEvidenceProvider().collect(empty_input) == ()
