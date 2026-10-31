"""Regression coverage for submission review findings."""
import csv
import io
import sys
from types import SimpleNamespace

import pytest

from backend.app import create_app
from backend.app.core.config import Settings
from backend.app.engines.router import execute_pipeline
from backend.app.engines.validator import validate_input_text


@pytest.fixture
def client(tmp_path):
    return create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{tmp_path / 'api.sqlite3'}"}).test_client()


@pytest.mark.parametrize("body", [{"texts": [123]}, {"texts": [{}]}, ["happy"], {"texts": []}, {"texts": "happy"}])
def test_malformed_batch_is_client_error(client, body):
    assert client.post("/api/v1/emotion/batch", json=body).status_code in (400, 422)
    assert client.get("/api/v1/emotion/stats").json["stats"]["total"] == 0


def test_batch_limit_is_atomic(client, monkeypatch):
    monkeypatch.setenv("MAX_BATCH_ROWS", "2")
    assert client.post("/api/v1/emotion/batch", json={"texts": ["happy", "sad", "angry"]}).status_code == 400
    assert client.get("/api/v1/emotion/stats").json["stats"]["total"] == 0


@pytest.mark.parametrize("header", ["\ufefftext", "id,message"])
def test_csv_headers_are_not_analyzed(client, header):
    content = header + "\n" + ("1," if header == "id,message" else "") + "I am happy"
    response = client.post("/api/v1/emotion/batch", data={"file": (io.BytesIO(content.encode()), "test.csv")})
    assert response.status_code == 200
    assert response.json["total_processed"] == 1
    assert response.json["results"][0]["input_text"] == "I am happy"
    assert response.json["results"][0]["mode"] == "batch"


def test_partial_batch_reports_errors_without_fake_predictions(client):
    response = client.post("/api/v1/emotion/batch", json={"texts": ["happy", "", "x" * 4001]}).json
    assert (response["total_succeeded"], response["total_failed"]) == (1, 2)
    assert response["results"][1]["row_number"] == 2
    assert "primary_emotion" not in response["results"][1]


def test_empty_after_sanitization():
    with pytest.raises(ValueError):
        validate_input_text("\x00\x01")


@pytest.mark.parametrize("text", ["This is my favorite song.", "I can't wait to celebrate my birthday!", "I couldn't be happier!"])
def test_sincere_positive_idioms(text):
    result = execute_pipeline(text)
    assert not result.sarcasm
    assert result.primary_emotion == "joy"


def test_unknown_fallback_requires_review():
    assert execute_pipeline("asdf qwer zxcv").uncertain


def test_csv_export_and_formula_escaping(client):
    client.post("/api/v1/emotion/process", json={"input": "=1+1"})
    response = client.get("/api/v1/emotion/export")
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert response.status_code == 200
    assert rows[0]["input_text"] == "'=1+1"


def test_app_databases_are_isolated(tmp_path):
    first = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{tmp_path / 'a.db'}"}).test_client()
    second = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{tmp_path / 'b.db'}"}).test_client()
    first.post("/api/v1/emotion/process", json={"input": "happy"})
    assert second.get("/api/v1/emotion/stats").json["stats"]["total"] == 0


def test_unsupported_database_does_not_silently_use_sqlite():
    with pytest.raises(ValueError, match="Only sqlite"):
        Settings(database_url="postgresql://localhost/example").sqlite_path


def test_malformed_llm_response_retries_then_falls_back(monkeypatch):
    from backend.app.engines.llm import generate_rationale
    from backend.app.domain.emotion_schema import EmotionScore
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="unstructured response"))])
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=lambda **kw: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))))
    monkeypatch.setenv("LLM_MODE", "api")
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    rationale, used = generate_rationale("happy", "joy", [EmotionScore("joy", .9)], False, 0, [])
    assert len(calls) == 2 and not used
    assert "unstructured response" not in rationale
