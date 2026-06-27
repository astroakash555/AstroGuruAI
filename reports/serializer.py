"""Serialize unified report results to JSON."""

from __future__ import annotations

from typing import Any

from reports.schemas import UnifiedReportJSON
from reports.types import UnifiedReportResult
from reports.utilities import normalize_highest_dosha_severity


def to_json_dict(result: UnifiedReportResult) -> dict[str, Any]:
    """Convert unified report result to JSON-serializable dictionary."""
    payload = UnifiedReportJSON(
        generated_at=result.generated_at,
        subject=dict(result.subject),
        kundali=result.kundali,
        navamsha=result.navamsha,
        dasha=result.dasha,
        yogas=result.yogas,
        doshas=result.doshas,
        transits=result.transits,
        problem_analysis=result.problem_analysis,
        lal_kitab=result.lal_kitab,
        kp_analysis=result.kp_analysis,
        astro_intelligence=result.astro_intelligence,
        remedy_recommendations=result.remedy_recommendations,
        vedic=result.vedic,
        kp=result.kp,
        lal_kitab_intelligence=result.lal_kitab_intelligence,
        fusion=result.fusion,
        summary={
            "lagna_sign": result.summary.lagna_sign,
            "moon_sign": result.summary.moon_sign,
            "moon_nakshatra": result.summary.moon_nakshatra,
            "present_yogas_count": result.summary.present_yogas_count,
            "present_doshas_count": result.summary.present_doshas_count,
            "highest_dosha_severity": normalize_highest_dosha_severity(
                result.summary.highest_dosha_severity
            ),
            "current_mahadasha": result.summary.current_mahadasha,
            "current_antardasha": result.summary.current_antardasha,
            "problem_category": result.summary.problem_category,
            "problem_severity": result.summary.problem_severity,
            "lal_kitab_findings_count": result.summary.lal_kitab_findings_count,
            "kp_supported_events": result.summary.kp_supported_events,
            "intelligence_severity_score": result.summary.intelligence_severity_score,
            "recommended_remedies_count": result.summary.recommended_remedies_count,
            "reasoning_confidence_score": result.summary.reasoning_confidence_score,
        },
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: UnifiedReportResult, *, indent: int | None = 2) -> str:
    """Convert unified report result to formatted JSON string."""
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
