"""Pydantic schema for astro interpretation JSON."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AstroInterpretationJSON(BaseSchema):
    generated_at: datetime
    root_cause_explanation: str
    affected_planets_explanation: str
    affected_houses_explanation: str
    dasha_impact_explanation: str
    transit_impact_explanation: str
    kp_findings_explanation: str
    lal_kitab_findings_explanation: str
    summary: str
    metadata: dict[str, object]
