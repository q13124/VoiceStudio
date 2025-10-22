"""
Integration tests for TTS API with audio metrics
"""
import os, pytest
from fastapi.testclient import TestClient
from shutil import which
from services.api.api_tts import router
from services.api.voice_engine_router import app

# Create a test app that includes the TTS router
test_app = app
test_app.include_router(router)

@pytest.mark.skipif(which("ffmpeg") is None or which("ffprobe") is None, reason="ffmpeg not available")
def test_metrics_enabled_returns_block(monkeypatch):
    monkeypatch.setenv("METRICS_ENABLED", "true")
    client = TestClient(test_app)
    r = client.post("/v1/generate", json={"text":"Hello world"})
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and isinstance(data["items"], list)
    if data["items"]:
        assert "metrics" in data["items"][0]

def test_metrics_disabled_returns_none_metrics(monkeypatch):
    monkeypatch.setenv("METRICS_ENABLED", "false")
    client = TestClient(test_app)
    r = client.post("/v1/generate", json={"text":"Hello world"})
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and isinstance(data["items"], list)
    if data["items"]:
        assert data["items"][0]["metrics"] is None

def test_generate_tts_basic():
    client = TestClient(test_app)
    r = client.post("/v1/generate", json={
        "text": "Hello world",
        "language": "en",
        "quality": "balanced"
    })
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert len(data["items"]) > 0
    
    item = data["items"][0]
    assert "id" in item
    assert "engine" in item
    assert "url" in item
    assert "metrics" in item

def test_generate_tts_with_voice_profile():
    client = TestClient(test_app)
    r = client.post("/v1/generate", json={
        "text": "Testing voice profile",
        "language": "en",
        "quality": "quality",
        "voice_profile": {"speaker_wavs": []},
        "params": {"sample_rate": 22050}
    })
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert len(data["items"]) > 0

def test_generate_tts_invalid_request():
    client = TestClient(test_app)
    # Empty text should fail
    r = client.post("/v1/generate", json={"text": ""})
    assert r.status_code == 422  # Validation error

def test_list_engines():
    client = TestClient(test_app)
    r = client.get("/v1/engines")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # Should have at least the stub engines
    assert len(data) > 0

def test_health_check():
    client = TestClient(test_app)
    r = client.get("/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "engines" in data
    assert "metrics_enabled" in data
    assert data["status"] == "healthy"

@pytest.mark.skipif(which("ffmpeg") is None or which("ffprobe") is None, reason="ffmpeg not available")
def test_metrics_computation_with_real_audio(monkeypatch):
    monkeypatch.setenv("METRICS_ENABLED", "true")
    client = TestClient(test_app)
    r = client.post("/v1/generate", json={
        "text": "This is a longer test sentence to generate meaningful audio for metrics analysis.",
        "language": "en",
        "quality": "balanced"
    })
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert len(data["items"]) > 0
    
    item = data["items"][0]
    metrics = item.get("metrics")
    
    if metrics:
        # Check that metrics contain expected fields
        expected_fields = ["lufs", "lra", "true_peak", "clip_pct", "dc_offset", "head_ms", "tail_ms"]
        for field in expected_fields:
            assert field in metrics
            # Values should be either None or appropriate numeric types
            if metrics[field] is not None:
                assert isinstance(metrics[field], (int, float))

def test_multiple_engines_ab_test():
    client = TestClient(test_app)
    r = client.post("/abtest", json={
        "text": "A/B test sample",
        "language": "en",
        "quality": "balanced"
    })
    assert r.status_code == 200
    data = r.json()
    assert "candidates" in data
    assert "results" in data
    assert len(data["candidates"]) > 0
    assert len(data["results"]) > 0
