"""Tests for ConsultationEvidenceBundle."""

from backend.app.services.consultation_brain.collectors import EvidenceCollector
from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidenceBundle
from backend.app.services.consultation_brain.serializers import evidence_bundle_to_dict


def test_bundle_all_evidence_flattens_grouped_items(sample_consultation_input):
    bundle = EvidenceCollector().collect(sample_consultation_input)
    sources = {item.source for item in bundle.all_evidence}
    assert EvidenceSource.YOGAS in sources
    assert EvidenceSource.PROFESSIONAL_REPORT in sources
    assert bundle.evidence_count == len(bundle.all_evidence)


def test_empty_bundle_defaults():
    bundle = ConsultationEvidenceBundle()
    assert bundle.all_evidence == ()
    assert bundle.evidence_count == 0


def test_bundle_serializer_outputs_schema(sample_consultation_input):
    bundle = EvidenceCollector().collect(sample_consultation_input)
    payload = evidence_bundle_to_dict(bundle)
    assert set(payload.keys()) >= {
        "yogas",
        "dasha",
        "transit",
        "kp",
        "lal_kitab",
        "rule_studio",
        "case_learning",
        "fusion",
        "golden_dataset",
        "professional_report",
        "metadata",
        "all_evidence",
        "evidence_count",
    }
    assert payload["evidence_count"] == bundle.evidence_count
    assert isinstance(payload["yogas"], list)
