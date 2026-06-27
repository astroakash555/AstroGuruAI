"""Build Lal Kitab knowledge databases."""

from __future__ import annotations

PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")

RIN_TYPES = (
    ("pitra_rin", "Pitra Rin", "Sun-Saturn ancestral karmic debt"),
    ("matri_rin", "Matri Rin", "Moon-Rahu maternal karmic debt"),
    ("stree_rin", "Stree Rin", "Venus-Mars relationship karmic debt"),
    ("bhratri_rin", "Bhratri Rin", "Mars-Mercury sibling karmic debt"),
    ("rnanubandh_rin", "Rnanubandh Rin", "Saturn-Rahu bondage karmic debt"),
)

DOSH_TYPES = (
    ("saturn_rahu_dosh", "Saturn-Rahu Dosh"),
    ("mars_8th_dosh", "Mars 8th House Dosh"),
    ("ketu_6th_dosh", "Ketu 6th House Dosh"),
    ("sun_affliction_dosh", "Sun Affliction Dosh"),
    ("moon_affliction_dosh", "Moon Affliction Dosh"),
)


def build_rin_database() -> dict:
    entries = []
    for idx, (rin_id, name, meaning) in enumerate(RIN_TYPES):
        for house in (4, 5, 7, 9, 12):
            entries.append({
                "rin_id": f"{rin_id}_house_{house}",
                "name": name,
                "meaning": meaning,
                "house": house,
                "effects": [f"{name} activated when linked to house {house}."],
                "indicators": [f"Check Lal Kitab planet-house placement for {name}."],
                "severity": 0.6 + (idx % 3) * 0.1,
            })
    return {"system": "lal_kitab", "database": "rin", "count": len(entries), "entries": entries}


def build_dosh_database() -> dict:
    entries = []
    for dosh_id, name in DOSH_TYPES:
        for planet in PLANETS[:6]:
            entries.append({
                "dosh_id": f"{dosh_id}_{planet.lower()}",
                "name": name,
                "planet": planet,
                "description": f"{name} indicator involving {planet} in Lal Kitab framework.",
                "effects": [f"Monitor {planet} house placement and LK recommendations."],
                "severity": 0.65,
            })
    return {"system": "lal_kitab", "database": "dosh", "count": len(entries), "entries": entries}


def build_remedy_database() -> dict:
    entries = []
    for house in range(1, 13):
        for planet in PLANETS:
            entries.append({
                "remedy_id": f"lk_remedy_{planet.lower()}_h{house}",
                "planet": planet,
                "house": house,
                "remedy_type": "behavioral",
                "description": f"Lal Kitab corrective action when {planet} occupies house {house}.",
                "expected_effect": f"Reduce Lal Kitab affliction of {planet} in house {house}.",
                "priority": 2 + (house % 3),
            })
    return {"system": "lal_kitab", "database": "remedy", "count": len(entries), "entries": entries}


def build_planet_house_database() -> dict:
    entries = []
    effect_codes = ("harmony", "restriction", "expansion", "conflict", "karmic_test")
    for house in range(1, 13):
        for planet in PLANETS:
            code = effect_codes[(house + len(planet)) % len(effect_codes)]
            entries.append({
                "entry_id": f"lk_ph_{planet.lower()}_h{house}",
                "planet": planet,
                "house": house,
                "effect_code": code,
                "meaning": f"{planet} in house {house} expresses {code} in Lal Kitab logic.",
                "strengths": [f"Positive {code} when planet is supported."],
                "weaknesses": [f"Negative {code} when afflicted."],
            })
    return {"system": "lal_kitab", "database": "planet_house", "count": len(entries), "entries": entries}
