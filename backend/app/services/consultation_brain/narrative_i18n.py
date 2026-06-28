"""Localized templates for the human consultation narrative engine."""

from __future__ import annotations

from backend.app.services.consultation_brain.narrative_models import NarrativeLanguage, NarrativeSectionId
from backend.app.services.consultation_brain.priority_models import PriorityDomain
from backend.app.services.consultation_brain.recommendation_models import RecommendationCategory

SECTION_TITLES: dict[NarrativeLanguage, dict[NarrativeSectionId, str]] = {
    NarrativeLanguage.HINDI: {
        NarrativeSectionId.GREETING: "अभिवादन",
        NarrativeSectionId.OVERALL_CHART_IMPRESSION: "कुंडली की समग्र झलक",
        NarrativeSectionId.HIGHEST_PRIORITY_TOPIC: "सबसे महत्वपूर्ण विषय",
        NarrativeSectionId.SUPPORTING_EVIDENCE: "सहायक प्रमाण",
        NarrativeSectionId.DASHA_DISCUSSION: "दशा चर्चा",
        NarrativeSectionId.TRANSIT_DISCUSSION: "गोचर चर्चा",
        NarrativeSectionId.YOGAS: "योग",
        NarrativeSectionId.PRACTICAL_GUIDANCE: "व्यावहारिक मार्गदर्शन",
        NarrativeSectionId.RECOMMENDATIONS: "सिफारिशें",
        NarrativeSectionId.CLOSING_SUMMARY: "समापन सारांश",
    },
    NarrativeLanguage.HINGLISH: {
        NarrativeSectionId.GREETING: "Namaste / Greeting",
        NarrativeSectionId.OVERALL_CHART_IMPRESSION: "Overall Chart Impression",
        NarrativeSectionId.HIGHEST_PRIORITY_TOPIC: "Sabse Important Topic",
        NarrativeSectionId.SUPPORTING_EVIDENCE: "Supporting Evidence",
        NarrativeSectionId.DASHA_DISCUSSION: "Dasha Discussion",
        NarrativeSectionId.TRANSIT_DISCUSSION: "Transit Discussion",
        NarrativeSectionId.YOGAS: "Yogas",
        NarrativeSectionId.PRACTICAL_GUIDANCE: "Practical Guidance",
        NarrativeSectionId.RECOMMENDATIONS: "Recommendations",
        NarrativeSectionId.CLOSING_SUMMARY: "Closing Summary",
    },
    NarrativeLanguage.ENGLISH: {
        NarrativeSectionId.GREETING: "Greeting",
        NarrativeSectionId.OVERALL_CHART_IMPRESSION: "Overall Chart Impression",
        NarrativeSectionId.HIGHEST_PRIORITY_TOPIC: "Highest Priority Topic",
        NarrativeSectionId.SUPPORTING_EVIDENCE: "Supporting Evidence",
        NarrativeSectionId.DASHA_DISCUSSION: "Dasha Discussion",
        NarrativeSectionId.TRANSIT_DISCUSSION: "Transit Discussion",
        NarrativeSectionId.YOGAS: "Yogas",
        NarrativeSectionId.PRACTICAL_GUIDANCE: "Practical Guidance",
        NarrativeSectionId.RECOMMENDATIONS: "Recommendations",
        NarrativeSectionId.CLOSING_SUMMARY: "Closing Summary",
    },
}

