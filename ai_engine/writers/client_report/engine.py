"""Client report writer engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ai_engine.writers.client_report.schemas import ClientReportJSON
from ai_engine.writers.client_report.types import ClientReportInput, ClientReportResult


class ClientReportWriter:
    """Assemble the 10-section client-facing report from structured analysis JSON."""

    def write(self, report_input: ClientReportInput) -> ClientReportResult:
        report = report_input.report_json
        interpretation = report_input.interpretation_json
        remedies = report_input.remedy_generation_json.get("remedies", [])
        problem = report_input.problem_text or "No explicit client problem statement was supplied."
        intelligence = report.get("astro_intelligence", {})
        summary = report.get("summary", {})

        short_term = (
            f"Near-term focus: dasha lords {summary.get('current_mahadasha')} / "
            f"{summary.get('current_antardasha')} with intelligence severity "
            f"{intelligence.get('severity_score', 0)}."
        )
        long_term = (
            f"Long-term themes are shaped by lagna {summary.get('lagna_sign')}, "
            f"moon nakshatra {summary.get('moon_nakshatra')}, and recurring root cause grahas "
            f"{', '.join(intelligence.get('root_cause_planets', []))}."
        )

        return ClientReportResult(
            generated_at=datetime.now(timezone.utc),
            problem_summary=problem,
            astrological_root_cause=interpretation.get("root_cause_explanation", ""),
            planet_analysis=interpretation.get("affected_planets_explanation", ""),
            dasha_analysis=interpretation.get("dasha_impact_explanation", ""),
            transit_analysis=interpretation.get("transit_impact_explanation", ""),
            kp_analysis=interpretation.get("kp_findings_explanation", ""),
            lal_kitab_analysis=interpretation.get("lal_kitab_findings_explanation", ""),
            remedies=list(remedies),
            short_term_outlook=short_term,
            long_term_outlook=long_term,
            metadata={"engine": "client_report_writer_v1", "version": "1.0"},
        )

    def write_json(self, report_input: ClientReportInput) -> dict[str, Any]:
        result = self.write(report_input)
        payload = ClientReportJSON(
            generated_at=result.generated_at,
            problem_summary=result.problem_summary,
            astrological_root_cause=result.astrological_root_cause,
            planet_analysis=result.planet_analysis,
            dasha_analysis=result.dasha_analysis,
            transit_analysis=result.transit_analysis,
            kp_analysis=result.kp_analysis,
            lal_kitab_analysis=result.lal_kitab_analysis,
            remedies=result.remedies,
            short_term_outlook=result.short_term_outlook,
            long_term_outlook=result.long_term_outlook,
            metadata=dict(result.metadata),
        )
        return payload.model_dump(mode="json")
