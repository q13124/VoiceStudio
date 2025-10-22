"""
FastAPI test suite for Voice Engine Router endpoints
"""

from fastapi.testclient import TestClient
from services.api.voice_engine_router import app


def test_health_lists_engines():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    js = r.json()
    assert js.get("ok") is True and isinstance(js.get("engines"), dict)


def test_tts_sync_returns_b64():
    c = TestClient(app)
    r = c.post(
        "/tts",
        json={
            "text": "Hello from tests",
            "language": "en",
            "quality": "balanced",
            "voice_profile": {},
            "params": {"sample_rate": 16000},
            "mode": "sync",
        },
    )
    assert r.status_code == 200
    js = r.json()
    assert js["engine"] and js["result_b64_wav"]


def test_abtest_returns_candidates():
    c = TestClient(app)
    r = c.post("/abtest", json={"text": "ab", "language": "en", "quality": "balanced"})
    assert r.status_code == 200
    js = r.json()
    assert len(js["candidates"]) >= 1


def test_engines_endpoint():
    c = TestClient(app)
    r = c.get("/engines")
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js, dict)


def test_tts_async_mode():
    c = TestClient(app)
    r = c.post(
        "/tts",
        json={
            "text": "Test async",
            "language": "en",
            "quality": "balanced",
            "mode": "async",
        },
    )
    assert r.status_code == 200
    js = r.json()
    assert js["job_id"] is not None
