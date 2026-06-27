"""Problem category definitions for Vedic problem analysis."""

from __future__ import annotations

from enum import Enum


class ProblemCategory(str, Enum):
    MARRIAGE = "marriage"
    BUSINESS_FINANCE = "business_finance"
    CAREER = "career"
    HEALTH = "health"
    LEGAL = "legal"
    EDUCATION = "education"
    FAMILY = "family"
    PROPERTY = "property"
    SPIRITUAL = "spiritual"
    UNKNOWN = "unknown"


CATEGORY_LABELS: dict[ProblemCategory, str] = {
    ProblemCategory.MARRIAGE: "Marriage & Relationship",
    ProblemCategory.BUSINESS_FINANCE: "Business & Finance",
    ProblemCategory.CAREER: "Career & Profession",
    ProblemCategory.HEALTH: "Health & Wellbeing",
    ProblemCategory.LEGAL: "Legal & Court Matters",
    ProblemCategory.EDUCATION: "Education & Learning",
    ProblemCategory.FAMILY: "Family & Domestic Life",
    ProblemCategory.PROPERTY: "Property & Assets",
    ProblemCategory.SPIRITUAL: "Spiritual & Mental Peace",
    ProblemCategory.UNKNOWN: "Unknown / Unspecified",
}

# Primary and secondary houses associated with each problem domain
CATEGORY_HOUSES: dict[ProblemCategory, dict[str, tuple[int, ...]]] = {
    ProblemCategory.MARRIAGE: {
        "primary": (7,),
        "secondary": (2, 8, 5, 11),
        "supporting": (1, 4),
    },
    ProblemCategory.BUSINESS_FINANCE: {
        "primary": (2, 10, 11),
        "secondary": (6, 8, 12),
        "supporting": (5, 9),
    },
    ProblemCategory.CAREER: {
        "primary": (10,),
        "secondary": (6, 2, 11),
        "supporting": (1, 9),
    },
    ProblemCategory.HEALTH: {
        "primary": (6,),
        "secondary": (1, 8, 12),
        "supporting": (3, 4),
    },
    ProblemCategory.LEGAL: {
        "primary": (6, 7),
        "secondary": (8, 12, 2),
        "supporting": (10, 11),
    },
    ProblemCategory.EDUCATION: {
        "primary": (4, 5),
        "secondary": (9, 2),
        "supporting": (1, 3),
    },
    ProblemCategory.FAMILY: {
        "primary": (4, 2),
        "secondary": (5, 9, 11),
        "supporting": (1, 7),
    },
    ProblemCategory.PROPERTY: {
        "primary": (4,),
        "secondary": (2, 11, 12),
        "supporting": (8, 9),
    },
    ProblemCategory.SPIRITUAL: {
        "primary": (9, 12),
        "secondary": (1, 5, 8),
        "supporting": (4, 7),
    },
    ProblemCategory.UNKNOWN: {
        "primary": (1, 9),
        "secondary": (6, 8, 12),
        "supporting": (2, 7, 10),
    },
}

# Planets commonly examined for each problem domain
CATEGORY_PLANETS: dict[ProblemCategory, dict[str, tuple[str, ...]]] = {
    ProblemCategory.MARRIAGE: {
        "primary": ("Venus", "Jupiter"),
        "secondary": ("Mars", "Moon", "Saturn"),
        "shadow": ("Rahu", "Ketu"),
    },
    ProblemCategory.BUSINESS_FINANCE: {
        "primary": ("Mercury", "Jupiter", "Saturn"),
        "secondary": ("Sun", "Venus"),
        "shadow": ("Rahu", "Ketu"),
    },
    ProblemCategory.CAREER: {
        "primary": ("Sun", "Saturn", "Mercury"),
        "secondary": ("Jupiter", "Mars"),
        "shadow": ("Rahu",),
    },
    ProblemCategory.HEALTH: {
        "primary": ("Sun", "Moon", "Mars"),
        "secondary": ("Saturn", "Mercury"),
        "shadow": ("Rahu", "Ketu"),
    },
    ProblemCategory.LEGAL: {
        "primary": ("Saturn", "Mars", "Rahu"),
        "secondary": ("Sun", "Mercury"),
        "shadow": ("Ketu",),
    },
    ProblemCategory.EDUCATION: {
        "primary": ("Mercury", "Jupiter"),
        "secondary": ("Moon", "Sun"),
        "shadow": ("Rahu",),
    },
    ProblemCategory.FAMILY: {
        "primary": ("Moon", "Sun", "Jupiter"),
        "secondary": ("Mars", "Saturn"),
        "shadow": ("Rahu", "Ketu"),
    },
    ProblemCategory.PROPERTY: {
        "primary": ("Mars", "Saturn", "Venus"),
        "secondary": ("Moon", "Mercury"),
        "shadow": ("Rahu",),
    },
    ProblemCategory.SPIRITUAL: {
        "primary": ("Jupiter", "Ketu", "Saturn"),
        "secondary": ("Moon", "Sun"),
        "shadow": ("Rahu",),
    },
    ProblemCategory.UNKNOWN: {
        "primary": ("Saturn", "Rahu"),
        "secondary": ("Mars", "Sun", "Moon"),
        "shadow": ("Ketu",),
    },
}

