# GitHub Actions Error Report - VoiceStudio

## Overview
This document contains all GitHub Actions workflow failures for the VoiceStudio project. Each section includes the workflow name, error details, and context.

## How to Use This Document
1. Go to GitHub → Actions tab
2. For each failed workflow run, click on it to see the logs
3. Copy the error messages and paste them into the relevant sections below
4. Send this document to Claude for analysis

---

## Workflow Failures

### 1. handshake-status.yml
**Status**: ❌ FAILING
**Last Run**: [INSERT DATE/TIME]
**Error Details**:
```
[PASTE ERROR MESSAGES HERE]
```

**Steps that failed**:
- [ ] Build 60s status (auto-grab)
- [ ] Update docs/HANDSHAKE_STATUS.md
- [ ] Commit & push status
- [ ] Post to pinned 'Handshake Feed' issue

**Full Log Output**:
```
[PASTE FULL LOG OUTPUT HERE]
```

---

### 2. ci.yml
**Status**: ❌ FAILING
**Last Run**: [INSERT DATE/TIME]
**Error Details**:
```
[PASTE ERROR MESSAGES HERE]
```

**Steps that failed**:
- [ ] Generate lockfile
- [ ] Run Alembic migrations (SQLite)
- [ ] Run Alembic migrations (PostgreSQL)
- [ ] Run tests

**Full Log Output**:
```
[PASTE FULL LOG OUTPUT HERE]
```

---

### 3. db-migrate.yml
**Status**: ❌ FAILING
**Last Run**: [INSERT DATE/TIME]
**Error Details**:
```
[PASTE ERROR MESSAGES HERE]
```

**Steps that failed**:
- [ ] Run migrations (upgrade head)
- [ ] Smoke import models

**Full Log Output**:
```
[PASTE FULL LOG OUTPUT HERE]
```

---

### 4. VoiceStudio Ultimate Tests
**Status**: ❌ FAILING
**Last Run**: [INSERT DATE/TIME]
**Error Details**:
```
[PASTE ERROR MESSAGES HERE]
```

**Steps that failed**:
- [ ] Install dependencies
- [ ] Run tests

**Full Log Output**:
```
[PASTE FULL LOG OUTPUT HERE]
```

---

### 5. Dependency Lock Check
**Status**: ❌ FAILING
**Last Run**: [INSERT DATE/TIME]
**Error Details**:
```
[PASTE ERROR MESSAGES HERE]
```

**Steps that failed**:
- [ ] Generate lockfile
- [ ] Verify lockfile drift

**Full Log Output**:
```
[PASTE FULL LOG OUTPUT HERE]
```

---

### 6. OpenAPI Schema Validation
**Status**: ❌ FAILING
**Last Run**: [INSERT DATE/TIME]
**Error Details**:
```
[PASTE ERROR MESSAGES HERE]
```

**Steps that failed**:
- [ ] Generate OpenAPI schema
- [ ] Validate schema

**Full Log Output**:
```
[PASTE FULL LOG OUTPUT HERE]
```

---

## Common Error Patterns

### Import Errors
- `ModuleNotFoundError: No module named 'app.main'`
- `ModuleNotFoundError: No module named 'services.main'`
- `ModuleNotFoundError: No module named 'app.core.settings'`

### Database Errors
- `sqlite3.OperationalError: no such index`
- `alembic.util.messaging] Multiple head revisions`
- `psycopg2.OperationalError: connection refused`

### Test Errors
- `pytest: ERROR: Multiple head revisions`
- `AttributeError: 'Response' object has no attribute 'ok'`
- `Failed: async def function`

### Workflow Errors
- `bash: tooling/lock/generate_lock.sh: No such file or directory`
- `chmod: cannot access 'tooling/lock/generate_lock.sh'`
- `gh: command not found`

---

## Instructions for Claude

Please analyze the error patterns above and provide:

1. **Root Cause Analysis**: What's causing each workflow to fail?
2. **Fix Priority**: Which fixes should be applied first?
3. **Specific Solutions**: Exact code changes needed for each error
4. **Testing Strategy**: How to verify fixes work before claiming success
5. **Prevention**: How to avoid these errors in the future

**Important**: Do not claim anything is fixed until the user confirms the workflows are actually passing in GitHub Actions.

---

## Recent Fixes Attempted

1. **Alembic migrations**: Removed duplicate migration files, generated proper initial migration
2. **Test conflicts**: Removed conflicting test directories
3. **Import paths**: Fixed `services.main` vs `app.main` issues
4. **Dependencies**: Regenerated `requirements.txt`
5. **Workflow robustness**: Added `continue-on-error` to various steps
6. **Handshake throttling**: Changed from hourly to every 15 minutes

**Status**: All fixes tested locally but workflows still failing in GitHub Actions environment.
