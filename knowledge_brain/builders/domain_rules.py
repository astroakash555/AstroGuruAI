"""Build domain-specific astrology rule databases."""

from __future__ import annotations

PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
HOUSES = tuple(range(1, 13))

MARRIAGE_CATEGORIES = (
    "delayed_marriage",
    "early_marriage",
    "second_marriage",
    "divorce",
    "love_marriage",
    "inter_caste_marriage",
    "denial_of_marriage",
)

CAREER_CATEGORIES = (
    "government_job",
    "private_job",
    "business",
    "partnership",
    "promotion",
    "unemployment",
)

HEALTH_CATEGORIES = (
    "chronic_disease",
    "mental_stress",
    "surgery",
    "accident",
    "recovery",
)

FINANCE_CATEGORIES = (
    "wealth",
    "debt",
    "losses",
    "inheritance",
    "speculation",
)


def _rule(
    *,
    rule_id: str,
    system: str,
    domain: str,
    category: str,
    title: str,
    description: str,
    planets: tuple[str, ...],
    houses: tuple[int, ...],
    effects: tuple[str, ...],
    strength: float,
    confidence: float,
    tags: tuple[str, ...],
) -> dict:
    return {
        "rule_id": rule_id,
        "system": system,
        "domain": domain,
        "category": category,
        "title": title,
        "description": description,
        "conditions": {
            "planets": list(planets),
            "houses": list(houses),
            "signs": [],
            "nakshatras": [],
            "aspects": [],
            "dasha_lords": [],
            "transits": [],
            "tags": list(tags),
        },
        "effects": list(effects),
        "strength_weight": round(strength, 3),
        "confidence": round(confidence, 3),
        "tags": list(tags),
        "severity": "moderate" if strength < 0.75 else "high",
    }


def build_marriage_rules(min_rules: int = 300) -> dict:
    rules: list[dict] = []
    counter = 0
    for category in MARRIAGE_CATEGORIES:
        for planet in PLANETS:
            for house in (5, 7, 8, 11, 12):
                counter += 1
                rules.append(
                    _rule(
                        rule_id=f"marriage_{category}_{planet.lower()}_h{house}_{counter:04d}",
                        system="vedic",
                        domain="marriage",
                        category=category,
                        title=f"{category.replace('_', ' ').title()} — {planet} in house {house}",
                        description=(
                            f"When {planet} influences marriage axis through house {house}, "
                            f"it contributes to {category.replace('_', ' ')} indicators."
                        ),
                        planets=(planet,),
                        houses=(house,),
                        effects=[
                            f"Evaluate {planet} dignity and 7th lord relation for {category}.",
                            "Cross-check navamsha and Venus strength.",
                        ],
                        strength=0.55 + (counter % 5) * 0.05,
                        confidence=0.6 + (counter % 4) * 0.05,
                        tags=(category, planet.lower(), f"house_{house}", "marriage"),
                    )
                )
                if len(rules) >= min_rules:
                    break
            if len(rules) >= min_rules:
                break
        if len(rules) >= min_rules:
            break

    # Lal Kitab marriage supplements
    for idx in range(20):
        rules.append(
            _rule(
                rule_id=f"marriage_lk_supplement_{idx:03d}",
                system="lal_kitab",
                domain="marriage",
                category=MARRIAGE_CATEGORIES[idx % len(MARRIAGE_CATEGORIES)],
                title=f"Lal Kitab marriage indicator {idx + 1}",
                description="Lal Kitab planet-house protocol affecting marriage timing and harmony.",
                planets=(PLANETS[idx % len(PLANETS)],),
                houses=(7, 8),
                effects=["Apply Lal Kitab house-based interpretation."],
                strength=0.65,
                confidence=0.62,
                tags=("lal_kitab", "marriage"),
            )
        )

    return {
        "domain": "marriage",
        "version": "1.0",
        "count": len(rules),
        "categories": list(MARRIAGE_CATEGORIES),
        "rules": rules,
    }


