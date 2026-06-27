"""Build Vedic core knowledge JSON structures."""

from __future__ import annotations

PLANETS = (
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
)
SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)
SIGN_LORDS = (
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
)
NAKSHATRAS = (
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
)
NAKSHATRA_LORDS = ("Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury") * 3

PLANET_PROFILES: dict[str, dict[str, tuple[str, ...]]] = {
    "Sun": {
        "meanings": ("soul", "authority", "vitality", "father"),
        "strengths": ("leadership", "confidence", "recognition"),
        "weaknesses": ("ego", "dominance", "pride"),
        "effects": ("career visibility", "government linkage", "health vitality"),
    },
    "Moon": {
        "meanings": ("mind", "emotion", "mother", "public"),
        "strengths": ("adaptability", "nurture", "intuition"),
        "weaknesses": ("mood swings", "dependency", "restlessness"),
        "effects": ("mental peace", "domestic life", "public response"),
    },
    "Mars": {
        "meanings": ("energy", "courage", "siblings", "property"),
        "strengths": ("drive", "decisiveness", "technical skill"),
        "weaknesses": ("anger", "conflict", "impulsiveness"),
        "effects": ("accidents", "surgery", "competition"),
    },
    "Mercury": {
        "meanings": ("intellect", "speech", "trade", "analysis"),
        "strengths": ("communication", "learning", "business acumen"),
        "weaknesses": ("nervousness", "indecision", "overthinking"),
        "effects": ("education", "contracts", "accounts"),
    },
    "Jupiter": {
        "meanings": ("wisdom", "dharma", "teacher", "fortune"),
        "strengths": ("guidance", "ethics", "expansion"),
        "weaknesses": ("overoptimism", "weight", "complacency"),
        "effects": ("marriage blessing", "children", "wealth growth"),
    },
    "Venus": {
        "meanings": ("love", "marriage", "luxury", "arts"),
        "strengths": ("harmony", "creativity", "relationship skill"),
        "weaknesses": ("indulgence", "attachment", "passivity"),
        "effects": ("partnership", "vehicles", "comfort"),
    },
    "Saturn": {
        "meanings": ("karma", "discipline", "delay", "service"),
        "strengths": ("perseverance", "structure", "maturity"),
        "weaknesses": ("delay", "fear", "isolation"),
        "effects": ("chronic issues", "responsibility", "long-term results"),
    },
    "Rahu": {
        "meanings": ("obsession", "foreign", "technology", "sudden change"),
        "strengths": ("ambition", "innovation", "breakthrough"),
        "weaknesses": ("confusion", "scandal", "addiction"),
        "effects": ("unconventional paths", "foreign links", " sudden events"),
    },
    "Ketu": {
        "meanings": ("detachment", "past karma", "spirituality", "research"),
        "strengths": ("intuition", "moksha inclination", "specialization"),
        "weaknesses": ("separation", "lack of direction", "isolation"),
        "effects": ("breaks", "spiritual turns", "hidden matters"),
    },
}

HOUSE_THEMES = {
    1: ("self", "body", "personality", "overall life direction"),
    2: ("wealth", "family", "speech", "food"),
    3: ("courage", "siblings", "communication", "short travel"),
    4: ("home", "mother", "property", "peace"),
    5: ("children", "education", "creativity", "romance"),
    6: ("enemies", "disease", "service", "litigation"),
    7: ("marriage", "partnership", "business partner", "public dealings"),
    8: ("longevity", "transformation", "inheritance", "occult"),
    9: ("fortune", "father", "dharma", "long travel"),
    10: ("career", "status", "authority", "karma in world"),
    11: ("gains", "income", "friends", "aspirations"),
    12: ("loss", "expenses", "foreign", "moksha"),
}


def build_planets() -> dict:
    entities = []
    for planet in PLANETS:
        profile = PLANET_PROFILES[planet]
        weaknesses = profile.get("weaknesses") or profile.get("weaknesss", ())
        entities.append({
            "entity_id": f"vedic_planet_{planet.lower()}",
            "entity_type": "planet",
            "name": planet,
            "system": "vedic",
            "meanings": list(profile["meanings"]),
            "strengths": list(profile["strengths"]),
            "weaknesses": list(weaknesses),
            "effects": list(profile["effects"]),
            "metadata": {"natural_significator": True},
        })
    return {"system": "vedic", "entity_type": "planet", "count": len(entities), "entities": entities}


