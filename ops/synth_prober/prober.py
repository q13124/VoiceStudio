#!/usr/bin/env python3
import argparse, time, json, os, sys
import requests
from datetime import datetime, timezone

parser = argparse.ArgumentParser()
parser.add_argument('--api', required=True, help='API base, e.g. http://localhost:8000')
parser.add_argument('--text', default='Hello from prober')
parser.add_argument('--timeout', type=float, default=15.0)
parser.add_argument('--pushgateway', default=None, help='http://host:9091 (optional)')
args = parser.parse_args()

base = args.api.rstrip('/')
start = time.time()
status = 0
try:
    r = requests.post(base + '/v1/generate', json={'text': args.text}, timeout=args.timeout)
    status = 1 if r.ok else 0
except Exception:
    status = 0
latency = time.time() - start

# Print Prometheus exposition text (for scrape or Pushgateway)
metric = f'''# HELP voicestudio_probe_success Success of synthetic TTS probe (1/0)
# TYPE voicestudio_probe_success gauge
voicestudio_probe_success {status}
# HELP voicestudio_probe_latency_seconds Latency seconds of synthetic TTS probe
# TYPE voicestudio_probe_latency_seconds gauge
voicestudio_probe_latency_seconds {latency:.6f}
'''
print(metric)

if args.pushgateway:
    # Push as a single job
    try:
        requests.post(args.pushgateway.rstrip('/') + '/metrics/job/voicestudio_prober', data=metric.encode('utf-8'), headers={'Content-Type':'text/plain; version=0.0.4'})
    except Exception as e:
        print('Pushgateway push failed:', e, file=sys.stderr)
