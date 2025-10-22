#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
mkdir -p "$ROOT/.github/workflows" "$ROOT/scripts/tests" "$ROOT/docs"

# day-runner workflow (manual + 10:00 AM CT weekdays)
cat > "$ROOT/.github/workflows/day-runner.yml" <<'YAML'
name: day-runner
on:
  workflow_dispatch:
    inputs:
      day:         { description: "Day number", default: "1" }
      feature:     { description: "Feature label", default: "TBD" }
      test_preset: { description: "python|frontend|api|all", default: "python" }
  schedule: [ { cron: "0 15 * * 1-5" } ]   # 10:00 AM CDT weekdays
jobs:
  run-day:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.10" }
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: "npm" }
      - run: |
          if [ -f web/frontend/package.json ]; then (cd web/frontend && npm ci || npm i); else echo "no frontend"; fi
      - run: |
          python -m pip install --upgrade pip
          if [ -f requirements.lock.txt ]; then pip install --require-hashes -r requirements.lock.txt; elif [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - id: cmd
        run: |
          chmod +x scripts/tests/presets.sh || true
          if [ -x scripts/tests/presets.sh ]; then
            echo "cmd=$(scripts/tests/presets.sh '${{ github.event.inputs.test_preset || 'python' }}' | tr -d '\n')" >> $GITHUB_OUTPUT
          else
            echo "cmd=pytest -q" >> $GITHUB_OUTPUT
          fi
      - name: Run tests
        run: |
          echo "Day ${{ github.event.inputs.day || 'N/A' }}: ${{ github.event.inputs.feature || 'TBD' }}"
          echo "CMD: ${{ steps.cmd.outputs.cmd }}"
          bash -lc "${{ steps.cmd.outputs.cmd }}"
YAML

# daily nudge (reminder only)
cat > "$ROOT/.github/workflows/daily-nudge.yml" <<'YAML'
name: daily-nudge
on:
  schedule: [ { cron: "0 15 * * 1-5" } ]  # 10:00 AM CDT weekdays
  workflow_dispatch:
jobs:
  remind:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Time for your 15-min sprint: open docs/15_MINUTE_WORKFLOW.md"
YAML

# Makefile presets (append or create)
MF="$ROOT/Makefile"; [ -f "$MF" ] || echo "# Makefile" > "$MF"
cat >> "$MF" <<'MAKE'
.PHONY: test-python test-frontend test-api test-all day-plan day-exec day-test day-review day-fix day-commit day-all day-preset
PY_TEST?=pytest -q
FE_TEST?=npm test -w web/frontend --silent
API_SMOKE?=python - <<'PY'
from fastapi.testclient import TestClient
try:
  from app.main import app
  c = TestClient(app)
  r = c.post('/v1/generate', json={'text':'hello'})
  print('status', r.status_code); print('ok', r.ok)
except Exception as e:
  print('smoke failed', e)
PY
test-python:; $(PY_TEST)
test-frontend:; $(FE_TEST)
test-api:; $(API_SMOKE)
test-all: test-python test-frontend test-api
day-plan:; @printf "\n=== ChatGPT Prompt ===\nVoiceStudio Day $$DAY: $$FEATURE\n\nOutput ONLY:\n1. File path\n2. Complete code\n3. Test command\n\nNo explanations.\n"; echo "\n(See docs/15_MINUTE_WORKFLOW.md)"
day-exec:; @echo "Open Cursor → Ctrl+K → paste plan → accept."
day-test:; @test -n "$$TEST" || (echo "Set TEST=..."; exit 1); echo "Running: $$TEST"; bash -lc "$$TEST"
day-review:; @printf "\n=== ChatGPT Prompt (Review) ===\nQuick review: [paste diff/output]. Critical issues only.\n"
day-fix:; @echo "Cursor Ctrl+L → paste issues → accept."
day-commit:; @git add -A && git commit -m "Day $$DAY: $$FEATURE" && git push
day-all: day-plan day-exec day-test day-review day-fix day-commit
TEST_PRESET?=python
day-preset:
	@case "$(TEST_PRESET)" in \
	  python)  TEST='$(PY_TEST)';; \
	  frontend)TEST='$(FE_TEST)';; \
	  api)     TEST='$(API_SMOKE)';; \
	  all)     TEST='$(PY_TEST) && $(FE_TEST) && $(API_SMOKE)';; \
	  *) echo "unknown TEST_PRESET=$(TEST_PRESET)"; exit 2;; \
	esac; \
	TEST="$$TEST" DAY=$(DAY) FEATURE="$(FEATURE)" $(MAKE) day-all
MAKE

# preset script
mkdir -p "$ROOT/scripts/tests"
cat > "$ROOT/scripts/tests/presets.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
case "${1:-python}" in
  python)   echo "pytest -q" ;;
  frontend) echo "npm test -w web/frontend --silent" ;;
  api)      cat <<'PY'
python - <<'PY'
from fastapi.testclient import TestClient
try:
  from app.main import app
  c = TestClient(app)
  r = c.post('/v1/generate', json={'text':'hello'})
  print('status', r.status_code); print('ok', r.ok)
except Exception as e:
  print('smoke failed', e)
PY
PY
  ;;
  all)      echo "pytest -q && npm test -w web/frontend --silent && python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
r = c.post('/v1/generate', json={'text':'hello'})
print('status', r.status_code); print('ok', r.ok)
PY" ;;
  *)        echo "Unknown preset: $1" >&2; exit 2 ;;
esac
SH
chmod +x "$ROOT/scripts/tests/presets.sh"

if git rev-parse --git-dir >/dev/null 2>&1; then
  git add .github/workflows/day-runner.yml .github/workflows/daily-nudge.yml scripts/tests/presets.sh Makefile || true
  git commit -m "bootstrap: day-runner + daily-nudge + Makefile presets" || echo "No changes to commit"
  echo "✅ Push to enable: git push"
else
  echo "✅ Files written (not a git repo)."
fi
