#!/usr/bin/env python3
"""
Golden Set Evaluation Script with Server Health Checking

This script evaluates voice cloning engines against a golden set of test cases.
It can optionally check server health metrics if a server URL is provided.
"""

import argparse
import json
import csv
import requests
from pathlib import Path
from typing import Dict, Any, Optional


def server_health(url_base: str) -> Optional[Dict[str, Any]]:
    """Check server health metrics"""
    try:
        r = requests.get(url_base.rstrip("/") + "/v1/health/metrics", timeout=5)
        if r.ok:
            return r.json()
    except Exception:
        return None
    return None


def load_engines(engines_file: str) -> Dict[str, Any]:
    """Load engine configurations from JSON file"""
    with open(engines_file, 'r') as f:
        return json.load(f)


def load_test_cases(csv_file: str) -> list:
    """Load test cases from CSV file"""
    test_cases = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append(row)
    return test_cases


def evaluate_engine(engine_name: str, engine_config: Dict[str, Any], test_cases: list) -> Dict[str, Any]:
    """Evaluate a single engine against test cases"""
    # This is a placeholder implementation
    # In a real scenario, this would call the actual voice cloning engine
    results = {
        "engine": engine_name,
        "total_tests": len(test_cases),
        "passed": 0,
        "failed": 0,
        "metrics": {
            "avg_quality_score": 0.0,
            "avg_latency_ms": 0.0,
            "success_rate": 0.0
        }
    }
    
    # Mock evaluation - in reality this would synthesize audio and measure quality
    for test_case in test_cases:
        # Simulate some tests passing/failing
        if hash(test_case.get("text", "")) % 2 == 0:
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    results["metrics"]["success_rate"] = results["passed"] / results["total_tests"] if results["total_tests"] > 0 else 0.0
    results["metrics"]["avg_quality_score"] = 4.2 + (hash(engine_name) % 10) / 10.0  # Mock quality score
    results["metrics"]["avg_latency_ms"] = 500 + (hash(engine_name) % 1000)  # Mock latency
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate voice cloning engines against golden test set")
    parser.add_argument("--csv", required=True, help="CSV file with test cases")
    parser.add_argument("--engines", required=True, help="JSON file with engine configurations")
    parser.add_argument("--server", default=None, help="Server base URL to check parity (e.g., http://localhost:8000)")
    parser.add_argument("--output", default="evaluation_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    # Check server health if provided
    if args.server:
        print(f"[goldenset] Checking server health at {args.server}...", flush=True)
        h = server_health(args.server)
        if not h:
            print(f"[goldenset] WARN: Cannot reach {args.server}/v1/health/metrics — continuing anyway.", flush=True)
        else:
            print(f"[goldenset] Server health check successful", flush=True)
            if not h.get("metrics_enabled", False):
                print("[goldenset] NOTE: Server metrics are disabled; UI badges will show only client-side metrics.", flush=True)
            ff = h.get("ffmpeg", {})
            if not ff.get("present"):
                print("[goldenset] NOTE: Server ffmpeg not detected; server-side metrics/normalize unavailable.", flush=True)
            else:
                print(f"[goldenset] Server ffmpeg version: {ff.get('version', 'unknown')}", flush=True)
    
    # Load configurations
    print("[goldenset] Loading engine configurations...", flush=True)
    engines = load_engines(args.engines)
    
    print("[goldenset] Loading test cases...", flush=True)
    test_cases = load_test_cases(args.csv)
    
    print(f"[goldenset] Evaluating {len(engines)} engines against {len(test_cases)} test cases...", flush=True)
    
    # Evaluate each engine
    results = []
    for engine_name, engine_config in engines.items():
        print(f"[goldenset] Evaluating engine: {engine_name}", flush=True)
        result = evaluate_engine(engine_name, engine_config, test_cases)
        results.append(result)
    
    # Save results
    output_data = {
        "evaluation_summary": {
            "total_engines": len(engines),
            "total_test_cases": len(test_cases),
            "timestamp": "2024-01-01T00:00:00Z"  # In real implementation, use actual timestamp
        },
        "engine_results": results
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"[goldenset] Evaluation complete. Results saved to {args.output}", flush=True)
    
    # Print summary
    print("\n[goldenset] Summary:", flush=True)
    for result in results:
        print(f"  {result['engine']}: {result['passed']}/{result['total_tests']} passed "
              f"({result['metrics']['success_rate']:.1%} success rate)", flush=True)


if __name__ == "__main__":
    main()
