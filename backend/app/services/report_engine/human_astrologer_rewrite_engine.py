"""Post-processing rewrite engine: Consultation Brain output → human Hindi consultation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import (
    ConsultationBrainOutput,
    ConsultationEvidence,
    ConsultationPriority,
    ConsultationRecommendation,
)
from backend.app.services.consultation_brain.narrative_models import NarrativeSectionId
from backend.app.services.report_engine.human_astrologer_rewrite_models import (
    DELIVERY_MODE,
    HUMAN_ASTROLOGER_SECTION_ORDER,
    HumanAstrologerConsultation,
    HumanAstrologerSection,
    HumanAstrologerSectionId,
)
from backend.app.services.report_engine.human_astrologer_text import (
    humanize_astrology_text,
    humanize_domain,
    is_technical_paragraph,
    join_paragraphs,
    rewrite_evidence_for_client,
)

SECTION_TITLES: dict[HumanAstrologerSectionId, str] = {
    HumanAstrologerSectionId.GREETING: "अभिवादन",
    HumanAstrologerSectionId.UNDERSTANDING_PROBLEM: "आपकी समस्या को समझना",
    HumanAstrologerSectionId.WHY_PROBLEM_EXISTS: "यह समस्या क्यों है",
    HumanAstrologerSectionId.CURRENT_SITUATION: "वर्तमान स्थिति",
    HumanAstrologerSectionId.POSITIVE_FACTORS: "सकारात्मक पक्ष",
    HumanAstrologerSectionId.NEGATIVE_FACTORS: "चुनौतियाँ और सावधानी",
    HumanAstrologerSectionId.FUTURE_OUTLOOK: "भविष्य की दिशा",
    HumanAstrologerSectionId.REMEDIES: "उपाय",
    HumanAstrologerSectionId.PRACTICAL_ADVICE: "व्यवहारिक सलाह",
    HumanAstrologerSectionId.FINAL_BLESSING: "अंतिम संदेश",
}

SECTION_FALLBACKS: dict[HumanAstrologerSectionId, str] = {
    HumanAstrologerSectionId.GREETING: "नमस्ते। आपका हार्दिक स्वागत है। मैं आपकी कुंडली देखकर सीधे और सहज भाषा में बात कर रहा हूँ।",
    HumanAstrologerSectionId.UNDERSTANDING_PROBLEM: "मैंने आपकी चिंता को ध्यान से समझा है और नीचे उसे सरल शब्दों में समझा रहा हूँ।",
    HumanAstrologerSectionId.WHY_PROBLEM_EXISTS: "कुंडली में कुछ संयोग ऐसे हैं जिनसे यह स्थिति धीरे-धीरे बनती दिखती है।",
    HumanAstrologerSectionId.CURRENT_SITUATION: "अभी का समय आपको धैर्य, सजगता और संतुलित निर्णय की ओर मार्गदर्शन कर रहा है।",
    HumanAstrologerSectionId.POSITIVE_FACTORS: "आपकी कुंडली में कई सकारात्मक संकेत भी मौजूद हैं जो सहारा और आशा देते हैं।",
    HumanAstrologerSectionId.NEGATIVE_FACTORS: "कुछ संकेत सावधानी और संयम की ओर इशारा करते हैं, परंतु सही कदमों से इन्हें नरम किया जा सकता है।",
    HumanAstrologerSectionId.FUTURE_OUTLOOK: "आने वाले समय में परिस्थितियाँ धीरे-धीरे अनुकूल होती दिखाई देती हैं।",
    HumanAstrologerSectionId.REMEDIES: "साधारण, नियमित और सकारात्मक उपायों से मन को स्थिरता और सही दिशा मिल सकती है।",
    HumanAstrologerSectionId.PRACTICAL_ADVICE: "रोज़मर्रा की छोटी आदतें, संयम और सकारात्मक दृष्टिकोण बड़ा बदलाव ला सकते हैं।",
    HumanAstrologerSectionId.FINAL_BLESSING: "ईश्वर आपको सही दिशा, धैर्य और शांति प्रदान करें। आप अकेले नहीं हैं।",
}

NARRATIVE_SECTION_MAP: dict[NarrativeSectionId, HumanAstrologerSectionId] = {
    NarrativeSectionId.GREETING: HumanAstrologerSectionId.GREETING,
    NarrativeSectionId.OVERALL_CHART_IMPRESSION: HumanAstrologerSectionId.UNDERSTANDING_PROBLEM,
    NarrativeSectionId.HIGHEST_PRIORITY_TOPIC: HumanAstrologerSectionId.WHY_PROBLEM_EXISTS,
    NarrativeSectionId.SUPPORTING_EVIDENCE: HumanAstrologerSectionId.WHY_PROBLEM_EXISTS,
    NarrativeSectionId.DASHA_DISCUSSION: HumanAstrologerSectionId.CURRENT_SITUATION,
    NarrativeSectionId.TRANSIT_DISCUSSION: HumanAstrologerSectionId.FUTURE_OUTLOOK,
    NarrativeSectionId.YOGAS: HumanAstrologerSectionId.POSITIVE_FACTORS,
    NarrativeSectionId.PRACTICAL_GUIDANCE: HumanAstrologerSectionId.PRACTICAL_ADVICE,
    NarrativeSectionId.RECOMMENDATIONS: HumanAstrologerSectionId.REMEDIES,
    NarrativeSectionId.CLOSING_SUMMARY: HumanAstrologerSectionId.FINAL_BLESSING,
}


class HumanAstrologerRewriteEngine:
    """Rewrite consultation brain conclusions into a natural Hindi astrologer consultation."""

    def rewrite(
        self,
        brain_output: ConsultationBrainOutput,
        *,
        problem_text: str | None = None,
        language: str = "hi",
    ) -> HumanAstrologerConsultation:
        composer = _RewriteComposer(
            brain_output=brain_output,
            problem_text=problem_text,
            language=language or "hi",
        )
        sections = tuple(composer.build(section_id) for section_id in HUMAN_ASTROLOGER_SECTION_ORDER)
        return HumanAstrologerConsultation(language=language or "hi", sections=sections)

    def rewrite_to_client_dict(
        self,
        brain_output: ConsultationBrainOutput,
        *,
        problem_text: str | None = None,
        language: str = "hi",
    ) -> dict[str, Any]:
        consultation = self.rewrite(
            brain_output,
            problem_text=problem_text,
            language=language,
        )
        return consultation_to_client_dict(consultation)


def consultation_to_client_dict(consultation: HumanAstrologerConsultation) -> dict[str, Any]:
    return {
        "language": consultation.language,
        "delivery_mode": DELIVERY_MODE,
        "sections": [
            {
                "section_id": section.section_id.value,
                "title": section.title,
                "paragraphs": list(section.paragraphs),
                "body": section.body,
            }
            for section in consultation.sections
        ],
    }


class _RewriteComposer:
    def __init__(
        self,
        *,
        brain_output: ConsultationBrainOutput,
        problem_text: str | None,
        language: str,
    ) -> None:
        self._brain = brain_output
        self._problem_text = (problem_text or "").strip() or None
        self._language = language
        self._narrative_buckets: dict[HumanAstrologerSectionId, list[str]] = {
            section_id: [] for section_id in HUMAN_ASTROLOGER_SECTION_ORDER
        }
        self._collect_narrative_paragraphs()

    def build(self, section_id: HumanAstrologerSectionId) -> HumanAstrologerSection:
        builders = {
            HumanAstrologerSectionId.GREETING: self._build_greeting,
            HumanAstrologerSectionId.UNDERSTANDING_PROBLEM: self._build_understanding,
            HumanAstrologerSectionId.WHY_PROBLEM_EXISTS: self._build_why,
            HumanAstrologerSectionId.CURRENT_SITUATION: self._build_current,
            HumanAstrologerSectionId.POSITIVE_FACTORS: self._build_positive,
            HumanAstrologerSectionId.NEGATIVE_FACTORS: self._build_challenges,
            HumanAstrologerSectionId.FUTURE_OUTLOOK: self._build_future,
            HumanAstrologerSectionId.REMEDIES: self._build_remedies,
            HumanAstrologerSectionId.PRACTICAL_ADVICE: self._build_practical,
            HumanAstrologerSectionId.FINAL_BLESSING: self._build_closing,
        }
        paragraphs = builders[section_id]()
        if not paragraphs:
            paragraphs = (SECTION_FALLBACKS[section_id],)
        return HumanAstrologerSection(
            section_id=section_id,
            title=SECTION_TITLES[section_id],
            paragraphs=paragraphs,
        )

    def _collect_narrative_paragraphs(self) -> None:
        narrative = self._brain.narrative
        if narrative is None:
            return
        for section in narrative.sections:
            target = NARRATIVE_SECTION_MAP.get(section.section_id)
            if target is None:
                continue
            for paragraph in section.paragraphs:
                cleaned = humanize_astrology_text(paragraph)
                if cleaned and not is_technical_paragraph(cleaned):
                    self._narrative_buckets[target].append(cleaned)

    def _build_greeting(self) -> tuple[str, ...]:
        paragraphs: list[str] = []
        if self._problem_text:
            top = self._brain.priorities[0] if self._brain.priorities else None
            opening = (
                f"नमस्ते। आपका हार्दिक स्वागत है। आपने '{self._problem_text}' के बारे में पूछा है — "
                "मैंने आपकी कुंडली को ध्यान से देखा है।"
            )
            if top:
                rationale = humanize_astrology_text(top.rationale)
                opening += (
                    f" सबसे पहले सीधा उत्तर: {humanize_domain(top.domain)} से जुड़ी यह स्थिति "
                    f"{rationale or 'कुंडली के मुख्य संकेतों से जुड़ी है'}।"
                )
            else:
                opening += " सबसे पहले सीधा उत्तर: कुंडली के मुख्य संकेत आपके प्रश्न से जुड़े हुए हैं।"
            paragraphs.append(opening)
        narrative_parts = _finalize_paragraphs(self._narrative_buckets[HumanAstrologerSectionId.GREETING])
        if paragraphs:
            opening_line = humanize_astrology_text(paragraphs[0])
            if opening_line:
                if narrative_parts:
                    return (opening_line, *narrative_parts)
                return (opening_line,)
        return narrative_parts or (SECTION_FALLBACKS[HumanAstrologerSectionId.GREETING],)

    def _build_understanding(self) -> tuple[str, ...]:
        paragraphs = list(self._narrative_buckets[HumanAstrologerSectionId.UNDERSTANDING_PROBLEM])
        if self._problem_text:
            paragraphs.insert(
                0,
                f"आपकी मुख्य चिंता '{self._problem_text}' है। मैं इसे केवल तकनीकी शब्दों में नहीं, "
                "बल्कि व्यक्तिगत और सहज भाषा में समझाना चाहता हूँ।",
            )
        summary = humanize_astrology_text(self._brain.executive_summary)
        if summary and not is_technical_paragraph(summary):
            paragraphs.append(summary)
        return _finalize_paragraphs(paragraphs)

    def _build_why(self) -> tuple[str, ...]:
        paragraphs = list(self._narrative_buckets[HumanAstrologerSectionId.WHY_PROBLEM_EXISTS])
        paragraphs.extend(_priority_paragraphs(self._brain.priorities[:3]))
        paragraphs.extend(
            _evidence_paragraphs(
                self._brain.evidence,
                sources=(
                    EvidenceSource.RULE_STUDIO,
                    EvidenceSource.YOGAS,
                    EvidenceSource.LAL_KITAB,
                    EvidenceSource.FUSION,
                ),
                limit=3,
            )
        )
        return _finalize_paragraphs(paragraphs)

    def _build_current(self) -> tuple[str, ...]:
        paragraphs = list(self._narrative_buckets[HumanAstrologerSectionId.CURRENT_SITUATION])
        paragraphs.extend(
            _evidence_paragraphs(
                self._brain.evidence,
                sources=(EvidenceSource.DASHA, EvidenceSource.TRANSIT),
                limit=4,
            )
        )
        return _finalize_paragraphs(paragraphs)

    def _build_positive(self) -> tuple[str, ...]:
        paragraphs = list(self._narrative_buckets[HumanAstrologerSectionId.POSITIVE_FACTORS])
        paragraphs.extend(
            _evidence_paragraphs(
                self._brain.evidence,
                sources=(EvidenceSource.YOGAS, EvidenceSource.GOLDEN_DATASET),
                categories=(EvidenceCategory.SPIRITUAL, EvidenceCategory.GENERAL),
                limit=4,
            )
        )
        return _finalize_paragraphs(paragraphs)

    def _build_challenges(self) -> tuple[str, ...]:
        paragraphs = list(self._narrative_buckets[HumanAstrologerSectionId.NEGATIVE_FACTORS])
        paragraphs.extend(
            _evidence_paragraphs(
                self._brain.evidence,
                sources=(EvidenceSource.LAL_KITAB, EvidenceSource.TRANSIT),
                categories=(EvidenceCategory.RELATIONSHIP, EvidenceCategory.CAREER, EvidenceCategory.HEALTH),
                limit=3,
            )
        )
        if self._brain.conflicts:
            paragraphs.append(
                "कुछ संकेत एक-दूसरे से भिन्न दिखते हैं, इसलिए अत्यधिक उतावले या हठ से बचें और धीरे-धीरे निर्णय लें।"
            )
        paragraphs.append(
            "जल्दबाज़ी, कटु वचन और असंतुलित निर्णय इस समय परहेज़ रखने योग्य बातें हैं।"
        )
        return _finalize_paragraphs(paragraphs)

    def _build_future(self) -> tuple[str, ...]:
        paragraphs = list(self._narrative_buckets[HumanAstrologerSectionId.FUTURE_OUTLOOK])
        paragraphs.extend(
            _evidence_paragraphs(
                self._brain.evidence,
                sources=(EvidenceSource.DASHA, EvidenceSource.TRANSIT),
                categories=(EvidenceCategory.TIMING,),
                limit=4,
            )
        )
        if not paragraphs:
            paragraphs.append("आने वाले समय में परिस्थितियाँ धीरे-धीरे अनुकूल होती दिखाई देती हैं।")
        return _finalize_paragraphs(paragraphs)

    def _build_remedies(self) -> tuple[str, ...]:
        paragraphs = list(self._narrative_buckets[HumanAstrologerSectionId.REMEDIES])
        paragraphs.extend(_recommendation_paragraphs(self._brain.recommendations))
        paragraphs.extend(
            _evidence_paragraphs(
                self._brain.evidence,
                categories=(EvidenceCategory.REMEDY,),
                limit=3,
            )
        )
        return _finalize_paragraphs(paragraphs)

    def _build_practical(self) -> tuple[str, ...]:
        paragraphs = list(self._narrative_buckets[HumanAstrologerSectionId.PRACTICAL_ADVICE])
        for recommendation in self._brain.recommendations[:4]:
            for action in recommendation.action_items[:2]:
                label = humanize_astrology_text(action.replace("_", " "))
                if label:
                    paragraphs.append(f"रोज़मर्रा की ज़िंदगी में {label} पर ध्यान दें — यह व्यावहारिक और संतुलित रहेगा।")
        return _finalize_paragraphs(paragraphs)

    def _build_closing(self) -> tuple[str, ...]:
        paragraphs = list(self._narrative_buckets[HumanAstrologerSectionId.FINAL_BLESSING])
        if not paragraphs:
            paragraphs.append(SECTION_FALLBACKS[HumanAstrologerSectionId.FINAL_BLESSING])
        return _finalize_paragraphs(paragraphs)


def _priority_paragraphs(priorities: Sequence[ConsultationPriority]) -> list[str]:
    paragraphs: list[str] = []
    for priority in priorities:
        rationale = humanize_astrology_text(priority.rationale)
        title = humanize_astrology_text(priority.title)
        if not rationale and not title:
            continue
        domain = humanize_domain(priority.domain)
        if rationale:
            paragraphs.append(f"{domain} के संदर्भ में {rationale}")
        elif title:
            paragraphs.append(f"{domain} से जुड़ा एक महत्वपूर्ण संकेत {title} है।")
    return paragraphs


def _recommendation_paragraphs(recommendations: Sequence[ConsultationRecommendation]) -> list[str]:
    paragraphs: list[str] = []
    for recommendation in recommendations[:6]:
        title = humanize_astrology_text(recommendation.title.replace("_", " "))
        narrative = humanize_astrology_text(recommendation.narrative)
        if narrative:
            paragraphs.append(f"{title}: {narrative}" if title else narrative)
        elif title:
            paragraphs.append(f"{title} पर ध्यान देना लाभकारी रह सकता है।")
    return paragraphs


def _evidence_paragraphs(
    evidence: Sequence[ConsultationEvidence],
    *,
    sources: Sequence[EvidenceSource] = (),
    categories: Sequence[EvidenceCategory] = (),
    limit: int = 3,
) -> list[str]:
    paragraphs: list[str] = []
    for item in sorted(evidence, key=lambda entry: (-entry.weight, -entry.confidence)):
        if sources and item.source not in sources:
            continue
        if categories and item.category not in categories:
            continue
        sentence = rewrite_evidence_for_client(
            title=item.title,
            summary=item.summary,
            category=item.category.value,
        )
        if sentence and not is_technical_paragraph(sentence):
            paragraphs.append(sentence)
        if len(paragraphs) >= limit:
            break
    return paragraphs


def _finalize_paragraphs(paragraphs: Sequence[str]) -> tuple[str, ...]:
    body = join_paragraphs(list(paragraphs))
    if not body:
        return ()
    return tuple(part for part in body.split("\n\n") if part.strip())
