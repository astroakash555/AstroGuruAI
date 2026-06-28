"""Client-facing presentation helpers for professional report output."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from backend.app.services.report_engine.types import ReportLanguage

FORBIDDEN_PATTERNS = (
    r"\[object Object\]",
    r"supported\s*=\s*true",
    r"supported\s*=\s*false",
    r"supported=true",
    r"supported=false",
    r"professional_report_engine",
    r"engine_locked",
    r"engine output",
    r"Engine remedy",
    r"Engine उपाय",
    r"fusion_id",
    r"observation_ids",
    r'"is_supported"\s*:',
    r"'is_supported'\s*:",
)

FORBIDDEN_REGEXES = tuple(re.compile(pattern, re.IGNORECASE) for pattern in FORBIDDEN_PATTERNS)


def assert_client_safe_text(text: str) -> None:
    """Raise when forbidden diagnostic text appears in client output."""
    for pattern in FORBIDDEN_REGEXES:
        if pattern.search(text):
            raise ValueError(f"Forbidden client report text matched pattern: {pattern.pattern}")


def scrub_client_text(text: str | None) -> str:
    """Remove diagnostic phrasing from client-visible strings."""
    if not text:
        return ""
    cleaned = str(text)
    cleaned = re.sub(r"supported\s*=\s*true", "सकारात्मक संकेत", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"supported\s*=\s*false", "मिश्रित संकेत", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bengine output\b", "विश्लेषण", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bEngine remedy\b", "उपाय", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bEngine उपाय\b", "उपाय", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bvedic\b", "वैदिक", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def format_confidence(value: float | int | None) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and value <= 1.0:
        return f"{int(round(value * 100))}%"
    return f"{int(value)}%"


def format_iso_date(value: str | None, *, language: ReportLanguage) -> str:
    if not value:
        return "—"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value.split("T")[0] if "T" in value else value
    if language == ReportLanguage.ENGLISH:
        return parsed.strftime("%d %B %Y")
    return parsed.strftime("%d/%m/%Y")


def format_planet_position_line(planet: dict[str, Any], *, language: ReportLanguage) -> str:
    sign = planet.get("sign") or "—"
    house = planet.get("house") or "—"
    nakshatra = planet.get("nakshatra") or "—"
    pada = planet.get("pada") or "—"
    degree = planet.get("degree_in_sign")
    degree_text = f"{float(degree):.1f}°" if degree is not None else "—"
    retro = planet.get("is_retrograde")
    retro_hi = " (वक्री)" if retro else ""
    retro_en = " (retrograde)" if retro else ""
    if language == ReportLanguage.ENGLISH:
        return (
            f"{planet.get('name')}: {sign} at {degree_text}, house {house}, "
            f"{nakshatra} pada {pada}{retro_en}"
        )
    return (
        f"{planet.get('name')}: {sign} {degree_text}, भाव {house}, "
        f"{nakshatra} की {pada}वीं पada{retro_hi}"
    )


def format_planet_interpretation(
    planet: dict[str, Any],
    observations: list[str],
    *,
    language: ReportLanguage,
) -> str:
    base = format_planet_position_line(planet, language=language)
    if not observations:
        suffix = "इस ग्रह के लिए कोई अतिरिक्त विशेष टिप्पणी उपलब्ध नहीं है।"
        if language == ReportLanguage.ENGLISH:
            suffix = "No additional specific notes are available for this planet."
        return scrub_client_text(f"{base} {suffix}")
    joined = " ".join(observations[:2])
    if language == ReportLanguage.ENGLISH:
        return scrub_client_text(f"{base} Key influence: {joined}")
    return scrub_client_text(f"{base} प्रमुख प्रभाव: {joined}")


def format_kp_analysis(unified_report: dict[str, Any], *, language: ReportLanguage) -> str:
    events = (unified_report.get("kp_analysis") or {}).get("events") or []
    lines: list[str] = []
    for event in events[:5]:
        event_type = event.get("event_type") or event.get("name")
        if not event_type:
            continue
        if event.get("is_supported") is True:
            line_hi = f"{event_type}: KP विश्लेषण में यह क्षेत्र सकारात्मक संकेत दिखाता है।"
            line_en = f"{event_type}: KP analysis indicates supportive indications for this area."
        elif event.get("is_supported") is False:
            line_hi = f"{event_type}: KP विश्लेषण में यह क्षेत्र मिश्रित या कमजोर संकेत दिखाता है।"
            line_en = f"{event_type}: KP analysis indicates mixed or weak indications for this area."
        else:
            line_hi = f"{event_type}: KP विश्लेषण उपलब्ध है।"
            line_en = f"{event_type}: KP analysis is available."
        lines.append(line_hi if language != ReportLanguage.ENGLISH else line_en)
    if not lines:
        return scrub_client_text(
            "KP विश्लेषण उपलब्ध नहीं है।"
            if language != ReportLanguage.ENGLISH
            else "KP analysis is not available."
        )
    return scrub_client_text("\n".join(lines))


def format_lal_kitab_analysis(unified_report: dict[str, Any], *, language: ReportLanguage) -> str:
    lal = unified_report.get("lal_kitab") or {}
    lal_intel = unified_report.get("lal_kitab_intelligence") or {}
    lines: list[str] = []

    for finding in (lal.get("dosh_findings") or [])[:3]:
        name = finding.get("finding_name") or finding.get("name")
        if not name:
            continue
        if language == ReportLanguage.ENGLISH:
            lines.append(f"Lal Kitab note: {name}. Remedial attention is advised where applicable.")
        else:
            lines.append(f"लाल किताब संकेत: {name}। आवश्यकता होने पर उपाय अपनाएँ।")

    for remedy in (lal_intel.get("remedies") or lal.get("remedies") or [])[:3]:
        title = remedy.get("title") or remedy.get("remedy") or remedy.get("name")
        if title:
            if language == ReportLanguage.ENGLISH:
                lines.append(f"Suggested Lal Kitab remedy: {title}")
            else:
                lines.append(f"सुझावित लाल किताब उपाय: {title}")

    if not lines:
        return scrub_client_text(
            "लाल किताब से कोई विशेष उपाय या व्याख्या उपलब्ध नहीं है।"
            if language != ReportLanguage.ENGLISH
            else "No Lal Kitab interpretation or remedy is available."
        )
    return scrub_client_text("\n".join(lines))


def format_dasha_narrative(facts: dict[str, Any], *, language: ReportLanguage) -> str:
    md = facts.get("current_mahadasha") or "—"
    ad = facts.get("current_antardasha") or "—"
    balance = facts.get("balance_lord") or "—"
    md_start = format_iso_date(facts.get("current_mahadasha_start"), language=language)
    md_end = format_iso_date(facts.get("current_mahadasha_end"), language=language)
    ad_start = format_iso_date(facts.get("current_antardasha_start"), language=language)
    ad_end = format_iso_date(facts.get("current_antardasha_end"), language=language)
    if language == ReportLanguage.ENGLISH:
        return scrub_client_text(
            f"You are currently running {md} mahadasha ({md_start} to {md_end}) "
            f"with {ad} antardasha active from {ad_start} to {ad_end}. "
            f"The birth dasha balance began with {balance}."
        )
    return scrub_client_text(
        f"वर्तमान समय में {md} की महादशा ({md_start} से {md_end}) चल रही है। "
        f"इसी अवधि में {ad} की अंतर्दशा {ad_start} से {ad_end} तक सक्रिय है। "
        f"जन्म के समय शेष दशा {balance} की थी।"
    )


def normalize_client_facts(facts: Any) -> list[str]:
    """Coerce any facts payload into a client-safe string array."""
    if facts is None:
        return []
    if isinstance(facts, str):
        stripped = facts.strip()
        return [stripped] if stripped else []
    if isinstance(facts, list):
        return [str(item) for item in facts if item is not None and str(item).strip()]
    if isinstance(facts, dict):
        return [str(value) for value in facts.values() if value is not None and str(value).strip()]
    text = str(facts).strip()
    return [text] if text else []


def format_section_facts(
    section_id: str,
    facts: Any,
    *,
    language: ReportLanguage,
) -> list[str]:
    """Convert structured facts into client-safe display lines."""
    if facts is None:
        return []
    if isinstance(facts, str):
        return normalize_client_facts(facts)
    if isinstance(facts, list):
        return normalize_client_facts(facts)
    if not isinstance(facts, dict) or not facts:
        return normalize_client_facts(facts)

    if section_id == "birth_details":
        labels_hi = {
            "birth_place": "जन्म स्थान",
            "date_of_birth": "जन्म तिथि",
            "birth_time": "जन्म समय",
            "timezone": "समय क्षेत्र",
            "latitude": "अक्षांश",
            "longitude": "देशांतर",
            "problem_text": "प्रश्न",
        }
        lines = []
        for key, label in labels_hi.items():
            value = facts.get(key)
            if value:
                lines.append(f"{label}: {value}")
        return lines

    if section_id == "planetary_positions":
        return [format_planet_position_line(planet, language=language) for planet in facts.get("planets", [])]

    if section_id == "planet_wise_interpretation":
        formatted = []
        for planet in facts.get("planets", []):
            formatted.append(
                format_planet_interpretation(
                    planet,
                    planet.get("observation_summary") or [],
                    language=language,
                )
            )
        return formatted

    if section_id == "house_wise_interpretation":
        lines = []
        for house in facts.get("houses", []):
            occupants = ", ".join(house.get("occupants") or []) or "—"
            summary = house.get("summary") or "—"
            if language == ReportLanguage.ENGLISH:
                lines.append(
                    f"House {house.get('house')} ({house.get('sign')}): {occupants}. {summary}"
                )
            else:
                lines.append(
                    f"भाव {house.get('house')} ({house.get('sign')}): ग्रह {occupants}। {summary}"
                )
        return lines

    if section_id == "yoga_analysis":
        return [
            f"{item.get('name')}: {item.get('meaning')}"
            for item in facts.get("yogas", [])
            if item.get("name")
        ]

    if section_id == "current_dasha":
        return [format_dasha_narrative(facts, language=language)]

    if section_id == "personalized_remedies":
        return [f"{item.get('priority')}: {item.get('title')}" for item in facts.get("remedies", []) if item.get("title")]

    if section_id == "strengths":
        return [str(item.get("text")) for item in facts.get("items", []) if item.get("text")]

    if section_id == "challenges":
        return [str(item.get("text")) for item in facts.get("items", []) if item.get("text")]

    if section_id == "final_summary":
        return [
            line
            for line in [
                facts.get("executive_summary"),
                facts.get("chart_summary"),
            ]
            if line
        ]

    if section_id == "problem_analysis":
        lines = []
        if facts.get("problem_text"):
            lines.append(f"प्रश्न: {facts['problem_text']}")
        if facts.get("category"):
            lines.append(f"श्रेणी: {facts['category']}")
        if facts.get("severity"):
            lines.append(f"गंभीरता: {facts['severity']}")
        lines.extend(facts.get("root_cause_summaries") or [])
        return lines

    generic_lines = []
    for key, value in facts.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            if value not in (None, ""):
                generic_lines.append(f"{key}: {value}")
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            generic_lines.extend(value)
    return generic_lines


def clean_remedy_items(remedies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for remedy in remedies[:10]:
        cleaned.append(
            {
                "title": remedy.get("title") or remedy.get("name") or "Remedy",
                "description": scrub_client_text(
                    str(remedy.get("description") or remedy.get("summary") or "")
                ),
                "priority": remedy.get("priority", 3),
            }
        )
    return cleaned
