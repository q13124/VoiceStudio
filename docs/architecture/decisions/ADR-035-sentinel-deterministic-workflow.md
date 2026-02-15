# ADR-035: Sentinel Deterministic Workflow

**Status:** Accepted
**Date:** 2026-02-12
**Decision Makers:** VoiceStudio Architecture Team

## Context

VoiceStudio requires a deterministic, reproducible method to validate the complete audio processing pipeline across different environments and configurations. Manual testing is insufficient for:

- Pre-release validation of API contract compliance
- CI/CD pipeline quality gates
- Regression detection in audio synthesis
- Debugging production issues with reproducible evidence

We need a "sentinel" workflow that exercises the full VoiceStudio pipeline with known inputs and produces verifiable outputs.

## Decision

We adopt a 7-step sentinel workflow architecture with reproducibility packets ("repro packets"):

### Workflow Steps

| Step | Endpoint | Purpose |
|------|----------|---------|
| 1. Health | `GET /api/health/simple` | Preflight/readiness check |
| 2. Upload | `POST /api/audio/upload` | Audio file import |
| 3. Sync Synth | `POST /api/voice/synthesize` | Synchronous TTS |
| 4. Async Synth | `POST /api/batch/jobs` | Batch job creation |
| 5. Poll Job | `GET /api/batch/jobs/{id}` | Job completion polling |
| 6. A/B Test | `POST /api/voice/synthesize/ab` | Engine comparison |
| 7. Eval | `GET /api/audio/{id}/analysis` | Quality metrics |

### Repro Packet Structure

```
artifacts/sentinel_runs/{run_id}/
├── summary.json         # Overall run status, invariants, timing
├── steps.jsonl          # Step-by-step execution log
├── requests/            # Request payloads per step
│   ├── health.json
│   ├── upload.json
│   └── ...
├── responses/           # Response payloads per step
│   ├── health.json
│   ├── upload.json
│   └── ...
└── outputs/             # Generated audio files (if any)
```

### JSON Schema Contracts

All API interactions are validated against JSON schemas in `tests/sentinel/contracts/`:

- `health_response.schema.json`
- `upload_response.schema.json`
- `tts_request.schema.json`
- `tts_response.schema.json`
- `job_response.schema.json`
- `ab_summary_response.schema.json`

### Resilience Patterns

1. **Retry with Exponential Backoff**: Transient failures (429, 500-504) are retried with jitter
2. **Circuit Breaker**: Prevents cascading failures after repeated errors
3. **Correlation IDs**: All requests carry correlation headers for tracing
4. **Structured Logging**: All events are logged with context for debugging

### Configuration

Environment variable overrides via `scripts/proof_runs/config.py`:

```
SENTINEL_API_BASE         - API base URL
SENTINEL_HEALTH_TIMEOUT   - Health check timeout (seconds)
SENTINEL_RETRY_COUNT      - Maximum retry attempts
SENTINEL_CB_FAILURE_THRESHOLD - Circuit breaker threshold
```

## Rationale

### Why Deterministic?

- Same fixture + same API state = same results
- SHA256 hashes of requests/responses enable diff-based debugging
- Run IDs include timestamps for chronological ordering

### Why 7 Steps?

These steps exercise the critical path through VoiceStudio:
1. Health: Ensures API is ready
2. Upload: Tests audio ingestion
3. Sync Synth: Tests immediate TTS
4. Async Synth: Tests job queue integration
5. Poll: Tests async completion detection
6. A/B: Tests engine comparison feature
7. Eval: Tests quality metrics pipeline

### Why JSON Schemas?

- Contract-first development: schemas define API surface
- Runtime validation: responses are validated against schemas
- Documentation: schemas serve as API documentation
- Versioning: schema changes are tracked in git

## Consequences

### Positive

- Reproducible: Any failure can be reproduced with the repro packet
- Deterministic: Same inputs produce comparable outputs
- CI-Integrated: GitHub Actions workflow runs sentinel on every push
- Debuggable: Correlation IDs trace requests through the system
- Documented: JSON schemas serve as API contracts

### Negative

- Storage: Repro packets consume disk space (~50KB per run)
- CI Time: Full sentinel run adds ~2-3 minutes to CI pipeline
- Maintenance: Schema changes require coordinated updates

### Mitigation

- Artifacts are retained for 7 days in CI, indefinitely for important runs
- Sentinel tests run in parallel with other CI jobs
- Schema validation tests catch contract drift early

## Implementation

### Key Files

| File | Purpose |
|------|---------|
| `scripts/proof_runs/sentinel_audio_workflow.py` | Main runner implementation |
| `scripts/proof_runs/config.py` | Configuration management |
| `tests/sentinel/test_sentinel_audio_workflow.py` | Test suite |
| `tests/sentinel/conftest.py` | Pytest fixtures |
| `tests/sentinel/contracts/*.schema.json` | JSON Schema contracts |
| `.github/workflows/sentinel_backend_smoke.yml` | CI workflow |
| `fixtures/audio/sentinel_16k_mono.wav` | Deterministic test fixture |

### Usage

```bash
# Run sentinel workflow directly
python scripts/proof_runs/sentinel_audio_workflow.py --api-base http://localhost:8000

# Run pytest suite
python -m pytest tests/sentinel/ -v -m smoke

# Run with backend (integration tests)
python -m pytest tests/sentinel/ -v -m backend_required
```

## Related Decisions

- ADR-007: IPC Boundary (defines control plane vs data plane)
- ADR-027: Unified Verification Harness (overall verification strategy)
- ADR-031: API Versioning Strategy (contract evolution)
- ADR-032: Middleware Stack (correlation ID propagation)

## References

- `docs/design/DETERMINISTIC_SENTINEL_IMPLEMENTATION_PLAN.md`
- `docs/developer/SENTINEL_TESTING_GUIDE.md`
- `docs/REFERENCE/SENTINEL_CONTRACT_SCHEMAS.md`
