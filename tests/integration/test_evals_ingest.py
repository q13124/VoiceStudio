"""
Integration tests for evaluation ingest endpoint
"""

import pytest
from fastapi.testclient import TestClient
from services.main import app
from datetime import datetime

def test_evals_ingest_disabled():
    """Test that ingest endpoint returns 403 when disabled"""
    client = TestClient(app)
    payload = {
        "runId": "test-run-1",
        "date": datetime.now().isoformat(),
        "perEngine": {
            "xtts": {
                "wr": 0.75,
                "latency_p50": 500.0,
                "latency_p95": 1000.0,
                "clip_rate": 0.02,
                "lufs_med": -23.1
            }
        }
    }
    
    response = client.post("/v1/evals/ingest", json=payload)
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()

@pytest.mark.skipif(True, reason="Requires EVALS_INGEST_ENABLED=true")
def test_evals_ingest_enabled():
    """Test ingest endpoint when enabled (requires env var)"""
    client = TestClient(app)
    payload = {
        "runId": "test-run-2",
        "date": datetime.now().isoformat(),
        "perEngine": {
            "xtts": {
                "wr": 0.75,
                "latency_p50": 500.0,
                "latency_p95": 1000.0,
                "clip_rate": 0.02,
                "lufs_med": -23.1
            },
            "openvoice": {
                "wr": 0.68,
                "latency_p50": 750.0,
                "latency_p95": 1200.0,
                "clip_rate": 0.05,
                "lufs_med": -22.8
            }
        }
    }
    
    response = client.post("/v1/evals/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["runId"] == "test-run-2"
    assert data["engines_ingested"] == 2
    assert "successfully" in data["message"]

def test_evals_ingest_validation():
    """Test payload validation"""
    client = TestClient(app)
    
    # Invalid win rate
    payload = {
        "runId": "test-run-3",
        "date": datetime.now().isoformat(),
        "perEngine": {
            "xtts": {
                "wr": 1.5,  # Invalid: > 1.0
                "latency_p50": 500.0
            }
        }
    }
    
    response = client.post("/v1/evals/ingest", json=payload)
    assert response.status_code == 422  # Validation error
