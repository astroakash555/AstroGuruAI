"""Naming suggestion JSON schema."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class NameSuggestionSchema(BaseSchema):
    name: str
    syllable_seed: str
    nakshatra: str
    pada: int = Field(..., ge=1, le=4)
    rashi: str
    score: float = Field(..., ge=0, le=1)
    reasoning: str


class NamingJSON(BaseSchema):
    generated_at: datetime
    suggestions: list[NameSuggestionSchema]
    metadata: dict[str, object]
