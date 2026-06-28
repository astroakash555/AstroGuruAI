"""Place resolution API schemas."""

from __future__ import annotations

from pydantic import Field

from backend.app.schemas.common import BaseSchema


class PlaceSuggestionResponse(BaseSchema):
    place_id: str
    label: str
    description: str


class PlaceAutocompleteResponse(BaseSchema):
    items: list[PlaceSuggestionResponse]


class PlaceResolveRequest(BaseSchema):
    place_id: str | None = Field(default=None, min_length=1, max_length=64)
    query: str | None = Field(default=None, min_length=2, max_length=512)


class PlaceResolveResponse(BaseSchema):
    place_id: str
    birth_place: str
    display_name: str
    latitude: float
    longitude: float
    timezone: str
    country: str | None = None
    state: str | None = None
