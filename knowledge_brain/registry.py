"""Unified knowledge registry."""

from __future__ import annotations

from knowledge_brain.loader import KnowledgeLoader
from knowledge_brain.models.entities import KnowledgeEntity
from knowledge_brain.models.rules import AstrologyRule


class KnowledgeRegistry:
    """Central registry for all astrology knowledge assets."""

    def __init__(self, loader: KnowledgeLoader | None = None) -> None:
        self._loader = loader or KnowledgeLoader()
        self._entities: tuple[KnowledgeEntity, ...] | None = None
        self._rules: tuple[AstrologyRule, ...] | None = None
        self._manifest: dict | None = None

    @property
    def manifest(self) -> dict:
        if self._manifest is None:
            self._manifest = self._loader.load_manifest()
        return self._manifest

    @property
    def entities(self) -> tuple[KnowledgeEntity, ...]:
        if self._entities is None:
            self._entities = self._loader.load_all_vedic_entities()
        return self._entities

    @property
    def rules(self) -> tuple[AstrologyRule, ...]:
        if self._rules is None:
            self._rules = self._loader.load_all_domain_rules()
        return self._rules

    def rules_by_domain(self, domain: str) -> tuple[AstrologyRule, ...]:
        return tuple(rule for rule in self.rules if rule.domain == domain)

    def rules_by_category(self, category: str) -> tuple[AstrologyRule, ...]:
        return tuple(rule for rule in self.rules if rule.category == category)

    def entities_by_type(self, entity_type: str) -> tuple[KnowledgeEntity, ...]:
        return tuple(entity for entity in self.entities if entity.entity_type == entity_type)

    def entity_by_id(self, entity_id: str) -> KnowledgeEntity | None:
        for entity in self.entities:
            if entity.entity_id == entity_id:
                return entity
        return None
