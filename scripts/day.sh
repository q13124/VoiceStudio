#!/usr/bin/env bash
set -euo pipefail
DAY="${DAY:-$(date +%j)}"
FEATURE="${FEATURE:-TBD}"
TEST="${TEST:-python -c 'print(\"OK\")'}"
echo "Day $DAY: $FEATURE"
echo "Open Cursor (Ctrl+K) with the plan from docs/15_MINUTE_WORKFLOW.md"
echo "When ready, run quick test:"
echo "  $TEST"