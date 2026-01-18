# VoiceStudio — OpenMemory

This file is a **living index** of VoiceStudio’s architecture, contracts, and current recovery gate status.

## Overview

- **Primary goal**: upgrade voice cloning quality + functionality without architectural drift.
- **Architecture**:
  - **Frontend**: WinUI 3 (.NET) app under `src/` (MVVM).
  - **Backend API**: Python FastAPI service under `backend/`.
  - **Engine layer**: Python engine implementations and runtime management under `app/`.
  - **Shared contracts**: JSON/schema artifacts under `shared/` (interop boundary).
- **Packaging lane**: unpackaged apphost EXE + installer only (`WindowsPackageType=None`; MSIX archived/removed).
- **WinAppSDK versioning**: `Directory.Build.props` centralizes `MicrosoftWindowsAppSDKVersion` (override via `WinAppSdkVersionOverride`); WinUI/CommunityToolkit/NAudio pinned in the same file.
- **Model root defaults**: `backend/api/main.py` sets `VOICESTUDIO_MODELS_PATH=E:\VoiceStudio\models` with HF/TTS/whisper/piper subfolders expected under that root.
- **Native tools**: ffmpeg can be overridden via `VOICESTUDIO_FFMPEG_PATH` (fallback PATH + common locations).
- **Publish status**: Gate C script `scripts/gatec-publish-launch.ps1` produces binlogs under `.buildlogs/`. Latest proof run (2026-01-13) is **green**: Release publish + UI smoke exits 0 with 0 binding failures (see `.buildlogs/gatec-latest.txt`).
- **Installer lane**: `installer/build-installer.ps1` publishes the frontend via Gate C (`scripts/gatec-publish-launch.ps1 -NoLaunch`) and Inno Setup packages from the Gate C publish directory (`installer/VoiceStudio.iss` via `MyAppSourceDir`).
- **Crash artifacts (Gate C)**:
  - `%LOCALAPPDATA%\VoiceStudio\crashes\latest.log` (managed unhandled exception pointer)
  - `%LOCALAPPDATA%\VoiceStudio\crashes\boot_latest.json` + `latest_startup_exception.log` (startup stage + pre-App exception pointer)
  - Native dumps (when enabled): `scripts/enable-wer-localdumps.ps1` → `%LOCALAPPDATA%\VoiceStudio\dumps\*.dmp`

## Gate status (A–H)

- **Gate A**: COMPLETE
- **Gate B**: COMPLETE (RuleGuard enforced)
- **Gate C**: COMPLETE (VS-0012 UI smoke proof captured)
- **Gate D**: See `Recovery Plan/QUALITY_LEDGER.md`
- **Gate E**: See `Recovery Plan/QUALITY_LEDGER.md`
- **Gate F/G**: See `Recovery Plan/QUALITY_LEDGER.md`
- **Gate H**: COMPLETE (VS-0003 installer lifecycle proof captured)

## Key components and contracts

- **Engine interface contract (Gate E)**: `VoiceStudio.Core.Engines` interfaces (`IEngine`, `ITextToSpeechEngine`, `ITranscriptionEngine`) + `EngineCapabilities`.
- **Frontend engine orchestration (Gate E)**: `src/VoiceStudio.App/Services/EngineManager.cs` with adapters in `src/VoiceStudio.App/Services/Engines/`.
- **Backend engine discovery/lifecycle**: `backend/api/routes/engines.py` (`/api/engines/*`).
- **Voice cloning quality metrics**: engine quality metrics pipeline uses ML prediction enablement for major voice cloning engines (tracked in VS-0009).

## Governance source of truth

- **Ledger**: `Recovery Plan/QUALITY_LEDGER.md` (canonical)
- **Change handoffs**: `docs/governance/overseer/handoffs/` (proof runs + file lists)
- **Role task lists**: `docs/governance/overseer/role_tasks/INDEX.md` (what each role does next)
- **Progression log (living; high-level + blockers + compatibility)**: `docs/governance/overseer/PROJECT_PROGRESSION_LOG.md` (snapshot: `docs/governance/overseer/PROJECT_PROGRESSION_LOG_2026-01-11.md`)
- **Production build plan (execution playbook)**: `VoiceStudio_Production_Build_Plan.md`
- **Role prompts + direction (7 roles)**: `docs/governance/overseer/ALL_ROLE_PROMPTS.md`
- **Proof archive helper**: `scripts/archive-proof-artifacts.ps1` copies proof runs into `.buildlogs\\proof_runs`.

## User Defined Namespaces

- Leave blank - user populates

## Backend voice cloning routes

- **Voice routes**: `backend/api/routes/voice.py`
  - Uses `_audio_storage` (`audio_id -> file_path`) to serve `/api/voice/audio/{audio_id}`.
  - `_audio_storage` is backed by a disk-backed registry (`backend/services/AudioArtifactRegistry.py`) so audio IDs survive backend restarts.
  - `/api/voice/clone` accepts optional `project_id` and will persist outputs to the project audio folder when provided.
  - Normalizes engine IDs; supports alias `xtts` -> `xtts_v2`.
  - Many engines write to `output_path` and return `None` (or `(None, metrics)`); treat a written file as
    success and still return a playable `audio_url`.
  - `/api/voice/clone` registers the generated file under a new `audio_id` and returns
    `/api/voice/audio/{audio_id}`.
  - XTTS quality metrics now include `voice_profile_match` (from reference audio) in
    `quality_metrics` alongside artifacts/clicks/distortion when available.
- **Wizard routes**: `backend/api/routes/voice_cloning_wizard.py`
  - Prefix: `/api/voice/clone/wizard` (used by
    `src/VoiceStudio.App/ViewModels/VoiceCloningWizardViewModel.cs`).
  - Wizard job state is persisted via `backend/services/JobStateStore.py` (no longer in-memory only).
  - Wizard UI displays parsed quality metrics in Step 4 (MOS/Similarity/Naturalness/SNR/Artifacts/Clicks/Distortion).
  - Wizard + quick clone ViewModels normalize profile names and use local copies of nullable inputs before API calls.
  - Real-time converter and quality optimization ViewModels now use local session/profile IDs for backend calls.
  - Wizard Step 4 binds quality metrics via a nested DataContext to avoid XamlCompiler failures on dotted bindings.

## Key enforcement hooks

- **RuleGuard**: `tools/verify_no_stubs_placeholders.py`
- **XAML toolchain**: wrapper/targets under `tools/` + MSBuild targets.

## Engine notes

- **So-VITS-SVC**: `app/core/engines/sovits_svc_engine.py` now supports external inference via
  `SOVITS_SVC_INFER_COMMAND` (or engine config `infer_command`) with optional `infer_workdir`
  and `allow_passthrough`.
- **Voice engines**: fallback `EngineProtocol` implementations in voice TTS engines now return
  explicit defaults instead of empty bodies to avoid incomplete method stubs.
- **Engine batch metrics**: engine batch helpers now log when performance metrics are unavailable
  instead of silently no-oping, and fallback `EngineProtocol` implementations in image engines
  return explicit defaults to avoid empty method stubs.
- **Voice cloning wizard**: wizard now supports quality mode selection and displays candidate metrics in Step 4.  
