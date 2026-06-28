"""Master astrologer conversation engine — emotionally intelligent client consultation."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.master_consultation_i18n import (
    blessing_paragraph,
    empathy_paragraph,
    empty_section_paragraph,
    greeting_paragraph,
    normalize_language,
    outlook_label,
    section_title,
)
from backend.app.services.consultation_brain.master_consultation_models import (
    MASTER_CONSULTATION_SECTION_ORDER,
    MasterConsultation,
    MasterConsultationLanguage,
    MasterConsultationSection,
    MasterConsultationSectionId,
)
from backend.app.services.consultation_brain.models import (
    ConsultationBrainOutput,
    ConsultationConflict,
    ConsultationEvidence,
    ConsultationPriority,
    ConsultationRecommendation,
)

TECHNICAL_DUMP_PATTERNS = (
    re.compile(r"\bSun in \w+", re.IGNORECASE),
    re.compile(r"\bMoon in \w+", re.IGNORECASE),
    re.compile(r"\bVenus Combust\b", re.IGNORECASE),
    re.compile(r"\bRaj Yoga\b", re.IGNORECASE),
    re.compile(r"\bHouse \d+\b", re.IGNORECASE),
    re.compile(r"category=[\w_]+\|", re.IGNORECASE),
)
STRUCTURED_REASON_PATTERN = re.compile(
    r"category=[\w_]+\|domain=[\w_]+\|",
    re.IGNORECASE,
)
WHITESPACE_PATTERN = re.compile(r"\s+")


class MasterConsultationEngine:
    """Transforms consultation brain intelligence into a warm master consultation."""

    def generate(
        self,
        brain_output: ConsultationBrainOutput,
        professional_report: Mapping[str, Any] | None,
        unified_report: Mapping[str, Any],
        *,
        language: str = "hi",
        problem_text: str | None = None,
    ) -> MasterConsultation:
        resolved_language = normalize_language(language)
        concern = _resolve_problem_text(problem_text, unified_report, professional_report)
        composer = _ConsultationComposer(
            brain_output=brain_output,
            professional_report=professional_report,
            unified_report=unified_report,
            language=resolved_language,
            problem_text=concern,
        )
        sections = tuple(
            MasterConsultationSection(
                section_id=section_id,
                title=section_title(section_id, resolved_language),
                paragraphs=composer.build(section_id),
            )
            for section_id in MASTER_CONSULTATION_SECTION_ORDER
        )
        return MasterConsultation(
            language=resolved_language,
            sections=sections,
            metadata={
                "section_count": len(sections),
                "evidence_count": len(brain_output.evidence),
                "priority_count": len(brain_output.priorities),
                "recommendation_count": len(brain_output.recommendations),
                "conflict_count": len(brain_output.conflicts),
                "overall_confidence": brain_output.overall_confidence,
                "problem_text": concern,
            },
        )


class _ConsultationComposer:
    """Builds consultation sections from existing evidence without repetition."""

    def __init__(
        self,
        *,
        brain_output: ConsultationBrainOutput,
        professional_report: Mapping[str, Any] | None,
        unified_report: Mapping[str, Any],
        language: MasterConsultationLanguage,
        problem_text: str | None,
    ) -> None:
        self._brain_output = brain_output
        self._professional_report = professional_report
        self._unified_report = unified_report
        self._language = language
        self._problem_text = problem_text
        self._used_evidence_ids: set[str] = set()
        self._used_phrases: set[str] = set()

    def build(self, section_id: MasterConsultationSectionId) -> tuple[str, ...]:
        builders = {
            MasterConsultationSectionId.GREETING: self._build_greeting,
            MasterConsultationSectionId.UNDERSTANDING_PROBLEM: self._build_understanding,
            MasterConsultationSectionId.WHY_PROBLEM_EXISTS: self._build_why_problem,
            MasterConsultationSectionId.CURRENT_SITUATION: self._build_current_situation,
            MasterConsultationSectionId.POSITIVE_FACTORS: self._build_positive_factors,
            MasterConsultationSectionId.NEGATIVE_FACTORS: self._build_negative_factors,
            MasterConsultationSectionId.FUTURE_OUTLOOK: self._build_future_outlook,
            MasterConsultationSectionId.REMEDIES: self._build_remedies,
            MasterConsultationSectionId.PRACTICAL_ADVICE: self._build_practical_advice,
            MasterConsultationSectionId.FINAL_BLESSING: self._build_final_blessing,
        }
        return builders[section_id]()

    def _build_greeting(self) -> tuple[str, ...]:
        return (greeting_paragraph(language=self._language, problem_text=self._problem_text),)

    def _build_understanding(self) -> tuple[str, ...]:
        paragraphs = [empathy_paragraph(language=self._language, problem_text=self._problem_text)]
        report_line = _professional_report_summary(self._professional_report)
        if report_line:
            paragraphs.append(_humanize(report_line))
        return tuple(paragraphs)

    def _build_why_problem(self) -> tuple[str, ...]:
        sentences: list[str] = []
        for source in (
            EvidenceSource.RULE_STUDIO,
            EvidenceSource.FUSION,
            EvidenceSource.YOGAS,
            EvidenceSource.DASHA,
            EvidenceSource.TRANSIT,
            EvidenceSource.KP,
            EvidenceSource.LAL_KITAB,
        ):
            sentences.extend(self._consume_evidence_by_source(source, limit=1))
        sentences.extend(self._priority_sentences(limit=2))
        sentences.extend(self._conflict_sentences(limit=1))
        if not sentences:
            return (empty_section_paragraph(section_id=MasterConsultationSectionId.WHY_PROBLEM_EXISTS, language=self._language),)
        return (_join_flowing_paragraph(sentences, language=self._language),)

    def _build_current_situation(self) -> tuple[str, ...]:
        sentences: list[str] = []
        sentences.extend(self._consume_evidence_by_source(EvidenceSource.DASHA, limit=2))
        sentences.extend(self._consume_evidence_by_source(EvidenceSource.TRANSIT, limit=2))
        sentences.extend(self._timing_lines_from_unified())
        if self._brain_output.priorities:
            top = self._brain_output.priorities[0]
            sentences.append(
                _localize(
                    self._language,
                    hi=(
                        f"आपके प्रश्न से जुड़ा सबसे सक्रिय विषय '{top.title}' है, "
                        f"जिसकी तात्कालिकता वर्तमान चरण में अधिक महसूस हो सकती है।"
                    ),
                    en=(
                        f"The most active theme linked to your concern is '{top.title}', "
                        "which may feel especially present during this phase."
                    ),
                )
            )
        if not sentences:
            return (empty_section_paragraph(section_id=MasterConsultationSectionId.CURRENT_SITUATION, language=self._language),)
        return (_join_flowing_paragraph(sentences, language=self._language),)

    def _build_positive_factors(self) -> tuple[str, ...]:
        sentences = self._collect_unused_evidence(
            predicate=lambda item: item.weight >= 0.55 or item.confidence >= 0.65,
            limit=4,
        )
        if not sentences:
            return (empty_section_paragraph(section_id=MasterConsultationSectionId.POSITIVE_FACTORS, language=self._language),)
        intro = _localize(
            self._language,
            hi="आपकी कुंडली में कुछ संकेत सहारा दे रहे हैं। ",
            en="Some signals in your chart are offering support. ",
        )
        return (intro + _join_flowing_paragraph(sentences, language=self._language),)

    def _build_negative_factors(self) -> tuple[str, ...]:
        sentences = self._conflict_sentences(limit=2)
        sentences.extend(
            self._collect_unused_evidence(
                predicate=lambda item: item.weight < 0.5 or item.confidence < 0.45,
                limit=3,
            )
        )
        if not sentences:
            return (empty_section_paragraph(section_id=MasterConsultationSectionId.NEGATIVE_FACTORS, language=self._language),)
        intro = _localize(
            self._language,
            hi="कुछ संकेत धैर्य और सावधानी मांगते हैं। ",
            en="Some signals ask for patience and careful steps. ",
        )
        return (intro + _join_flowing_paragraph(sentences, language=self._language),)

    def _build_future_outlook(self) -> tuple[str, ...]:
        paragraphs: list[str] = []
        short_lines = self._outlook_for_horizon("short")
        medium_lines = self._outlook_for_horizon("medium")
        long_lines = self._outlook_for_horizon("long")
        if short_lines:
            paragraphs.append(
                f"{outlook_label(horizon='short', language=self._language)}: "
                f"{_join_flowing_paragraph(short_lines, language=self._language)}"
            )
        if medium_lines:
            paragraphs.append(
                f"{outlook_label(horizon='medium', language=self._language)}: "
                f"{_join_flowing_paragraph(medium_lines, language=self._language)}"
            )
        if long_lines:
            paragraphs.append(
                f"{outlook_label(horizon='long', language=self._language)}: "
                f"{_join_flowing_paragraph(long_lines, language=self._language)}"
            )
        if not paragraphs:
            return (empty_section_paragraph(section_id=MasterConsultationSectionId.FUTURE_OUTLOOK, language=self._language),)
        return tuple(paragraphs)

    def _build_remedies(self) -> tuple[str, ...]:
        paragraphs: list[str] = []
        for recommendation in self._brain_output.recommendations[:6]:
            paragraph = _format_remedy_paragraph(recommendation, self._brain_output.evidence, language=self._language)
            if paragraph and paragraph not in self._used_phrases:
                self._used_phrases.add(paragraph)
                paragraphs.append(paragraph)
        if not paragraphs:
            return (empty_section_paragraph(section_id=MasterConsultationSectionId.REMEDIES, language=self._language),)
        return tuple(paragraphs)

    def _build_practical_advice(self) -> tuple[str, ...]:
        advice: list[str] = []
        for recommendation in self._brain_output.recommendations[:5]:
            if recommendation.action_items:
                label = recommendation.action_items[0].replace("_", " ")
                advice.append(
                    _localize(
                        self._language,
                        hi=f"रोज़मर्रा की ज़िंदगी में {label} पर ध्यान दें — यह व्यावहारिक और संतुलित रहेगा।",
                        en=f"In daily life, pay gentle attention to {label}; this keeps your approach balanced.",
                    )
                )
        narrative = self._narrative_paragraph("practical_guidance")
        if narrative:
            advice.insert(0, narrative)
        if not advice:
            return (empty_section_paragraph(section_id=MasterConsultationSectionId.PRACTICAL_ADVICE, language=self._language),)
        return (_join_flowing_paragraph(advice, language=self._language),)

    def _build_final_blessing(self) -> tuple[str, ...]:
        closing = self._narrative_paragraph("closing_summary")
        blessing = blessing_paragraph(language=self._language)
        if closing:
            return (closing, blessing)
        return (blessing,)

    def _consume_evidence_by_source(self, source: EvidenceSource, *, limit: int) -> list[str]:
        items = [item for item in self._brain_output.evidence if item.source == source]
        return self._sentences_from_evidence(items, limit=limit, mark_used=True)

    def _collect_unused_evidence(
        self,
        *,
        predicate,
        limit: int,
    ) -> list[str]:
        items = [item for item in self._brain_output.evidence if predicate(item)]
        return self._sentences_from_evidence(items, limit=limit, mark_used=True)

    def _sentences_from_evidence(
        self,
        items: Sequence[ConsultationEvidence],
        *,
        limit: int,
        mark_used: bool,
    ) -> list[str]:
        sentences: list[str] = []
        for item in sorted(items, key=lambda entry: (-entry.confidence, entry.evidence_id)):
            if item.evidence_id in self._used_evidence_ids:
                continue
            sentence = _evidence_sentence(item, language=self._language)
            if not sentence or sentence in self._used_phrases:
                continue
            sentences.append(sentence)
            self._used_phrases.add(sentence)
            if mark_used:
                self._used_evidence_ids.add(item.evidence_id)
            if len(sentences) >= limit:
                break
        return sentences

    def _priority_sentences(self, *, limit: int) -> list[str]:
        sentences: list[str] = []
        for priority in self._brain_output.priorities[:limit]:
            sentence = _priority_sentence(priority, language=self._language)
            if sentence and sentence not in self._used_phrases:
                sentences.append(sentence)
                self._used_phrases.add(sentence)
        return sentences

    def _conflict_sentences(self, *, limit: int) -> list[str]:
        sentences: list[str] = []
        for conflict in self._brain_output.conflicts[:limit]:
            sentence = _conflict_sentence(conflict, language=self._language)
            if sentence and sentence not in self._used_phrases:
                sentences.append(sentence)
                self._used_phrases.add(sentence)
        return sentences

    def _timing_lines_from_unified(self) -> list[str]:
        lines: list[str] = []
        dasha = self._unified_report.get("dasha") or {}
        current = dasha.get("current") or {}
        mahadasha = current.get("mahadasha") or {}
        antardasha = current.get("antardasha") or {}
        md_end = mahadasha.get("end")
        ad_end = antardasha.get("end")
        if md_end:
            lines.append(
                _localize(
                    self._language,
                    hi=f"उपलब्ध dasha संकेत के अनुसार वर्तमान महादशा अवधि { _format_date(md_end) } तक चल सकती है।",
                    en=f"According to available dasha signals, the current mahadasha phase may continue until {_format_date(md_end)}.",
                )
            )
        if ad_end:
            lines.append(
                _localize(
                    self._language,
                    hi=f"वर्तमान antardasha संकेत { _format_date(ad_end) } तक सक्रिय रह सकता है।",
                    en=f"The current antardasha signal may remain active until {_format_date(ad_end)}.",
                )
            )
        return lines

    def _outlook_for_horizon(self, horizon: str) -> list[str]:
        if horizon == "short":
            return self._consume_evidence_by_source(EvidenceSource.TRANSIT, limit=2) or self._timing_lines_from_unified()
        if horizon == "medium":
            return self._consume_evidence_by_source(EvidenceSource.DASHA, limit=2)
        return self._priority_sentences(limit=2) or self._collect_unused_evidence(
            predicate=lambda item: item.category.value in {"general", "spiritual"},
            limit=2,
        )

    def _narrative_paragraph(self, section_key: str) -> str:
        narrative = self._brain_output.narrative
        if narrative is None:
            return ""
        for section in narrative.sections:
            if section.section_id.value == section_key and section.paragraphs:
                return _humanize(section.paragraphs[0])
        return ""


def _resolve_problem_text(
    problem_text: str | None,
    unified_report: Mapping[str, Any],
    professional_report: Mapping[str, Any] | None,
) -> str | None:
    if problem_text and problem_text.strip():
        return problem_text.strip()
    problem = unified_report.get("problem_analysis") or {}
    if isinstance(problem, dict):
        text = problem.get("problem_text") or problem.get("question")
        if text:
            return str(text).strip()
    if isinstance(professional_report, dict):
        for section in professional_report.get("sections") or []:
            if isinstance(section, dict) and section.get("section_id") == "problem_analysis":
                facts = section.get("facts") or []
                if facts:
                    return str(facts[0]).strip()
    return None


def _professional_report_summary(professional_report: Mapping[str, Any] | None) -> str:
    if not isinstance(professional_report, dict):
        return ""
    for section in professional_report.get("sections") or []:
        if not isinstance(section, dict):
            continue
        facts = section.get("facts") or section.get("key_points") or []
        for fact in facts[:2]:
            text = str(fact).strip()
            if text:
                return text
        narrative = section.get("narrative")
        if narrative:
            return str(narrative).strip()
    return ""


def _evidence_sentence(item: ConsultationEvidence, *, language: MasterConsultationLanguage) -> str:
    summary = _humanize(item.summary or item.title)
    if not summary:
        return ""
    return _localize(
        language,
        hi=f"{summary} (विश्वास {int(round(item.confidence * 100))}%)",
        en=f"{summary} (confidence {int(round(item.confidence * 100))}%)",
    )


def _priority_sentence(priority: ConsultationPriority, *, language: MasterConsultationLanguage) -> str:
    rationale = _humanize(priority.rationale)
    return _localize(
        language,
        hi=f"{priority.title}: {rationale}",
        en=f"{priority.title}: {rationale}",
    )


def _conflict_sentence(conflict: ConsultationConflict, *, language: MasterConsultationLanguage) -> str:
    return _localize(
        language,
        hi=f"कुछ संकेत एक-दूसरे से भिन्न दिखे — { _humanize(conflict.description) }। समाधान: { _humanize(conflict.resolution) }।",
        en=f"Some signals appeared mixed — {_humanize(conflict.description)}. Resolution: {_humanize(conflict.resolution)}.",
    )


def _format_remedy_paragraph(
    recommendation: ConsultationRecommendation,
    evidence: Sequence[ConsultationEvidence],
    *,
    language: MasterConsultationLanguage,
) -> str:
    title = recommendation.title.replace("_", " ")
    supporting = _evidence_text_for_ids(recommendation.evidence_ids, evidence)
    reason = supporting or _localize(
        language,
        hi="उपलब्ध प्रमाणों के आधार पर यह उपाय सुझाया गया है।",
        en="This remedy is suggested based on the available supporting evidence.",
    )
    benefit = _localize(
        language,
        hi="इससे मन को स्थिरता और सही दिशा मिलने की संभावना बढ़ती है।",
        en="This may help you feel steadier and more aligned with the right direction.",
    )
    return _localize(
        language,
        hi=(
            f"{title}: {reason} {benefit} "
            f"(प्राथमिकता {recommendation.priority_rank}, विश्वास {int(round(recommendation.confidence * 100))}%)"
        ),
        en=(
            f"{title}: {reason} {benefit} "
            f"(priority {recommendation.priority_rank}, confidence {int(round(recommendation.confidence * 100))}%)"
        ),
    )


def _evidence_text_for_ids(
    evidence_ids: tuple[str, ...],
    evidence: Sequence[ConsultationEvidence],
) -> str:
    summaries: list[str] = []
    for evidence_id in evidence_ids:
        for item in evidence:
            if item.evidence_id == evidence_id:
                text = _humanize(item.summary)
                if text:
                    summaries.append(text)
                break
    return " ".join(summaries[:2])


def _humanize(text: str | None) -> str:
    if not text:
        return ""
    cleaned = str(text).strip()
    cleaned = STRUCTURED_REASON_PATTERN.sub("", cleaned)
    for pattern in TECHNICAL_DUMP_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    cleaned = WHITESPACE_PATTERN.sub(" ", cleaned).strip(" ,.;")
    return cleaned


def _join_flowing_paragraph(sentences: Sequence[str], *, language: MasterConsultationLanguage) -> str:
    unique: list[str] = []
    for sentence in sentences:
        normalized = _humanize(sentence)
        if normalized and normalized not in unique:
            unique.append(normalized)
    if not unique:
        return ""
    if language is MasterConsultationLanguage.HINDI:
        return " ".join(unique)
    return " ".join(unique)


def _localize(language: MasterConsultationLanguage, *, hi: str, en: str) -> str:
    if language is MasterConsultationLanguage.HINDI:
        return hi
    if language is MasterConsultationLanguage.HINGLISH:
        return en
    return en


def _format_date(value: Any) -> str:
    text = str(value)
    if "T" in text:
        return text.split("T")[0]
    return text
