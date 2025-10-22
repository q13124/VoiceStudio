#!/usr/bin/env python3
"""
Simple test for A/B Summary and Evaluation Ingest endpoints
"""
import os
import requests
import json

# Set environment variables
os.environ["EVALS_INGEST_ENABLED"] = "true"
os.environ["EVALS_INGEST_TOKEN"] = "supersecrettoken"
os.environ["AB_PERSIST_ENABLED"] = "true"
os.environ["DB_URL"] = "sqlite:///./test.db"


def test_ab_summary():
    """Test A/B summary endpoint"""
    print("=== Testing A/B Summary Endpoint ===")

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


def main():
    """Main test function"""
    print("VoiceStudio A/B Summary & Evaluation Ingest Test")
    print("=" * 50)

    # Run tests
    tests = [test_ab_summary, test_evals_ingest]

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


if __name__ == "__main__":
    import sys

    sys.exit(main())
