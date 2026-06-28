"""Professional report builder and serializer tests."""

from backend.app.services.report_engine.report_builder import ProfessionalReportBuilder
from backend.app.services.report_engine.serializers import (
    professional_report_to_client_json,
    professional_report_to_dict,
    section_to_dict,
)
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage


def test_professional_report_builder_produces_all_sections(
    sample_unified_report,
    sample_remedy_generation,
):
    builder = ProfessionalReportBuilder()
    result = builder.build(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
        )
    )
    assert len(result.sections) == 14
    section_ids = {section.section_id for section in result.sections}
    assert "birth_details" in section_ids
    assert "final_summary" in section_ids
    assert result.language == ReportLanguage.HINDI
    assert result.overall_confidence == 0.82


def test_client_json_preserves_legacy_fields(
    sample_unified_report,
    sample_remedy_generation,
):
    builder = ProfessionalReportBuilder()
    payload = builder.build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.ENGLISH,
        )
    )
    assert payload["problem_summary"] == "Marriage delay"
    assert payload["planet_analysis"]
    assert payload["dasha_analysis"]
    assert payload["transit_analysis"]
    assert payload["remedies"]
    assert payload["language"] == "en"
    assert len(payload["sections"]) == 14
    assert payload["metadata"]["version"] == "2.0"
    assert "engine" not in payload["metadata"]


def test_serializers_round_trip_section(sample_unified_report):
    builder = ProfessionalReportBuilder()
    result = builder.build(
        ProfessionalReportInput(unified_report=sample_unified_report, language=ReportLanguage.HINGLISH)
    )
    section_dict = section_to_dict(result.sections[0])
    assert section_dict["section_id"] == result.sections[0].section_id
    report_dict = professional_report_to_dict(result)
    assert report_dict["language"] == "hinglish"
    assert len(report_dict["sections"]) == 14


def test_client_json_uses_engine_remedies_when_generation_empty(sample_unified_report):
    builder = ProfessionalReportBuilder()
    payload = builder.build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation={},
            language=ReportLanguage.HINDI,
        )
    )
    assert payload["remedies"][0]["title"] == "Shani mantra"
