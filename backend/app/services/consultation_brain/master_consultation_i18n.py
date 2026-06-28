"""Localized templates for the master astrologer conversation engine."""

from __future__ import annotations

from backend.app.services.consultation_brain.master_consultation_models import (
    MasterConsultationLanguage,
    MasterConsultationSectionId,
)

SECTION_TITLES: dict[MasterConsultationLanguage, dict[MasterConsultationSectionId, str]] = {
    MasterConsultationLanguage.HINDI: {
        MasterConsultationSectionId.GREETING: "अभिवादन",
        MasterConsultationSectionId.UNDERSTANDING_PROBLEM: "आपकी चिंता को समझना",
        MasterConsultationSectionId.WHY_PROBLEM_EXISTS: "यह समस्या क्यों है",
        MasterConsultationSectionId.CURRENT_SITUATION: "वर्तमान स्थिति",
        MasterConsultationSectionId.POSITIVE_FACTORS: "सकारात्मक पक्ष",
        MasterConsultationSectionId.NEGATIVE_FACTORS: "बाधाएँ",
        MasterConsultationSectionId.FUTURE_OUTLOOK: "भविष्य की झलक",
        MasterConsultationSectionId.REMEDIES: "उपाय",
        MasterConsultationSectionId.PRACTICAL_ADVICE: "व्यावहारिक सलाह",
        MasterConsultationSectionId.FINAL_BLESSING: "आशीर्वाद",
    },
    MasterConsultationLanguage.HINGLISH: {
        MasterConsultationSectionId.GREETING: "Namaste / Greeting",
        MasterConsultationSectionId.UNDERSTANDING_PROBLEM: "Aapki Concern Samajhna",
        MasterConsultationSectionId.WHY_PROBLEM_EXISTS: "Problem Kyon Hai",
        MasterConsultationSectionId.CURRENT_SITUATION: "Current Situation",
        MasterConsultationSectionId.POSITIVE_FACTORS: "Positive Factors",
        MasterConsultationSectionId.NEGATIVE_FACTORS: "Obstacles",
        MasterConsultationSectionId.FUTURE_OUTLOOK: "Future Outlook",
        MasterConsultationSectionId.REMEDIES: "Upay / Remedies",
        MasterConsultationSectionId.PRACTICAL_ADVICE: "Practical Advice",
        MasterConsultationSectionId.FINAL_BLESSING: "Final Blessing",
    },
    MasterConsultationLanguage.ENGLISH: {
        MasterConsultationSectionId.GREETING: "Greeting",
        MasterConsultationSectionId.UNDERSTANDING_PROBLEM: "Understanding Your Concern",
        MasterConsultationSectionId.WHY_PROBLEM_EXISTS: "Why This Challenge Exists",
        MasterConsultationSectionId.CURRENT_SITUATION: "Current Situation",
        MasterConsultationSectionId.POSITIVE_FACTORS: "Positive Factors",
        MasterConsultationSectionId.NEGATIVE_FACTORS: "Obstacles",
        MasterConsultationSectionId.FUTURE_OUTLOOK: "Future Outlook",
        MasterConsultationSectionId.REMEDIES: "Remedies",
        MasterConsultationSectionId.PRACTICAL_ADVICE: "Practical Advice",
        MasterConsultationSectionId.FINAL_BLESSING: "Final Blessing",
    },
}


def normalize_language(language: str | None) -> MasterConsultationLanguage:
    if not language:
        return MasterConsultationLanguage.HINDI
    normalized = language.strip().lower().replace("_", "-")
    if normalized in {"hi", "hin", "hindi"}:
        return MasterConsultationLanguage.HINDI
    if normalized in {"hinglish", "hi-en", "hi-en-in"}:
        return MasterConsultationLanguage.HINGLISH
    if normalized in {"en", "eng", "english"}:
        return MasterConsultationLanguage.ENGLISH
    return MasterConsultationLanguage.HINDI


def section_title(section_id: MasterConsultationSectionId, language: MasterConsultationLanguage) -> str:
    return SECTION_TITLES[language][section_id]


