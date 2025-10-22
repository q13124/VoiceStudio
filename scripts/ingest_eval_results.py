#!/usr/bin/env python3
"""
Parse evaluation results and ingest them into VoiceStudio API
"""

import argparse
import json
import requests
from datetime import datetime
from typing import Dict, Any

def parse_eval_results(results_file: str) -> Dict[str, Any]:
    """Parse evaluation results JSON into ingest format"""
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Extract metrics from evaluation results
    per_engine = {}
    for result in data.get("engine_results", []):
        engine = result["engine"]
        metrics = result.get("metrics", {})
        per_engine[engine] = {
            "wr": metrics.get("success_rate", 0.0),
            "latency_p50": metrics.get("avg_latency_ms"),
            "latency_p95": None,  # Would need to be calculated from raw data
            "clip_rate": metrics.get("clip_rate", 0.0),
            "lufs_med": metrics.get("avg_lufs")
        }
    
    return {
        "runId": f"nightly-{datetime.now().strftime('%Y%m%d')}",
        "date": datetime.now().isoformat(),
        "perEngine": per_engine
    }

def ingest_to_api(api_url: str, payload: Dict[str, Any]) -> None:
    """Send evaluation data to VoiceStudio API"""
    response = requests.post(
        f"{api_url.rstrip('/')}/v1/evals/ingest",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
    print(f"Ingested {result['engines_ingested']} engines: {result['message']}")

def main():
    parser = argparse.ArgumentParser(description="Ingest evaluation results")
    parser.add_argument("--input", required=True, help="Evaluation results JSON file")
    parser.add_argument("--api-url", required=True, help="VoiceStudio API URL")
    
    args = parser.parse_args()
    
    try:
        payload = parse_eval_results(args.input)
        print(f"Parsed {len(payload['perEngine'])} engines from {args.input}")
        ingest_to_api(args.api_url, payload)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
