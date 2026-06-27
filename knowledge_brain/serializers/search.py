"""Knowledge search serializers."""

from __future__ import annotations

from typing import Any

from knowledge_brain.models.search import KnowledgeSearchResult
from knowledge_brain.schemas.search import KnowledgeSearchJSON


def to_json_dict(result: KnowledgeSearchResult) -> dict[str, Any]:
    payload = KnowledgeSearchJSON(
        queried_at=result.queried_at,
        query={
            "problem_text": result.query.problem_text,
            "domain": result.query.domain,
            "category": result.query.category,
            "systems": list(result.query.systems),
            "planets": list(result.query.planets),
            "houses": list(result.query.houses),
            "signs": list(result.query.signs),
            "tags": list(result.query.tags),
            "max_results": result.query.max_results,
        },
        ranked_rules=[
            {
                "rule_id": item.rule.rule_id,
                "system": item.rule.system,
                "domain": item.rule.domain,
                "category": item.rule.category,
                "title": item.rule.title,
                "description": item.rule.description,
                "score": item.score,
                "match_reasons": list(item.match_reasons),
                "conditions": {
                    "planets": list(item.rule.conditions.planets),
                    "houses": list(item.rule.conditions.houses),
                    "tags": list(item.rule.tags),
                },
                "effects": list(item.rule.effects),
                "confidence": item.rule.confidence,
            }
            for item in result.ranked_rules
        ],
        matched_entities=list(result.matched_entities),
        summary=dict(result.summary),
        metadata=dict(result.metadata),
    )
    return payload.model_dump(mode="json")
