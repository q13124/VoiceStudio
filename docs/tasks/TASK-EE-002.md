# TASK-EE-002: Quality Metrics Dashboard Backend

## Objective

Implement backend services for the Quality Metrics Dashboard: real-time engine quality metrics, historical trends, SLO tracking, and durable persistence. TASK-EE-002 (Role 5 Engine Engineer).

## Status

- [x] Complete

## Owner

- **Role 5 (Engine Engineer)**

## Deliverables

### 1. Quality Metrics Endpoints

- **GET /api/quality/metrics** — Current metrics for all engines (aggregated from quality history and engine list).
- **GET /api/quality/metrics/{engine_id}** — Detailed metrics for a specific engine (avg MOS, similarity, latency P50/P95, SLO compliance).
- **GET /api/quality/slo** — SLO compliance status for all engines (MOS >= 3.5, Similarity >= 0.7, P50 latency <= 3s, P95 <= 10s).
- **POST /api/quality/benchmark** — Already existed; run quality benchmark across engines.

### 2. Quality Metrics Persistence

- **File**: [backend/services/quality_metrics_db.py](../../backend/services/quality_metrics_db.py)
- **Features**:
  - SQLite-backed storage at `.voicestudio/quality_metrics.db`
  - `insert(entry)` — Store quality history entry
  - `get_entries_by_profile(profile_id, limit, since, until)` — History by profile
  - `get_all_entries_for_aggregation()` — All entries for /metrics and /slo
  - `query(engine_id, since)` — Entries by engine
  - `get_engine_metrics(engine_id, period)` — Aggregated metrics for engine
  - Per-profile and total entry limits (1000 per profile, 10000 total)

### 3. Quality Routes Integration

- [backend/api/routes/quality.py](../../backend/api/routes/quality.py):
  - `store_quality_history`: Writes to DB when `HAS_QUALITY_DB`; in-memory fallback retained.
  - `get_quality_history`: Reads from DB when available; returns `QualityHistoryResponse`.
  - `get_quality_trends`, degradation, baseline, dashboard: Use `_get_entries_for_profile()` / `_get_quality_history_entries()` so data comes from DB when available.

### 4. SLO Targets (per ENGINE_REFERENCE / ROLE_5)

- MOS score: >= 3.5
- Similarity: >= 0.7
- Latency P50: <= 3.0 s
- Latency P95: <= 10.0 s

## Verification

```powershell
# Syntax and imports
python -c "from backend.services.quality_metrics_db import get_quality_metrics_db; get_quality_metrics_db()"
python scripts/run_verification.py

# When backend running
curl http://localhost:8001/api/quality/metrics
curl http://localhost:8001/api/quality/slo
curl http://localhost:8001/api/quality/metrics/xtts_v2
```

## Acceptance Criteria

- [x] GET /api/quality/metrics returns engine metrics
- [x] GET /api/quality/metrics/{engine_id} returns single-engine metrics
- [x] GET /api/quality/slo returns SLO compliance summary
- [x] QualityMetricsDatabase persists entries across restarts
- [x] Quality history endpoints use DB when available
- [x] Verification script PASS

## References

- [ROLE_5_ENGINE_ENGINEER_GUIDE.md](../governance/roles/ROLE_5_ENGINE_ENGINEER_GUIDE.md)
- [ENGINE_REFERENCE.md](../REFERENCE/ENGINE_REFERENCE.md)
- [QUALITY_METRICS_DASHBOARD_SPEC](../design/QUALITY_METRICS_DASHBOARD_SPEC.md) (if present)
