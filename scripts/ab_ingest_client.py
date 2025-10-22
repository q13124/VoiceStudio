#!/usr/bin/env python3
import json, sys, argparse, requests

parser = argparse.ArgumentParser(description="Post A/B summary and ingest payloads")
parser.add_argument("--api", required=True, help="API base, e.g. http://localhost:8000")
parser.add_argument("--session", required=True, help="Session ID for summary")
parser.add_argument(
    "--ratings", required=True, help="Path to ratings JSON (array of ABRating)"
)
parser.add_argument("--run-id", required=True, help="Run ID for ingest")
parser.add_argument("--date", required=True, help="YYYY-MM-DD for ingest")
parser.add_argument(
    "--per-engine", required=True, help="Path to perEngine JSON map for ingest"
)
parser.add_argument("--token", default=None, help="Bearer token for ingest")
args = parser.parse_args()

base = args.api.rstrip("/")

# 1) Post summary
ratings = json.loads(open(args.ratings, "r", encoding="utf-8").read())
sum_payload = {"sessionId": args.session, "ratings": ratings}
rs = requests.post(f"{base}/v1/ab/summary", json=sum_payload, timeout=20)
rs.raise_for_status()
summary = rs.json()
print("Summary OK:", json.dumps(summary, indent=2))

# 2) Post ingest
per_engine = json.loads(open(args.per_engine, "r", encoding="utf-8").read())
ing_payload = {"runId": args.run_id, "date": args.date, "perEngine": per_engine}
headers = {"Authorization": f"Bearer {args.token}"} if args.token else {}
ri = requests.post(
    f"{base}/v1/evals/ingest", json=ing_payload, headers=headers, timeout=20
)
ri.raise_for_status()
print("Ingest OK:", ri.json())
