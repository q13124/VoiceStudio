"""
Integration tests for health metrics endpoint
"""

from fastapi.testclient import TestClient
from services.main import app


def test_health_metrics_ok():
    """Test health metrics endpoint returns expected structure"""
    c = TestClient(app)
    r = c.get("/v1/health/metrics")
    assert r.status_code == 200
    data = r.json()
    
    # Check required fields
    for key in ("metrics_enabled", "ffmpeg", "ffprobe", "postfx", "openapi_version"):
        assert key in data
    
    # Check nested structure
    assert isinstance(data["ffmpeg"], dict)
    assert "present" in data["ffmpeg"]
    assert isinstance(data["ffprobe"], dict)
    assert "present" in data["ffprobe"]
    assert isinstance(data["postfx"], dict)
    assert "available" in data["postfx"]
    
    # Check OpenAPI version
    assert data["openapi_version"] == "3.1.0"


def test_health_metrics_structure():
    """Test health metrics response structure matches model"""
    c = TestClient(app)
    r = c.get("/v1/health/metrics")
    assert r.status_code == 200
    data = r.json()
    
    # Validate ffmpeg structure
    ffmpeg = data["ffmpeg"]
    assert isinstance(ffmpeg["present"], bool)
    if ffmpeg["version"] is not None:
        assert isinstance(ffmpeg["version"], str)
    
    # Validate ffprobe structure
    ffprobe = data["ffprobe"]
    assert isinstance(ffprobe["present"], bool)
    if ffprobe["version"] is not None:
        assert isinstance(ffprobe["version"], str)
    
    # Validate postfx structure
    postfx = data["postfx"]
    assert isinstance(postfx["available"], bool)
    assert isinstance(postfx["ffmpeg_used_by_default"], bool)
    
    # Validate build structure (optional)
    if data.get("build") is not None:
        build = data["build"]
        if build.get("version") is not None:
            assert isinstance(build["version"], str)
        if build.get("git_sha") is not None:
            assert isinstance(build["git_sha"], str)
        if build.get("build_time_utc") is not None:
            assert isinstance(build["build_time_utc"], str)
