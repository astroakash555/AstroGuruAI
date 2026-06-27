"""Client API endpoint tests with mocked service layer."""

import uuid
from datetime import date, datetime, time, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.v1.endpoints.clients import get_client_service
from backend.app.models.enums import Gender
from backend.app.schemas.client import ClientListResponse, ClientResponse
from backend.app.services.client_service import ClientService
from tests.helpers import override_current_user


@pytest.fixture
def sample_client_response() -> ClientResponse:
    now = datetime.now(timezone.utc)
    return ClientResponse(
        id=uuid.uuid4(),
        name="Love Sharma",
        gender=Gender.MALE,
        email=None,
        phone=None,
        preferred_language="en",
        timezone="Asia/Kolkata",
        notes=None,
        is_active=True,
        birth_detail={
            "id": uuid.uuid4(),
            "date_of_birth": date(1995, 6, 15),
            "birth_time": time(10, 30),
            "birth_place": "New Delhi, India",
            "birth_datetime": datetime(1995, 6, 15, 10, 30, tzinfo=timezone.utc),
            "timezone": "Asia/Kolkata",
            "latitude": Decimal("28.6139"),
            "longitude": Decimal("77.2090"),
            "is_primary": True,
        },
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def mock_client_service(sample_client_response: ClientResponse) -> AsyncMock:
    service = AsyncMock(spec=ClientService)
    service.create_client.return_value = sample_client_response
    service.get_client.return_value = sample_client_response
    service.list_clients.return_value = ClientListResponse(
        items=[sample_client_response],
        total=1,
        page=1,
        page_size=20,
        pages=1,
    )
    service.update_client.return_value = sample_client_response
    service.delete_client.return_value = None
    return service


@pytest.fixture
async def client_with_service(app, mock_client_service: AsyncMock, test_user):
    app.dependency_overrides[get_client_service] = lambda: mock_client_service
    override_current_user(app, test_user)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_client_endpoint(client_with_service, mock_client_service):
    payload = {
        "name": "Love Sharma",
        "gender": "male",
        "date_of_birth": "1995-06-15",
        "birth_time": "10:30:00",
        "birth_place": "New Delhi, India",
        "timezone": "Asia/Kolkata",
    }
    response = await client_with_service.post("/api/v1/clients", json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "Love Sharma"
    mock_client_service.create_client.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_clients_endpoint(client_with_service):
    response = await client_with_service.get("/api/v1/clients")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


@pytest.mark.asyncio
async def test_get_client_endpoint(client_with_service, sample_client_response):
    response = await client_with_service.get(f"/api/v1/clients/{sample_client_response.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(sample_client_response.id)


@pytest.mark.asyncio
async def test_update_client_endpoint(
    client_with_service,
    sample_client_response,
    mock_client_service: AsyncMock,
):
    response = await client_with_service.patch(
        f"/api/v1/clients/{sample_client_response.id}",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 200
    mock_client_service.update_client.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_client_endpoint(
    client_with_service,
    sample_client_response,
    mock_client_service: AsyncMock,
):
    response = await client_with_service.delete(f"/api/v1/clients/{sample_client_response.id}")
    assert response.status_code == 204
    mock_client_service.delete_client.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_client_validation_error(client_with_service):
    response = await client_with_service.post(
        "/api/v1/clients",
        json={
            "name": "A",
            "gender": "male",
            "date_of_birth": "1995-06-15",
            "birth_time": "10:30:00",
            "birth_place": "Delhi",
        },
    )
    assert response.status_code == 422
