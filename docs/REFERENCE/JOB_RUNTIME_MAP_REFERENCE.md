# Job Runtime Map Reference

**Domain:** Core Platform (Role 4)
**Created:** 2026-02-10
**Status:** Active

## Overview

This document describes VoiceStudio's job execution model, state management, and cancellation flow.

## Job States

```
PENDING → RUNNING → COMPLETED
              ↓
           FAILED
              ↓
         CANCELLED
```

| State | Description |
|-------|-------------|
| `pending` | Job queued, awaiting resources |
| `running` | Job actively processing |
| `completed` | Job finished successfully |
| `failed` | Job encountered an error |
| `cancelled` | Job stopped by user request |

## Job Types

| Type | Engine | Estimated Duration |
|------|--------|-------------------|
| `synthesis` | XTTS, Piper, etc. | 2-30s |
| `transcription` | Whisper, Vosk | 1-5x audio length |
| `training` | Voice cloning | 5-60 min |
| `conversion` | RVC | 10-60s |
| `translation` | S2S | 2-30s |

## JobStateStore

Location: `backend/services/JobStateStore.py`

Key methods:
- `create_job(job_type, params)` → `JobId`
- `update_status(job_id, status, progress)`
- `get_job(job_id)` → `JobState`
- `cancel_job(job_id)`

## Cancellation Flow

1. Client calls `POST /api/jobs/{id}/cancel`
2. JobStateStore marks job as `cancelling`
3. Engine receives cancellation signal
4. Engine cleanup runs
5. Job marked as `cancelled`

## API Endpoints

- `GET /api/jobs` - List jobs
- `GET /api/jobs/{id}` - Get job details
- `POST /api/jobs` - Create job
- `DELETE /api/jobs/{id}` - Cancel job

## Related Documents

- [Storage Durability Reference](STORAGE_DURABILITY_REFERENCE.md)
- [Preflight Reference](PREFLIGHT_REFERENCE.md)
