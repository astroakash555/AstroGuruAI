"""Horoscope JSON schema."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HoroscopePeriodSchema(BaseSchema):
    period_type: str
    start_date: date
    end_date: date
    theme: str
    focus_areas: list[str]
    guidance: list[str]
    energy_score: float = Field(..., ge=0, le=1)


class HoroscopeJSON(BaseSchema):
    generated_at: datetime
    moon_sign: str
    lagna_sign: str
    daily: HoroscopePeriodSchema
    weekly: HoroscopePeriodSchema
    monthly: HoroscopePeriodSchema
    metadata: dict[str, object]
