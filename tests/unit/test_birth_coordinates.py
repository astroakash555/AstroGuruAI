"""Birth coordinate validation tests."""

import pytest

from backend.app.core.exceptions import ValidationError
from backend.app.utils.coordinates import is_null_island, validate_birth_coordinates


def test_is_null_island_detects_zero_coordinates() -> None:
    assert is_null_island(0.0, 0.0) is True
    assert is_null_island(0.0005, -0.0005) is True
    assert is_null_island(28.6139, 77.2090) is False


def test_validate_birth_coordinates_rejects_zero_by_default() -> None:
    with pytest.raises(ValidationError, match="0,0"):
        validate_birth_coordinates(0.0, 0.0, birth_place="Unknown")


def test_validate_birth_coordinates_allows_null_island_name() -> None:
    validate_birth_coordinates(0.0, 0.0, birth_place="Null Island")


def test_validate_birth_coordinates_rejects_out_of_range() -> None:
    with pytest.raises(ValidationError, match="latitude"):
        validate_birth_coordinates(95.0, 10.0)
    with pytest.raises(ValidationError, match="longitude"):
        validate_birth_coordinates(10.0, 200.0)
