.PHONY: help install dev prod test clean migrate backup restore docker-up docker-down day-plan day-exec day-test day-review day-fix day-commit day-all exporter-build exporter-run exporter-stop exporter-logs agent-run agent-stop agent-logs prober-run prober-push db-upgrade db-revise test-python test-frontend test-api test-all day-preset cursor-agent cursor-agent-optimal

# Default target
help:
	@echo "VoiceStudio Operations Makefile"
	@echo ""
	@echo "Development:"
	@echo "  dev          - Start development environment"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo ""
	@echo "Database:"
	@echo "  migrate      - Run database migrations"
	@echo "  backup       - Create database backup"
	@echo "  restore      - Restore from backup (requires BACKUP_FILE)"
	@echo ""
	@echo "Production:"
	@echo "  prod         - Start production environment"
	@echo "  docker-up    - Start all Docker services"
	@echo "  docker-down  - Stop all Docker services"
	@echo ""
	@echo "Monitoring:"
	@echo "  exporter-build - Build SQLite metrics exporter Docker image"
	@echo "  exporter-run   - Start SQLite metrics exporter"
	@echo "  exporter-stop  - Stop SQLite metrics exporter"
	@echo "  exporter-logs  - View exporter logs"
	@echo "  agent-run      - Start Grafana Agent"
	@echo "  agent-stop     - Stop Grafana Agent"
	@echo "  agent-logs     - View agent logs"
	@echo "  prober-run     - Run synthetic health probe"
	@echo "  prober-push    - Push probe metrics to Pushgateway"
	@echo ""
	@echo "Testing:"
	@echo "  test-python    - Run Python tests"
	@echo "  test-frontend  - Run frontend tests"
	@echo "  test-api       - Run API smoke tests"
	@echo "  test-all       - Run all tests"
	@echo ""
	@echo "Database:"
	@echo "  db-upgrade     - Run database migrations"
	@echo "  db-revise      - Create new migration"
	@echo ""
	@echo "Utilities:"
	@echo "  clean        - Clean temporary files"
	@echo "  client-test  - Test A/B ingest client"
	@echo "  cursor-agent - Run Cursor agent for automated task execution"
	@echo "  cursor-agent-optimal - Run optimized Cursor agent with smart file detection"
	@echo ""
	@echo "Daily Workflow (15-min sprints):"
	@echo "  day-plan     - Show ChatGPT prompt template"
	@echo "  day-exec     - Guide for Cursor execution"
	@echo "  day-test     - Run quick test (requires TEST=)"
	@echo "  day-review   - Show ChatGPT review prompt"
	@echo "  day-fix      - Guide for Cursor fixes"
	@echo "  day-commit   - Commit changes (requires DAY=, FEATURE=)"
	@echo "  day-all      - Complete workflow (requires DAY=, FEATURE=, TEST=)"
	@echo "  day-preset   - Run preset workflow (requires DAY=, FEATURE=, TEST_PRESET=)"

# Development
dev:
	@echo "Starting development environment..."
	@if [ ! -f .env ]; then cp env.example .env; fi
	@export $$(cat .env | xargs) && uvicorn services.main:app --reload --host 0.0.0.0 --port 8000

install:
	@echo "Installing dependencies..."
	pip install -r requirements.lock.txt

test:
	@echo "Running tests..."
	pytest -v

# Database operations
migrate:
	@echo "Running database migrations..."
	alembic upgrade head

backup:
	@echo "Creating database backup..."
	python scripts/backup_db.py --backup-dir ./backups

restore:
	@if [ -z "$(BACKUP_FILE)" ]; then echo "Error: BACKUP_FILE not set"; exit 1; fi
	@echo "Restoring from $(BACKUP_FILE)..."
	@if echo "$(BACKUP_FILE)" | grep -q "\.gz$$"; then \
		gunzip -c "$(BACKUP_FILE)" | psql "$(DB_URL)"; \
	else \
		psql "$(DB_URL)" < "$(BACKUP_FILE)"; \
	fi

# Production
prod:
	@echo "Starting production environment..."
	@if [ ! -f .env ]; then cp env.example .env; fi
	@export $$(cat .env | xargs) && python scripts/deploy.sh

# Docker operations
docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

# Monitoring
exporter:
	@echo "Starting SQLite metrics exporter..."
	docker-compose -f docker-compose.sqlite-exporter.yml up -d

grafana:
	@echo "Grafana available at: http://localhost:3000"
	@echo "Admin password: admin (change in production)"

# Utilities
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .coverage

client-test:
	@echo "Testing A/B ingest client..."
	python scripts/ab_ingest_client.py \
		--api http://localhost:8000 \
		--session ab-test-$(shell date +%Y%m%d) \
		--ratings examples/ratings.json \
		--run-id nightly-$(shell date +%Y%m%d) \
		--date $(shell date +%Y-%m-%d) \
		--per-engine examples/per_engine.json \
		--token supersecrettoken

# CI/CD helpers
ci-test:
	@echo "Running CI tests..."
	pytest --cov=app --cov-report=xml

ci-migrate:
	@echo "Running CI migrations..."
	alembic upgrade head

# Health checks
health:
	@echo "Checking application health..."
	curl -f http://localhost:8000/v1/health/metrics || echo "Health check failed"

# Database status
db-status:
	@echo "Database status:"
	@python -c "from app.core.db import engine; print('Connected' if engine.connect() else 'Failed')"

# Show environment
env:
	@echo "Current environment:"
	@env | grep -E "(DB_URL|AB_PERSIST|EVALS_INGEST)" | sort

