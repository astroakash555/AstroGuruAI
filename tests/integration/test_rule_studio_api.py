"""Rule studio API integration tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.v1.endpoints.rule_studio import get_rule_studio_service
from backend.app.main import create_app


SAMPLE_RULE = {
    "rule_name": "KP Marriage Event Support",
    "system": "kp",
    "description": "KP marriage event supported by 7th cusp sub lord.",
    "conditions": {
        "planets": ["Venus"],
        "houses": [2, 7, 11],
        "tags": ["marriage"],
    },
    "weight": 0.7,
    "confidence": 0.65,
    "outcome": "moderate_support",
    "source_book": "KP Reader Vol 1",
    "notes": "Event timing rule.",
    "domain": "marriage",
}


@pytest.fixture
def mock_rule_studio_service(tmp_path):
    from backend.app.services.rule_studio_service import RuleStudioService

    return RuleStudioService(data_root=str(tmp_path))


@pytest.fixture
async def rule_studio_client(mock_rule_studio_service):
    app = create_app()
    app.dependency_overrides[get_rule_studio_service] = lambda: mock_rule_studio_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_and_get_rule_api(rule_studio_client):
    create_response = await rule_studio_client.post("/api/v1/rule-studio/rules", json=SAMPLE_RULE)
    assert create_response.status_code == 201
    rule_id = create_response.json()["rule"]["rule_id"]

    get_response = await rule_studio_client.get(f"/api/v1/rule-studio/rules/{rule_id}")
    assert get_response.status_code == 200
    assert get_response.json()["rule"]["system"] == "kp"


@pytest.mark.asyncio
async def test_approval_workflow_api(rule_studio_client):
    rule_id = (await rule_studio_client.post("/api/v1/rule-studio/rules", json=SAMPLE_RULE)).json()["rule"]["rule_id"]

    assert (await rule_studio_client.post(f"/api/v1/rule-studio/rules/{rule_id}/submit", json={"actor": "expert"})).status_code == 200
    assert (await rule_studio_client.post(f"/api/v1/rule-studio/rules/{rule_id}/approve", json={"actor": "senior_guru"})).status_code == 200
    assert (await rule_studio_client.post(f"/api/v1/rule-studio/rules/{rule_id}/activate", json={"actor": "senior_guru"})).status_code == 200

    detail = (await rule_studio_client.get(f"/api/v1/rule-studio/rules/{rule_id}")).json()
    assert detail["rule"]["is_active"] is True


@pytest.mark.asyncio
async def test_sandbox_api(rule_studio_client):
    rule_id = (await rule_studio_client.post("/api/v1/rule-studio/rules", json=SAMPLE_RULE)).json()["rule"]["rule_id"]
    response = await rule_studio_client.post(f"/api/v1/rule-studio/rules/{rule_id}/sandbox", json={})
    assert response.status_code == 200
    assert response.json()["sandbox"]["rule_id"] == rule_id


@pytest.mark.asyncio
async def test_studio_report_api(rule_studio_client):
    await rule_studio_client.post("/api/v1/rule-studio/rules", json=SAMPLE_RULE)
    response = await rule_studio_client.get("/api/v1/rule-studio/report")
    assert response.status_code == 200
    assert response.json()["total_rules"] >= 1
