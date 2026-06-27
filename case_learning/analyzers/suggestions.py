"""Rule improvement and candidate suggestion analyzer."""

from __future__ import annotations

from collections import Counter
from uuid import uuid4

from case_learning.constants import OBSOLETE_RULE_THRESHOLD, TRACKED_CATEGORIES, WEAK_RULE_THRESHOLD
from case_learning.metrics.calculator import _prediction_match, _rule_match
from case_learning.types import ConsultationCase, RuleSuggestion


def generate_suggestions(cases: tuple[ConsultationCase, ...]) -> tuple[RuleSuggestion, ...]:
    suggestions: list[RuleSuggestion] = []
    rule_stats = _rule_performance(cases)

    for rule_id, stats in rule_stats.items():
        accuracy = stats["accuracy"]
        usage = stats["usage"]

        if accuracy < OBSOLETE_RULE_THRESHOLD and usage >= 2:
            suggestions.append(
                RuleSuggestion(
                    suggestion_id=str(uuid4()),
                    suggestion_type="obsolete_rule",
                    rule_id=rule_id,
                    category=stats["primary_category"],
                    priority="high",
                    reason=f"Rule {rule_id} accuracy {accuracy} across {usage} cases.",
                    suggested_action="Deactivate or archive rule; review conditions against failed cases.",
                    evidence={"accuracy": accuracy, "usage": usage, "failed_cases": stats["failed_cases"]},
                )
            )
        elif accuracy < WEAK_RULE_THRESHOLD:
            suggestions.append(
                RuleSuggestion(
                    suggestion_id=str(uuid4()),
                    suggestion_type="weak_rule",
                    rule_id=rule_id,
                    category=stats["primary_category"],
                    priority="medium",
                    reason=f"Rule {rule_id} underperforming with accuracy {accuracy}.",
                    suggested_action="Adjust weight, confidence, or conditions in rule studio.",
                    evidence={"accuracy": accuracy, "usage": usage},
                )
            )
        elif 0.45 <= accuracy < 0.7:
            suggestions.append(
                RuleSuggestion(
                    suggestion_id=str(uuid4()),
                    suggestion_type="rule_improvement",
                    rule_id=rule_id,
                    category=stats["primary_category"],
                    priority="medium",
                    reason=f"Rule {rule_id} needs refinement accuracy {accuracy}.",
                    suggested_action="Update conditions based on case learning feedback.",
                    evidence={"accuracy": accuracy, "usage": usage},
                )
            )

    for category in TRACKED_CATEGORIES:
        category_cases = [case for case in cases if case.category == category]
        no_rule_cases = [case for case in category_cases if not case.applied_rules]
        if len(no_rule_cases) >= 2:
            patterns = _extract_patterns(no_rule_cases)
            suggestions.append(
                RuleSuggestion(
                    suggestion_id=str(uuid4()),
                    suggestion_type="new_rule_candidate",
                    rule_id=None,
                    category=category,
                    priority="high" if len(no_rule_cases) >= 3 else "medium",
                    reason=f"{len(no_rule_cases)} {category} cases lack matching rules.",
                    suggested_action="Author new rule in rule studio using extracted patterns.",
                    evidence={"case_count": len(no_rule_cases), "patterns": patterns},
                )
            )

    return tuple(suggestions)


def _rule_performance(cases: tuple[ConsultationCase, ...]) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for case in cases:
        case_accuracy = _rule_match(case)
        for rule_id in case.applied_rules:
            bucket = stats.setdefault(
                rule_id,
                {
                    "usage": 0,
                    "accuracy_total": 0.0,
                    "failed_cases": [],
                    "categories": Counter(),
                },
            )
            bucket["usage"] += 1
            bucket["accuracy_total"] += case_accuracy
            bucket["categories"][case.category] += 1
            if case_accuracy < WEAK_RULE_THRESHOLD:
                bucket["failed_cases"].append(case.case_id)

    for rule_id, bucket in stats.items():
        bucket["accuracy"] = round(bucket["accuracy_total"] / bucket["usage"], 4)
        bucket["primary_category"] = bucket["categories"].most_common(1)[0][0]
    return stats


def _extract_patterns(cases: list[ConsultationCase]) -> dict[str, list]:
    planets: Counter[str] = Counter()
    houses: Counter[int] = Counter()
    outcomes: Counter[str] = Counter()

    for case in cases:
        outcomes[case.final_outcome] += 1
        for planet in case.system_prediction.get("planets", []):
            planets[planet] += 1
        for house in case.system_prediction.get("houses", []):
            houses[int(house)] += 1
        for planet in case.kundali_snapshot.get("planets", []):
            if isinstance(planet, dict) and planet.get("name"):
                planets[planet["name"]] += 1

    return {
        "top_planets": [name for name, _ in planets.most_common(3)],
        "top_houses": [house for house, _ in houses.most_common(3)],
        "top_outcomes": [outcome for outcome, _ in outcomes.most_common(3)],
    }
