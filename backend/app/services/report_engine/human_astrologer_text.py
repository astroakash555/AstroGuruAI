"""Human-language scrubbing and astrological phrase rewriting for client delivery."""

from __future__ import annotations

import re

from backend.app.services.report_engine.presentation import scrub_client_text

PLANET_HINDI: dict[str, str] = {
    "Sun": "सूर्य",
    "Moon": "चंद्र",
    "Mars": "मंगल",
    "Mercury": "बुध",
    "Jupiter": "गुरु",
    "Venus": "शुक्र",
    "Saturn": "शनि",
    "Rahu": "राहु",
    "Ketu": "केतु",
}

HOUSE_LIFE_AREA: dict[int, str] = {
    1: "व्यक्तित्व और स्वभाव",
    2: "धन और परिवार",
    3: "साहस और संचार",
    4: "घर और मानसिक शांति",
    5: "संतान और रचनात्मकता",
    6: "सेवा और स्वास्थ्य",
    7: "विवाह और साझेदारी",
    8: "परिवर्तन और गहन अनुभव",
    9: "भाग्य और धर्म",
    10: "करियर और सम्मान",
    11: "लाभ और सामाजिक संबंध",
    12: "विदेश, खर्च और मोक्ष",
}

DOMAIN_HINDI: dict[str, str] = {
    "relationship": "संबंध",
    "marriage": "विवाह",
    "career": "करियर",
    "finance": "वित्त",
    "health": "स्वास्थ्य",
    "spiritual": "आध्यात्म",
    "general": "सामान्य",
    "timing": "समय",
    "remedy": "उपाय",
}

CATEGORY_CONTEXT_HINDI: dict[str, str] = {
    "relationship": "संबंधों के संदर्भ में",
    "marriage": "विवाह के संदर्भ में",
    "career": "करियर के संदर्भ में",
    "finance": "धन और स्थिरता के संदर्भ में",
    "health": "स्वास्थ्य के संदर्भ में",
    "spiritual": "आध्यात्मिक दृष्टि से",
    "general": "कुंडली के समग्र संकेतों में",
    "timing": "समय के संकेतों में",
    "remedy": "उपाय के रूप में",
}

TECHNICAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"supported\s*=\s*(true|false)", re.IGNORECASE),
    re.compile(r"is_supported", re.IGNORECASE),
    re.compile(r"category=[\w_]+\|[^|]*", re.IGNORECASE),
    re.compile(r"reason=[^\s|]+", re.IGNORECASE),
    re.compile(r"\bevidence_id\b", re.IGNORECASE),
    re.compile(r"\bfusion_id\b", re.IGNORECASE),
    re.compile(r"\brule_id\b", re.IGNORECASE),
    re.compile(r"\b[\w]+_rule\b", re.IGNORECASE),
    re.compile(r"\b[\w]+_id\b", re.IGNORECASE),
    re.compile(r"\bprofessional_report_engine\b", re.IGNORECASE),
    re.compile(r"\bengine output\b", re.IGNORECASE),
    re.compile(r"\bconsultation_brain\b", re.IGNORECASE),
    re.compile(r"\(विश्वास\s*\d+%\)", re.IGNORECASE),
    re.compile(r"\(confidence\s*\d+%\)", re.IGNORECASE),
    re.compile(r"\(priority\s*\d+,\s*confidence\s*\d+%\)", re.IGNORECASE),
    re.compile(r"priority\s*\d+,\s*confidence\s*\d+%", re.IGNORECASE),
    re.compile(r"confidence\s*0?\.\d+", re.IGNORECASE),
    re.compile(r"support score\s*0?\.\d+", re.IGNORECASE),
    re.compile(r"priority score\s*0?\.\d+", re.IGNORECASE),
    re.compile(r"urgency\s*0?\.\d+", re.IGNORECASE),
    re.compile(r"match score\s*0?\.\d+", re.IGNORECASE),
    re.compile(r"similarity\s*0?\.\d+", re.IGNORECASE),
    re.compile(r"strength\s*0?\.\d+", re.IGNORECASE),
    re.compile(r"\b\d+%\b"),
    re.compile(r"planets\s*:", re.IGNORECASE),
    re.compile(r"houses\s*:", re.IGNORECASE),
    re.compile(r"conflict type\s*:", re.IGNORECASE),
    re.compile(r"weighted resolution", re.IGNORECASE),
    re.compile(r"\bSun in \w+", re.IGNORECASE),
    re.compile(r"\bRaj Yoga\b", re.IGNORECASE),
    re.compile(r"\bGaj[a]?\s*Kesari\b", re.IGNORECASE),
    re.compile(r"\bHouse \d+\b", re.IGNORECASE),
    re.compile(r"\bExecutive Summary\b", re.IGNORECASE),
    re.compile(r"\bTimeline\s*:", re.IGNORECASE),
    re.compile(r"\bRoot cause\s*:", re.IGNORECASE),
    re.compile(r"\bCurrent\s*:", re.IGNORECASE),
    re.compile(r"\bKP\b", re.IGNORECASE),
    re.compile(r"\bCuspal\b", re.IGNORECASE),
    re.compile(r"\bSignificator\b", re.IGNORECASE),
    re.compile(r"\bFusion\b", re.IGNORECASE),
    re.compile(r"\bLal Kitab\b", re.IGNORECASE),
    re.compile(r"\bRule Studio\b", re.IGNORECASE),
    re.compile(r"strength assessment", re.IGNORECASE),
    re.compile(r"intelligence confidence", re.IGNORECASE),
    re.compile(r"antardasha lord is", re.IGNORECASE),
    re.compile(r"mahadasha lord is", re.IGNORECASE),
    re.compile(r"\b\d+(?:st|nd|rd|th)\s+house\b", re.IGNORECASE),
    re.compile(r"\bafflict(?:ed|ion)\b", re.IGNORECASE),
    re.compile(r"\bbenchmark\b", re.IGNORECASE),
    re.compile(r"\bpattern_id\b", re.IGNORECASE),
    re.compile(r"\bdosh finding\b", re.IGNORECASE),
    re.compile(r"house from lagna", re.IGNORECASE),
    re.compile(r"current house from lagna", re.IGNORECASE),
    re.compile(r"consultation brain foundation", re.IGNORECASE),
    re.compile(r"evidence placeholders collected", re.IGNORECASE),
    re.compile(r"future phase", re.IGNORECASE),
    re.compile(r"intelligence root cause", re.IGNORECASE),
    re.compile(r"general guidance", re.IGNORECASE),
    re.compile(r"\blegacy\b", re.IGNORECASE),
)

