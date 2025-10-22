#!/usr/bin/env python3
"""
Simple test script for evaluation ingest endpoint
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from services.main import app
from datetime import datetime

def test_evals_endpoint():
    client = TestClient(app)
    
    # Test disabled endpoint
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
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Should return 403 when disabled
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()
    print("✅ Evaluation ingest endpoint working correctly (disabled by default)")

if __name__ == "__main__":
    test_evals_endpoint()