def greeting_paragraph(*, language: MasterConsultationLanguage, problem_text: str | None) -> str:
    concern = problem_text.strip() if problem_text else None
    if language is MasterConsultationLanguage.HINDI:
        if concern:
            return (
                f"नमस्ते। आपका स्वागत है। मैंने आपकी कुंडली और आपके प्रश्न '{concern}' "
                "को ध्यान से देखा है। नीचे मैं आपको सरल और सहज भाषा में समझा रहा हूँ — "
                "बिना किसी भय के, केवल स्पष्ट मार्गदर्शन के साथ।"
            )
        return (
            "नमस्ते। आपका हार्दिक स्वागत है। मैंने आपकी कुंडली का शांत और गहन अध्ययन किया है "
            "और अब आपको व्यक्तिगत रूप से समझाना चाहूँगा कि उपलब्ध संकेत क्या कहते हैं।"
        )
    if language is MasterConsultationLanguage.HINGLISH:
        if concern:
            return (
                f"Namaste. Aapka swagat hai. Maine aapki kundli aur aapka sawal '{concern}' "
                "dhyan se dekha hai. Neeche main simple aur warm language mein samjha raha hoon — "
                "bina dar ke, sirf clear guidance ke saath."
            )
        return (
            "Namaste. Aapka dil se swagat hai. Maine aapki kundli ka calm review kiya hai "
            "aur ab personally batana chahta hoon ki available signals kya keh rahe hain."
        )
    if concern:
        return (
            f"Welcome. Thank you for trusting me with your chart and your question about '{concern}'. "
            "I have reviewed the available signals carefully, and I will explain everything in warm, "
            "plain language — without fear, only honest guidance."
        )
    return (
        "Welcome. Thank you for being here. I have studied your chart with care, "
        "and I would like to personally explain what the available evidence suggests for you."
    )


def empathy_paragraph(*, language: MasterConsultationLanguage, problem_text: str | None) -> str:
    concern = problem_text.strip() if problem_text else None
    if language is MasterConsultationLanguage.HINDI:
        if concern:
            return (
                f"मैं समझता हूँ कि '{concern}' आपके मन में बार-बार उठता होगा। "
                "यह चिंता स्वाभाविक है, और आप अकेले नहीं हैं — कई लोग ऐसे ही संकेतों "
                "के बीच अपना रास्ता खोजते हैं।"
            )
        return (
            "आपकी चिंता स्वाभाविक है। जीवन के कुछ चरण ऐसे आते हैं जहाँ मन को "
            "स्पष्ट उत्तर और सहारे की ज़रूरत होती है — और यही इस परामर्श का उद्देश्य है।"
        )
    if language is MasterConsultationLanguage.HINGLISH:
        if concern:
            return (
                f"Main samajhta hoon ki '{concern}' aapke man mein baar-baar aata hoga. "
                "Yeh concern bilkul natural hai, aur aap akela nahi hain."
            )
        return "Aapki chinta natural hai. Kabhi-kabhi mind ko clear answer aur support chahiye hota hai."
    if concern:
        return (
            f"I understand that '{concern}' may weigh on your mind. "
            "That feeling is natural, and you are not alone in seeking clarity."
        )
    return (
        "Your search for clarity is completely natural. "
        "Sometimes we simply need a calm voice to help us see the path ahead."
    )


