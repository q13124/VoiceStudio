# Overseer Issue System – Operational Runbook

Operational playbook for common scenarios when using the Overseer issue logging and recommendation system.

## Prerequisites

- Project root is the current directory (so `tools.overseer.issues` is importable).
- Optional: `VOICESTUDIO_ISSUES_LOG_DIR` set if using a custom log directory.
- Optional: `VOICESTUDIO_ISSUES_ASYNC=1` for non-blocking issue recording on hot paths.

## 1. Triage a spike of new issues

**Goal**: Identify top patterns and acknowledge or resolve in batch.

```bash
# List new issues (last 24h) by severity
python -m tools.overseer.cli.main issues query --status new --limit 50 --format table

# Top patterns in last 24h
python -m tools.overseer.cli.main issues patterns --time-window 24h --limit 20

# Batch-acknowledge all new issues matching a filter
python -m tools.overseer.cli.main issues bulk-ack --status new --limit 100 -v

# Batch-resolve with a note (e.g. after deploy)
python -m tools.overseer.cli.main issues bulk-resolve --status acknowledged --note "Fixed in release X" -v
```

## 2. Investigate a single issue and apply a recommendation

**Goal**: Get recommendations, apply an action, and record outcome for calibration.

```bash
# Fetch issue with recommendations
python -m tools.overseer.cli.main issues get <issue-id>

# Resolve and record that a recommendation worked (feedback for confidence calibration)
python -m tools.overseer.cli.main issues resolve <issue-id> --note "Restarted engine" --action restart --outcome success

# Or record feedback without resolving (e.g. tried action but deferred)
python -m tools.overseer.cli.main issues feedback <issue-id> retry_with_params deferred --note "Will retry later"
```

## 3. Export for AI review or external tools

**Goal**: Export issues as JSONL or CSV for dashboards or AI review.

```bash
# JSONL (default) for AI/scripts
python -m tools.overseer.cli.main issues export --output review.jsonl --severity critical,high --limit 500

# CSV for spreadsheets
python -m tools.overseer.cli.main issues export --format csv --output issues.csv --limit 1000

# Query with paging and CSV to stdout
python -m tools.overseer.cli.main issues query --format csv --page 1 --page-size 50
```

## 4. Watch for new issues (tail-style)

**Goal**: Stream new issues as they are recorded (e.g. during a test run).

```bash
# Poll every 5 seconds, print new issues (Ctrl+C to stop)
python -m tools.overseer.cli.main issues watch --interval 5 --limit 100
```

## 5. Query by error code

**Goal**: Find all issues that mention a specific error code (e.g. CS0234, HTTP500).

Use the programmatic store or future CLI flag; the store supports `query(error_codes=[...])`. Example from Python:

```python
from tools.overseer.issues.store import IssueStore
store = IssueStore()
issues = store.query(error_codes=["CS0234", "HTTP500"], limit=50)
```

## 6. Prometheus metrics

**Goal**: Expose issue counts for dashboards or alerting.

```python
from tools.overseer.issues.metrics import get_prometheus_metrics
text = get_prometheus_metrics(time_window_hours=24)
# Serve text on GET /metrics or write to a file
```

Metrics include `overseer_issues_total` (by severity/status/instance_type) and `overseer_recommendation_feedback_total` (by outcome).

## 7. Frontend / API reporting

**Goal**: Record issues from the WinUI app or from API 5xx responses.

- **Frontend**: Use `IBackendClient.ReportOverseerIssueAsync(message, category, severity, context)` from C#. The backend writes to the issue store with `instance_type=frontend`.
- **API 5xx**: Backend exception handlers already record 5xx and unhandled exceptions to the issue store with `instance_type=backend` (no extra configuration).

## 8. Storage and retention

- **Location**: `%APPDATA%/VoiceStudio/logs/overseer_issues/` (or `VOICESTUDIO_ISSUES_LOG_DIR`).
- **Files**: `issues_YYYY-MM-DD_NNN.jsonl`; older files are gzip-compressed to `.jsonl.gz` after 1 day (configurable).
- **Retention**: Default 90 days; older files are removed by `IssueStore.cleanup_old_logs()` (run periodically or via a scheduled task).
- **Recommendation feedback**: Stored in `recommendation_feedback.jsonl` in the same directory; used for confidence calibration.

## 9. Failure modes and recovery

| Symptom | Check | Action |
|--------|--------|--------|
| No issues in store | Hooks may be failing with ImportError | Run from repo root; ensure `tools.overseer.issues` is on PYTHONPATH. |
| "Issue not found" | Append-only store; ID might be from an old record | Use `query` with filters; `get_by_id` returns latest occurrence. |
| Recommendations always "investigate" | No learned patterns or low similarity | Add resolution notes; use `learn_from_resolution` or feedback (`resolve --action X --outcome success`). |
| Disk full / permission denied | Store or feedback file unwritable | Fix disk or permissions; async queue may drop issues if store fails. |
| Lock timeout on append | Another process holding the file lock | Increase load spacing or ensure only one writer per log file. |

## 10. Related docs

- **System overview**: [OVERSEER_ISSUE_SYSTEM.md](OVERSEER_ISSUE_SYSTEM.md)
- **SLO definitions**: [SERVICE_LEVEL_OBJECTIVES.md](../governance/SERVICE_LEVEL_OBJECTIVES.md) (issue categories map to SLOs via `tools.overseer.issues.metrics.get_affected_slos`)
- **JSON Schema**: `shared/schemas/issue.schema.json`
- **Canonical registry**: [CANONICAL_REGISTRY.md](../governance/CANONICAL_REGISTRY.md)
