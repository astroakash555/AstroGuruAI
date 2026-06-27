"""Agent 1 — Vedic Astrologer."""

from __future__ import annotations

from typing import Any

from consultation_layer.constants import AGENT_VEDIC
from consultation_layer.types import AgentFinding
from reasoning_layer.types import AuditEntry


def analyze_vedic(report: dict[str, Any]) -> AgentFinding:
    kundali = report.get("kundali", {})
    dasha = report.get("dasha", {})
    yogas = report.get("yogas", {})
    doshas = report.get("doshas", {})
    intelligence = report.get("astro_intelligence", {})

    lagna = kundali.get("ascendant", {}).get("sign", {}).get("name_en", "unknown")
    planets = kundali.get("planets", [])
    key_planets = [
        {
            "name": planet.get("name"),
            "house": planet.get("house"),
            "sign": planet.get("sign", {}).get("name_en"),
            "nakshatra": planet.get("nakshatra", {}).get("name"),
        }
        for planet in planets
    ]

    current = dasha.get("current", {})
    dasha_periods = []
    for key in ("mahadasha", "antardasha", "pratyantar_dasha"):
        period = current.get(key)
        if period:
            dasha_periods.append({"period": key, "lord": period.get("lord")})

    present_yogas = [
        {
            "yoga_id": item.get("yoga_id"),
            "strength": item.get("strength"),
            "planets_involved": item.get("planets_involved", []),
            "houses_involved": item.get("houses_involved", []),
        }
        for item in yogas.get("present_yogas", [])
    ]

    present_doshas = [
        {
            "dosha_id": item.get("dosha_id"),
            "severity": item.get("severity"),
            "planets_involved": item.get("planets_involved", []),
            "houses_involved": item.get("houses_involved", []),
        }
        for item in doshas.get("present_doshas", [])
    ]

    audit: list[AuditEntry] = []
    evidence: list[str] = []

    for dosha in present_doshas:
        evidence.append(f"dosha:{dosha['dosha_id']}:severity:{dosha['severity']}")
        audit.append(
            AuditEntry(
                rule_source="doshas_engine",
                engine_source=AGENT_VEDIC,
                reason_used=f"Present dosha {dosha['dosha_id']}",
                reference_id=dosha["dosha_id"],
            )
        )

    for yoga in present_yogas:
        evidence.append(f"yoga:{yoga['yoga_id']}:strength:{yoga['strength']}")
        audit.append(
            AuditEntry(
                rule_source="yogas_engine",
                engine_source=AGENT_VEDIC,
                reason_used=f"Present yoga {yoga['yoga_id']}",
                reference_id=yoga["yoga_id"],
            )
        )

    for period in dasha_periods:
        evidence.append(f"dasha:{period['period']}:lord:{period['lord']}")
        audit.append(
            AuditEntry(
                rule_source="dasha_engine",
                engine_source=AGENT_VEDIC,
                reason_used=f"Active {period['period']} lord {period['lord']}",
                reference_id=period["period"],
            )
        )

    confidence = min(
        1.0,
        0.4
        + len(present_yogas) * 0.05
        + len(present_doshas) * 0.05
        + (intelligence.get("confidence_score") or 0) * 0.2,
    )

    return AgentFinding(
        agent_id=AGENT_VEDIC,
        agent_role="Vedic Astrologer",
        findings={
            "kundali_analysis": {
                "lagna_sign": lagna,
                "planets": key_planets,
                "affected_houses": intelligence.get("affected_houses", []),
            },
            "dasha_analysis": {
                "system": dasha.get("system"),
                "active_periods": dasha_periods,
                "moon_nakshatra": dasha.get("moon", {}).get("nakshatra"),
            },
            "yoga_findings": present_yogas,
            "dosha_findings": present_doshas,
            "root_cause_planets": intelligence.get("root_cause_planets", []),
        },
        evidence=tuple(evidence),
        confidence=round(confidence, 3),
        audit=tuple(audit),
    )
