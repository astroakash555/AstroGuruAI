"""Client report writer types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ClientReportInput:
    report_json: dict[str, Any]
    interpretation_json: dict[str, Any]
    remedy_generation_json: dict[str, Any]
    problem_text: str | None = None


@dataclass(frozen=True)
class ClientReportResult:
    generated_at: datetime
    problem_summary: str
    astrological_root_cause: str
    planet_analysis: str
    dasha_analysis: str
    transit_analysis: str
    kp_analysis: str
    lal_kitab_analysis: str
    remedies: list[dict[str, Any]]
    short_term_outlook: str
    long_term_outlook: str
    metadata: dict[str, object] = field(default_factory=dict)
