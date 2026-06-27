"""Rule conflict detection."""

from __future__ import annotations

from rule_studio.constants import CONFLICT_OVERLAP_THRESHOLD
from rule_studio.types import ExpertRule, RuleConflict


def detect_conflicts(rules: tuple[ExpertRule, ...]) -> tuple[RuleConflict, ...]:
    conflicts: list[RuleConflict] = []
    active_rules = [rule for rule in rules if rule.is_active or rule.status in {"approved", "active"}]

    for index, rule_a in enumerate(active_rules):
        for rule_b in active_rules[index + 1 :]:
            if rule_a.system != rule_b.system:
                continue
            overlap = _condition_overlap(rule_a, rule_b)
            if overlap < CONFLICT_OVERLAP_THRESHOLD:
                continue
            if rule_a.outcome == rule_b.outcome:
                continue

            conflict_type = "outcome_conflict"
            if rule_a.domain and rule_b.domain and rule_a.domain == rule_b.domain:
                conflict_type = "domain_outcome_conflict"

            conflicts.append(
                RuleConflict(
                    rule_id_a=rule_a.rule_id,
                    rule_id_b=rule_b.rule_id,
                    conflict_type=conflict_type,
                    overlap_score=round(overlap, 3),
                    details={
                        "system": rule_a.system,
                        "outcome_a": rule_a.outcome,
                        "outcome_b": rule_b.outcome,
                        "domain_a": rule_a.domain,
                        "domain_b": rule_b.domain,
                    },
                )
            )
    return tuple(conflicts)


def _condition_overlap(rule_a: ExpertRule, rule_b: ExpertRule) -> float:
    scores: list[float] = []

    planet_overlap = _set_overlap(rule_a.conditions.planets, rule_b.conditions.planets)
    if planet_overlap is not None:
        scores.append(planet_overlap)

    house_overlap = _set_overlap(rule_a.conditions.houses, rule_b.conditions.houses)
    if house_overlap is not None:
        scores.append(house_overlap)

    tag_overlap = _set_overlap(rule_a.conditions.tags, rule_b.conditions.tags)
    if tag_overlap is not None:
        scores.append(tag_overlap)

    if rule_a.domain and rule_b.domain and rule_a.domain == rule_b.domain:
        scores.append(1.0)

    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def _set_overlap(a: tuple, b: tuple) -> float | None:
    set_a, set_b = set(a), set(b)
    if not set_a and not set_b:
        return None
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)
