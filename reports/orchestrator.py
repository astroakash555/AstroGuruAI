"""Unified report orchestrator."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from ai_engine.analyzers.problem import ProblemAnalyzer, ProblemAnalyzerInput
from ai_engine.analyzers.problem.serializer import to_json_dict as problem_to_json_dict
from astro_intelligence import AstroIntelligenceEngine, AstroIntelligenceInput
from astro_intelligence.serializers.serializer import to_json_dict as intelligence_to_json_dict
from astrology_engine.core.base import BirthData
from astrology_engine.dasha.serializer import to_json_dict as dasha_to_json_dict
from astrology_engine.doshas.serializer import to_json_dict as dosha_to_json_dict
from astrology_engine.engine import VedicAstrologyEngine
from astrology_engine.transits.serializer import to_json_dict as transit_to_json_dict
from astrology_engine.yogas.serializer import to_json_dict as yoga_to_json_dict
from kp_engine import KPEngine
from kp_engine.serializers.serializer import to_json_dict as kp_to_json_dict
from lal_kitab_engine import LalKitabEngine
from lal_kitab_engine.serializers.serializer import to_json_dict as lal_kitab_to_json_dict
from remedy_engine.engine import RemedyMatchContext
from remedy_engine.serializers.serializer import to_json_dict as remedy_to_json_dict
from backend.app.services.reasoning.integration import (
    IntelligenceReportIntegration,
    chart_inputs_from_lagna,
    fusion_confidence_score,
)
from reports.builders import build_dasha_input_from_chart
from reports.charts.serializer import charts_from_bundle
from reports.serializer import to_json_dict, to_json_string
from reports.types import ReportInput, ReportSummary, UnifiedReportResult
from reports.utilities import normalize_highest_dosha_severity


class ReportOrchestrator:
    """
    Combines kundali, navamsha, dasha, yogas, doshas, transits, Lal Kitab, KP,
    problem analysis, astro intelligence, fused intelligence, and remedy
    recommendations into one report.

    Output is JSON only — no AI interpretation layer.
    """

    def __init__(
        self,
        astrology_engine: VedicAstrologyEngine | None = None,
        problem_analyzer: ProblemAnalyzer | None = None,
        lal_kitab_engine: LalKitabEngine | None = None,
        kp_engine: KPEngine | None = None,
        intelligence_engine: AstroIntelligenceEngine | None = None,
        intelligence_integration: IntelligenceReportIntegration | None = None,
    ) -> None:
        self._astrology = astrology_engine or VedicAstrologyEngine()
        self._problem_analyzer = problem_analyzer or ProblemAnalyzer()
        self._lal_kitab = lal_kitab_engine or LalKitabEngine()
        self._kp = kp_engine or KPEngine()
        self._intelligence = intelligence_engine or AstroIntelligenceEngine()
        self._intelligence_integration = intelligence_integration or IntelligenceReportIntegration()

    def generate(self, report_input: ReportInput) -> UnifiedReportResult:
        """Generate a unified structured report from birth data and optional problem text."""
        chart = self._astrology.compute_chart(report_input.birth_data)
        kundali_json, navamsha_json = charts_from_bundle(chart)

        dasha_input = build_dasha_input_from_chart(
            chart,
            birth_place=report_input.birth_place,
            timezone=report_input.birth_data.timezone,
        )
        dasha_result = self._astrology.compute_vimshottari_dasha(
            dasha_input,
            reference_datetime=report_input.reference_datetime,
        )
        yoga_result = self._astrology.detect_yogas(chart)
        dosha_result = self._astrology.detect_doshas(chart)
        transit_result = self._astrology.analyze_transits(
            chart,
            target_date=report_input.target_date or date.today(),
            timezone=report_input.birth_data.timezone,
        )
        lal_kitab_result = self._lal_kitab.analyze(chart)
        kp_result = self._kp.analyze(chart)

        problem_json: dict[str, Any] | None = None
        if report_input.include_problem_analysis and report_input.problem_text:
            problem_result = self._problem_analyzer.analyze(
                ProblemAnalyzerInput(
                    problem_text=report_input.problem_text,
                    client_id=report_input.client_id,
                    locale=report_input.locale,
                )
            )
            problem_json = problem_to_json_dict(problem_result)

        dasha_json = dasha_to_json_dict(dasha_result)
        yoga_json = yoga_to_json_dict(yoga_result)
        dosha_json = dosha_to_json_dict(dosha_result)
        transit_json = transit_to_json_dict(transit_result)
        lal_kitab_json = lal_kitab_to_json_dict(lal_kitab_result)
        kp_json = kp_to_json_dict(kp_result)

        intelligence_input = AstroIntelligenceInput(
            kundali=kundali_json,
            navamsha=navamsha_json,
            dasha=dasha_json,
            yogas=yoga_json,
            doshas=dosha_json,
            transits=transit_json,
            problem_analysis=problem_json,
            lal_kitab=lal_kitab_json,
            kp_analysis=kp_json,
        )
        intelligence_result = self._intelligence.analyze(intelligence_input)
        intelligence_json = intelligence_to_json_dict(intelligence_result)

        planet_positions, houses = chart_inputs_from_lagna(chart.lagna_kundali)
        intelligence_pipeline = self._intelligence_integration.run(
            planet_positions=planet_positions,
            houses=houses,
            reference_datetime=report_input.reference_datetime,
        )

        remedy_context = RemedyMatchContext(
            root_cause_planets=intelligence_result.root_cause_planets,
            affected_houses=intelligence_result.affected_houses,
            categories=(
                (problem_json.get("category", {}).get("category", "unknown"),)
                if problem_json
                else ()
            ),
            severity_level=(
                problem_json.get("severity", {}).get("level", "moderate")
                if problem_json
                else "moderate"
            ),
        )
        remedy_json = remedy_to_json_dict(self._intelligence.remedy_engine.match(remedy_context))

        summary = _build_summary(
            kundali_json=kundali_json,
            dasha_json=dasha_json,
            yoga_json=yoga_json,
            dosha_json=dosha_json,
            problem_json=problem_json,
            lal_kitab_json=lal_kitab_json,
            kp_json=kp_json,
            intelligence_json=intelligence_json,
            intelligence_pipeline=intelligence_pipeline,
        )

        return UnifiedReportResult(
            generated_at=datetime.now(timezone.utc),
            subject=_build_subject(report_input, chart.metadata.datetime_utc),
            kundali=kundali_json,
            navamsha=navamsha_json,
            dasha=dasha_json,
            yogas=yoga_json,
            doshas=dosha_json,
            transits=transit_json,
            problem_analysis=problem_json,
            lal_kitab=lal_kitab_json,
            kp_analysis=kp_json,
            astro_intelligence=intelligence_json,
            remedy_recommendations=remedy_json,
            vedic=intelligence_pipeline.vedic,
            kp=intelligence_pipeline.kp,
            lal_kitab_intelligence=intelligence_pipeline.lal_kitab,
            fusion=intelligence_pipeline.fusion,
            summary=summary,
            metadata={
                "orchestrator": "report_orchestrator_v2",
                "ai_interpretation": False,
                "components": [
                    component
                    for component in (
                        "kundali",
                        "navamsha",
                        "dasha",
                        "yogas",
                        "doshas",
                        "transits",
                        "problem_analysis" if problem_json else None,
                        "lal_kitab",
                        "kp_analysis",
                        "astro_intelligence",
                        "vedic",
                        "kp",
                        "lal_kitab_intelligence",
                        "fusion",
                        "remedy_recommendations",
                    )
                    if component
                ],
                "reference_date": (report_input.target_date or date.today()).isoformat(),
                "intelligence_engines": intelligence_pipeline.fusion.get("metadata", {}).get(
                    "active_engines",
                    [],
                ),
            },
        )

    def generate_from_birth(
        self,
        birth_data: BirthData,
        *,
        birth_place: str,
        problem_text: str | None = None,
        client_id: str | None = None,
        locale: str = "en",
        target_date: date | None = None,
        reference_datetime: datetime | None = None,
        include_problem_analysis: bool = True,
    ) -> UnifiedReportResult:
        """Convenience wrapper around `generate` using birth data directly."""
        return self.generate(
            ReportInput(
                birth_data=birth_data,
                birth_place=birth_place,
                problem_text=problem_text,
                client_id=client_id,
                locale=locale,
                target_date=target_date,
                reference_datetime=reference_datetime,
                include_problem_analysis=include_problem_analysis,
            )
        )

    def generate_json(self, report_input: ReportInput) -> dict[str, Any]:
        """Generate unified report and return JSON dictionary."""
        return to_json_dict(self.generate(report_input))

    def generate_json_string(self, report_input: ReportInput, *, indent: int | None = 2) -> str:
        """Generate unified report and return formatted JSON string."""
        return to_json_string(self.generate(report_input), indent=indent)


def _build_subject(report_input: ReportInput, birth_datetime_utc: datetime) -> dict[str, Any]:
    return {
        "client_id": report_input.client_id,
        "birth_place": report_input.birth_place,
        "timezone": report_input.birth_data.timezone,
        "latitude": report_input.birth_data.latitude,
        "longitude": report_input.birth_data.longitude,
        "datetime_utc": birth_datetime_utc,
    }


def _build_summary(
    *,
    kundali_json: dict[str, Any],
    dasha_json: dict[str, Any],
    yoga_json: dict[str, Any],
    dosha_json: dict[str, Any],
    problem_json: dict[str, Any] | None,
    lal_kitab_json: dict[str, Any],
    kp_json: dict[str, Any],
    intelligence_json: dict[str, Any],
    intelligence_pipeline,
) -> ReportSummary:
    current = dasha_json.get("current", {})
    mahadasha = current.get("mahadasha")
    antardasha = current.get("antardasha")

    return ReportSummary(
        lagna_sign=kundali_json["ascendant"]["sign"]["name_en"],
        moon_sign=_moon_sign_from_kundali(kundali_json),
        moon_nakshatra=dasha_json["moon"]["nakshatra"],
        present_yogas_count=yoga_json["summary"]["present_count"],
        present_doshas_count=dosha_json["summary"]["present_count"],
        highest_dosha_severity=normalize_highest_dosha_severity(
            dosha_json["summary"].get("highest_severity")
        ),
        current_mahadasha=mahadasha["lord"] if mahadasha else None,
        current_antardasha=antardasha["lord"] if antardasha else None,
        problem_category=(
            problem_json["category"]["category"] if problem_json else None
        ),
        problem_severity=(
            problem_json["severity"]["level"] if problem_json else None
        ),
        lal_kitab_findings_count=lal_kitab_json["summary"]["present_count"],
        kp_supported_events=kp_json["summary"]["supported_events"],
        intelligence_severity_score=intelligence_json.get("severity_score"),
        recommended_remedies_count=len(intelligence_json.get("recommended_remedies", [])),
        reasoning_confidence_score=fusion_confidence_score(intelligence_pipeline),
    )


def _moon_sign_from_kundali(kundali_json: dict[str, Any]) -> str:
    for planet in kundali_json["planets"]:
        if planet["name"] == "Moon":
            return planet["sign"]["name_en"]
    raise ValueError("Moon not found in kundali chart data.")
