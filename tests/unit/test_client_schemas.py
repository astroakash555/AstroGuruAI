"""Client schema validation tests."""

from datetime import date, time

import pytest
from pydantic import ValidationError

from backend.app.models.enums import Gender
from backend.app.schemas.client import ClientCreate, ClientUpdate


def test_client_create_valid_payload():
    payload = ClientCreate(
        name="Love Sharma",
        gender=Gender.MALE,
        date_of_birth=date(1995, 6, 15),
        birth_time=time(10, 30),
        birth_place="New Delhi, India",
        timezone="Asia/Kolkata",
    )
    assert payload.name == "Love Sharma"
    assert payload.gender == Gender.MALE


def test_client_create_rejects_future_birth_date():
    with pytest.raises(ValidationError) as exc:
        ClientCreate(
            name="Future Person",
            gender=Gender.FEMALE,
            date_of_birth=date(2099, 1, 1),
            birth_time=time(8, 0),
            birth_place="Mumbai",
        )
    assert "Date of birth cannot be in the future" in str(exc.value)


def test_client_create_rejects_short_name():
    with pytest.raises(ValidationError):
        ClientCreate(
            name="A",
            gender=Gender.MALE,
            date_of_birth=date(1990, 1, 1),
            birth_time=time(8, 0),
            birth_place="Delhi",
        )


def test_client_create_rejects_invalid_birth_place():
    with pytest.raises(ValidationError):
        ClientCreate(
            name="Valid Name",
            gender=Gender.MALE,
            date_of_birth=date(1990, 1, 1),
            birth_time=time(8, 0),
            birth_place="X",
        )


def test_client_create_normalizes_name_whitespace():
    payload = ClientCreate(
        name="  Love   Sharma  ",
        gender=Gender.MALE,
        date_of_birth=date(1995, 6, 15),
        birth_time=time(10, 30, 45, 999),
        birth_place="  New Delhi  ",
    )
    assert payload.name == "Love Sharma"
    assert payload.birth_time == time(10, 30, 45)
    assert payload.birth_place == "New Delhi"


def test_client_update_allows_partial_fields():
    payload = ClientUpdate(name="Updated Name")
    assert payload.name == "Updated Name"
    assert payload.gender is None
