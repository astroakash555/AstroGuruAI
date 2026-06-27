"""Agent 4 — Problem Specialist."""

from __future__ import annotations

from typing import Any

from consultation_layer.constants import AGENT_PROBLEM
from consultation_layer.types import AgentFinding
from reasoning_layer.types import AuditEntry


HIDDEN_PROBLEM_KEYWORDS: dict[str, tuple[str, ...]] = {
    "marriage": ("commitment", "family pressure", "compatibility", "delay"),
    "career": ("stability", "recognition", "job security", "promotion block"),
    "health": ("stress", "chronic", "anxiety", "recovery"),
    "finance": ("debt", "loss", "instability", "inheritance"),
}


def analyze_problem(report: dict[str, Any], problem_text: str | None) -> AgentFinding:
    problem = report.get("problem_analysis") or {}
    reasoning = report.get("reasoning", {})
    knowledge = report.get("knowledge_search", {})

    category = problem.get("category", {}).get("category", "unknown")
    severity = problem.get("severity", {})

    problem_understanding = {
        "original_text": problem.get("original_text") or problem_text,
        "category": category,
        "severity_level": severity.get("level"),
        "severity_score": severity.get("score"),
        "primary_houses": problem.get("houses", {}).get("primary", []),
        "primary_planets": problem.get("planets", {}).get("primary", []),
    }

    hidden_problem = _detect_hidden_problem(category, problem_text, problem)
    matched_rule_groups = _match_rule_groups(knowledge, category)

    audit: list[AuditEntry] = []
    evidence: list[str] = []

    evidence.append(f"category:{category}:severity:{severity.get('score', 0)}")
    audit.append(
        AuditEntry(
            rule_source="problem_analyzer",
            engine_source=AGENT_PROBLEM,
            reason_used=f"Problem classified as {category}",
        )
    )

    for hidden in hidden_problem.get("indicators", []):
        evidence.append(f"hidden:{hidden}")
        audit.append(
            AuditEntry(
                rule_source="problem_analyzer",
                engine_source=AGENT_PROBLEM,
                reason_used=f"Hidden indicator {hidden}",
            )
        )

    for group in matched_rule_groups:
        evidence.append(f"rule_group:{group['group_id']}:count:{group['rule_count']}")
        audit.append(
            AuditEntry(
                rule_source="knowledge_brain",
                engine_source=AGENT_PROBLEM,
                reason_used=f"Matched rule group {group['group_id']}",
                reference_id=group["group_id"],
            )
        )

    confidence = min(
        1.0,
        0.3
        + (problem.get("category", {}).get("confidence") or 0.5) * 0.3
        + len(matched_rule_groups) * 0.08,
    )

    return AgentFinding(
        agent_id=AGENT_PROBLEM,
        agent_role="Problem Specialist",
        findings={
            "problem_understanding": problem_understanding,
            "hidden_problem": hidden_problem,
            "matched_rule_groups": matched_rule_groups,
        },
        evidence=tuple(evidence),
        confidence=round(confidence, 3),
        audit=tuple(audit),
    )


def _detect_hidden_problem(
    category: str,
    problem_text: str | None,
    problem: dict[str, Any],
) -> dict[str, Any]:
    text = (problem_text or problem.get("normalized_text") or "").lower()
    keywords = HIDDEN_PROBLEM_KEYWORDS.get(category, ())
    indicators = [keyword for keyword in keywords if keyword in text]

    shadow_planets = problem.get("planets", {}).get("shadow", [])
    root_indicators = problem.get("root_cause_indicators", [])

    if shadow_planets:
        indicators.extend([f"shadow_planet:{planet}" for planet in shadow_planets])
    if root_indicators:
        indicators.extend([f"root_indicator:{item}" for item in root_indicators[:3]])

    hidden_type = indicators[0] if indicators else "none_detected"
    return {
        "hidden_type": hidden_type,
        "indicators": indicators,
        "shadow_planets": shadow_planets,
    }


def _match_rule_groups(knowledge: dict[str, Any], category: str) -> list[dict[str, Any]]:
    ranked = knowledge.get("ranked_rules", []) if knowledge else []
    groups: dict[str, list[dict[str, Any]]] = {}

    for rule in ranked:
        group_key = rule.get("category") or rule.get("domain") or "general"
        groups.setdefault(group_key, []).append(rule)

    return [
        {
            "group_id": group_id,
            "domain": category,
            "rule_count": len(rules),
            "top_rule_ids": [rule.get("rule_id") for rule in rules[:3]],
            "average_score": round(
                sum(rule.get("score", 0) for rule in rules) / max(len(rules), 1),
                3,
            ),
        }
        for group_id, rules in sorted(groups.items(), key=lambda item: len(item[1]), reverse=True)[:5]
    ]