SNAKE_CASE_PATTERN = re.compile(r"\b[a-z]+(?:_[a-z]+)+\b")


def humanize_astrology_text(text: str | None) -> str:
    if not text:
        return ""
    cleaned = scrub_client_text(str(text))
    cleaned = re.sub(
        r"\bVenus Combust\b",
        "शुक्र ग्रह इस समय अपनी पूरी शक्ति से कार्य नहीं कर पा रहा है",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\bMars Combust\b",
        "मंगल ग्रह की ऊर्जा इस समय संतुलित रूप से प्रकट नहीं हो रही है",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = SNAKE_CASE_PATTERN.sub(lambda match: match.group(0).replace("_", " "), cleaned)
    for english, hindi in PLANET_HINDI.items():
        cleaned = re.sub(rf"\b{english}\b", hindi, cleaned, flags=re.IGNORECASE)

    def _replace_house(match: re.Match[str]) -> str:
        number = int(match.group(1))
        return HOUSE_LIFE_AREA.get(number, "जीवन के उस क्षेत्र")

    cleaned = re.sub(r"\b(?:house|bhava)\s*(\d{1,2})\b", _replace_house, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(\d{1,2})(?:th|st|nd|rd)\s+house\b", _replace_house, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(\d{1,2})\s*वें?\s*भाव\b", _replace_house, cleaned, flags=re.IGNORECASE)

    for pattern in TECHNICAL_PATTERNS:
        cleaned = pattern.sub("", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,.;:-")
    return cleaned


def humanize_domain(domain: str | None) -> str:
    if not domain:
        return "आपकी चिंता"
    normalized = domain.strip().lower().replace("-", "_")
    return DOMAIN_HINDI.get(normalized, humanize_astrology_text(domain.replace("_", " ")) or "आपकी चिंता")


def rewrite_evidence_for_client(*, title: str, summary: str, category: str) -> str:
    raw = humanize_astrology_text(summary or title)
    if raw and not is_technical_paragraph(raw):
        return raw
    context = CATEGORY_CONTEXT_HINDI.get(category.lower(), "कुंडली में")
    title_clean = humanize_astrology_text(title)
    if title_clean and not is_technical_paragraph(title_clean):
        return f"{context} {title_clean} एक महत्वपूर्ण संकेत देता है।"
    return f"{context} स्थिति को समझने वाला एक संकेत है, जिस पर धैर्य और सही कदमों से काम किया जा सकता है।"


def polish_remedy_item(item: dict[str, object]) -> dict[str, object]:
    title = humanize_astrology_text(str(item.get("title") or item.get("name") or "उपाय"))
    description = humanize_astrology_text(str(item.get("description") or item.get("summary") or ""))
    if not title:
        title = "व्यक्तिगत उपाय"
    if not description:
        description = "यह उपाय मन को शांत रखने और सही दिशा देने में सहायक हो सकता है।"
    return {
        "title": title[:80],
        "description": description,
        "priority": item.get("priority", 2),
    }


def is_technical_paragraph(text: str) -> bool:
    if not text:
        return True
    hindi_chars = sum(1 for char in text if "\u0900" <= char <= "\u097f")
    if hindi_chars >= 24:
        return any(pattern.search(text) for pattern in TECHNICAL_PATTERNS)
    if any(pattern.search(text) for pattern in TECHNICAL_PATTERNS):
        return True
    if re.search(r"\b0\.\d+\b", text):
        return True
    lowered = text.lower()
    if SNAKE_CASE_PATTERN.search(text):
        return True
    ascii_ratio = sum(char.isascii() and char.isalpha() for char in text) / max(len(text), 1)
    technical_tokens = (
        "score",
        "signal",
        "metric",
        "engine",
        "significator",
        "cuspal",
        "benchmark",
        "observation",
        "supported",
        "placeholder",
        "foundation summary",
    )
    return ascii_ratio > 0.55 and any(token in lowered for token in technical_tokens)


def join_paragraphs(paragraphs: list[str]) -> str:
    unique: list[str] = []
    seen: set[str] = set()
    for paragraph in paragraphs:
        cleaned = humanize_astrology_text(paragraph)
        if not cleaned or is_technical_paragraph(cleaned):
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(cleaned)
    return "\n\n".join(unique)
