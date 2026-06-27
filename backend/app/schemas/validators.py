"""Shared Pydantic field validators."""

import re
from datetime import date, time


NAME_PATTERN = re.compile(r"^[\w\s.\-'()]+$", re.UNICODE)
BIRTH_PLACE_PATTERN = re.compile(r"^[\w\s.,\-'()/]+$", re.UNICODE)


def normalize_whitespace(value: str) -> str:
    """Collapse internal whitespace and strip edges."""
    return " ".join(value.split())


def validate_person_name(value: str) -> str:
    """Validate and normalize a person's name."""
    normalized = normalize_whitespace(value)
    if len(normalized) < 2:
        raise ValueError("Name must be at least 2 characters long.")
    if len(normalized) > 255:
        raise ValueError("Name must not exceed 255 characters.")
    if not NAME_PATTERN.match(normalized):
        raise ValueError("Name contains invalid characters.")
    return normalized


def validate_birth_place(value: str) -> str:
    """Validate and normalize a birth place string."""
    normalized = normalize_whitespace(value)
    if len(normalized) < 2:
        raise ValueError("Birth place must be at least 2 characters long.")
    if len(normalized) > 512:
        raise ValueError("Birth place must not exceed 512 characters.")
    if not BIRTH_PLACE_PATTERN.match(normalized):
        raise ValueError("Birth place contains invalid characters.")
    return normalized


def validate_birth_date(value: date) -> date:
    """Ensure birth date is not in the future."""
    if value > date.today():
        raise ValueError("Date of birth cannot be in the future.")
    return value


def validate_birth_time_value(value: time) -> time:
    """Ensure birth time is provided with second precision."""
    return value.replace(microsecond=0)
