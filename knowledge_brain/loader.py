"""Load knowledge JSON databases into typed models."""

from __future__ import annotations

import json
from pathlib import Path

from knowledge_brain.models.entities import KnowledgeEntity
from knowledge_brain.models.rules import AstrologyRule, RuleConditions


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_entity(raw: dict) -> KnowledgeEntity:
    return KnowledgeEntity(
        entity_id=raw["entity_id"],
        entity_type=raw["entity_type"],
        name=raw["name"],
        system=raw["system"],
        meanings=tuple(raw.get("meanings", [])),
        strengths=tuple(raw.get("strengths", [])),
        weaknesses=tuple(raw.get("weaknesses", [])),
        effects=tuple(raw.get("effects", [])),
        metadata=dict(raw.get("metadata", {})),
    )


def _parse_rule(raw: dict) -> AstrologyRule:
    conditions_raw = raw.get("conditions", {})
    conditions = RuleConditions(
        planets=tuple(conditions_raw.get("planets", [])),
        houses=tuple(conditions_raw.get("houses", [])),
        signs=tuple(conditions_raw.get("signs", [])),
        nakshatras=tuple(conditions_raw.get("nakshatras", [])),
        aspects=tuple(conditions_raw.get("aspects", [])),
        dasha_lords=tuple(conditions_raw.get("dasha_lords", [])),
        transits=tuple(conditions_raw.get("transits", [])),
        tags=tuple(conditions_raw.get("tags", [])),
    )
    return AstrologyRule(
        rule_id=raw["rule_id"],
        system=raw["system"],
        domain=raw["domain"],
        category=raw["category"],
        title=raw["title"],
        description=raw["description"],
        conditions=conditions,
        effects=tuple(raw.get("effects", [])),
        strength_weight=float(raw.get("strength_weight", 0.5)),
        confidence=float(raw.get("confidence", 0.5)),
        tags=tuple(raw.get("tags", [])),
        severity=raw.get("severity", "moderate"),
    )


class KnowledgeLoader:
    """Load structured knowledge from the knowledgebase directory."""

    def __init__(self, base_path: str | Path = "knowledgebase") -> None:
        self._root = Path(base_path)

    @property
    def root(self) -> Path:
        return self._root

    def load_manifest(self) -> dict:
        return _load_json(self._root / "manifest.json")

    def load_entities(self, relative_path: str) -> tuple[KnowledgeEntity, ...]:
        payload = _load_json(self._root / relative_path)
        if "entities" in payload:
            return tuple(_parse_entity(item) for item in payload["entities"])
        return tuple()

    def load_rules(self, relative_path: str) -> tuple[AstrologyRule, ...]:
        payload = _load_json(self._root / relative_path)
        return tuple(_parse_rule(item) for item in payload.get("rules", []))

    def load_all_vedic_entities(self) -> tuple[KnowledgeEntity, ...]:
        paths = (
            "vedic/planets.json",
            "vedic/houses.json",
            "vedic/signs.json",
            "vedic/nakshatras.json",
            "vedic/padas.json",
        )
        entities: list[KnowledgeEntity] = []
        for path in paths:
            entities.extend(self.load_entities(path))
        return tuple(entities)

    def load_all_domain_rules(self) -> tuple[AstrologyRule, ...]:
        paths = (
            "domains/marriage_rules.json",
            "domains/career_rules.json",
            "domains/health_rules.json",
            "domains/finance_rules.json",
        )
        rules: list[AstrologyRule] = []
        for path in paths:
            rules.extend(self.load_rules(path))
        return tuple(rules)

    def load_lal_kitab_entries(self) -> dict[str, list[dict]]:
        files = ("rin.json", "dosh.json", "remedies.json", "planet_house.json")
        result: dict[str, list[dict]] = {}
        for name in files:
            payload = _load_json(self._root / "lal_kitab" / name)
            result[name.replace(".json", "")] = payload.get("entries", [])
        return result

    def load_kp_rules(self) -> dict[str, list[dict]]:
        files = (
            "event_rules.json",
            "significator_rules.json",
            "star_lord_rules.json",
            "sub_lord_rules.json",
        )
        result: dict[str, list[dict]] = {}
        for name in files:
            payload = _load_json(self._root / "kp" / name)
            result[name.replace(".json", "")] = payload.get("rules", [])
        return result
