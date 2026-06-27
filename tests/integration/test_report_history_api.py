"""Integration tests for report history API endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.v1.endpoints.dashboard import get_report_service
from backend.app.core.exceptions import NotFoundError
from backend.app.main import create_app


@pytest.fixture
def mock_report_service():
    service = AsyncMock()
    service.generate_report.return_value = {
        "report_id": str(uuid.uuid4()),
        "version": "unified_report_v2",
        "unified_report": {"summary": {"lagna_sign": "Aries"}},
        "interpretation": {},
        "remedy_generation": {},
        "client_report": {},
        "pdf": None,
        "generated_at": datetime.now(timezone.utc),
    }
    service.list_reports.return_value = {
        "items": [
            {
                "report_id": str(uuid.uuid4()),
                "client_id": None,
                "birth_detail_id": None,
                "version": "unified_report_v2",
                "problem_text": "Marriage delay",
                "lagna_sign": "Aries",
                "moon_sign": "Cancer",
                "generated_at": datetime.now(timezone.utc),
                "has_pdf": False,
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "pages": 1,
    }
    service.get_report.return_value = {
        "report_id": str(uuid.uuid4()),
        "client_id": None,
        "birth_detail_id": None,
        "version": "unified_report_v2",
        "problem_text": "Marriage delay",
        "unified_report": {"summary": {"lagna_sign": "Aries"}},
        "interpretation": {"summary": "Interpretation"},
        "remedy_generation": {"remedies": []},
        "client_report": {"problem_summary": "Marriage delay"},
        "pdf": None,
        "generated_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    service.delete_report.return_value = None
    return service


@pytest.fixture
async def history_client(mock_report_service):
    app = create_app()
    app.dependency_overrides[get_report_service] = lambda: mock_report_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_reports_endpoint(history_client, mock_report_service):
    client_id = str(uuid.uuid4())
    response = await history_client.get(
        "/api/v1/dashboard/reports",
        params={"client_id": client_id, "page": 1, "page_size": 10},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["lagna_sign"] == "Aries"
    mock_report_service.list_reports.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_report_endpoint(history_client, mock_report_service):
    report_id = uuid.uuid4()
    mock_report_service.get_report.return_value = {
        "report_id": str(report_id),
        "client_id": None,
        "birth_detail_id": None,
        "version": "unified_report_v2",
        "problem_text": "Marriage delay",
        "unified_report": {"summary": {"lagna_sign": "Aries"}},
        "interpretation": {"summary": "Interpretation"},
        "remedy_generation": {"remedies": []},
        "client_report": {"problem_summary": "Marriage delay"},
        "pdf": None,
        "generated_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    response = await history_client.get(f"/api/v1/dashboard/reports/{report_id}")
    assert response.status_code == 200
    assert response.json()["report_id"] == str(report_id)
    mock_report_service.get_report.assert_awaited_once_with(report_id)


@pytest.mark.asyncio
async def test_get_report_not_found(history_client, mock_report_service):
    report_id = uuid.uuid4()
    mock_report_service.get_report.side_effect = NotFoundError(
        f"Report with id '{report_id}' was not found."
    )

    response = await history_client.get(f"/api/v1/dashboard/reports/{report_id}")
    assert response.status_code == 404
    assert "Report" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_report_endpoint(history_client, mock_report_service):
    report_id = uuid.uuid4()
    response = await history_client.delete(f"/api/v1/dashboard/reports/{report_id}")

    assert response.status_code == 204
    mock_report_service.delete_report.assert_awaited_once_with(report_id)


@pytest.mark.asyncio
async def test_delete_report_not_found(history_client, mock_report_service):
    report_id = uuid.uuid4()
    mock_report_service.delete_report.side_effect = NotFoundError(
        f"Report with id '{report_id}' was not found."
    )

    response = await history_client.delete(f"/api/v1/dashboard/reports/{report_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_reports_invalid_client_id_returns_422(history_client):
    response = await history_client.get(
        "/api/v1/dashboard/reports",
        params={"client_id": "not-a-uuid"},
    )
    assert response.status_code == 422