def empty_section_paragraph(
    *,
    section_id: MasterConsultationSectionId,
    language: MasterConsultationLanguage,
) -> str:
    messages = {
        MasterConsultationLanguage.HINDI: {
            MasterConsultationSectionId.WHY_PROBLEM_EXISTS: "इस समय कोई विशेष कारण-संकेत उपलब्ध नहीं है।",
            MasterConsultationSectionId.CURRENT_SITUATION: "वर्तमान समय के बारे में कोई स्पष्ट timing संकेत उपलब्ध नहीं है।",
            MasterConsultationSectionId.POSITIVE_FACTORS: "अभी कोई स्पष्ट सहायक संकेत दर्ज नहीं है।",
            MasterConsultationSectionId.NEGATIVE_FACTORS: "अभी कोई स्पष्ट बाधा दर्ज नहीं है।",
            MasterConsultationSectionId.FUTURE_OUTLOOK: "भविष्य के बारे में कोई विशिष्ट समय-सीमा उपलब्ध नहीं है।",
            MasterConsultationSectionId.REMEDIES: "इस समय कोई व्यक्तिगत उपाय सुझाया नहीं गया है।",
            MasterConsultationSectionId.PRACTICAL_ADVICE: "अभी कोई अतिरिक्त व्यावहारिक सलाह उपलब्ध नहीं है।",
        },
        MasterConsultationLanguage.HINGLISH: {
            MasterConsultationSectionId.WHY_PROBLEM_EXISTS: "Abhi koi clear reason signal available nahi hai.",
            MasterConsultationSectionId.CURRENT_SITUATION: "Current timing ke baare mein koi clear signal nahi hai.",
            MasterConsultationSectionId.POSITIVE_FACTORS: "Abhi koi clear supportive signal nahi hai.",
            MasterConsultationSectionId.NEGATIVE_FACTORS: "Abhi koi clear obstacle signal nahi hai.",
            MasterConsultationSectionId.FUTURE_OUTLOOK: "Future ke liye koi specific timeline available nahi hai.",
            MasterConsultationSectionId.REMEDIES: "Abhi koi personalized upay suggest nahi hua hai.",
            MasterConsultationSectionId.PRACTICAL_ADVICE: "Abhi koi extra practical advice available nahi hai.",
        },
        MasterConsultationLanguage.ENGLISH: {
            MasterConsultationSectionId.WHY_PROBLEM_EXISTS: "No specific cause signals are available at this time.",
            MasterConsultationSectionId.CURRENT_SITUATION: "No clear timing signals are available for the present phase.",
            MasterConsultationSectionId.POSITIVE_FACTORS: "No explicit supportive signals are recorded yet.",
            MasterConsultationSectionId.NEGATIVE_FACTORS: "No explicit obstacle signals are recorded yet.",
            MasterConsultationSectionId.FUTURE_OUTLOOK: "No specific timeline is available for the future outlook.",
            MasterConsultationSectionId.REMEDIES: "No personalized remedies have been suggested at this time.",
            MasterConsultationSectionId.PRACTICAL_ADVICE: "No additional practical advice is available at this time.",
        },
    }
    return messages[language][section_id]


def outlook_label(*, horizon: str, language: MasterConsultationLanguage) -> str:
    labels = {
        ("short", MasterConsultationLanguage.HINDI): "निकट भविष्य",
        ("medium", MasterConsultationLanguage.HINDI): "मध्यम अवधि",
        ("long", MasterConsultationLanguage.HINDI): "दीर्घ अवधि",
        ("short", MasterConsultationLanguage.HINGLISH): "Short term",
        ("medium", MasterConsultationLanguage.HINGLISH): "Medium term",
        ("long", MasterConsultationLanguage.HINGLISH): "Long term",
        ("short", MasterConsultationLanguage.ENGLISH): "Short term",
        ("medium", MasterConsultationLanguage.ENGLISH): "Medium term",
        ("long", MasterConsultationLanguage.ENGLISH): "Long term",
    }
    return labels[(horizon, language)]


def blessing_paragraph(*, language: MasterConsultationLanguage) -> str:
    if language is MasterConsultationLanguage.HINDI:
        return (
            "आप धैर्य और सकारात्मकता के साथ आगे बढ़ें। जो भी कदम उठाएँ, उन्हें शांत मन "
            "और सच्चे विश्वास के साथ अपनाएँ। भगवान आपको सही दिशा और शांति प्रदान करें। "
            "मेरा आशीर्वाद आपके साथ है।"
        )
    if language is MasterConsultationLanguage.HINGLISH:
        return (
            "Aap patience aur positivity ke saath aage badhein. Jo bhi step lein, "
            "use shaant mann aur faith ke saath apnayein. Meri shubhkamnayein aapke saath hain."
        )
    return (
        "Move forward with patience and hope. Take each step with a calm mind and sincere faith. "
        "May you find clarity, peace, and the right direction. My warm wishes are with you."
    )
