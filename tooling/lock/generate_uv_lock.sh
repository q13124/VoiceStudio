#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

IN="requirements.txt"
OUT="requirements.lock.txt"

echo "==> Generating $OUT with uv (no upgrade; additive only)"
# Re-resolve transitive deps with hashes, honoring pinned versions in requirements.txt
uv pip compile "$IN" --no-upgrade --generate-hashes --output-file "$OUT"

echo "==> Done. $(grep -c '==' "$OUT") packages locked with hashes."
