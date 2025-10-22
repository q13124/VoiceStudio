#!/usr/bin/env python3
"""
Test script for A/B Summary and Evaluation Ingest endpoints
"""
import subprocess
import time
import requests
import json
import sys
from pathlib import Path


def start_server():
    """Start the FastAPI server in background"""
    print("Starting FastAPI server...")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "services.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/docs", timeout=2)
            if response.status_code == 200:
                print("Server started successfully")
                return process
        except:
            time.sleep(1)

    print("Failed to start server")
    process.terminate()
    return None


def test_ab_summary():
    """Test A/B summary endpoint"""
    print("\n=== Testing A/B Summary Endpoint ===")

    payload = {
        "sessionId": "test-session-123",
        "ratings": [
            {
                "itemId": "cand-01",
                "engine": "hidden-A",
                "score": 4.6,
                "winner": True,
                "metrics": {"lufs": -23.1, "clip_pct": 0.0},
            },
            {
                "itemId": "cand-02",
                "engine": "hidden-B",
                "score": 4.2,
                "winner": False,
                "metrics": {"lufs": -21.9, "clip_pct": 0.2},
            },
        ],
    }

    try:
        response = requests.post(
            "http://localhost:8000/v1/ab/summary", json=payload, timeout=10
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("A/B Summary successful!")
            print(f"Session: {data['sessionId']}")
            print(f"Total items: {data['total_items']}")
            print(f"Engines: {len(data['engines'])}")

            for engine in data["engines"]:
                print(
                    f"  {engine['engine']}: {engine['wins']}/{engine['n_items']} wins ({engine['win_rate']:.2%})"
                )

            return True
        else:
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"Exception: {e}")
        return False


def test_evals_ingest():
    """Test evaluation ingest endpoint"""
    print("\n=== Testing Evaluation Ingest Endpoint ===")

    payload = {
        "runId": "test-run-123",
        "date": "2025-01-21",
        "perEngine": {
            "xtts": {
                "wr": 0.62,
                "latency_p50": 180,
                "latency_p95": 420,
                "clip_rate": 0.01,
                "lufs_med": -23.1,
            },
            "openvoice": {
                "wr": 0.58,
                "latency_p50": 220,
                "latency_p95": 480,
                "clip_rate": 0.03,
                "lufs_med": -22.8,
            },
        },
    }

    headers = {"Authorization": "Bearer supersecrettoken"}

    try:
        response = requests.post(
            "http://localhost:8000/v1/evals/ingest",
            json=payload,
            headers=headers,
            timeout=10,
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("Evaluation ingest successful!")
            print(f"Accepted: {data['accepted']}")
            print(f"Stored: {data['stored']} records")
            return True
        else:
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"Exception: {e}")
        return False


def test_health_metrics():
    """Test health metrics endpoint"""
    print("\n=== Testing Health Metrics Endpoint ===")

    try:
        response = requests.get("http://localhost:8000/v1/health/metrics", timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("Health metrics successful!")
            print(f"Metrics enabled: {data['metrics_enabled']}")
            print(f"FFmpeg present: {data['ffmpeg']['present']}")
            print(f"OpenAPI version: {data['openapi_version']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"Exception: {e}")
        return False


def main():
    """Main test function"""
    print("VoiceStudio A/B Summary & Evaluation Ingest Test")
    print("=" * 50)

    # Start server
    process = start_server()
    if not process:
        return 1

    try:
        # Run tests
        tests = [test_health_metrics, test_ab_summary, test_evals_ingest]

        passed = 0
        for test in tests:
            if test():
                passed += 1

        print(f"\n=== Test Results ===")
        print(f"Passed: {passed}/{len(tests)}")

        if passed == len(tests):
            print("All tests passed!")
            return 0
        else:
            print("Some tests failed")
            return 1

    finally:
        # Clean up
        print("\nStopping server...")
        process.terminate()
        process.wait()


if __name__ == "__main__":
    sys.exit(main())
