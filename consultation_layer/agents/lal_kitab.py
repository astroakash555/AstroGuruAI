"""Agent 3 — Lal Kitab Expert."""

from __future__ import annotations

from typing import Any

from consultation_layer.constants import AGENT_LAL_KITAB
from consultation_layer.types import AgentFinding
from reasoning_layer.types import AuditEntry


def analyze_lal_kitab(report: dict[str, Any]) -> AgentFinding:
    lk = report.get("lal_kitab", {})
    remedies = report.get("remedy_recommendations", {})

    rin_findings = [
        {
            "finding_id": item.get("finding_id"),
            "finding_name": item.get("finding_name"),
            "is_present": item.get("is_present"),
            "strength": item.get("strength"),
            "planets_involved": item.get("planets_involved", []),
        }
        for item in lk.get("rin_findings", [])
        if item.get("is_present")
    ]

    dosh_findings = [
        {
            "finding_id": item.get("finding_id"),
            "finding_name": item.get("finding_name"),
            "is_present": item.get("is_present"),
            "strength": item.get("strength"),
            "planets_involved": item.get("planets_involved", []),
            "recommendation_ids": item.get("recommendation_ids", []),
        }
        for item in lk.get("dosh_findings", [])
        if item.get("is_present")
    ]

    lk_remedies = [
        {
            "remedy_id": match.get("remedy", {}).get("remedy_id"),
            "remedy_name": match.get("remedy", {}).get("remedy_name"),
            "match_score": match.get("match_score"),
            "match_reasons": match.get("match_reasons", []),
        }
        for match in remedies.get("matched_remedies", [])
        if match.get("remedy", {}).get("astrology_system") == "lal_kitab"
    ]

    if not lk_remedies:
        lk_remedies = [
            {
                "remedy_id": item.get("finding_id"),
                "remedy_name": item.get("finding_name"),
                "match_score": item.get("strength"),
                "match_reasons": item.get("recommendation_ids", []),
            }
            for item in lk.get("recommendations", [])
            if item.get("is_present")
        ]

    audit: list[AuditEntry] = []
    evidence: list[str] = []

    for finding in rin_findings:
        evidence.append(f"rin:{finding['finding_id']}:strength:{finding['strength']}")
        audit.append(
            AuditEntry(
                rule_source="lal_kitab_rin",
                engine_source=AGENT_LAL_KITAB,
                reason_used=f"Rin {finding['finding_id']} present",
                reference_id=finding["finding_id"],
            )
        )

    for finding in dosh_findings:
        evidence.append(f"dosh:{finding['finding_id']}:strength:{finding['strength']}")
        audit.append(
            AuditEntry(
                rule_source="lal_kitab_dosh",
                engine_source=AGENT_LAL_KITAB,
                reason_used=f"Dosh {finding['finding_id']} present",
                reference_id=finding["finding_id"],
            )
        )

    for remedy in lk_remedies[:5]:
        evidence.append(f"remedy:{remedy['remedy_id']}:score:{remedy['match_score']}")
        audit.append(
            AuditEntry(
                rule_source="remedy_engine",
                engine_source=AGENT_LAL_KITAB,
                reason_used=f"Selected remedy {remedy['remedy_id']}",
                reference_id=remedy["remedy_id"],
            )
        )

    confidence = min(1.0, 0.35 + len(dosh_findings) * 0.1 + len(lk_remedies) * 0.08)

    return AgentFinding(
        agent_id=AGENT_LAL_KITAB,
        agent_role="Lal Kitab Expert",
        findings={
            "rin_analysis": rin_findings,
            "dosh_analysis": dosh_findings,
            "remedy_selection": lk_remedies,
            "summary": lk.get("summary", {}),
        },
        evidence=tuple(evidence),
        confidence=round(confidence, 3),
        audit=tuple(audit),
    )
