"""Rule ranking for knowledge search."""

from __future__ import annotations

from knowledge_brain.models.rules import AstrologyRule
from knowledge_brain.models.search import KnowledgeQuery, RankedRule


def rank_rules(query: KnowledgeQuery, rules: tuple[AstrologyRule, ...]) -> tuple[RankedRule, ...]:
    ranked: list[RankedRule] = []
    tokens = _tokenize(query.problem_text)

    for rule in rules:
        if rule.system not in query.systems:
            continue
        if query.domain and rule.domain != query.domain:
            continue
        if query.category and rule.category != query.category:
            continue

        score, reasons = _score_rule(rule, query, tokens)
        if score <= 0:
            continue
        ranked.append(
            RankedRule(
                rule=rule,
                score=round(min(score, 1.0), 3),
                match_reasons=tuple(reasons),
            )
        )

    ranked.sort(key=lambda item: (-item.score, -item.rule.confidence, item.rule.rule_id))
    return tuple(ranked[: query.max_results])


def _score_rule(
    rule: AstrologyRule,
    query: KnowledgeQuery,
    tokens: set[str],
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if query.planets:
        overlap = set(rule.conditions.planets) & set(query.planets)
        if overlap:
            score += 0.25 * len(overlap)
            reasons.append(f"Planet overlap: {', '.join(sorted(overlap))}.")

    if query.houses:
        overlap = set(rule.conditions.houses) & set(query.houses)
        if overlap:
            score += 0.2 * len(overlap)
            reasons.append(f"House overlap: {', '.join(str(h) for h in sorted(overlap))}.")

    if query.tags:
        overlap = set(rule.tags) & set(query.tags)
        if overlap:
            score += 0.15 * len(overlap)
            reasons.append(f"Tag overlap: {', '.join(sorted(overlap))}.")

    if tokens:
        haystack = f"{rule.title} {rule.description} {' '.join(rule.tags)}".lower()
        token_hits = sum(1 for token in tokens if token in haystack)
        if token_hits:
            score += min(0.25, token_hits * 0.05)
            reasons.append(f"Text token matches: {token_hits}.")

    if query.domain and rule.domain == query.domain:
        score += 0.1
        reasons.append(f"Domain match: {rule.domain}.")

    if query.category and rule.category == query.category:
        score += 0.15
        reasons.append(f"Category match: {rule.category}.")

    score += rule.strength_weight * 0.1
    score += rule.confidence * 0.05

    if score == 0 and not query.planets and not query.houses and not tokens:
        return 0.0, reasons

    if score == 0 and (query.planets or query.houses):
        return 0.0, reasons

    return score, reasons


def _tokenize(text: str) -> set[str]:
    if not text:
        return set()
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text.lower())
    return {token for token in cleaned.split() if len(token) > 2}
