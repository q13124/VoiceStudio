#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

IN="requirements.txt"
OUT="requirements.lock.txt"
CONSTRAINTS="constraints.txt"

echo "==> Generating $OUT (no upgrades; additive only)"
if [[ -f "$CONSTRAINTS" ]]; then
  pip-compile \
    --generate-hashes \
    --no-emit-index-url \
    --no-emit-trusted-host \
    --no-upgrade \
    --allow-unsafe \
    -o "$OUT" \
    -c "$CONSTRAINTS" \
    "$IN"
else
  pip-compile \
    --generate-hashes \
    --no-emit-index-url \
    --no-emit-trusted-host \
    --no-upgrade \
    --allow-unsafe \
    -o "$OUT" \
    "$IN"
fi

echo "==> Done. Locked to $(grep -c '==' "$OUT") packages with hashes."