DOMAIN_LABELS: dict[NarrativeLanguage, dict[PriorityDomain, str]] = {
    NarrativeLanguage.HINDI: {
        PriorityDomain.CAREER: "करियर",
        PriorityDomain.FINANCE: "वित्त",
        PriorityDomain.MARRIAGE: "विवाह",
        PriorityDomain.RELATIONSHIP: "संबंध",
        PriorityDomain.HEALTH: "स्वास्थ्य",
        PriorityDomain.EDUCATION: "शिक्षा",
        PriorityDomain.CHILDREN: "संतान",
        PriorityDomain.PROPERTY: "संपत्ति",
        PriorityDomain.BUSINESS: "व्यवसाय",
        PriorityDomain.SPIRITUALITY: "आध्यात्म",
        PriorityDomain.FOREIGN_TRAVEL: "विदेश यात्रा",
        PriorityDomain.LEGAL: "कानूनी",
        PriorityDomain.MENTAL_WELLBEING: "मानसिक कल्याण",
        PriorityDomain.FAMILY: "परिवार",
    },
    NarrativeLanguage.HINGLISH: {
        PriorityDomain.CAREER: "Career",
        PriorityDomain.FINANCE: "Finance",
        PriorityDomain.MARRIAGE: "Marriage",
        PriorityDomain.RELATIONSHIP: "Relationship",
        PriorityDomain.HEALTH: "Health",
        PriorityDomain.EDUCATION: "Education",
        PriorityDomain.CHILDREN: "Children",
        PriorityDomain.PROPERTY: "Property",
        PriorityDomain.BUSINESS: "Business",
        PriorityDomain.SPIRITUALITY: "Spirituality",
        PriorityDomain.FOREIGN_TRAVEL: "Foreign Travel",
        PriorityDomain.LEGAL: "Legal",
        PriorityDomain.MENTAL_WELLBEING: "Mental Wellbeing",
        PriorityDomain.FAMILY: "Family",
    },
    NarrativeLanguage.ENGLISH: {
        PriorityDomain.CAREER: "Career",
        PriorityDomain.FINANCE: "Finance",
        PriorityDomain.MARRIAGE: "Marriage",
        PriorityDomain.RELATIONSHIP: "Relationship",
        PriorityDomain.HEALTH: "Health",
        PriorityDomain.EDUCATION: "Education",
        PriorityDomain.CHILDREN: "Children",
        PriorityDomain.PROPERTY: "Property",
        PriorityDomain.BUSINESS: "Business",
        PriorityDomain.SPIRITUALITY: "Spirituality",
        PriorityDomain.FOREIGN_TRAVEL: "Foreign Travel",
        PriorityDomain.LEGAL: "Legal",
        PriorityDomain.MENTAL_WELLBEING: "Mental Wellbeing",
        PriorityDomain.FAMILY: "Family",
    },
}

CATEGORY_LABELS: dict[NarrativeLanguage, dict[RecommendationCategory, str]] = {
    NarrativeLanguage.HINDI: {
        RecommendationCategory.IMMEDIATE_ACTIONS: "तत्काल कार्य",
        RecommendationCategory.LIFESTYLE: "जीवनशैली",
        RecommendationCategory.SPIRITUAL: "आध्यात्मिक",
        RecommendationCategory.MANTRA: "मंत्र",
        RecommendationCategory.DONATION: "दान",
        RecommendationCategory.GEMSTONE: "रत्न",
        RecommendationCategory.BEHAVIOURAL: "व्यवहार",
        RecommendationCategory.TIMING_ADVICE: "समय सलाह",
        RecommendationCategory.CAREER_ADVICE: "करियर सलाह",
        RecommendationCategory.MARRIAGE_ADVICE: "विवाह सलाह",
        RecommendationCategory.EDUCATION_ADVICE: "शिक्षा सलाह",
        RecommendationCategory.HEALTH_ADVICE: "स्वास्थ्य सलाह",
        RecommendationCategory.FINANCIAL_ADVICE: "वित्तीय सलाह",
        RecommendationCategory.GENERAL_GUIDANCE: "सामान्य मार्गदर्शन",
    },
    NarrativeLanguage.HINGLISH: {
        RecommendationCategory.IMMEDIATE_ACTIONS: "Immediate Actions",
        RecommendationCategory.LIFESTYLE: "Lifestyle",
        RecommendationCategory.SPIRITUAL: "Spiritual",
        RecommendationCategory.MANTRA: "Mantra",
        RecommendationCategory.DONATION: "Donation",
        RecommendationCategory.GEMSTONE: "Gemstone",
        RecommendationCategory.BEHAVIOURAL: "Behavioural",
        RecommendationCategory.TIMING_ADVICE: "Timing Advice",
        RecommendationCategory.CAREER_ADVICE: "Career Advice",
        RecommendationCategory.MARRIAGE_ADVICE: "Marriage Advice",
        RecommendationCategory.EDUCATION_ADVICE: "Education Advice",
        RecommendationCategory.HEALTH_ADVICE: "Health Advice",
        RecommendationCategory.FINANCIAL_ADVICE: "Financial Advice",
        RecommendationCategory.GENERAL_GUIDANCE: "General Guidance",
    },
    NarrativeLanguage.ENGLISH: {
        RecommendationCategory.IMMEDIATE_ACTIONS: "Immediate Actions",
        RecommendationCategory.LIFESTYLE: "Lifestyle",
        RecommendationCategory.SPIRITUAL: "Spiritual",
        RecommendationCategory.MANTRA: "Mantra",
        RecommendationCategory.DONATION: "Donation",
        RecommendationCategory.GEMSTONE: "Gemstone",
        RecommendationCategory.BEHAVIOURAL: "Behavioural",
        RecommendationCategory.TIMING_ADVICE: "Timing Advice",
        RecommendationCategory.CAREER_ADVICE: "Career Advice",
        RecommendationCategory.MARRIAGE_ADVICE: "Marriage Advice",
        RecommendationCategory.EDUCATION_ADVICE: "Education Advice",
        RecommendationCategory.HEALTH_ADVICE: "Health Advice",
        RecommendationCategory.FINANCIAL_ADVICE: "Financial Advice",
        RecommendationCategory.GENERAL_GUIDANCE: "General Guidance",
    },
}


