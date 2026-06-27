"""Agent 5 — Senior Astro Guru."""

from __future__ import annotations

from typing import Any

from consultation_layer.constants import AGENT_SENIOR_GURU
from consultation_layer.types import AgentFinding, SeniorGuruConclusion
from reasoning_layer.types import AuditEntry


def synthesize_conclusion(
    specialists: tuple[AgentFinding, ...],
    report: dict[str, Any],
) -> SeniorGuruConclusion:
    reasoning = report.get("reasoning", {})
    remedies = report.get("remedy_recommendations", {})

    compared = {
        agent.agent_id: {
            "confidence": agent.confidence,
            "key_findings": _extract_key_findings(agent),
            "evidence_count": len(agent.evidence),
        }
        for agent in specialists
    }

    resolved_conflicts = _resolve_conflicts(specialists, reasoning)
    strongest_causes = _select_strongest_causes(specialists, reasoning)
    strongest_remedies = _select_strongest_remedies(specialists, remedies)

    consensus = reasoning.get("consensus", {}) if reasoning else {}
    final_conclusion = {
        "problem_domain": reasoning.get("problem_domain") or _infer_domain(specialists),
        "consensus_outcome": consensus.get("final_consensus", "mixed_signals"),
        "confidence_score": reasoning.get("confidence", {}).get("overall_score"),
        "primary_causes": [cause["planet"] for cause in strongest_causes[:3] if cause.get("planet")],
        "recommended_remedy_ids": [
            remedy["remedy_id"] for remedy in strongest_remedies[:3]
        ],
        "supporting_systems": _supporting_systems(specialists),
    }

    audit: list[AuditEntry] = []
    for agent in specialists:
        audit.extend(agent.audit)

    if reasoning:
        for entry in reasoning.get("audit_trail", []):
            audit.append(
                AuditEntry(
                    rule_source=entry.get("rule_source", "reasoning_layer"),
                    engine_source=AGENT_SENIOR_GURU,
                    reason_used=entry.get("reason_used", "Reasoning layer evidence"),
                    reference_id=entry.get("reference_id"),
                )
            )

    audit.append(
        AuditEntry(
            rule_source="consultation_synthesis",
            engine_source=AGENT_SENIOR_GURU,
            reason_used="Final conclusion synthesized from specialist agents",
        )
    )

    return SeniorGuruConclusion(
        compared_findings=compared,
        resolved_conflicts=tuple(resolved_conflicts),
        strongest_causes=tuple(strongest_causes),
        strongest_remedies=tuple(strongest_remedies),
        final_conclusion=final_conclusion,
        audit=tuple(audit),
    )


def _extract_key_findings(agent: AgentFinding) -> list[str]:
    if agent.agent_id == "vedic_astrologer":
        return list(agent.findings.get("root_cause_planets", []))
    if agent.agent_id == "kp_astrologer":
        return [
            event.get("event_id", "")
            for event in agent.findings.get("event_timing", [])
            if event.get("is_supported")
        ]
    if agent.agent_id == "lal_kitab_expert":
        return [
            item.get("finding_id", "")
            for item in agent.findings.get("dosh_analysis", [])
        ]
    if agent.agent_id == "problem_specialist":
        return [
            group.get("group_id", "")
            for group in agent.findings.get("matched_rule_groups", [])
        ]
    return list(agent.evidence[:3])