def build_houses() -> dict:
    entities = []
    for house in range(1, 13):
        themes = HOUSE_THEMES[house]
        entities.append({
            "entity_id": f"vedic_house_{house}",
            "entity_type": "house",
            "name": f"House {house}",
            "system": "vedic",
            "meanings": list(themes),
            "strengths": [f"Positive expression of {themes[0]} when well supported."],
            "weaknesses": [f"Affliction to house {house} disturbs {themes[-1]}."],
            "effects": [f"Influences life outcomes related to {', '.join(themes)}."],
            "metadata": {"house_number": house},
        })
    return {"system": "vedic", "entity_type": "house", "count": len(entities), "entities": entities}


def build_signs() -> dict:
    entities = []
    for index, sign in enumerate(SIGNS):
        lord = SIGN_LORDS[index]
        entities.append({
            "entity_id": f"vedic_sign_{sign.lower()}",
            "entity_type": "sign",
            "name": sign,
            "system": "vedic",
            "meanings": [f"Rashi {sign}", f"ruled by {lord}"],
            "strengths": [f"Supports traits of {lord} when unafflicted."],
            "weaknesses": [f"Afflicted {sign} distorts {lord} significations."],
            "effects": [f"Modifies planetary results in {sign}."],
            "metadata": {"sign_index": index, "lord": lord},
        })
    return {"system": "vedic", "entity_type": "sign", "count": len(entities), "entities": entities}


def build_nakshatras() -> dict:
    entities = []
    for index, name in enumerate(NAKSHATRAS):
        lord = NAKSHATRA_LORDS[index]
        entities.append({
            "entity_id": f"vedic_nakshatra_{index}",
            "entity_type": "nakshatra",
            "name": name,
            "system": "vedic",
            "meanings": [f"Lunar mansion {name}", f"star lord {lord}"],
            "strengths": [f"Dasha seeding through {lord}."],
            "weaknesses": [f"Afflicted nakshatra disturbs lunar outcomes."],
            "effects": [f"Fine-tunes Moon and KP star lord analysis."],
            "metadata": {"nakshatra_index": index, "lord": lord, "pada_count": 4},
        })
    return {"system": "vedic", "entity_type": "nakshatra", "count": len(entities), "entities": entities}


def build_padas() -> dict:
    entities = []
    for nak_index, nak_name in enumerate(NAKSHATRAS):
        for pada in range(1, 5):
            entities.append({
                "entity_id": f"vedic_pada_{nak_index}_{pada}",
                "entity_type": "pada",
                "name": f"{nak_name} Pada {pada}",
                "system": "vedic",
                "meanings": [f"Quarter division of {nak_name}"],
                "strengths": [f"Used in naming and micro-lunar analysis."],
                "weaknesses": [f"Afflicted pada affects naming and temperament nuance."],
                "effects": [f"Refines birth nakshatra interpretation for pada {pada}."],
                "metadata": {
                    "nakshatra": nak_name,
                    "nakshatra_index": nak_index,
                    "pada": pada,
                    "lord": NAKSHATRA_LORDS[nak_index],
                },
            })
    return {"system": "vedic", "entity_type": "pada", "count": len(entities), "entities": entities}


def build_combinations() -> dict:
    combinations = []
    pairs = [
        ("Saturn", 7, "delayed_marriage"),
        ("Mars", 7, "marriage_conflict"),
        ("Venus", 7, "relationship_harmony"),
        ("Jupiter", 7, "marriage_blessing"),
        ("Rahu", 7, "unconventional_marriage"),
        ("Saturn", 10, "career_delay"),
        ("Sun", 10, "authority_career"),
        ("Mercury", 6, "service_job"),
        ("Moon", 4, "mental_peace_home"),
        ("Mars", 8, "accident_surgery"),
        ("Saturn", 2, "financial_constraint"),
        ("Jupiter", 11, "wealth_gain"),
    ]
    for planet, house, theme in pairs:
        combinations.append({
            "combination_id": f"vedic_{planet.lower()}_house_{house}",
            "system": "vedic",
            "planets": [planet],
            "houses": [house],
            "theme": theme,
            "meaning": f"{planet} influencing house {house} indicates {theme.replace('_', ' ')} themes.",
            "effects": [f"Check dignity, aspects, and dasha for {theme} outcomes."],
        })
    return {"system": "vedic", "entity_type": "combination", "count": len(combinations), "combinations": combinations}