def normalize_language(language: str | None) -> NarrativeLanguage:
    """Map input language codes to supported narrative languages."""
    if not language:
        return NarrativeLanguage.HINDI
    normalized = language.strip().lower().replace("_", "-")
    if normalized in {"hi", "hin", "hindi"}:
        return NarrativeLanguage.HINDI
    if normalized in {"hinglish", "hi-en", "hi-en-in"}:
        return NarrativeLanguage.HINGLISH
    if normalized in {"en", "eng", "english"}:
        return NarrativeLanguage.ENGLISH
    return NarrativeLanguage.HINDI


def section_title(section_id: NarrativeSectionId, language: NarrativeLanguage) -> str:
    return SECTION_TITLES[language][section_id]


def domain_label(domain: PriorityDomain, language: NarrativeLanguage) -> str:
    return DOMAIN_LABELS[language].get(domain, domain.value.replace("_", " ").title())


def category_label(category: RecommendationCategory, language: NarrativeLanguage) -> str:
    return CATEGORY_LABELS[language].get(category, category.value.replace("_", " ").title())


def greeting_paragraph(*, language: NarrativeLanguage, problem_text: str | None) -> str:
    concern = problem_text.strip() if problem_text else None
    if language is NarrativeLanguage.HINDI:
        if concern:
            return (
                f"नमस्ते। आपकी चिंता '{concern}' के संबंध में हमने उपलब्ध कुंडली प्रमाणों "
                "का सावधानीपूर्वक अध्ययन किया है। नीचे केवल मौजूदा प्रमाणों पर आधारित स्पष्ट "
                "और सरल मार्गदर्शन है।"
            )
        return (
            "नमस्ते। हमने आपकी कुंडली से जुड़े उपलब्ध प्रमाणों का अध्ययन किया है। "
            "नीचे केवल मौजूदा साक्ष्य पर आधारित सलाह दी गई है।"
        )
    if language is NarrativeLanguage.HINGLISH:
        if concern:
            return (
                f"Namaste. Aapki concern '{concern}' ke liye humne available chart evidence "
                "carefully review kiya hai. Neeche sirf existing evidence par based simple guidance hai."
            )
        return (
            "Namaste. Humne aapki kundli se linked available evidence review kiya hai. "
            "Neeche sirf existing proof par based guidance hai."
        )
    if concern:
        return (
            f"Welcome. For your concern about '{concern}', we have carefully reviewed the "
            "available chart evidence. The guidance below is based only on existing signals."
        )
    return (
        "Welcome. We have reviewed the available chart evidence linked to your consultation. "
        "The guidance below is based only on existing signals."
    )


def empty_section_paragraph(*, section_id: NarrativeSectionId, language: NarrativeLanguage) -> str:
    messages = {
        NarrativeLanguage.HINDI: {
            NarrativeSectionId.OVERALL_CHART_IMPRESSION: "इस समय कोई विशेष प्रोफेशनल रिपोर्ट या सामान्य प्रमाण उपलब्ध नहीं है।",
            NarrativeSectionId.HIGHEST_PRIORITY_TOPIC: "इस समय कोई प्राथमिक विषय रैंक नहीं किया गया है।",
            NarrativeSectionId.SUPPORTING_EVIDENCE: "प्राथमिक विषय के लिए कोई सहायक प्रमाण उपलब्ध नहीं है।",
            NarrativeSectionId.DASHA_DISCUSSION: "इस समय दशा से संबंधित कोई प्रमाण उपलब्ध नहीं है।",
            NarrativeSectionId.TRANSIT_DISCUSSION: "इस समय गोचर से संबंधित कोई प्रमाण उपलब्ध नहीं है।",
            NarrativeSectionId.YOGAS: "इस समय योग से संबंधित कोई प्रमाण उपलब्ध नहीं है।",
            NarrativeSectionId.PRACTICAL_GUIDANCE: "इस समय कोई व्यावहारिक सिफारिश उपलब्ध नहीं है।",
            NarrativeSectionId.RECOMMENDATIONS: "इस समय कोई संरचित सिफारिश उपलब्ध नहीं है।",
        },
        NarrativeLanguage.HINGLISH: {
            NarrativeSectionId.OVERALL_CHART_IMPRESSION: "Abhi koi special professional report ya general evidence available nahi hai.",
            NarrativeSectionId.HIGHEST_PRIORITY_TOPIC: "Abhi koi primary topic rank nahi hua hai.",
            NarrativeSectionId.SUPPORTING_EVIDENCE: "Primary topic ke liye supporting evidence available nahi hai.",
            NarrativeSectionId.DASHA_DISCUSSION: "Abhi dasha related koi evidence available nahi hai.",
            NarrativeSectionId.TRANSIT_DISCUSSION: "Abhi transit related koi evidence available nahi hai.",
            NarrativeSectionId.YOGAS: "Abhi yoga related koi evidence available nahi hai.",
            NarrativeSectionId.PRACTICAL_GUIDANCE: "Abhi koi practical recommendation available nahi hai.",
            NarrativeSectionId.RECOMMENDATIONS: "Abhi koi structured recommendation available nahi hai.",
        },
        NarrativeLanguage.ENGLISH: {
            NarrativeSectionId.OVERALL_CHART_IMPRESSION: "No professional report or general evidence is available at this time.",
            NarrativeSectionId.HIGHEST_PRIORITY_TOPIC: "No primary topic has been ranked at this time.",
            NarrativeSectionId.SUPPORTING_EVIDENCE: "No supporting evidence is available for the primary topic.",
            NarrativeSectionId.DASHA_DISCUSSION: "No dasha-related evidence is available at this time.",
            NarrativeSectionId.TRANSIT_DISCUSSION: "No transit-related evidence is available at this time.",
            NarrativeSectionId.YOGAS: "No yoga-related evidence is available at this time.",
            NarrativeSectionId.PRACTICAL_GUIDANCE: "No practical recommendations are available at this time.",
            NarrativeSectionId.RECOMMENDATIONS: "No structured recommendations are available at this time.",
        },
    }
    return messages[language][section_id]


