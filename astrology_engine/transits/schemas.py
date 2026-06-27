"""Pydantic schemas for transit JSON output."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ZodiacSignSchema(BaseSchema):
    index: int
    name_en: str
    name_sa: str
    lord: str
    degree_in_sign: float


class NakshatraSchema(BaseSchema):
    index: int
    name: str
    lord: str
    pada: int


class SnapshotSchema(BaseSchema):
    planet: str
    datetime: datetime
    longitude: float
    sign: ZodiacSignSchema
    house_from_lagna: int
    house_from_moon: int
    is_retrograde: bool
    nakshatra: NakshatraSchema
    speed: float


class SignChangeSchema(BaseSchema):
    planet: str
    datetime: datetime
    from_sign: str
    to_sign: str
    from_house_lagna: int
    to_house_lagna: int


class NatalImpactSchema(BaseSchema):
    impact_type: str
    description: str
    strength: float = Field(..., ge=0, le=1)
    target: str | None = None
    house_from_lagna: int | None = None
    house_from_moon: int | None = None


class PlanetAnalysisSchema(BaseSchema):
    planet: str
    theme: str
    current: SnapshotSchema | None
    sign_changes: list[SignChangeSchema]
    natal_impacts: list[NatalImpactSchema]
    highlights: list[str]


class DailyTransitSchema(BaseSchema):
    date: date
    snapshots: list[SnapshotSchema]
    analyses: list[PlanetAnalysisSchema]


class MonthlyTransitSchema(BaseSchema):
    year: int
    month: int
    period_start: date
    period_end: date
    sign_changes: list[SignChangeSchema]
    analyses: list[PlanetAnalysisSchema]
    highlights: list[str]


class YearlyTransitSchema(BaseSchema):
    year: int
    period_start: date
    period_end: date
    sign_changes: list[SignChangeSchema]
    monthly_highlights: list[str]
    analyses: list[PlanetAnalysisSchema]
    highlights: list[str]


class TransitAnalysisJSON(BaseSchema):
    computed_at: datetime
    natal_lagna_sign: str
    natal_moon_sign: str
    daily: DailyTransitSchema | None = None
    monthly: MonthlyTransitSchema | None = None
    yearly: YearlyTransitSchema | None = None
    saturn: PlanetAnalysisSchema
    jupiter: PlanetAnalysisSchema
    rahu: PlanetAnalysisSchema
    ketu: PlanetAnalysisSchema
    metadata: dict[str, object]
