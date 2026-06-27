"""Pydantic schema for client report JSON."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ClientReportJSON(BaseSchema):
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
    metadata: dict[str, object]