# Root cause indicator templates per category (contextual, not remedies)
ROOT_CAUSE_TEMPLATES: dict[ProblemCategory, tuple[str, ...]] = {
    ProblemCategory.MARRIAGE: (
        "Affliction to 7th house or Venus may indicate relationship friction.",
        "Mars influence on 7th house can suggest conflict or delay in marriage.",
        "Rahu/Ketu axis involving 2nd or 7th house may destabilize partnerships.",
        "Weak or afflicted Jupiter can reduce marital harmony and support.",
    ),
    ProblemCategory.BUSINESS_FINANCE: (
        "Affliction to 2nd, 10th, or 11th houses may correlate with financial strain.",
        "Saturn pressure on wealth houses can indicate prolonged business hardship.",
        "Mercury weakness may affect trade, contracts, and cash flow decisions.",
        "Rahu influence on 11th house can create unstable gains or sudden losses.",
    ),
    ProblemCategory.CAREER: (
        "10th house affliction may block professional growth or recognition.",
        "Saturn delays in 10th house can indicate slow career progression.",
        "Sun weakness may reduce authority, visibility, or leadership outcomes.",
        "6th house conflict patterns can suggest workplace obstacles.",
    ),
    ProblemCategory.HEALTH: (
        "6th, 8th, or 12th house afflictions may relate to health vulnerability.",
        "Malefic influence on lagna or Moon can reflect vitality concerns.",
        "Mars-Saturn combinations may indicate chronic or inflammatory patterns.",
        "Afflicted Moon can suggest stress-related or emotional health impact.",
    ),
    ProblemCategory.LEGAL: (
        "6th house activation may correlate with disputes and litigation.",
        "Saturn-Mars affliction can indicate prolonged legal conflict.",
        "Rahu involvement in 6th/7th/8th axis may suggest complex court matters.",
        "12th house linkage can indicate hidden legal expenses or confinement risk.",
    ),
    ProblemCategory.EDUCATION: (
        "4th or 5th house affliction may affect learning focus and outcomes.",
        "Mercury weakness can indicate communication or exam-related challenges.",
        "Jupiter affliction may reduce guidance, confidence, or academic support.",
    ),
    ProblemCategory.FAMILY: (
        "4th house affliction may reflect domestic discord or parental stress.",
        "Moon affliction can indicate emotional turbulence within family life.",
        "2nd house weakness may relate to family resources or speech conflicts.",
    ),
    ProblemCategory.PROPERTY: (
        "4th house affliction may affect property ownership or domestic assets.",
        "Mars-Saturn influence on 4th house can indicate property disputes.",
        "8th house linkage may suggest inheritance or shared asset complications.",
    ),
    ProblemCategory.SPIRITUAL: (
        "9th or 12th house affliction may reflect spiritual restlessness.",
        "Ketu influence can indicate detachment or identity confusion.",
        "Saturn pressure on 9th house may delay faith, guidance, or peace of mind.",
    ),
    ProblemCategory.UNKNOWN: (
        "Problem statement lacks specificity; trik house patterns (6, 8, 12) warrant review.",
        "General lagna and Moon condition may reveal underlying life stress.",
        "Saturn or Rahu dominance in current period may amplify unclear challenges.",
    ),
}

# Fix PROPERTY - I made a mistake using dict syntax