def build_career_rules(min_rules: int = 300) -> dict:
    rules: list[dict] = []
    counter = 0
    career_houses = (2, 6, 7, 10, 11)
    for category in CAREER_CATEGORIES:
        for planet in PLANETS:
            for house in career_houses:
                counter += 1
                rules.append(
                    _rule(
                        rule_id=f"career_{category}_{planet.lower()}_h{house}_{counter:04d}",
                        system="vedic",
                        domain="career",
                        category=category,
                        title=f"{category.replace('_', ' ').title()} — {planet} in house {house}",
                        description=(
                            f"{planet} influencing house {house} contributes to {category.replace('_', ' ')} "
                            "career patterns when supported by dasha."
                        ),
                        planets=(planet,),
                        houses=(house,),
                        effects=[
                            f"Assess 10th lord and {planet} dignity for {category}.",
                            "Review Saturn/Jupiter support for stability.",
                        ],
                        strength=0.5 + (counter % 6) * 0.05,
                        confidence=0.58 + (counter % 5) * 0.04,
                        tags=(category, planet.lower(), f"house_{house}", "career"),
                    )
                )
                if len(rules) >= min_rules:
                    break
            if len(rules) >= min_rules:
                break
        if len(rules) >= min_rules:
            break

    idx = 0
    while len(rules) < min_rules:
        rules.append(
            _rule(
                rule_id=f"career_kp_supplement_{idx:03d}",
                system="kp",
                domain="career",
                category=CAREER_CATEGORIES[idx % len(CAREER_CATEGORIES)],
                title=f"KP career significator rule {idx + 1}",
                description="KP significator chain influencing career event fructification.",
                planets=(PLANETS[idx % len(PLANETS)],),
                houses=(6, 10, 11),
                effects=["Verify cusp sub lord and event support score."],
                strength=0.63,
                confidence=0.6,
                tags=("kp", "career", "significator"),
            )
        )
        idx += 1

    return {
        "domain": "career",
        "version": "1.0",
        "count": len(rules),
        "categories": list(CAREER_CATEGORIES),
        "rules": rules,
    }


def build_health_rules(min_rules: int = 150) -> dict:
    rules: list[dict] = []
    counter = 0
    health_houses = (1, 6, 8, 12)
    for category in HEALTH_CATEGORIES:
        for planet in PLANETS:
            for house in health_houses:
                counter += 1
                rules.append(
                    _rule(
                        rule_id=f"health_{category}_{planet.lower()}_h{house}_{counter:04d}",
                        system="vedic",
                        domain="health",
                        category=category,
                        title=f"{category.replace('_', ' ').title()} — {planet} in house {house}",
                        description=f"{planet} in dusthana-related house {house} contributes to {category} themes.",
                        planets=(planet,),
                        houses=(house,),
                        effects=[f"Check 6th/8th lord relation for {category}."],
                        strength=0.55 + (counter % 4) * 0.06,
                        confidence=0.62,
                        tags=(category, planet.lower(), "health"),
                    )
                )
    return {"domain": "health", "version": "1.0", "count": len(rules), "categories": list(HEALTH_CATEGORIES), "rules": rules}


def build_finance_rules(min_rules: int = 150) -> dict:
    rules: list[dict] = []
    counter = 0
    finance_houses = (2, 5, 8, 11, 12)
    for category in FINANCE_CATEGORIES:
        for planet in PLANETS:
            for house in finance_houses:
                counter += 1
                rules.append(
                    _rule(
                        rule_id=f"finance_{category}_{planet.lower()}_h{house}_{counter:04d}",
                        system="vedic",
                        domain="finance",
                        category=category,
                        title=f"{category.replace('_', ' ').title()} — {planet} in house {house}",
                        description=f"{planet} in house {house} influences {category} outcomes in finance domain.",
                        planets=(planet,),
                        houses=(house,),
                        effects=[f"Assess 2nd/11th lords for {category}."],
                        strength=0.52 + (counter % 5) * 0.05,
                        confidence=0.6,
                        tags=(category, planet.lower(), "finance"),
                    )
                )
    return {"domain": "finance", "version": "1.0", "count": len(rules), "categories": list(FINANCE_CATEGORIES), "rules": rules}