def _resolve_conflicts(
    specialists: tuple[AgentFinding, ...],
    reasoning: dict[str, Any],
) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []

    for contradiction in reasoning.get("contradictions", []) if reasoning else []:
        resolved.append(
            {
                "topic": contradiction.get("topic"),
                "resolution": "evidence_weighted",
                "confidence_score": contradiction.get("confidence_score"),
                "supporting_systems": [
                    item.get("system")
                    for item in contradiction.get("supporting_evidence", [])
                ],
                "opposing_systems": [
                    item.get("system")
                    for item in contradiction.get("opposing_evidence", [])
                ],
            }
        )

    vedic = _find_agent(specialists, "vedic_astrologer")
    kp = _find_agent(specialists, "kp_astrologer")
    if vedic and kp:
        vedic_doshas = len(vedic.findings.get("dosha_findings", []))
        kp_supported = sum(
            1 for event in kp.findings.get("event_timing", [])
            if event.get("is_supported")
        )
        if vedic_doshas > 0 and kp_supported == 0:
            resolved.append(
                {
                    "topic": "vedic_dosha_vs_kp_delay",
                    "resolution": "timing_delay_with_structural_block",
                    "confidence_score": round((vedic.confidence + kp.confidence) / 2 * 100, 1),
                    "supporting_systems": ["vedic"],
                    "opposing_systems": ["kp"],
                }
            )

    return resolved


def _select_strongest_causes(
    specialists: tuple[AgentFinding, ...],
    reasoning: dict[str, Any],
) -> list[dict[str, Any]]:
    causes: list[dict[str, Any]] = []

    for item in reasoning.get("root_causes", []) if reasoning else []:
        causes.append(
            {
                "cause_type": item.get("cause_type"),
                "planet": item.get("triggering_planet"),
                "supporting_planet": item.get("supporting_planet"),
                "severity": item.get("severity"),
                "source": "reasoning_layer",
            }
        )

    vedic = _find_agent(specialists, "vedic_astrologer")
    if vedic:
        for planet in vedic.findings.get("root_cause_planets", []):
            causes.append(
                {
                    "cause_type": "vedic_root",
                    "planet": planet,
                    "severity": vedic.confidence,
                    "source": "vedic_astrologer",
                }
            )

    causes.sort(key=lambda item: item.get("severity", 0), reverse=True)
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for cause in causes:
        key = f"{cause.get('planet')}:{cause.get('cause_type')}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(cause)
    return unique[:5]


def _select_strongest_remedies(
    specialists: tuple[AgentFinding, ...],
    remedies: dict[str, Any],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []

    for match in remedies.get("matched_remedies", []):
        remedy = match.get("remedy", {})
        selected.append(
            {
                "remedy_id": remedy.get("remedy_id"),
                "remedy_name": remedy.get("remedy_name"),
                "astrology_system": remedy.get("astrology_system"),
                "match_score": match.get("match_score"),
                "match_reasons": match.get("match_reasons", []),
                "source": "remedy_engine",
            }
        )

    lk = _find_agent(specialists, "lal_kitab_expert")
    if lk:
        for remedy in lk.findings.get("remedy_selection", []):
            selected.append(
                {
                    "remedy_id": remedy.get("remedy_id"),
                    "remedy_name": remedy.get("remedy_name"),
                    "astrology_system": "lal_kitab",
                    "match_score": remedy.get("match_score"),
                    "match_reasons": remedy.get("match_reasons", []),
                    "source": "lal_kitab_expert",
                }
            )

    selected.sort(key=lambda item: item.get("match_score") or 0, reverse=True)
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for remedy in selected:
        remedy_id = remedy.get("remedy_id")
        if not remedy_id or remedy_id in seen:
            continue
        seen.add(remedy_id)
        unique.append(remedy)
    return unique[:5]


def _supporting_systems(specialists: tuple[AgentFinding, ...]) -> list[str]:
    return [
        agent.agent_id
        for agent in specialists
        if agent.confidence >= 0.5
    ]


def _infer_domain(specialists: tuple[AgentFinding, ...]) -> str | None:
    problem = _find_agent(specialists, "problem_specialist")
    if problem:
        return problem.findings.get("problem_understanding", {}).get("category")
    return None


def _find_agent(specialists: tuple[AgentFinding, ...], agent_id: str) -> AgentFinding | None:
    for agent in specialists:
        if agent.agent_id == agent_id:
            return agent
    return None
