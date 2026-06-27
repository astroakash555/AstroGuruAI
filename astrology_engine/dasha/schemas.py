"""Pydantic schemas for structured Vimshottari dasha JSON output."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PeriodSchema(BaseSchema):
    lord: str
    start: datetime
    end: datetime
    duration_years: float = Field(..., ge=0)
    duration_days: float = Field(..., ge=0)
    level: str


class PratyantarDashaSchema(PeriodSchema):
    level: str = "pratyantar"


class AntardashaSchema(PeriodSchema):
    level: str = "antardasha"
    pratyantar_dashas: list[PratyantarDashaSchema]


class MahadashaSchema(PeriodSchema):
    level: str = "mahadasha"
    antardashas: list[AntardashaSchema]


class MoonContextSchema(BaseSchema):
    longitude: float
    nakshatra: str
    nakshatra_index: int
    pada: int
    lord: str


class BalanceSchema(BaseSchema):
    lord: str
    elapsed_fraction: float = Field(..., ge=0, le=1)
    remaining_fraction: float = Field(..., ge=0, le=1)
    duration_years: float = Field(..., ge=0)
    duration_days: float = Field(..., ge=0)


class BirthSchema(BaseSchema):
    datetime: datetime
    birth_place: str
    timezone: str
    date_of_birth: str
    birth_time: str


class ActiveDashaSchema(BaseSchema):
    lord: str
    start: datetime
    end: datetime
    duration_years: float
    duration_days: float


class CurrentDashaSchema(BaseSchema):
    mahadasha: ActiveDashaSchema | None = None
    antardasha: ActiveDashaSchema | None = None
    pratyantar_dasha: ActiveDashaSchema | None = None


class VimshottariDashaJSON(BaseSchema):
    """Top-level structured JSON output for Vimshottari dasha."""

    system: str = "vimshottari"
    birth: BirthSchema
    moon: MoonContextSchema
    balance: BalanceSchema
    current: CurrentDashaSchema
    mahadashas: list[MahadashaSchema]
