"""Delivery layer: overlay Master Consultation narratives onto client reports."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from backend.app.services.consultation_brain.models import ConsultationBrainOutput
from backend.app.services.consultation_brain import ConsultationBrain, ConsultationInput, MasterConsultationEngine
from backend.app.services.consultation_brain.master_consultation_models import (
    MASTER_CONSULTATION_SECTION_ORDER,
    MasterConsultation,
    MasterConsultationSectionId,
)
from backend.app.services.report_engine.human_astrologer_rewrite_engine import HumanAstrologerRewriteEngine
from backend.app.services.report_engine.human_astrologer_rewrite_models import DELIVERY_MODE as HUMAN_REWRITE_MODE
from backend.app.services.report_engine.presentation import scrub_client_text
from backend.app.services.report_engine.types import (
    ProfessionalReportInput,
    ProfessionalReportResult,
    ReportLanguage,
    ReportSection,
)

DELIVERY_MODE = "master_consultation_v1"


@dataclass(frozen=True)
class MasterSourceSpec:
    section_id: MasterConsultationSectionId
    part: int = 0
    parts: int = 1


REPORT_SECTION_MASTER_SOURCES: dict[str, tuple[MasterSourceSpec, ...]] = {
    "birth_details": (MasterSourceSpec(MasterConsultationSectionId.GREETING),),
    "planetary_positions": (
        MasterSourceSpec(MasterConsultationSectionId.UNDERSTANDING_PROBLEM, 0, 2),
    ),
    "ascendant_analysis": (
        MasterSourceSpec(MasterConsultationSectionId.UNDERSTANDING_PROBLEM, 1, 2),
    ),
    "moon_analysis": (MasterSourceSpec(MasterConsultationSectionId.CURRENT_SITUATION, 0, 2),),
    "planet_wise_interpretation": (
        MasterSourceSpec(MasterConsultationSectionId.WHY_PROBLEM_EXISTS, 0, 2),
    ),
    "house_wise_interpretation": (
        MasterSourceSpec(MasterConsultationSectionId.WHY_PROBLEM_EXISTS, 1, 2),
    ),
    "yoga_analysis": (MasterSourceSpec(MasterConsultationSectionId.POSITIVE_FACTORS),),
    "current_dasha": (MasterSourceSpec(MasterConsultationSectionId.CURRENT_SITUATION, 1, 2),),
    "transit_analysis": (MasterSourceSpec(MasterConsultationSectionId.FUTURE_OUTLOOK, 0, 2),),
    "problem_analysis": (
        MasterSourceSpec(MasterConsultationSectionId.UNDERSTANDING_PROBLEM),
        MasterSourceSpec(MasterConsultationSectionId.WHY_PROBLEM_EXISTS),
    ),
    "personalized_remedies": (
        MasterSourceSpec(MasterConsultationSectionId.REMEDIES),
        MasterSourceSpec(MasterConsultationSectionId.PRACTICAL_ADVICE),
    ),
    "strengths": (MasterSourceSpec(MasterConsultationSectionId.POSITIVE_FACTORS, 0, 2),),
    "challenges": (MasterSourceSpec(MasterConsultationSectionId.NEGATIVE_FACTORS),),
    "final_summary": (
        MasterSourceSpec(MasterConsultationSectionId.FUTURE_OUTLOOK, 1, 2),
        MasterSourceSpec(MasterConsultationSectionId.FINAL_BLESSING),
    ),
}

CLIENT_SCRUB_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"supported\s*=\s*(true|false)", re.IGNORECASE),
    re.compile(r"category=[\w_]+\|[^|]*", re.IGNORECASE),
    re.compile(r"reason=[^\s|]+", re.IGNORECASE),
    re.compile(r"\bevidence_id\b", re.IGNORECASE),
    re.compile(r"\bfusion_id\b", re.IGNORECASE),
    re.compile(r"\bprofessional_report_engine\b", re.IGNORECASE),
    re.compile(r"\bengine output\b", re.IGNORECASE),
    re.compile(r"\(विश्वास\s*\d+%\)", re.IGNORECASE),
    re.compile(r"\(confidence\s*\d+%\)", re.IGNORECASE),
    re.compile(r"\(priority\s*\d+,\s*confidence\s*\d+%\)", re.IGNORECASE),
    re.compile(r"priority\s*\d+,\s*confidence\s*\d+%", re.IGNORECASE),
    re.compile(r"\bSun in \w+", re.IGNORECASE),
    re.compile(r"\bVenus Combust\b", re.IGNORECASE),
    re.compile(r"\bRaj Yoga\b", re.IGNORECASE),
    re.compile(r"\bHouse \d+\b", re.IGNORECASE),
    re.compile(r"\bExecutive Summary\b", re.IGNORECASE),
    re.compile(r"\bTimeline\s*:", re.IGNORECASE),
    re.compile(r"\bRoot cause\s*:", re.IGNORECASE),
    re.compile(r"\bCurrent\s*:", re.IGNORECASE),
    re.compile(r"\bKP\b", re.IGNORECASE),
    re.compile(r"\bFusion\b", re.IGNORECASE),
    re.compile(r"\bconflict count\b", re.IGNORECASE),
)

CONSULTATION_TAB_HINDI_TITLES: dict[MasterConsultationSectionId, str] = {
    MasterConsultationSectionId.GREETING: "अभिवादन",
    MasterConsultationSectionId.UNDERSTANDING_PROBLEM: "आपकी समस्या को समझना",
    MasterConsultationSectionId.WHY_PROBLEM_EXISTS: "यह समस्या क्यों है",
    MasterConsultationSectionId.CURRENT_SITUATION: "वर्तमान स्थिति",
    MasterConsultationSectionId.POSITIVE_FACTORS: "सकारात्मक पक्ष",
    MasterConsultationSectionId.NEGATIVE_FACTORS: "चुनौतियाँ",
    MasterConsultationSectionId.FUTURE_OUTLOOK: "भविष्य की दिशा",
    MasterConsultationSectionId.REMEDIES: "उपाय",
    MasterConsultationSectionId.PRACTICAL_ADVICE: "व्यवहारिक सलाह",
    MasterConsultationSectionId.FINAL_BLESSING: "अंतिम संदेश",
}

TECHNICAL_CONSULTATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"confidence\s*0?\.\d+", re.IGNORECASE),
    re.compile(r"planets\s*:", re.IGNORECASE),
    re.compile(r"houses\s*:", re.IGNORECASE),
    re.compile(r"conflict type\s*:", re.IGNORECASE),
    re.compile(r"weighted resolution", re.IGNORECASE),
    re.compile(r"support score", re.IGNORECASE),
    re.compile(r"priority score", re.IGNORECASE),
    re.compile(r"urgency\s*0?\.\d+", re.IGNORECASE),
    re.compile(r"antardasha lord is", re.IGNORECASE),
    re.compile(r"lal kitab", re.IGNORECASE),
    re.compile(r"intelligence confidence", re.IGNORECASE),
    re.compile(r"executive summary", re.IGNORECASE),
    re.compile(r"root cause\s*:", re.IGNORECASE),
    re.compile(r"timeline\s*:", re.IGNORECASE),
)

CONSULTATION_SECTION_FALLBACKS: dict[MasterConsultationSectionId, str] = {
    MasterConsultationSectionId.GREETING: "नमस्ते। आपका हार्दिक स्वागत है। मैं आपकी कुंडली को ध्यान से देखकर आपसे सीधे बात कर रहा हूँ।",
    MasterConsultationSectionId.UNDERSTANDING_PROBLEM: "आपकी चिंता को मैंने गहराई से समझा है और नीचे उसे सरल शब्दों में समझा रहा हूँ।",
    MasterConsultationSectionId.WHY_PROBLEM_EXISTS: "कुंडली में कुछ संयोग ऐसे हैं जिनसे यह स्थिति धीरे-धीरे बनती दिखती है।",
    MasterConsultationSectionId.CURRENT_SITUATION: "अभी का समय आपको धैर्य और सजग निर्णय की ओर मार्गदर्शन कर रहा है।",
    MasterConsultationSectionId.POSITIVE_FACTORS: "आपकी कुंडली में कई सकारात्मक संकेत भी मौजूद हैं जो सहारा देते हैं।",
    MasterConsultationSectionId.NEGATIVE_FACTORS: "कुछ संकेत सावधानी और संयम की ओर इशारा करते हैं, परंतु इन पर नियंत्रण संभव है।",
    MasterConsultationSectionId.FUTURE_OUTLOOK: "आने वाले समय में परिस्थितियाँ धीरे-धीरे अनुकूल होती दिखाई देती हैं।",
    MasterConsultationSectionId.REMEDIES: "साधारण, नियमित और सकारात्मक उपायों से मन को स्थिरता मिल सकती है।",
    MasterConsultationSectionId.PRACTICAL_ADVICE: "रोज़मर्रा की छोटी आदतें, संयम और सकारात्मक दृष्टिकोण बड़ा बदलाव ला सकते हैं।",
    MasterConsultationSectionId.FINAL_BLESSING: "ईश्वर आपको सही दिशा, धैर्य और शांति प्रदान करें। आप अकेले नहीं हैं।",
}


def report_language_to_master_code(language: ReportLanguage) -> str:
    return language.value


def serialize_master_consultation_for_client(
    master: MasterConsultation,
    *,
    language: str = "hi",
    brain_output: ConsultationBrainOutput | None = None,
    problem_text: str | None = None,
) -> dict[str, Any]:
    """Serialize consultation for the Consultation tab."""
    if brain_output is not None:
        return HumanAstrologerRewriteEngine().rewrite_to_client_dict(
            brain_output,
            problem_text=problem_text,
            language=language or "hi",
        )
    resolved_language = language or "hi"
    sections: list[dict[str, Any]] = []
    for section_id in MASTER_CONSULTATION_SECTION_ORDER:
        paragraphs = _master_paragraphs(master, section_id)
        cleaned_paragraphs = [polish_consultation_paragraph(paragraph) for paragraph in paragraphs]
        cleaned_paragraphs = [paragraph for paragraph in cleaned_paragraphs if paragraph]
        if not cleaned_paragraphs:
            cleaned_paragraphs = [CONSULTATION_SECTION_FALLBACKS[section_id]]
        title = CONSULTATION_TAB_HINDI_TITLES.get(section_id, section_id.value)
        if resolved_language != "hi":
            for section in master.sections:
                if section.section_id == section_id:
                    title = section.title
                    break
        sections.append(
            {
                "section_id": section_id.value,
                "title": title,
                "paragraphs": cleaned_paragraphs,
                "body": "\n\n".join(cleaned_paragraphs),
            }
        )
    return {
        "language": resolved_language,
        "sections": sections,
    }


def attach_master_consultation_to_client_report(
    client_report: dict[str, Any],
    master: MasterConsultation,
    *,
    brain_output: ConsultationBrainOutput,
    problem_text: str | None = None,
    language: str = "hi",
) -> None:
    """Persist human astrologer consultation alongside delivered client report JSON."""
    client_report["master_consultation"] = serialize_master_consultation_for_client(
        master,
        language=language,
        brain_output=brain_output,
        problem_text=problem_text,
    )


def resolve_master_consultation_payload(
    *,
    unified_report: Mapping[str, Any],
    client_report: Mapping[str, Any],
    problem_text: str | None,
    language: str = "hi",
) -> dict[str, Any]:
    """Return stored master consultation or regenerate it for older reports."""
    existing = client_report.get("master_consultation")
    if isinstance(existing, dict) and existing.get("sections"):
        if existing.get("delivery_mode") == HUMAN_REWRITE_MODE:
            return dict(existing)
        return polish_master_consultation_payload(existing, language=language)
    brain_output = ConsultationBrain().run(
        ConsultationInput(
            unified_report=dict(unified_report),
            professional_report=None,
            problem_text=problem_text,
            language=language,
        )
    )
    master = MasterConsultationEngine().generate(
        brain_output,
        None,
        dict(unified_report),
        language=language,
        problem_text=problem_text,
    )
    return HumanAstrologerRewriteEngine().rewrite_to_client_dict(
        brain_output,
        problem_text=problem_text,
        language=language,
    )


def _master_paragraphs(
    master: MasterConsultation,
    section_id: MasterConsultationSectionId,
) -> tuple[str, ...]:
    for section in master.sections:
        if section.section_id == section_id:
            return section.paragraphs
    return ()


def apply_master_consultation_delivery(
    result: ProfessionalReportResult,
    master: MasterConsultation,
    *,
    report_input: ProfessionalReportInput,
) -> ProfessionalReportResult:
    """Replace client-facing narratives with master consultation prose."""
    del report_input
    technical_facts: dict[str, Any] = {}
    delivered_sections: list[ReportSection] = []

    for section in result.sections:
        technical_facts[section.section_id] = section.facts
        sources = REPORT_SECTION_MASTER_SOURCES.get(section.section_id, ())
        narrative = deliverable_narrative(master, sources)
        if not narrative:
            narrative = scrub_deliverable_text(section.narrative)
        delivered_sections.append(
            ReportSection(
                section_id=section.section_id,
                title=section.title,
                narrative=narrative,
                facts={"client_summary": client_summary_bullets(narrative)},
                confidence=section.confidence,
            )
        )

    return ProfessionalReportResult(
        sections=tuple(delivered_sections),
        language=result.language,
        overall_confidence=result.overall_confidence,
        delivery_metadata={
            "delivery_mode": DELIVERY_MODE,
            "master_consultation_language": master.language.value,
            "technical_facts": technical_facts,
        },
    )


def deliverable_narrative(
    master: MasterConsultation,
    sources: Sequence[MasterSourceSpec],
) -> str:
    blocks: list[str] = []
    seen: set[str] = set()
    for source in sources:
        body = scrub_deliverable_text(_master_body_slice(master, source))
        if body and body not in seen:
            seen.add(body)
            blocks.append(body)
    return "\n\n".join(blocks)


def build_delivered_client_report(
    report_input: ProfessionalReportInput,
    *,
    builder: Any | None = None,
) -> dict[str, Any]:
    """Run brain, master consultation, professional report, and delivery overlay."""
    from backend.app.services.report_engine.report_builder import ProfessionalReportBuilder
    from backend.app.services.report_engine.serializers import professional_report_to_client_json

    builder = builder or ProfessionalReportBuilder()
    brain_output = report_input.consultation_brain_output
    if brain_output is None:
        brain_output = ConsultationBrain().run(
            ConsultationInput(
                unified_report=report_input.unified_report,
                professional_report=None,
                problem_text=report_input.problem_text,
                language=report_input.language.value,
            )
        )
    master = report_input.master_consultation
    if master is None:
        master = MasterConsultationEngine().generate(
            brain_output,
            None,
            report_input.unified_report,
            language=report_language_to_master_code(report_input.language),
            problem_text=report_input.problem_text,
        )
    enriched_input = ProfessionalReportInput(
        unified_report=report_input.unified_report,
        remedy_generation=report_input.remedy_generation,
        problem_text=report_input.problem_text,
        language=report_input.language,
        consultation_brain_output=brain_output,
        master_consultation=master,
    )
    result = builder.build(enriched_input)
    result = apply_master_consultation_delivery(
        result,
        master,
        report_input=enriched_input,
    )
    payload = professional_report_to_client_json(result, report_input=enriched_input)
    attach_master_consultation_to_client_report(
        payload,
        master,
        brain_output=brain_output,
        problem_text=report_input.problem_text,
        language=report_language_to_master_code(report_input.language),
    )
    return payload


def master_consultation_remedies(master: MasterConsultation) -> list[dict[str, Any]]:
    """Build deduplicated legacy remedy entries from master consultation."""
    remedies: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    remedy_text = deliverable_narrative(
        master,
        (
            MasterSourceSpec(MasterConsultationSectionId.REMEDIES),
            MasterSourceSpec(MasterConsultationSectionId.PRACTICAL_ADVICE),
        ),
    )
    for index, paragraph in enumerate(remedy_text.split("\n\n"), start=1):
        cleaned = scrub_deliverable_text(paragraph)
        if not cleaned:
            continue
        title = _remedy_title(cleaned)
        if title in seen_titles:
            continue
        seen_titles.add(title)
        remedies.append(
            {
                "title": title,
                "description": cleaned,
                "priority": min(index, 3),
            }
        )
    return remedies[:8]


def master_legacy_analysis(master: MasterConsultation, *, kind: str) -> str:
    if kind == "kp":
        return deliverable_narrative(
            master,
            (
                MasterSourceSpec(MasterConsultationSectionId.WHY_PROBLEM_EXISTS, 0, 2),
                MasterSourceSpec(MasterConsultationSectionId.CURRENT_SITUATION, 0, 2),
            ),
        )
    if kind == "lal_kitab":
        return deliverable_narrative(
            master,
            (
                MasterSourceSpec(MasterConsultationSectionId.NEGATIVE_FACTORS),
                MasterSourceSpec(MasterConsultationSectionId.REMEDIES, 0, 2),
            ),
        )
    return ""


def _master_body_slice(master: MasterConsultation, source: MasterSourceSpec) -> str:
    body = _master_body(master, source.section_id)
    if source.parts <= 1:
        return body
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", body) if item.strip()]
    if not sentences:
        return ""
    chunk_size = max(1, (len(sentences) + source.parts - 1) // source.parts)
    start = min(source.part * chunk_size, len(sentences))
    end = min(start + chunk_size, len(sentences)) if source.part < source.parts - 1 else len(sentences)
    if start >= len(sentences):
        return sentences[-1] if sentences else ""
    return " ".join(sentences[start:end])


def scrub_deliverable_text(text: str | None) -> str:
    if not text:
        return ""
    cleaned = scrub_client_text(str(text))
    cleaned = re.sub(
        r"\bVenus Combust\b",
        "शुक्र ग्रह इस समय अपनी पूरी शक्ति से कार्य नहीं कर पा रहा है",
        cleaned,
        flags=re.IGNORECASE,
    )
    for pattern in CLIENT_SCRUB_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,.;")
    return cleaned


def is_technical_consultation_paragraph(text: str) -> bool:
    return any(pattern.search(text) for pattern in TECHNICAL_CONSULTATION_PATTERNS)


def polish_consultation_paragraph(text: str | None) -> str:
    cleaned = scrub_deliverable_text(text)
    if not cleaned or is_technical_consultation_paragraph(cleaned):
        return ""
    return cleaned


def polish_master_consultation_payload(payload: Mapping[str, Any], *, language: str = "hi") -> dict[str, Any]:
    polished_sections: list[dict[str, Any]] = []
    for raw_section in payload.get("sections") or []:
        if not isinstance(raw_section, dict):
            continue
        section_id_value = str(raw_section.get("section_id") or "")
        try:
            section_id = MasterConsultationSectionId(section_id_value)
        except ValueError:
            section_id = None
        source_paragraphs = raw_section.get("paragraphs") or []
        if not source_paragraphs and raw_section.get("body"):
            source_paragraphs = str(raw_section.get("body")).split("\n\n")
        cleaned_paragraphs = [polish_consultation_paragraph(str(paragraph)) for paragraph in source_paragraphs]
        cleaned_paragraphs = [paragraph for paragraph in cleaned_paragraphs if paragraph]
        if not cleaned_paragraphs and section_id is not None:
            cleaned_paragraphs = [CONSULTATION_SECTION_FALLBACKS[section_id]]
        title = raw_section.get("title")
        if section_id is not None and (language or "hi") == "hi":
            title = CONSULTATION_TAB_HINDI_TITLES.get(section_id, title)
        polished_sections.append(
            {
                "section_id": section_id_value,
                "title": title,
                "paragraphs": cleaned_paragraphs,
                "body": "\n\n".join(cleaned_paragraphs),
            }
        )
    return {
        "language": language or payload.get("language") or "hi",
        "delivery_mode": payload.get("delivery_mode") or DELIVERY_MODE,
        "sections": polished_sections,
    }


def client_summary_bullets(narrative: str, *, limit: int = 4) -> list[str]:
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", narrative) if item.strip()]
    return sentences[:limit]


def _master_body(master: MasterConsultation, section_id: MasterConsultationSectionId) -> str:
    for section in master.sections:
        if section.section_id == section_id:
            return section.body_text
    return ""


def _remedy_title(paragraph: str) -> str:
    if ":" in paragraph:
        return paragraph.split(":", 1)[0].strip()[:80]
    if " — " in paragraph:
        return paragraph.split(" — ", 1)[0].strip()[:80]
    return paragraph[:80]
