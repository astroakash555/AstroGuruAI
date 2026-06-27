"""Build all knowledgebase JSON databases."""

from __future__ import annotations

import json
from pathlib import Path

from knowledge_brain.builders.domain_rules import (
    build_career_rules,
    build_finance_rules,
    build_health_rules,
    build_marriage_rules,
)
from knowledge_brain.builders.kp_kb import (
    build_event_rules,
    build_significator_rules,
    build_star_lord_rules,
    build_sub_lord_rules,
)
from knowledge_brain.builders.lal_kitab_kb import (
    build_dosh_database,
    build_planet_house_database,
    build_remedy_database,
    build_rin_database,
)
from knowledge_brain.builders.vedic_core import (
    build_combinations,
    build_houses,
    build_nakshatras,
    build_padas,
    build_planets,
    build_signs,
)


def build_all(base_path: str | Path = "knowledgebase") -> dict[str, int]:
    root = Path(base_path)
    counts: dict[str, int] = {}

    def write(relative: str, payload: dict) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        key = relative.replace("\\", "/")
        counts[key] = payload.get("count", len(payload.get("rules", payload.get("entities", payload.get("entries", [])))))

    write("vedic/planets.json", build_planets())
    write("vedic/houses.json", build_houses())
    write("vedic/signs.json", build_signs())
    write("vedic/nakshatras.json", build_nakshatras())
    write("vedic/padas.json", build_padas())
    write("vedic/combinations.json", build_combinations())
    write("domains/marriage_rules.json", build_marriage_rules())
    write("domains/career_rules.json", build_career_rules())
    write("domains/health_rules.json", build_health_rules())
    write("domains/finance_rules.json", build_finance_rules())
    write("lal_kitab/rin.json", build_rin_database())
    write("lal_kitab/dosh.json", build_dosh_database())
    write("lal_kitab/remedies.json", build_remedy_database())
    write("lal_kitab/planet_house.json", build_planet_house_database())
    write("kp/event_rules.json", build_event_rules())
    write("kp/significator_rules.json", build_significator_rules())
    write("kp/star_lord_rules.json", build_star_lord_rules())
    write("kp/sub_lord_rules.json", build_sub_lord_rules())

    manifest = {
        "version": "1.0",
        "name": "AstroGuruAI Knowledge Brain",
        "systems": ["vedic", "lal_kitab", "kp"],
        "domains": ["marriage", "career", "health", "finance"],
        "files": counts,
        "total_rule_count": (
            counts.get("domains/marriage_rules.json", 0)
            + counts.get("domains/career_rules.json", 0)
            + counts.get("domains/health_rules.json", 0)
            + counts.get("domains/finance_rules.json", 0)
        ),
    }
    write("manifest.json", manifest)
    return counts


if __name__ == "__main__":
    result = build_all()
    print(json.dumps(result, indent=2))
