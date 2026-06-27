"""Dashboard API tests with mocked services."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.v1.endpoints.dashboard import get_horoscope_service, get_naming_service, get_report_service
from backend.app.main import create_app
from tests.helpers import override_current_user


@pytest.fixture
def mock_report_service():
    service = AsyncMock()
    service.generate_report.return_value = {
        "report_id": "report-1",
        "version": "unified_report_v2",
        "unified_report": {"summary": {"lagna_sign": "Aries"}},
        "interpretation": {"summary": "Interpretation"},
        "remedy_generation": {"remedies": []},
        "client_report": {"problem_summary": "Test"},
        "pdf": None,
        "generated_at": datetime.now(timezone.utc),
    }
    service.generate_pdf_from_client_report.return_value = {
        "pdf_id": "pdf-1",
        "file_name": "report.pdf",
        "file_path": "reports/output/report.pdf",
        "file_size_bytes": 100,
        "download_url": "/api/v1/dashboard/reports/pdf/report.pdf",
        "generated_at": datetime.now(timezone.utc),
    }
    service.list_reports.return_value = {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "pages": 0,
    }
    return service


@pytest.fixture
def mock_horoscope_service():
    service = MagicMock()
    service.generate_horoscope.return_value = {
        "horoscope": {"daily": {"period_type": "daily"}, "weekly": {}, "monthly": {}}
    }
    return service


@pytest.fixture
def mock_naming_service():
    service = MagicMock()
    service.suggest_names.return_value = {"naming": {"suggestions": [{"name": "Aryan"}]}}
    return service


@pytest.fixture
async def dashboard_client(mock_report_service, mock_horoscope_service, mock_naming_service, test_user):
    app = create_app()
    app.dependency_overrides[get_report_service] = lambda: mock_report_service
    app.dependency_overrides[get_horoscope_service] = lambda: mock_horoscope_service
    app.dependency_overrides[get_naming_service] = lambda: mock_naming_service
    override_current_user(app, test_user)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_generate_report_endpoint(dashboard_client, mock_report_service):
    response = await dashboard_client.post(
        "/api/v1/dashboard/reports/generate",
        json={
            "date_of_birth": "1990-01-15",
            "birth_time": "05:00:00",
            "birth_place": "New Delhi, India",
            "timezone": "Asia/Kolkata",
            "latitude": "28.6139",
            "longitude": "77.2090",
            "problem_text": "Marriage delay",
        },
    )
    assert response.status_code == 200
    assert response.json()["version"] == "unified_report_v2"
    mock_report_service.generate_report.assert_awaited_once()


@pytest.mark.asyncio
async def test_horoscope_endpoint(dashboard_client, mock_horoscope_service):
    response = await dashboard_client.post(
        "/api/v1/dashboard/horoscope",
        json={"moon_sign_index": 1, "lagna_sign_index": 0},
    )
    assert response.status_code == 200
    assert "horoscope" in response.json()
    mock_horoscope_service.generate_horoscope.assert_called_once()


@pytest.mark.asyncio
async def test_naming_endpoint(dashboard_client, mock_naming_service):
    response = await dashboard_client.post(
        "/api/v1/dashboard/naming/suggestions",
        json={"nakshatra": "Ashwini", "pada": 1, "rashi_sign_index": 0},
    )
    assert response.status_code == 200
    assert response.json()["naming"]["suggestions"]
    mock_naming_service.suggest_names.assert_called_once()
