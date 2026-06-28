"""Professional report builder orchestrating all sections."""

from __future__ import annotations

from backend.app.services.report_engine.birth_details import build_birth_details_section
from backend.app.services.report_engine.confidence import fusion_confidence
from backend.app.services.report_engine.dasha_analysis import build_dasha_section
from backend.app.services.report_engine.house_analysis import build_house_wise_section
from backend.app.services.report_engine.moon_analysis import build_ascendant_section, build_moon_section
from backend.app.services.report_engine.planet_analysis import (
    build_planet_wise_section,
    build_planetary_positions_section,
)
from backend.app.services.report_engine.problem_analysis import build_problem_section
from backend.app.services.report_engine.remedy_analysis import build_remedy_section
from backend.app.services.report_engine.serializers import professional_report_to_client_json
from backend.app.services.report_engine.summary import (
    build_challenges_section,
    build_final_summary_section,
    build_strengths_section,
)
from backend.app.services.report_engine.transit_analysis import build_transit_section
from backend.app.services.report_engine.types import (
    ProfessionalReportInput,
    ProfessionalReportResult,
    ReportLanguage,
)
from backend.app.services.report_engine.yoga_analysis import build_yoga_section


class ProfessionalReportBuilder:
    """Compose a structured professional report from validated engine outputs."""

    def build(self, report_input: ProfessionalReportInput) -> ProfessionalReportResult:
        unified_report = report_input.unified_report
        language = report_input.language

        sections = (
            build_birth_details_section(
                unified_report,
                problem_text=report_input.problem_text,
                language=language,
            ),
            build_planetary_positions_section(unified_report, language=language),
            build_ascendant_section(unified_report, language=language),
            build_moon_section(unified_report, language=language),
            build_planet_wise_section(unified_report, language=language),
            build_house_wise_section(unified_report, language=language),
            build_yoga_section(unified_report, language=language),
            build_dasha_section(unified_report, language=language),
            build_transit_section(unified_report, language=language),
            build_problem_section(
                unified_report,
                problem_text=report_input.problem_text,
                language=language,
            ),
            build_remedy_section(
                unified_report,
                remedy_generation=report_input.remedy_generation,
                language=language,
            ),
            build_strengths_section(unified_report, language=language),
            build_challenges_section(unified_report, language=language),
            build_final_summary_section(unified_report, language=language),
        )
        return ProfessionalReportResult(
            sections=sections,
            language=language,
            overall_confidence=fusion_confidence(unified_report),
        )

    def build_json(self, report_input: ProfessionalReportInput) -> dict:
        """Build report and serialize to legacy-compatible client_report JSON."""
        result = self.build(report_input)
        return professional_report_to_client_json(result, report_input=report_input)
