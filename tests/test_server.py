import json

import pytest
from fastapi.testclient import TestClient

from railsafe.ingest import build_index
from railsafe.server import app


@pytest.fixture(scope="module")
def client(monkeypatch_module=None):
    build_index()
    return TestClient(app)


def _events(body: str) -> list[dict]:
    return [
        json.loads(line[5:])
        for line in body.split("\n\n")
        if line.strip().startswith("data:")
    ]


def test_health(client):
    data = client.get("/api/health").json()
    assert data["status"] == "ok"
    assert data["chunks"] > 0


def test_index_page_served(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Rail Safety Compliance Assistant" in resp.text


def test_chat_streams_sources_and_answer(client, monkeypatch):
    # Force demo mode so the test never needs an API key
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    resp = client.post(
        "/api/chat",
        json={"message": "maximum speed on class 3 track", "history": []},
    )
    assert resp.status_code == 200
    events = _events(resp.text)
    types = [e["type"] for e in events]
    assert types[0] == "sources"
    assert "delta" in types
    assert types[-1] == "done" and events[-1]["demo"] is True
    doc_ids = [s["doc_id"] for s in events[0]["sources"]]
    assert "fra-49cfr-213" in doc_ids


def test_chat_jurisdiction_filter(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    resp = client.post(
        "/api/chat",
        json={"message": "safety management system", "jurisdiction": "EU-ERA"},
    )
    sources = _events(resp.text)[0]["sources"]
    assert sources
    assert all(s["jurisdiction"] == "EU-ERA" for s in sources)
