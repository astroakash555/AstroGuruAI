"""Pydantic schema for remedy generation JSON."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GeneratedRemedySchema(BaseSchema):
    remedy_type: str
    astrology_system: str
    title: str
    description: str
    planet: str | None = None
    house: int | None = Field(default=None, ge=1, le=12)
    priority: int = Field(..., ge=1)
    confidence_score: float = Field(..., ge=0, le=1)
    expected_effect: str


class RemedyGenerationJSON(BaseSchema):
    generated_at: datetime
    remedies: list[GeneratedRemedySchema]
    summary: str
    metadata: dict[str, object]
