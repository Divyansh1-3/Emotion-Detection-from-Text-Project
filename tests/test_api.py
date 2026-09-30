"""Integration tests for Flask HTTP API and /inspect view."""
from __future__ import annotations

import pytest

from backend.app import create_app
from backend.app.services.analysis_service import get_repository


@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "test_emotion.sqlite3"
    app = create_app({
        "TESTING": True,
        "DATABASE_URL": f"sqlite:///{test_db}",
    })
    # Reset repo to temporary database
    repo = get_repository()
    repo.db_path = test_db
    repo.init_db()

    with app.test_client() as c:
        yield c


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert "models" in data
    assert "llm" in data


def test_single_process_endpoint(client):
    payload = {
        "input": "I am so happy and thrilled with our project success!",
        "session_id": "test_sess_01",
    }
    res = client.post("/api/v1/emotion/process", json=payload)
    assert res.status_code == 200
    data = res.get_json()

    assert data["success"] is True
    assert "result" in data
    result = data["result"]
    assert result["primary_emotion"] in ["joy", "surprise", "neutral", "anger", "sadness", "disgust", "fear"]
    assert "confidence" in result
    assert "sarcasm" in result
    assert "route" in result
    assert "latency_ms" in result
    assert isinstance(data["sources"], list)
    assert isinstance(data["warnings"], list)


def test_process_validation_error(client):
    # Blank text
    res = client.post("/api/v1/emotion/process", json={"input": "   "})
    assert res.status_code in (400, 422)


def test_batch_process_endpoint(client):
    payload = {
        "texts": [
            "We won the championship!",
            "Terrible customer service and broken product.",
            "Meeting rescheduled to Friday afternoon.",
        ]
    }
    res = client.post("/api/v1/emotion/batch", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["total_processed"] == 3
    assert len(data["results"]) == 3


def test_results_and_stats_endpoints(client):
    # Process one utterance
    client.post("/api/v1/emotion/process", json={"input": "Test sample for persistence."})

    # Query results list
    res_list = client.get("/api/v1/emotion/results")
    assert res_list.status_code == 200
    data_list = res_list.get_json()
    assert data_list["success"] is True
    assert data_list["total"] >= 1
    assert len(data_list["results"]) >= 1

    # Query specific ID
    first_id = data_list["results"][0]["id"]
    res_single = client.get(f"/api/v1/emotion/results/{first_id}")
    assert res_single.status_code == 200
    data_single = res_single.get_json()
    assert data_single["result"]["id"] == first_id

    # Query stats
    res_stats = client.get("/api/v1/emotion/stats")
    assert res_stats.status_code == 200
    assert "stats" in res_stats.get_json()


def test_server_rendered_views(client):
    # Dashboard view
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert b"P_098" in res_home.data

    # Server-rendered /inspect view
    res_inspect = client.get("/inspect")
    assert res_inspect.status_code == 200
    assert b"/inspect View" in res_inspect.data
