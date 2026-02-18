"""Backend tests for the full-stack template plugin."""

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

try:
    from plugin import register
    HAS_PLUGIN = True
except ImportError:
    HAS_PLUGIN = False


@pytest.fixture
def app():
    app = FastAPI()
    if HAS_PLUGIN:
        plugin_dir = Path(__file__).parent.parent
        register(app, plugin_dir)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_status_endpoint(client):
    if not HAS_PLUGIN:
        pytest.skip("Plugin module not found")

    response = client.get("/api/plugin/{{PLUGIN_NAME}}/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"active", "inactive"}


def test_process_endpoint(client):
    if not HAS_PLUGIN:
        pytest.skip("Plugin module not found")

    response = client.post(
        "/api/plugin/{{PLUGIN_NAME}}/process",
        json={"data": "hello"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "Processed: hello"
    assert "processed_at" in payload
