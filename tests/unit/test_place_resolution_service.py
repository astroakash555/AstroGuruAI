"""Place resolution service tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.core.exceptions import ValidationError
from backend.app.services.place_resolution_service import PlaceResolutionService


NOMINATIM_SEARCH_RESPONSE = [
    {
        "place_id": 123456,
        "osm_type": "relation",
        "osm_id": 1942586,
        "lat": "28.6139391",
        "lon": "77.2090212",
        "display_name": "New Delhi, Delhi, India",
        "address": {
            "city": "New Delhi",
            "state": "Delhi",
            "country": "India",
        },
    }
]


@pytest.fixture
def mock_http_client() -> AsyncMock:
    client = AsyncMock()
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json = MagicMock(return_value=NOMINATIM_SEARCH_RESPONSE)
    client.get = AsyncMock(return_value=response)
    return client


@pytest.fixture
def place_service(mock_http_client: AsyncMock) -> PlaceResolutionService:
    service = PlaceResolutionService(client=mock_http_client)
    finder = MagicMock()
    finder.timezone_at.return_value = "Asia/Kolkata"
    service._timezone_finder = finder
    return service


@pytest.mark.asyncio
async def test_autocomplete_returns_suggestions(place_service: PlaceResolutionService) -> None:
    suggestions = await place_service.autocomplete("New Delhi")
    assert len(suggestions) == 1
    assert suggestions[0].place_id == "R1942586"
    assert "New Delhi" in suggestions[0].label


@pytest.mark.asyncio
async def test_resolve_by_query_returns_coordinates_and_timezone(
    place_service: PlaceResolutionService,
) -> None:
    resolved = await place_service.resolve(query="New Delhi, India")
    assert resolved.latitude == pytest.approx(28.6139391)
    assert resolved.longitude == pytest.approx(77.2090212)
    assert resolved.timezone == "Asia/Kolkata"
    assert resolved.country == "India"
    assert resolved.state == "Delhi"


@pytest.mark.asyncio
async def test_resolve_rejects_unresolvable_query(place_service: PlaceResolutionService) -> None:
    place_service._client.get.return_value.json.return_value = []
    with pytest.raises(ValidationError, match="Could not resolve"):
        await place_service.resolve(query="ZZZZZZ Not A Place")


@pytest.mark.asyncio
async def test_resolve_rejects_zero_coordinates(place_service: PlaceResolutionService) -> None:
    place_service._client.get.return_value.json.return_value = [
        {
            "place_id": 1,
            "osm_type": "node",
            "osm_id": 1,
            "lat": "0",
            "lon": "0",
            "display_name": "Atlantic Ocean",
            "address": {},
        }
    ]
    with pytest.raises(ValidationError, match="0,0"):
        await place_service.resolve(query="Ocean")
