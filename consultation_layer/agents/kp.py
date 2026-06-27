"""Agent 2 — KP Astrologer."""

from __future__ import annotations

from typing import Any

from consultation_layer.constants import AGENT_KP
from consultation_layer.types import AgentFinding
from reasoning_layer.types import AuditEntry


def analyze_kp(report: dict[str, Any]) -> AgentFinding:
    kp = report.get("kp_analysis", {})
    cusps = kp.get("cusps", [])
    significators = kp.get("significators", [])
    events = kp.get("events", [])

    cuspal_analysis = [
        {
            "house": item.get("house"),
            "sign": item.get("sign"),
            "star_lord": item.get("star_lord"),
            "sub_lord": item.get("sub_lord"),
        }
        for item in cusps
    ]

    significator_analysis = [
        {
            "house": item.get("house"),
            "level_a": item.get("level_a", []),
            "level_b": item.get("level_b", []),
            "combined": item.get("combined", []),
        }
        for item in significators
    ]

    event_timing = [
        {
            "event_id": item.get("event_id"),
            "event_type": item.get("event_type"),
            "is_supported": item.get("is_supported"),
            "support_score": item.get("support_score"),
            "target_houses": item.get("target_houses", []),
            "significators_matched": item.get("significators_matched", []),
        }
        for item in events
    ]

    audit: list[AuditEntry] = []
    evidence: list[str] = []

    for event in event_timing:
        status = "supported" if event["is_supported"] else "unsupported"
        evidence.append(f"event:{event['event_id']}:{status}:{event['support_score']}")
        audit.append(
            AuditEntry(
                rule_source="kp_event_rules",
                engine_source=AGENT_KP,
                reason_used=f"Event {event['event_id']} {status} score {event['support_score']}",
                reference_id=event["event_id"],
            )
        )

    for cusp in cuspal_analysis[:4]:
        evidence.append(f"cusp:h{cusp['house']}:sub_lord:{cusp['sub_lord']}")
        audit.append(
            AuditEntry(
                rule_source="kp_cusp_rules",
                engine_source=AGENT_KP,
                reason_used=f"House {cusp['house']} sub lord {cusp['sub_lord']}",
            )
        )

    supported = sum(1 for event in event_timing if event.get("is_supported"))
    confidence = min(1.0, 0.35 + supported * 0.15 + len(significator_analysis) * 0.03)

    return AgentFinding(
        agent_id=AGENT_KP,
        agent_role="KP Astrologer",
        findings={
            "cuspal_analysis": cuspal_analysis,
            "significator_analysis": significator_analysis,
            "event_timing": event_timing,
            "summary": kp.get("summary", {}),
        },
        evidence=tuple(evidence),
        confidence=round(confidence, 3),
        audit=tuple(audit),
    )
