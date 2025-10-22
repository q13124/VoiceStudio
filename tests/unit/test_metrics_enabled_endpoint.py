import os, pytest
from fastapi.testclient import TestClient
from services.main import app
from shutil import which

@pytest.mark.skipif(which("ffmpeg") is None or which("ffprobe") is None, reason="ffmpeg not available")
def test_metrics_enabled_returns_block(monkeypatch):
    monkeypatch.setenv("METRICS_ENABLED", "true")
    client = TestClient(app)
    r = client.post("/v1/generate", json={"text":"Hello world"})
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and isinstance(data["items"], list)
    if data["items"]:
        assert "metrics" in data["items"][0]
