"""Rule-based fallback answers when no LLM provider is available."""

from __future__ import annotations

from typing import Any

DOMAIN_KEYWORDS = {
    "relationship": ("relationship", "partner", "love", "venus"),
    "marriage": ("marriage", "spouse", "wedding", "delay"),
    "career": ("career", "job", "profession", "work", "10th"),
    "business": ("business", "commerce", "trade", "profit"),
    "finance": ("finance", "money", "wealth", "income"),
    "health": ("health", "illness", "vitality", "medical"),
    "education": ("education", "study", "learning", "exam"),
    "spiritual_growth": ("spiritual", "meditation", "dharma"),
    "foreign_travel": ("foreign", "travel", "abroad", "visa"),
    "family": ("family", "home", "parents"),
    "children": ("children", "progeny", "pregnancy"),
}


def build_fallback_answer(*, report_context: dict[str, Any], user_message: str) -> str:
    """Compose an evidence-based answer from structured report context."""
    message = user_message.lower().strip()
    consultation = report_context.get("consultation_brain") or {}
    fusion = report_context.get("fusion") or {}
    summary = report_context.get("summary") or {}

    matched_sections = _matching_sections(consultation.get("sections", []), message)
    if matched_sections:
        section = matched_sections[0]
        advice = section.get("actionable_advice") or []
        advice_text = advice[0] if advice else "Review the active dasha and transit timing before deciding."
        return (
            f"Based on your report's {section.get('title', 'analysis')}: "
            f"{section.get('current_situation', '')} "
            f"Root cause: {section.get('root_cause', 'Multiple chart factors are interacting.')} "
            f"Recommended next step: {advice_text}"
        )

    recommendations = fusion.get("recommendations") or []
    if recommendations:
        top = recommendations[0]
        return (
            f"Your fused chart analysis highlights {top.get('title', 'a key priority')}: "
            f"{top.get('explanation', '')} "
            f"Current dasha context: "
            f"{_format_dasha(report_context.get('dasha'))}."
        )

    if consultation.get("executive_summary"):
        return (
            f"{consultation['executive_summary']} "
            f"Ask a more specific question about marriage, career, finance, health, or timing "
            f"for a sharper answer from your report."
        )

    lagna = summary.get("lagna_sign")
    moon = summary.get("moon_sign")
    if lagna and moon:
        return (
            f"Your report shows Lagna {lagna} and Moon in {moon}. "
            f"I can explain marriage, career, finance, health, or transit timing using the saved report evidence."
        )

    return (
        "I can answer questions using your saved Kundali report. "
        "Please ask about a specific life area such as marriage, career, finance, health, or current dasha timing."
    )


def _matching_sections(sections: Any, message: str) -> list[dict[str, Any]]:
    if not isinstance(sections, list):
        return []
    matches: list[tuple[int, dict[str, Any]]] = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        score = _section_score(section, message)
        if score > 0:
            matches.append((score, section))
    matches.sort(key=lambda item: item[0], reverse=True)
    return [section for _, section in matches]


def _section_score(section: dict[str, Any], message: str) -> int:
    score = 0
    section_id = str(section.get("section_id", "")).lower()
    title = str(section.get("title", "")).lower()
    if section_id and section_id.replace("_", " ") in message:
        score += 3
    if title and title.lower() in message:
        score += 3
    keywords = DOMAIN_KEYWORDS.get(section_id, ())
    for keyword in keywords:
        if keyword in message:
            score += 2
    return score


def _format_dasha(dasha: Any) -> str:
    if not isinstance(dasha, dict):
        return "dasha details are available in the saved report"
    current = dasha.get("current") if isinstance(dasha.get("current"), dict) else {}
    mahadasha = current.get("mahadasha") if isinstance(current.get("mahadasha"), dict) else {}
    antardasha = current.get("antardasha") if isinstance(current.get("antardasha"), dict) else {}
    maha_lord = mahadasha.get("lord")
    antara_lord = antardasha.get("lord")
    if maha_lord and antara_lord:
        return f"{maha_lord} mahadasha with {antara_lord} antardasha"
    if maha_lord:
        return f"{maha_lord} mahadasha"
    return "the active dasha period in your report"
