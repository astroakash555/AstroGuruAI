"""Knowledge search engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from knowledge_brain.models.search import KnowledgeQuery, KnowledgeSearchResult
from knowledge_brain.registry import KnowledgeRegistry
from knowledge_brain.search.ranker import rank_rules
from knowledge_brain.serializers.search import to_json_dict


class KnowledgeSearchEngine:
    """Search and rank astrology rules relevant to a client problem."""

    DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
        "marriage": ("marriage", "wedding", "spouse", "divorce", "relationship", "love"),
        "career": ("job", "career", "business", "promotion", "employment", "work"),
        "health": ("health", "disease", "surgery", "accident", "stress", "mental"),
        "finance": ("money", "finance", "debt", "wealth", "loss", "inheritance"),
    }

    def __init__(self, registry: KnowledgeRegistry | None = None) -> None:
        self._registry = registry or KnowledgeRegistry()

    def search(self, query: KnowledgeQuery) -> KnowledgeSearchResult:
        inferred_domain = query.domain or self._infer_domain(query.problem_text)
        enriched = KnowledgeQuery(
            problem_text=query.problem_text,
            domain=inferred_domain,
            category=query.category,
            systems=query.systems,
            planets=query.planets,
            houses=query.houses,
            signs=query.signs,
            tags=query.tags,
            max_results=query.max_results,
        )

        candidate_rules = self._registry.rules
        if enriched.domain:
            domain_rules = self._registry.rules_by_domain(enriched.domain)
            candidate_rules = domain_rules if domain_rules else candidate_rules

        ranked = rank_rules(enriched, candidate_rules)
        matched_entities = self._match_entities(enriched)

        return KnowledgeSearchResult(
            queried_at=datetime.now(timezone.utc),
            query=enriched,
            ranked_rules=ranked,
            matched_entities=tuple(matched_entities),
            summary={
                "total_rules_searched": len(candidate_rules),
                "matched_rule_count": len(ranked),
                "inferred_domain": inferred_domain,
                "top_categories": list({item.rule.category for item in ranked[:5]}),
            },
            metadata={
                "engine": "knowledge_search_v1",
                "ai_prediction": False,
                "manifest_version": self._registry.manifest.get("version"),
            },
        )

    def search_json(self, query: KnowledgeQuery) -> dict[str, Any]:
        return to_json_dict(self.search(query))

    def _infer_domain(self, problem_text: str) -> str | None:
        text = problem_text.lower()
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return domain
        return None

    def _match_entities(self, query: KnowledgeQuery) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for entity in self._registry.entities:
            if query.planets and entity.name not in query.planets:
                continue
            if query.houses and entity.entity_type == "house":
                house_num = entity.metadata.get("house_number")
                if house_num not in query.houses:
                    continue
            matches.append(
                {
                    "entity_id": entity.entity_id,
                    "entity_type": entity.entity_type,
                    "name": entity.name,
                    "meanings": list(entity.meanings),
                }
            )
            if len(matches) >= 10:
                break
        return matches
