"""Final client-report polish: human Hindi only, no engine leakage."""

from __future__ import annotations

from typing import Any

from backend.app.services.consultation_brain.models import ConsultationBrainOutput
from backend.app.services.report_engine.human_astrologer_rewrite_engine import (
    HumanAstrologerRewriteEngine,
    SECTION_FALLBACKS,
)
from backend.app.services.report_engine.human_astrologer_rewrite_models import HumanAstrologerSectionId
from backend.app.services.report_engine.human_astrologer_text import (
    humanize_astrology_text,
    is_technical_paragraph,
    join_paragraphs,
    polish_remedy_item,
)

_LEGACY_FIELD_FALLBACKS: dict[str, HumanAstrologerSectionId] = {
    "astrological_root_cause": HumanAstrologerSectionId.WHY_PROBLEM_EXISTS,
    "planet_analysis": HumanAstrologerSectionId.WHY_PROBLEM_EXISTS,
    "dasha_analysis": HumanAstrologerSectionId.CURRENT_SITUATION,
    "transit_analysis": HumanAstrologerSectionId.FUTURE_OUTLOOK,
    "kp_analysis": HumanAstrologerSectionId.FUTURE_OUTLOOK,
    "lal_kitab_analysis": HumanAstrologerSectionId.NEGATIVE_FACTORS,
    "short_term_outlook": HumanAstrologerSectionId.CURRENT_SITUATION,
    "long_term_outlook": HumanAstrologerSectionId.FUTURE_OUTLOOK,
}

_LEGACY_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "astrological_root_cause": ("why_problem_exists",),
    "planet_analysis": ("why_problem_exists", "current_situation"),
    "dasha_analysis": ("current_situation",),
    "transit_analysis": ("future_outlook",),
    "kp_analysis": ("future_outlook",),
    "lal_kitab_analysis": ("negative_factors", "remedies"),
    "short_term_outlook": ("current_situation",),
    "long_term_outlook": ("future_outlook", "final_blessing"),
}


def polish_client_report_for_human_delivery(
    client_report: dict[str, Any],
    brain_output: ConsultationBrainOutput,
    *,
    problem_text: str | None = None,
) -> None:
    """Rewrite all client-visible report strings into professional Hindi consultation prose."""
    rewrite = HumanAstrologerRewriteEngine().rewrite_to_client_dict(
        brain_output,
        problem_text=problem_text,
        language="hi",
    )
    section_bodies = {
        str(section.get("section_id")): str(section.get("body") or "")
        for section in rewrite.get("sections") or []
        if isinstance(section, dict)
    }

    for section in client_report.get("sections") or []:
        if not isinstance(section, dict):
            continue
        narrative = humanize_astrology_text(str(section.get("narrative") or ""))
        section["narrative"] = narrative or _body_for(section_bodies, section.get("section_id"))
        facts = section.get("facts")
        if isinstance(facts, list):
            cleaned_facts = [
                humanize_astrology_text(str(line))
                for line in facts
                if humanize_astrology_text(str(line)) and not is_technical_paragraph(str(line))
            ]
            section["facts"] = cleaned_facts[:4]
        section.pop("confidence", None)
        section.pop("confidence_label", None)

    if problem_text:
        client_report["problem_summary"] = humanize_astrology_text(problem_text) or problem_text
    else:
        client_report["problem_summary"] = section_bodies.get("understanding_problem", "")

    for field, source_ids in _LEGACY_FIELD_MAP.items():
        merged = _merged_body(section_bodies, source_ids)
        if not merged:
            fallback_id = _LEGACY_FIELD_FALLBACKS.get(field)
            merged = SECTION_FALLBACKS[fallback_id] if fallback_id else merged
        client_report[field] = merged

    remedies: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    for item in client_report.get("remedies") or []:
        if not isinstance(item, dict):
            continue
        polished = polish_remedy_item(item)
        title = str(polished.get("title") or "")
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        remedies.append(polished)
    if not remedies:
        remedy_body = section_bodies.get("remedies", "")
        if remedy_body:
            remedies.append(
                {
                    "title": "व्यक्तिगत उपाय",
                    "description": remedy_body.split("\n\n")[0],
                    "priority": 1,
                }
            )
    client_report["remedies"] = remedies[:8]

    metadata = client_report.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("overall_confidence", None)

    client_report["master_consultation"] = rewrite
    client_report["language"] = "hi"


def _merged_body(section_bodies: dict[str, str], section_ids: tuple[str, ...]) -> str:
    parts: list[str] = []
    for section_id in section_ids:
        body = section_bodies.get(section_id, "")
        if not body:
            continue
        parts.extend(chunk for chunk in body.split("\n\n") if chunk.strip())
    return join_paragraphs(parts)


def _body_for(section_bodies: dict[str, str], section_id: Any) -> str:
    return section_bodies.get(str(section_id or ""), "")
