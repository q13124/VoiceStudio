"""Plugin tests"""
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
    return FastAPI()

@pytest.fixture
def client(app):
    if HAS_PLUGIN:
        plugin_dir = Path(__file__).parent.parent
        register(app, plugin_dir)
    return TestClient(app)

def test_health(client):
    if not HAS_PLUGIN:
        pytest.skip("Plugin module not found")
    response = client.get("/api/plugin/{{PLUGIN_NAME}}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_process_audio(client):
    if not HAS_PLUGIN:
        pytest.skip("Plugin module not found")
    samples = [0.1, -0.1, 0.05]
    response = client.post("/api/plugin/{{PLUGIN_NAME}}/process", json={
        "samples": samples,
        "sample_rate": 44100,
        "gain_db": 0
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["sample_rate"] == 44100
    assert len(payload["samples"]) == len(samples)
