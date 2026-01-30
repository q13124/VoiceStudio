# Core Platform Engineer — Next task list

## Mission alignment

Keep the “local-first” foundations reliable: job runtime, persistence, artifact storage, and backend orchestration so engine/UI work is stable.

## Current state snapshot (relevant)

- Model root default: `E:\VoiceStudio\models` (env: `VOICESTUDIO_MODELS_PATH`)
- Engine configuration fallback resolves to `E:\VoiceStudio\models` when engine-specific paths are absent.
- ✅ Gate C is **DONE** (publish + `--smoke-ui` PASS).
- ✅ Gate H is **DONE** (VS-0003 lifecycle proof).

## What you do next (ordered)

### 1) Engine readiness for quality + functions

- [x] Ensure backend startup warns when the XTTS stack is not installed (coqui-tts) or model assets are not on disk; surface via preflight.
  - Evidence: `backend/services/model_preflight.py` adds XTTS dependency status + asset presence, and `/api/health/preflight` includes `xtts_v2`.
- [x] Verify `/api/engines/list` reports `xtts_v2` available on a clean machine after running the pinned engine install.
  - Evidence: `proof_runs\\baseline_workflow_20260116-091722_prosody\\proof_data.json` (`config.available_engines` includes `xtts_v2`)
- **Success**: Engine Engineer can run the baseline workflow proof and get a non-null `audio_id`.

### 2) Artifact persistence (voice workflow stability)

- [ ] Ensure generated audio artifacts are:
  - written to deterministic paths
  - registered in a durable mapping (`audio_id -> file_path`)
  - associated with projects where applicable
- **Success**: restart does not orphan artifacts; UI can re-open projects and still play outputs.

### 3) Job runtime + events (long-running engine tasks)

- [ ] Move any in-memory-only job tracking (wizard/training/progress) toward persistence or resilient tracking.
- [ ] Ensure cancellation + progress events remain consistent across engine types.
- **Success**: long jobs survive transient failures and progress reporting is deterministic.

### 4) Native tool availability (ffmpeg and other binaries)

- [ ] Establish a single place to locate bundled binaries (ffmpeg, whisper.cpp if using CLI, etc.).
- [ ] Ensure path discovery is deterministic and does not depend on user PATH.
- **Success**: engines that require ffmpeg/native tools work on clean machines.

**Code Quality Note:** Roslynator is integrated and configured as warnings (non-blocking). Fix warnings incrementally as you work to maintain reliable, high-quality platform code.

## Proof run expectation

- Run a minimal voice job that:
  - executes via runtime/job path
  - emits progress/events
  - persists an artifact that is retrievable after restart
