# ADR-043: Model Lifecycle Strategy

**Status:** Accepted
**Date:** 2026-02-21
**Decision Makers:** Overseer (Role 0)
**Phase:** 8 - Ecosystem Maturity

## Context

VoiceStudio engines use model artifacts (checkpoints, ONNX, GGUF) for synthesis and transcription. Prior to Phase 8:

- `engines/models.index.json` has a single seed catalog entry
- `app.core.models.storage.ModelStorage` manages model storage and checksums
- `backend/services/model_preflight.py` handles download and validation
- No centralized version tracking, active/archived status, or rollback
- No per-model performance baselines or degradation detection
- A/B testing exists but was not wired to engine/model version selection

## Decision

Introduce a **Model Lifecycle Service** that:

1. **Model Registry** (`backend/services/model_registry.py`): Centralized catalog of model artifacts with version tracking, active/available/archived status, and rollback. Persists to `data/model_registry.json` (local-first).

2. **Model health tracking** (`backend/services/model_baselines.py`): Per-model performance baselines (latency p95, RTF, throughput). Persists to `data/model_baselines.json`. Compares current metrics to baselines; emits warnings when degradation >20%.

3. **Engine A/B testing integration**: Experiments created via `POST /api/models/experiment` route synthesis to different model versions. Variants use config with `engine_id` and `model_version`.

4. **Model rollback**: When health check fails or user requests rollback, `POST /api/models/registry/{engine_id}/rollback` reverts to previous known-good version.

5. **API**: `GET /api/models/registry`, `GET /api/models/registry/{engine_id}`, `POST /api/models/registry/{engine_id}/activate`, `POST /api/models/registry/{engine_id}/rollback`, `POST /api/models/experiment`.

## Rationale

- **Local-first**: No cloud dependency; JSON files in `data/`.
- **Single developer**: Simple JSON store; no MLflow or SQL.
- **Complements existing**: Builds on `models.index.json`, `model_preflight`, `ab_testing`.
- **Production hardening**: Enables version control, rollback, and degradation detection.

## Consequences

### Positive

- Centralized model versioning and activation
- Rollback capability for failed deployments
- Performance baseline tracking and degradation alerts
- Engine A/B testing for model version comparison

### Negative

- Two registries: `ModelStorage` (storage/checksums) + `ModelRegistryService` (lifecycle). They serve different purposes; future consolidation possible.
- Baseline degradation is heuristic (20% threshold); may need tuning.

### Integration Points

- `model_preflight.py`: Validates rollback targets before activation
- `app.core.engines.metrics`: Feeds baseline updates and degradation checks
- `ab_testing.py`: Experiments with tags `engine:{engine_id}` for routing