def evidence_intro(language: NarrativeLanguage) -> str:
    if language is NarrativeLanguage.HINDI:
        return "उपलब्ध प्रमाण:"
    if language is NarrativeLanguage.HINGLISH:
        return "Available evidence:"
    return "Available evidence:"


def evidence_bullet(*, title: str, summary: str, language: NarrativeLanguage) -> str:
    if language is NarrativeLanguage.HINDI:
        return f"• {title}: {summary}"
    return f"• {title}: {summary}"


def priority_intro(*, domain_label_text: str, score: float, language: NarrativeLanguage) -> str:
    if language is NarrativeLanguage.HINDI:
        return (
            f"सबसे महत्वपूर्ण विषय '{domain_label_text}' है। "
            f"प्राथमिकता स्कोर {score:.2f} है।"
        )
    if language is NarrativeLanguage.HINGLISH:
        return (
            f"Sabse important topic '{domain_label_text}' hai. "
            f"Priority score {score:.2f} hai."
        )
    return (
        f"The highest priority topic is '{domain_label_text}'. "
        f"The priority score is {score:.2f}."
    )


def conflict_resolution_bullet(*, conflict_type: str, reason: str, language: NarrativeLanguage) -> str:
    if language is NarrativeLanguage.HINDI:
        return f"• संघर्ष ({conflict_type}): {reason}"
    if language is NarrativeLanguage.HINGLISH:
        return f"• Conflict ({conflict_type}): {reason}"
    return f"• Conflict ({conflict_type}): {reason}"


def recommendation_bullet(
    *,
    label: str,
    confidence: float,
    evidence_count: int,
    language: NarrativeLanguage,
) -> str:
    if language is NarrativeLanguage.HINDI:
        return f"• {label} (विश्वास {confidence:.2f}, प्रमाण {evidence_count})"
    if language is NarrativeLanguage.HINGLISH:
        return f"• {label} (confidence {confidence:.2f}, evidence {evidence_count})"
    return f"• {label} (confidence {confidence:.2f}, evidence {evidence_count})"


def closing_paragraph(
    *,
    language: NarrativeLanguage,
    priority_count: int,
    recommendation_count: int,
    evidence_count: int,
) -> str:
    if language is NarrativeLanguage.HINDI:
        return (
            f"सारांश: {evidence_count} प्रमाण, {priority_count} प्राथमिक विषय, "
            f"और {recommendation_count} सिफारिशें समीक्षा की गईं। "
            "कृपया केवल उपरोक्त प्रमाणों पर आधारित कदम उठाएं। शुभकामनाएं।"
        )
    if language is NarrativeLanguage.HINGLISH:
        return (
            f"Summary: {evidence_count} evidence, {priority_count} priority topics, "
            f"aur {recommendation_count} recommendations review kiye gaye. "
            "Please sirf upar ke evidence par based steps follow karein. Shubhkamnayein."
        )
    return (
        f"Summary: {evidence_count} evidence items, {priority_count} priority topics, "
        f"and {recommendation_count} recommendations were reviewed. "
        "Please follow steps based only on the evidence above. Best wishes."
    )
