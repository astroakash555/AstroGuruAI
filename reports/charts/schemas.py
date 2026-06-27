"""Pydantic schemas for chart JSON sections."""

from __future__ import annotations

from datetime import datetime

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


class PlanetSchema(BaseSchema):
    name: str
    longitude: float
    latitude: float
    speed: float
    is_retrograde: bool
    sign: ZodiacSignSchema
    nakshatra: NakshatraSchema
    house: int | None = None


class AscendantSchema(BaseSchema):
    longitude: float
    sign: ZodiacSignSchema
    nakshatra: NakshatraSchema


class HouseSchema(BaseSchema):
    number: int
    longitude: float
    sign: ZodiacSignSchema


class ChartMetadataSchema(BaseSchema):
    julian_day: float
    ayanamsa: str
    house_system: str
    latitude: float
    longitude: float
    datetime_utc: datetime


class LagnaKundaliJSON(BaseSchema):
    chart_type: str = "d1_lagna"
    metadata: ChartMetadataSchema
    ascendant: AscendantSchema
    planets: list[PlanetSchema]
    houses: list[HouseSchema]


class NavamshaChartJSON(BaseSchema):
    chart_type: str = "d9_navamsha"
    metadata: ChartMetadataSchema
    ascendant: AscendantSchema
    planets: list[PlanetSchema]
    houses: list[HouseSchema]
