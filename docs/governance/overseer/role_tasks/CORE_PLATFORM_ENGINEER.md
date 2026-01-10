# Core Platform Engineer — Next task list

## Mission alignment

Keep the “local-first” foundations reliable: job runtime, persistence, artifact storage, and backend orchestration so engine/UI work is stable.

## Current state snapshot (relevant)

- Model root default: `E:\VoiceStudio\models` (env: `VOICESTUDIO_MODELS_PATH`)
- Engine configuration fallback resolves to `E:\VoiceStudio\models` when engine-specific paths are absent.

## What you do next (ordered)

### 1) Pre-flight infrastructure checks (storage + paths)

- [ ] Add/verify a backend preflight that validates:
  - model root exists or can be created
  - artifact output directories exist (audio/images/projects)
  - `EngineConfigService` resolves paths consistently under the chosen model root
- **Success**: backend startup or a dedicated endpoint provides an operator-readable readiness report.

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

## Proof run expectation

- Run a minimal voice job that:
  - executes via runtime/job path
  - emits progress/events
  - persists an artifact that is retrievable after restart

