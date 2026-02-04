# Overseer Issue System

**Last Updated**: 2026-02-02  
**Owner**: Overseer (Role 0)

This document describes the VoiceStudio Overseer Issue System — a unified error tracking, pattern matching, and automatic task generation system for development operations.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [API Reference](#api-reference)
5. [CLI Commands](#cli-commands)
6. [Integration Guide](#integration-guide)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Overseer Issue System provides:

- **Unified Error Recording**: Capture errors from agents, engines, backend, and build systems
- **Pattern Matching**: Group similar issues using normalized message hashing
- **Automatic Task Creation**: Generate task briefs for critical/high severity issues
- **Recommendations**: ML-based suggestions for issue resolution
- **Cross-Role Escalation**: Route issues to appropriate role owners

### Design Principles

- **Local-first**: All data stored locally in JSONL files
- **Free-only**: No paid dependencies or external services
- **Append-only**: Issues are immutable once recorded; updates create new entries
- **Thread-safe**: Concurrent access protected by file locks

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Error Sources                            │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│   Agent     │   Engine    │   Backend   │   Build/Verify   │
│   Errors    │   Errors    │   Errors    │   Errors         │
└──────┬──────┴──────┬──────┴──────┬──────┴───────┬──────────┘
       │             │             │              │
       ▼             ▼             ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Issue Aggregator                          │
│  - Sanitize (remove secrets/PII)                            │
│  - Enrich context                                            │
│  - Calculate pattern hash                                    │
│  - Extract error codes                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Issue Store                              │
│  - Append-only JSONL storage                                 │
│  - File rotation (by size/date)                              │
│  - Compression (after N days)                                │
│  - Query interface                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│ Task Generator  │ │ Pattern     │ │ Recommendation  │
│ (auto-create    │ │ Matcher     │ │ Engine          │
│  task briefs)   │ │ (grouping)  │ │ (suggestions)   │
└─────────────────┘ └─────────────┘ └─────────────────┘
```

---

## Components

### 1. Issue Aggregator (`tools/overseer/issues/aggregator.py`)

Central entry point for all error recording.

**Key Functions**:

| Function | Description |
|----------|-------------|
| `record_issue()` | Main entry point for any issue type |
| `record_agent_error()` | Wrapper for agent audit errors |
| `record_backend_error()` | Wrapper for FastAPI errors |
| `record_engine_error()` | Wrapper for ML engine errors |
| `record_build_error()` | Wrapper for build/verification errors |

### 2. Issue Store (`tools/overseer/issues/store.py`)

Append-only JSONL storage with querying.

**Key Features**:
- Thread-safe with file locking
- Automatic file rotation (by size and date)
- Compression of old files
- Rich query interface

### 3. Task Generator (`tools/overseer/issues/task_generator.py`)

Automatically creates task briefs from qualifying issues.

**Qualification Criteria**:
- Severity: `critical` or `high`
- No existing linked task
- Auto-task not disabled via `VOICESTUDIO_AUTO_TASK_DISABLED`

### 4. Pattern Matcher (`tools/overseer/issues/pattern_matcher.py`)

Groups similar issues using TF-IDF and stack frame matching.

### 5. Recommendation Engine (`tools/overseer/issues/recommendation_engine.py`)

Generates resolution suggestions based on similar historical issues.

### 6. Sanitizer (`tools/overseer/issues/sanitizer.py`)

Removes secrets and PII from messages and context before storage.

---

## API Reference

### Recording Issues

```python
from tools.overseer.issues.aggregator import record_issue
from tools.overseer.issues.models import InstanceType, IssueSeverity

issue = record_issue(
    instance_type=InstanceType.ENGINE,
    instance_id="xtts-engine-001",
    correlation_id="req-12345",
    error_type="SynthesisError",
    message="Failed to synthesize audio: CUDA out of memory",
    context={"gpu_memory": "8GB", "model": "xtts_v2"},
    severity=IssueSeverity.HIGH,
    category="ENGINE",
    auto_task=True,  # Create task brief if qualifying
)

print(f"Issue ID: {issue.id}")
```

### Querying Issues

```python
from tools.overseer.issues.store import IssueStore

store = IssueStore()

# Get all critical issues from last 24 hours
issues = list(store.query(
    severity="critical",
    hours=24,
    limit=50,
))

# Get by pattern hash (similar issues)
similar = list(store.query(
    filters={"pattern_hash": "abc123def456"}
))
```

---

## CLI Commands

The issue system is accessible via the Overseer CLI.

### Query Issues

```bash
# List recent issues
python -m tools.overseer.cli.main issues query --hours 24

# Filter by severity
python -m tools.overseer.cli.main issues query --severity critical

# Filter by instance type
python -m tools.overseer.cli.main issues query --instance-type engine

# Export to JSON
python -m tools.overseer.cli.main issues query --format json > issues.json
```

### Issue Details

```bash
# Get specific issue
python -m tools.overseer.cli.main issues get <issue-id>

# Show similar issues (pattern matching)
python -m tools.overseer.cli.main issues patterns <issue-id>
```

### Issue Management

```bash
# Acknowledge an issue
python -m tools.overseer.cli.main issues acknowledge <issue-id>

# Resolve an issue
python -m tools.overseer.cli.main issues resolve <issue-id> --by "Role 5"

# Link to task
python -m tools.overseer.cli.main issues link-task <issue-id> TASK-0026
```

### Bulk Operations

```bash
# Acknowledge all matching issues
python -m tools.overseer.cli.main issues bulk-ack --severity low --hours 48

# Export for analysis
python -m tools.overseer.cli.main issues export --format csv > issues.csv
```

---

## Integration Guide

### Backend Error Handler Integration

Add to `backend/api/error_handling.py`:

```python
from tools.overseer.issues.aggregator import record_backend_error
import traceback

async def general_exception_handler(request: Request, exc: Exception):
    # Existing handling...
    
    # Record to issue system
    try:
        record_backend_error(
            error_type=type(exc).__name__,
            message=str(exc),
            severity="high" if is_critical(exc) else "medium",
            traceback=traceback.format_exc(),
            request_id=getattr(request.state, "request_id", None),
        )
    except Exception:
        pass  # Don't fail request on issue recording error
```

### Engine Runtime Integration

Add to engine exception handlers:

```python
from tools.overseer.issues.aggregator import record_engine_error

try:
    result = engine.synthesize(...)
except Exception as e:
    record_engine_error(
        engine_id=engine_id,
        error=e,
        correlation_id=job_id,
        context={"input": input_params},
    )
    raise
```

### Build/Verification Integration

Add to verification scripts:

```python
from tools.overseer.issues.aggregator import record_build_error

if check_failed:
    record_build_error(
        instance_id=f"verification-{check_name}",
        error_type="VerificationFailure",
        message=error_output,
        context={"check": check_name, "exit_code": exit_code},
    )
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VOICESTUDIO_ISSUES_DIR` | Issue storage directory | `~/.voicestudio/issues` |
| `VOICESTUDIO_ISSUES_ASYNC` | Enable async write-behind | `false` |
| `VOICESTUDIO_AUTO_TASK_DISABLED` | Disable auto-task creation | `false` |

### Config File

Located at `tools/overseer/issues/config.py`:

```python
ISSUES_LOG_DIR = Path.home() / ".voicestudio" / "issues"
MAX_FILE_SIZE_MB = 10
RETENTION_DAYS = 90
COMPRESS_AFTER_DAYS = 7
```

---

## Troubleshooting

### Issues Not Being Recorded

1. Check if aggregator is imported correctly:
   ```python
   python -c "from tools.overseer.issues.aggregator import record_issue"
   ```

2. Verify storage directory is writable:
   ```bash
   ls -la ~/.voicestudio/issues/
   ```

3. Check for import errors in logs.

### Task Generator Not Creating Tasks

1. Verify severity is `critical` or `high`
2. Check if auto-task is disabled:
   ```bash
   echo $VOICESTUDIO_AUTO_TASK_DISABLED
   ```
3. Verify `docs/tasks/` directory exists

### Pattern Matching Not Working

1. Run pattern analysis:
   ```bash
   python -m tools.overseer.cli.main issues patterns <issue-id>
   ```

2. Check TF-IDF index:
   ```bash
   python -c "from tools.overseer.issues.pattern_matcher import PatternMatcher; print(PatternMatcher().stats())"
   ```

---

## Related Documentation

- [Quality Ledger](../../Recovery%20Plan/QUALITY_LEDGER.md) — Source of truth for tracked issues
- [Debug Agent Guide](../governance/roles/ROLE_7_DEBUG_AGENT_GUIDE.md) — Debug workflow integration
- [Overseer Issue Runbook](OVERSEER_ISSUE_RUNBOOK.md) — Operational playbook
