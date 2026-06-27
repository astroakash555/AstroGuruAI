"""Build KP astrology knowledge databases."""

from __future__ import annotations

PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
EVENT_TYPES = ("marriage", "career", "health", "finance", "legal", "education", "property", "travel")
HOUSES = tuple(range(1, 13))


def build_event_rules() -> dict:
    rules = []
    for event in EVENT_TYPES:
        for house in HOUSES:
            rules.append({
                "rule_id": f"kp_event_{event}_house_{house}",
                "event_type": event,
                "target_houses": [house],
                "description": f"KP event analysis for {event} considering house {house} cusp chain.",
                "support_conditions": [
                    "Significators present in level A/B/C.",
                    "Cusp sub lord supports event type.",
                ],
                "confidence": 0.62,
            })
    return {"system": "kp", "database": "event_rules", "count": len(rules), "rules": rules}


def build_significator_rules() -> dict:
    rules = []
    for house in HOUSES:
        for level in ("A", "B", "C", "D"):
            rules.append({
                "rule_id": f"kp_significator_h{house}_level_{level}",
                "house": house,
                "level": level,
                "description": f"KP significator level {level} for house {house}.",
                "meaning": {
                    "A": "Occupants of the house.",
                    "B": "Planets in star of occupants.",
                    "C": "Planets in star of house lord.",
                    "D": "House lord itself.",
                }[level],
                "confidence": 0.7,
            })
    return {"system": "kp", "database": "significator_rules", "count": len(rules), "rules": rules}


def build_star_lord_rules() -> dict:
    rules = []
    for planet in PLANETS:
        for house in (1, 4, 7, 10):
            rules.append({
                "rule_id": f"kp_star_lord_{planet.lower()}_h{house}",
                "planet": planet,
                "reference_house": house,
                "description": f"Star lord of {planet} influencing house {house} significator chain.",
                "effects": [f"Use nakshatra lord of {planet} for event timing."],
                "confidence": 0.66,
            })
    return {"system": "kp", "database": "star_lord_rules", "count": len(rules), "rules": rules}


def build_sub_lord_rules() -> dict:
    rules = []
    for planet in PLANETS:
        for house in HOUSES:
            rules.append({
                "rule_id": f"kp_sub_lord_{planet.lower()}_cusp_{house}",
                "planet": planet,
                "cusp_house": house,
                "description": f"Sub lord analysis when {planet} appears in house {house} cusp chain.",
                "effects": ["Sub lord determines fructification precision in KP."],
                "confidence": 0.68,
            })
    return {"system": "kp", "database": "sub_lord_rules", "count": len(rules), "rules": rules}
