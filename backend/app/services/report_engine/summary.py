"""Strengths, challenges, and final summary sections (L, M, N)."""

from __future__ import annotations

from typing import Any

from backend.app.services.report_engine.base import join_lines, section
from backend.app.services.report_engine.confidence import fusion_confidence, section_confidence
from backend.app.services.report_engine.language import localize
from backend.app.services.report_engine.presentation import scrub_client_text
from backend.app.services.report_engine.types import ReportLanguage, ReportSection


def _item_text(item: dict[str, Any]) -> str:
    return str(item.get("title") or item.get("explanation") or "").strip()


def build_strengths_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
) -> ReportSection:
    consultation = unified_report.get("consultation_brain") or {}
    strengths = consultation.get("strengths") or []
    items = [{"text": _item_text(item)} for item in strengths[:8] if _item_text(item)]
    if not items:
        supportive = (unified_report.get("astro_intelligence") or {}).get("supportive_planets") or []
        if supportive:
            text = localize(
                language,
                hi=f"सहायक ग्रह: {', '.join(supportive)}",
                en=f"Supportive planets: {', '.join(supportive)}",
            )
            items = [{"text": text}]
    narrative = join_lines(item["text"] for item in items) if items else localize(
        language,
        hi="कोई विशेष शक्ति दर्ज नहीं है।",
        en="No explicit strengths recorded.",
    )
    return section(
        section_id="strengths",
        title=localize(language, hi="शक्तियाँ", en="Strengths"),
        narrative=scrub_client_text(narrative),
        facts={"items": items},
        confidence=section_confidence(unified_report, has_data=bool(items)),
    )


def build_challenges_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
) -> ReportSection:
    consultation = unified_report.get("consultation_brain") or {}
    risks = consultation.get("risks") or []
    items = [{"text": _item_text(item)} for item in risks[:8] if _item_text(item)]
    if not items:
        root_planets = (unified_report.get("astro_intelligence") or {}).get("root_cause_planets") or []
        if root_planets:
            text = localize(
                language,
                hi=f"मुख्य चुनौती से जुड़े ग्रह: {', '.join(root_planets)}",
                en=f"Primary challenge planets: {', '.join(root_planets)}",
            )
            items = [{"text": text}]
    narrative = join_lines(item["text"] for item in items) if items else localize(
        language,
        hi="कोई विशेष चुनौती दर्ज नहीं है।",
        en="No explicit challenges recorded.",
    )
    return section(
        section_id="challenges",
        title=localize(language, hi="चुनौतियाँ", en="Challenges"),
        narrative=scrub_client_text(narrative),
        facts={"items": items},
        confidence=section_confidence(unified_report, has_data=bool(items)),
    )


def build_final_summary_section(
    unified_report: dict[str, Any],
    *,
    language: ReportLanguage,
) -> ReportSection:
    summary = unified_report.get("summary") or {}
    consultation = unified_report.get("consultation_brain") or {}
    recommendations = [
        str(item.get("title") or item.get("explanation") or "")
        for item in (consultation.get("priorities") or [])[:5]
        if item.get("title") or item.get("explanation")
    ]
    chart_summary = localize(
        language,
        hi=(
            f"लग्न {summary.get('lagna_sign')}, चंद्र {summary.get('moon_sign')}, "
            f"वर्तमान दशा {summary.get('current_mahadasha')}/{summary.get('current_antardasha')}।"
        ),
        en=(
            f"Lagna {summary.get('lagna_sign')}, Moon {summary.get('moon_sign')}, "
            f"current dasha {summary.get('current_mahadasha')}/{summary.get('current_antardasha')}."
        ),
    )
    facts = {
        "executive_summary": consultation.get("executive_summary"),
        "chart_summary": chart_summary,
        "recommendations": recommendations,
    }
    narrative_parts = [consultation.get("executive_summary"), chart_summary]
    if recommendations:
        narrative_parts.append(
            localize(
                language,
                hi=f"सुझाव: {'; '.join(recommendations)}",
                en=f"Recommendations: {'; '.join(recommendations)}",
            )
        )
    narrative = join_lines([part for part in narrative_parts if part])
    return section(
        section_id="final_summary",
        title=localize(language, hi="अंतिम सारांश", en="Final Summary"),
        narrative=scrub_client_text(narrative),
        facts=facts,
        confidence=fusion_confidence(unified_report),
    )