# ===== Daily Workflow (15-min sprints) =====
# 0–2 min: ChatGPT plan (opens your doc for the prompt template)
day-plan:
	@printf "\n=== ChatGPT Prompt ===\nVoiceStudio Day $$DAY: $$FEATURE\n\nOutput ONLY:\n1. File path\n2. Complete code\n3. Test command\n\nNo explanations.\n" && \
	echo "\n(See docs/15_MINUTE_WORKFLOW.md)"

# 2–5 min: Cursor executes (just an echo to guide; you paste in Cursor)
day-exec:
	@echo "Open Cursor → Ctrl+K → paste plan → Ctrl+Enter (Accept)."

# 5–10 min: Quick test
day-test:
	@test -n "$$TEST" || (echo "Set TEST=\"your quick command\""; exit 1)
	@echo "Running: $$TEST"; bash -lc "$$TEST"

# 10–12 min: ChatGPT critical review
day-review:
	@printf "\n=== ChatGPT Prompt (Review) ===\nQuick review: [paste diff/output]. Critical issues only.\n"

# 12–15 min: Cursor fixes
day-fix:
	@echo "Cursor Ctrl+L → paste critical issues → accept."

# Commit
day-commit:
	@git add -A && git commit -m "Day $$DAY: $$FEATURE" && git push

# all-in-one skeleton (expects DAY, FEATURE, TEST env vars)
day-all: day-plan day-exec day-test day-review day-fix day-commit

# ===== SQLite → Prometheus exporter =====
.PHONY: exporter-build exporter-run exporter-stop exporter-logs

exporter-build:
	@docker build -t voicestudio-sqlite-exporter:latest ops/sqlite_metrics_exporter

exporter-run:
	@DB_URL?=sqlite:///./app.db
	@docker rm -f voicestudio-sqlite-exporter >/dev/null 2>&1 || true
	@docker run -d --name voicestudio-sqlite-exporter \
		-e DB_URL=$(DB_URL) \
		-p 8001:8001 \
		-v $$(pwd)/app.db:/app/app.db \
		voicestudio-sqlite-exporter:latest
	@echo "Exporter on http://localhost:8001/metrics"

exporter-stop:
	@docker rm -f voicestudio-sqlite-exporter >/dev/null 2>&1 || true

exporter-logs:
	@docker logs -f voicestudio-sqlite-exporter

# ===== Grafana Agent (scrapes API + exporter) =====
.PHONY: agent-run agent-stop agent-logs

agent-run:
	@REMOTE_USER?=user
	@REMOTE_PASS?=pass
	@docker rm -f voicestudio-agent >/dev/null 2>&1 || true
	@docker run -d --name voicestudio-agent \
		-p 12345:12345 \
		-e REMOTE_USER=$(REMOTE_USER) -e REMOTE_PASS=$(REMOTE_PASS) \
		-v $$(pwd)/ops/agent/agent.yaml:/etc/agent/agent.yaml \
		grafana/agent:latest \
		--config.file=/etc/agent/agent.yaml
	@echo "Agent running. Remote write per ops/agent/agent.yaml"

agent-stop:
	@docker rm -f voicestudio-agent >/dev/null 2>&1 || true

agent-logs:
	@docker logs -f voicestudio-agent

# ===== Synthetic prober =====
.PHONY: prober-run prober-push

prober-run:
	@API_BASE?=http://localhost:8000
	@TEXT?=Hello\, this is a health probe.
	python ops/synth_prober/prober.py --api $$API_BASE --text "$$TEXT"

prober-push:
	@API_BASE?=http://localhost:8000
	@PUSHGATEWAY_URL?=http://localhost:9091
	python ops/synth_prober/prober.py --api $$API_BASE --pushgateway $$PUSHGATEWAY_URL --text "Hello from CI"

# ===== DB Migrations convenience =====
.PHONY: db-upgrade db-revise

db-upgrade:
	@DB_URL?=sqlite:///./app.db
	DB_URL=$(DB_URL) alembic upgrade head

db-revise:
	@MSG?=changes
	@DB_URL?=sqlite:///./app.db
	DB_URL=$(DB_URL) alembic revision --autogenerate -m "$(MSG)"

# ===== Test presets =====
.PHONY: test-python test-frontend test-api test-all

# Customize these to your repo structure
PY_TEST?=pytest -q
FE_TEST?=npm test -w web/frontend --silent
API_SMOKE?=python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
r = c.post('/v1/generate', json={'text':'hello'})
print('status', r.status_code)
print('ok', r.ok)
assert r.status_code in (200, 422), 'endpoint reachable'
PY

# One-liners
test-python:
	$(PY_TEST)

test-frontend:
	$(FE_TEST)

test-api:
	$(API_SMOKE)

test-all: test-python test-frontend test-api

# ===== Day runner with presets =====
.PHONY: day-preset
# Usage: make day-preset DAY=5 FEATURE="X" TEST_PRESET=python|frontend|api|all

TEST_PRESET?=python

define _pick_test
if [ "$(TEST_PRESET)" = "python" ]; then \
  TEST='$(PY_TEST)'; \
elif [ "$(TEST_PRESET)" = "frontend" ]; then \
  TEST='$(FE_TEST)'; \
elif [ "$(TEST_PRESET)" = "api" ]; then \
  TEST='$(API_SMOKE)'; \
else \
  TEST='$(PY_TEST) && $(FE_TEST) && $(API_SMOKE)'; \
fi; \
TEST="$$TEST" DAY=$(DAY) FEATURE="$(FEATURE)" $(MAKE) day-all
endef

day-preset:
	@$(value _pick_test)

# ===== Cursor Agent =====
.PHONY: cursor-agent

cursor-agent:
	@python scripts/cursor_agent.py --file docs/CURSOR_INSTRUCTIONS.md --interval 20 --push

cursor-agent-optimal:
	@python scripts/cursor_agent/agent.py --interval 60 --push
