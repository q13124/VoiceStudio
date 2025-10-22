#!/usr/bin/env bash
set -euo pipefail
case "${1:-python}" in
  python)   echo "pytest -q" ;;
  frontend) echo "npm test -w web/frontend --silent" ;;
  api)      cat <<'PY'
python - <<'PY'
from fastapi.testclient import TestClient
from services.main import app
c = TestClient(app)
r = c.post('/v1/generate', json={'text':'hello'})
print('status', r.status_code)
assert r.status_code in (200, 422), 'endpoint reachable'
print('API test passed!')
PY
PY
  ;;
  all)      echo "pytest -q && npm test -w web/frontend --silent && python - <<'PY'
from fastapi.testclient import TestClient
from services.main import app
c = TestClient(app)
r = c.post('/v1/generate', json={'text':'hello'})
print('status', r.status_code)
assert r.status_code in (200, 422), 'endpoint reachable'
print('API test passed!')
PY" ;;
  *)        echo "Unknown preset: $1" >&2; exit 2 ;;
esac
