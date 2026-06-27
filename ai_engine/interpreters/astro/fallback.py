"""Rule-based astro interpretation fallback."""

from __future__ import annotations

from typing import Any


def build_fallback_interpretation(report_json: dict[str, Any]) -> dict[str, str]:
    intelligence = report_json.get("astro_intelligence", {})
    dasha = report_json.get("dasha", {}).get("current", {})
    summary = report_json.get("summary", {})
    root_causes = intelligence.get("root_cause_planets", [])
    houses = intelligence.get("affected_houses", [])
    mahadasha = (dasha.get("mahadasha") or {}).get("lord")
    antardasha = (dasha.get("antardasha") or {}).get("lord")

    root_text = (
        f"The primary karmic indicators involve {', '.join(root_causes)} "
        f"with severity score {intelligence.get('severity_score', 0)}."
        if root_causes
        else "No dominant root cause planet cluster was detected from the structured analysis."
    )
    planets_text = (
        f"Supportive influences include {', '.join(intelligence.get('supportive_planets', []))}. "
        f"Root cause grahas: {', '.join(root_causes)}."
    )
    houses_text = (
        f"Houses under active influence: {', '.join(str(h) for h in houses)}."
        if houses
        else "No major house cluster was flagged across dosha, transit, and problem mappings."
    )
    dasha_text = (
        f"Current Vimshottari period: {mahadasha} mahadasha with {antardasha} antardasha. "
        f"This timing layer modulates event fructification."
        if mahadasha
        else "Dasha timing could not be summarized from the supplied report."
    )
    transit_text = _summarize_transits(report_json.get("transits", {}))
    kp_text = _summarize_kp(report_json.get("kp_analysis", {}))
    lk_text = _summarize_lal_kitab(report_json.get("lal_kitab", {}))
    summary_text = (
        f"Lagna {summary.get('lagna_sign')} with Moon in {summary.get('moon_sign')}. "
        f"Intelligence confidence {intelligence.get('confidence_score', 0)}."
    )

    return {
        "root_cause_explanation": root_text,
        "affected_planets_explanation": planets_text,
        "affected_houses_explanation": houses_text,
        "dasha_impact_explanation": dasha_text,
        "transit_impact_explanation": transit_text,
        "kp_findings_explanation": kp_text,
        "lal_kitab_findings_explanation": lk_text,
        "summary": summary_text,
    }


def _summarize_transits(transits: dict[str, Any]) -> str:
    highlights = []
    for key in ("saturn", "jupiter", "rahu", "ketu"):
        section = transits.get(key, {})
        current = section.get("current") or {}
        if current:
            highlights.append(
                f"{section.get('planet', key.title())} transiting "
                f"{current.get('sign', {}).get('name_en', 'unknown sign')} "
                f"(house {current.get('house_from_lagna')} from lagna)."
            )
    return " ".join(highlights) if highlights else "Transit highlights were not available."


def _summarize_kp(kp: dict[str, Any]) -> str:
    events = [event for event in kp.get("events", []) if event.get("is_supported")]
    if not events:
        return "KP event framework did not show strong significator support in the supplied report."
    labels = ", ".join(event["event_type"] for event in events[:3])
    return f"KP analysis supports structured event channels for: {labels}."


def _summarize_lal_kitab(lk: dict[str, Any]) -> str:
    present = [
        item["finding_name"]
        for key in ("rin_findings", "dosh_findings")
        for item in lk.get(key, [])
        if item.get("is_present")
    ]
    if not present:
        return "No active Lal Kitab rin/dosh indicators were present in the structured analysis."
    return f"Lal Kitab indicators present: {', '.join(present[:4])}."
