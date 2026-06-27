"""Case learning API integration tests."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.v1.endpoints.case_learning import get_case_learning_service
from backend.app.main import create_app


SAMPLE_CASE = {
    "client_id": "client-001",
    "category": "marriage",
    "problem_text": "No marriage till age 38",
    "kundali_snapshot": {"planets": [{"name": "Saturn", "house": 7}]},
    "system_prediction": {"consensus_outcome": "delayed_outcome"},
    "applied_rules": ["marriage_delay_rule"],
    "applied_remedies": ["saturn_mantra"],
    "predicted_outcome": "delayed_outcome",
    "final_outcome": "delayed_outcome",
}


@pytest.fixture
def mock_case_learning_service(tmp_path):
    from backend.app.services.case_learning_service import CaseLearningService

    return CaseLearningService(data_root=str(tmp_path))


@pytest.fixture
async def case_learning_client(mock_case_learning_service):
    app = create_app()
    app.dependency_overrides[get_case_learning_service] = lambda: mock_case_learning_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_record_and_get_case_api(case_learning_client):
    create_response = await case_learning_client.post("/api/v1/case-learning/cases", json=SAMPLE_CASE)
    assert create_response.status_code == 201
    case_id = create_response.json()["case"]["case_id"]

    get_response = await case_learning_client.get(f"/api/v1/case-learning/cases/{case_id}")
    assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_follow_up_api(case_learning_client):
    case_id = (await case_learning_client.post("/api/v1/case-learning/cases", json=SAMPLE_CASE)).json()["case"]["case_id"]
    response = await case_learning_client.post(
        f"/api/v1/case-learning/cases/{case_id}/follow-up",
        json={"outcome_type": "success", "remedy_effectiveness": "effective"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_learning_report_api(case_learning_client):
    await case_learning_client.post("/api/v1/case-learning/cases", json=SAMPLE_CASE)
    response = await case_learning_client.get("/api/v1/case-learning/report")
    assert response.status_code == 200
    assert response.json()["total_cases"] >= 1
