"""Pydantic schemas for remedy JSON output."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RemedyRecordSchema(BaseSchema):
    remedy_id: str
    remedy_name: str
    remedy_type: str
    astrology_system: str
    planet: str | None = None
    house: int | None = Field(default=None, ge=1, le=12)
    severity: str
    category: str
    description: str
    expected_effect: str
    confidence_score: float = Field(..., ge=0, le=1)
    priority: int = Field(..., ge=1)


class RemedyMatchSchema(BaseSchema):
    remedy: RemedyRecordSchema
    match_score: float = Field(..., ge=0, le=1)
    match_reasons: list[str]


class RemedyMatchResultJSON(BaseSchema):
    matched_remedies: list[RemedyMatchSchema]
    metadata: dict[str, object]


class RemedyKnowledgeJSON(BaseSchema):
    remedies: list[RemedyRecordSchema]
    total_count: int = Field(..., ge=0)
    metadata: dict[str, object]
