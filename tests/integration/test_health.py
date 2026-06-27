"""API integration tests."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Health endpoint returns ok status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app_name"] == "AstroGuruAI"
    assert "environment" in payload
