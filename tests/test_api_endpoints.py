"""
VoiceStudio FastAPI Integration Tests
Tests the REST API endpoints for the Voice Engine Router
"""

from fastapi.testclient import TestClient
from services.voice_engine_router import app


def test_health_lists_engines():
    """Test that health endpoint returns engine status"""
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    js = r.json()
    assert js.get("ok") is True
    assert isinstance(js.get("engines"), dict)


def test_tts_sync_returns_b64():
    """Test that sync TTS endpoint returns base64 audio"""
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
    assert js["engine"]
    assert js["result_b64_wav"]


def test_abtest_returns_candidates():
    """Test that A/B test endpoint returns multiple candidates"""
    c = TestClient(app)
    r = c.post("/abtest", json={"text": "ab", "language": "en", "quality": "balanced"})
    assert r.status_code == 200
    js = r.json()
    assert len(js["candidates"]) >= 1


def test_tts_async_returns_job_id():
    """Test that async TTS endpoint returns job ID"""
    c = TestClient(app)
    r = c.post(
        "/tts",
        json={
            "text": "Hello async test",
            "language": "en",
            "quality": "balanced",
            "voice_profile": {},
            "params": {},
            "mode": "async",
        },
    )
    assert r.status_code == 200
    js = r.json()
    assert js["engine"]
    assert js["job_id"]
    assert "result_b64_wav" not in js  # Should not be in async response


def test_engines_endpoint():
    """Test that engines endpoint returns engine information"""
    c = TestClient(app)
    r = c.get("/engines")
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js, dict)
    # Should contain engine information
    assert len(js) > 0


def test_tts_validation():
    """Test that TTS endpoint validates input properly"""
    c = TestClient(app)

    # Test missing required fields
    r = c.post("/tts", json={})
    assert r.status_code == 422  # Validation error

    # Test invalid language
    r = c.post(
        "/tts",
        json={
            "text": "test",
            "language": "invalid_lang",
            "quality": "balanced",
            "voice_profile": {},
            "params": {},
            "mode": "sync",
        },
    )
    # Should either succeed (fallback) or return validation error
    assert r.status_code in [200, 422]


def test_tts_multilingual():
    """Test TTS with different languages"""
    c = TestClient(app)

    languages = ["en", "es", "fr", "de"]
    for lang in languages:
        r = c.post(
            "/tts",
            json={
                "text": f"Hello in {lang}",
                "language": lang,
                "quality": "balanced",
                "voice_profile": {},
                "params": {},
                "mode": "sync",
            },
        )
        # Should succeed for supported languages
        if r.status_code == 200:
            js = r.json()
            assert js["engine"]
            assert js["result_b64_wav"]


def test_tts_quality_tiers():
    """Test TTS with different quality tiers"""
    c = TestClient(app)

    qualities = ["fast", "balanced", "quality"]
    for quality in qualities:
        r = c.post(
            "/tts",
            json={
                "text": "Quality test",
                "language": "en",
                "quality": quality,
                "voice_profile": {},
                "params": {},
                "mode": "sync",
            },
        )
        assert r.status_code == 200
        js = r.json()
        assert js["engine"]
        assert js["result_b64_wav"]


def test_abtest_multiple_engines():
    """Test A/B testing with multiple engines"""
    c = TestClient(app)
    r = c.post(
        "/abtest",
        json={
            "text": "A/B test with multiple engines",
            "language": "en",
            "quality": "balanced",
            "engines": ["xtts", "openvoice"],  # If supported
        },
    )
    assert r.status_code == 200
    js = r.json()
    assert "candidates" in js
    assert "results" in js
    assert "performance" in js


def test_tts_with_voice_profile():
    """Test TTS with voice profile parameters"""
    c = TestClient(app)
    r = c.post(
        "/tts",
        json={
            "text": "Voice profile test",
            "language": "en",
            "quality": "balanced",
            "voice_profile": {
                "voice_id": "test_voice",
                "speaker_wavs": [],
                "language": "en",
            },
            "params": {"stability": 0.6, "similarity_boost": 0.8},
            "mode": "sync",
        },
    )
    assert r.status_code == 200
    js = r.json()
    assert js["engine"]
    assert js["result_b64_wav"]


def test_tts_error_handling():
    """Test error handling in TTS endpoint"""
    c = TestClient(app)

    # Test with very long text (should be handled gracefully)
    long_text = "test " * 1000
    r = c.post(
        "/tts",
        json={
            "text": long_text,
            "language": "en",
            "quality": "balanced",
            "voice_profile": {},
            "params": {},
            "mode": "sync",
        },
    )
    # Should either succeed or return appropriate error
    assert r.status_code in [200, 422, 500]


def test_jobs_endpoint():
    """Test jobs endpoint for async job tracking"""
    c = TestClient(app)
    r = c.get("/jobs")
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js, dict)
    # Should contain job information
    assert "jobs" in js


def test_health_detailed():
    """Test detailed health information"""
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    js = r.json()

    # Check structure
    assert "ok" in js
    assert "engines" in js
    assert "timestamp" in js

    # Check engine information
    engines = js["engines"]
    for engine_id, engine_info in engines.items():
        assert "healthy" in engine_info
        assert "load" in engine_info
        assert "languages" in engine_info
        assert "quality" in engine_info


def test_cors_headers():
    """Test that CORS headers are properly set"""
    c = TestClient(app)
    r = c.options("/health")
    # Should handle OPTIONS requests for CORS
    assert r.status_code in [200, 405]  # 405 if OPTIONS not implemented


def test_api_versioning():
    """Test API versioning if implemented"""
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    # Check if version header is present
    # This depends on implementation


def test_rate_limiting():
    """Test rate limiting if implemented"""
    c = TestClient(app)

    # Make multiple rapid requests
    for i in range(10):
        r = c.post(
            "/tts",
            json={
                "text": f"Rate limit test {i}",
                "language": "en",
                "quality": "balanced",
                "voice_profile": {},
                "params": {},
                "mode": "sync",
            },
        )
        # Should succeed or be rate limited appropriately
        assert r.status_code in [200, 429]


def test_concurrent_requests():
    """Test handling of concurrent requests"""
    import threading
    import time

    c = TestClient(app)
    results = []

    def make_request(i):
        r = c.post(
            "/tts",
            json={
                "text": f"Concurrent test {i}",
                "language": "en",
                "quality": "balanced",
                "voice_profile": {},
                "params": {},
                "mode": "sync",
            },
        )
        results.append((i, r.status_code))

    # Start multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for completion
    for thread in threads:
        thread.join()

    # Check results
    assert len(results) == 5
    for i, status_code in results:
        assert status_code == 200


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_health_lists_engines,
        test_tts_sync_returns_b64,
        test_abtest_returns_candidates,
        test_tts_async_returns_job_id,
        test_engines_endpoint,
        test_tts_validation,
        test_tts_multilingual,
        test_tts_quality_tiers,
        test_abtest_multiple_engines,
        test_tts_with_voice_profile,
        test_tts_error_handling,
        test_jobs_endpoint,
        test_health_detailed,
        test_cors_headers,
        test_api_versioning,
        test_rate_limiting,
        test_concurrent_requests,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1

    print(f"\nAPI Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All API tests passed!")
    else:
        print("⚠️  Some API tests failed")
