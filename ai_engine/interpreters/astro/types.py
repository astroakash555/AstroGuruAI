"""Astro interpretation types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class AstroInterpretationInput:
    report_json: dict[str, Any]
    locale: str = "en"


@dataclass(frozen=True)
class AstroInterpretationResult:
    generated_at: datetime
    root_cause_explanation: str
    affected_planets_explanation: str
    affected_houses_explanation: str
    dasha_impact_explanation: str
    transit_impact_explanation: str
    kp_findings_explanation: str
    lal_kitab_findings_explanation: str
    summary: str
    metadata: dict[str, object] = field(default_factory=dict)
