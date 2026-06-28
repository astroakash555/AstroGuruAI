"""Geographic coordinate validation for birth data."""

from __future__ import annotations

from backend.app.core.exceptions import ValidationError

NULL_ISLAND_TOLERANCE = 0.001


def is_null_island(latitude: float, longitude: float) -> bool:
    """Return True when coordinates are effectively 0,0 (Null Island)."""
    return abs(latitude) <= NULL_ISLAND_TOLERANCE and abs(longitude) <= NULL_ISLAND_TOLERANCE


def validate_birth_coordinates(
    latitude: float,
    longitude: float,
    *,
    birth_place: str = "",
) -> None:
    """
    Reject placeholder 0,0 coordinates unless the birth place is explicitly Null Island.

    Swiss Ephemeris accepts 0,0 as valid input, but it produces meaningless charts
    when users omit geocoding. This guard prevents silent bad data.
    """
    if not (-90.0 <= latitude <= 90.0):
        raise ValidationError(f"Invalid latitude {latitude}: must be between -90 and 90.")
    if not (-180.0 <= longitude <= 180.0):
        raise ValidationError(f"Invalid longitude {longitude}: must be between -180 and 180.")
    if is_null_island(latitude, longitude) and "null island" not in birth_place.lower():
        raise ValidationError(
            "Birth place coordinates are invalid (0,0). Select a resolved location from autocomplete."
        )
