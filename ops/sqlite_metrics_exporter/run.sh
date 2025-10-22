#!/usr/bin/env bash
set -euo pipefail
export DB_URL=${DB_URL:-sqlite:///./app.db}
uvicorn exporter:app --host 0.0.0.0 --port 8001