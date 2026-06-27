"""Pydantic schemas for client management APIs."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from decimal import Decimal

from pydantic import EmailStr, Field, field_validator

from backend.app.models.enums import Gender
from backend.app.schemas.common import BaseSchema
from backend.app.schemas.validators import (
    validate_birth_date,
    validate_birth_place,
    validate_birth_time_value,
    validate_person_name,
)


class BirthInfoBase(BaseSchema):
    """Shared birth information fields with validation."""

    date_of_birth: date = Field(..., description="Client date of birth")
    birth_time: time = Field(..., description="Client birth time (local)")
    birth_place: str = Field(..., min_length=2, max_length=512, description="City/place of birth")
    timezone: str = Field(
        default="UTC",
        min_length=1,
        max_length=64,
        description="IANA timezone for birth datetime",
    )
    latitude: Decimal | None = Field(
        default=None,
        ge=Decimal("-90"),
        le=Decimal("90"),
        description="Birth place latitude (optional until geocoding)",
    )
    longitude: Decimal | None = Field(
        default=None,
        ge=Decimal("-180"),
        le=Decimal("180"),
        description="Birth place longitude (optional until geocoding)",
    )

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        return validate_birth_date(value)

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, value: time) -> time:
        return validate_birth_time_value(value)

    @field_validator("birth_place")
    @classmethod
    def validate_birth_place_field(cls, value: str) -> str:
        return validate_birth_place(value)


class ClientCreate(BaseSchema):
    """Payload for creating a new client with primary birth profile."""

    name: str = Field(..., min_length=2, max_length=255, description="Full name of the client")
    gender: Gender = Field(..., description="Client gender")
    date_of_birth: date = Field(..., description="Client date of birth")
    birth_time: time = Field(..., description="Client birth time")
    birth_place: str = Field(..., min_length=2, max_length=512, description="Birth place")
    email: EmailStr | None = Field(default=None, description="Optional contact email")
    phone: str | None = Field(default=None, max_length=32, description="Optional contact phone")
    timezone: str = Field(default="UTC", min_length=1, max_length=64)
    latitude: Decimal | None = Field(default=None, ge=Decimal("-90"), le=Decimal("90"))
    longitude: Decimal | None = Field(default=None, ge=Decimal("-180"), le=Decimal("180"))
    preferred_language: str = Field(default="en", min_length=2, max_length=10)
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return validate_person_name(value)

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        return validate_birth_date(value)

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, value: time) -> time:
        return validate_birth_time_value(value)

    @field_validator("birth_place")
    @classmethod
    def validate_birth_place_field(cls, value: str) -> str:
        return validate_birth_place(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if len(cleaned) > 32:
            raise ValueError("Phone must not exceed 32 characters.")
        return cleaned


class ClientUpdate(BaseSchema):
    """Payload for partially updating a client and primary birth profile."""

    name: str | None = Field(default=None, min_length=2, max_length=255)
    gender: Gender | None = None
    date_of_birth: date | None = None
    birth_time: time | None = None
    birth_place: str | None = Field(default=None, min_length=2, max_length=512)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    latitude: Decimal | None = Field(default=None, ge=Decimal("-90"), le=Decimal("90"))
    longitude: Decimal | None = Field(default=None, ge=Decimal("-180"), le=Decimal("180"))
    preferred_language: str | None = Field(default=None, min_length=2, max_length=10)
    notes: str | None = Field(default=None, max_length=5000)
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_person_name(value)

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is None:
            return None
        return validate_birth_date(value)

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, value: time | None) -> time | None:
        if value is None:
            return None
        return validate_birth_time_value(value)

    @field_validator("birth_place")
    @classmethod
    def validate_birth_place_field(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_birth_place(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if len(cleaned) > 32:
            raise ValueError("Phone must not exceed 32 characters.")
        return cleaned


class BirthDetailResponse(BaseSchema):
    """Primary birth profile embedded in client responses."""

    id: uuid.UUID
    date_of_birth: date
    birth_time: time
    birth_place: str
    birth_datetime: datetime
    timezone: str
    latitude: Decimal
    longitude: Decimal
    is_primary: bool


class ClientResponse(BaseSchema):
    """Single client response."""

    id: uuid.UUID
    name: str
    gender: Gender
    email: str | None
    phone: str | None
    preferred_language: str
    timezone: str
    notes: str | None
    is_active: bool
    birth_detail: BirthDetailResponse | None
    created_at: datetime
    updated_at: datetime


class ClientListResponse(BaseSchema):
    """Paginated client list response."""

    items: list[ClientResponse]
    total: int
    page: int
    page_size: int
    pages: int
