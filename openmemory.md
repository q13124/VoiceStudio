# VoiceStudio — OpenMemory

This file is a **living index** of VoiceStudio’s architecture, contracts, and current recovery gate status.

## Overview

- **Primary goal**: upgrade voice cloning quality + functionality without architectural drift.
- **Architecture**:
  - **Frontend**: WinUI 3 (.NET) app under `src/` (MVVM).
  - **Backend API**: Python FastAPI service under `backend/`.
  - **Engine layer**: Python engine implementations and runtime management under `app/`.
  - **Shared contracts**: JSON/schema artifacts under `shared/` (interop boundary).
- **Packaging default**: unpackaged apphost EXE (`WindowsPackageType=None`, MSIX optional).
- **WinAppSDK versioning**: `Directory.Build.props` centralizes `MicrosoftWindowsAppSDKVersion` (override via `WinAppSdkVersionOverride`); WinUI/CommunityToolkit/NAudio pinned in the same file.
- **Model root defaults**: `backend/api/main.py` sets `VOICESTUDIO_MODELS_PATH=E:\VoiceStudio\models` with HF/TTS/whisper/piper subfolders expected under that root.
- **Native tools**: ffmpeg can be overridden via `VOICESTUDIO_FFMPEG_PATH` (fallback PATH + common locations).
- **Publish status**: Gate C script `scripts/gatec-publish-launch.ps1` produces binlogs under `.buildlogs/`. Latest proof run (2026-01-08) is **green**: Release publish + 10s smoke launch passes (see `.buildlogs/gatec-latest.txt`).
- **Crash artifacts (Gate C)**:
  - `%LOCALAPPDATA%\VoiceStudio\crashes\latest.log` (managed unhandled exception pointer)
  - `%LOCALAPPDATA%\VoiceStudio\crashes\boot_latest.json` + `latest_startup_exception.log` (startup stage + pre-App exception pointer)
  - Native dumps (when enabled): `scripts/enable-wer-localdumps.ps1` → `%LOCALAPPDATA%\VoiceStudio\dumps\*.dmp`

## Gate status (A–H)

- **Gate A**: COMPLETE
- **Gate B**: COMPLETE (RuleGuard enforced)
- **Gate C**: UNBLOCKED for publish+launch proof (`VS-0012` handoff updated; Release Engineer still needs UI smoke verification)
- **Gate D**: See `Recovery Plan/QUALITY_LEDGER.md`
- **Gate E**: See `Recovery Plan/QUALITY_LEDGER.md`
- **Gate F/G**: blocked by Gate C
- **Gate H**: See `Recovery Plan/QUALITY_LEDGER.md`

## Key components and contracts

- **Engine interface contract (Gate E)**: `VoiceStudio.Core.Engines` interfaces (`IEngine`, `ITextToSpeechEngine`, `ITranscriptionEngine`) + `EngineCapabilities`.
- **Frontend engine orchestration (Gate E)**: `src/VoiceStudio.App/Services/EngineManager.cs` with adapters in `src/VoiceStudio.App/Services/Engines/`.
- **Backend engine discovery/lifecycle**: `backend/api/routes/engines.py` (`/api/engines/*`).
- **Voice cloning quality metrics**: engine quality metrics pipeline uses ML prediction enablement for major voice cloning engines (tracked in VS-0009).

## Governance source of truth

- **Ledger**: `Recovery Plan/QUALITY_LEDGER.md` (canonical)
- **Change handoffs**: `docs/governance/overseer/handoffs/` (proof runs + file lists)
- **Role task lists**: `docs/governance/overseer/role_tasks/INDEX.md` (what each role does next)

## User Defined Namespaces

- [Leave blank - user populates]

# VoiceStudio OpenMemory Guide

## User Defined Namespaces

- [Leave blank - user populates]

## Overview

VoiceStudio is a WinUI 3 desktop application (C#/.NET) with a Python backend and pluggable engine layer.
The project is operated under a gated recovery model (Gates A–H) with governance handoffs and a single
quality ledger.

## Architecture (high level)

- **Frontend**: `src/VoiceStudio.App` (WinUI 3, MVVM).
- **Backend**: `backend/` (Python services) + `app/` (core engine/runtime Python).
- **Contracts**: JSON schemas in `shared/`.
- **Governance**: `docs/governance/overseer/` + `docs/governance/overseer/handoffs/`.

## Backend voice cloning routes

- **Voice routes**: `backend/api/routes/voice.py`
  - Uses `_audio_storage` (`audio_id -> file_path`) to serve `/api/voice/audio/{audio_id}`.
  - `_audio_storage` is backed by a disk-backed registry (`backend/services/AudioArtifactRegistry.py`) so audio IDs survive backend restarts.
  - Normalizes engine IDs; supports alias `xtts` -> `xtts_v2`.
  - Many engines write to `output_path` and return `None` (or `(None, metrics)`); treat a written file as
    success and still return a playable `audio_url`.
  - `/api/voice/clone` registers the generated file under a new `audio_id` and returns
    `/api/voice/audio/{audio_id}`.
- **Wizard routes**: `backend/api/routes/voice_cloning_wizard.py`
  - Prefix: `/api/voice/clone/wizard` (used by
    `src/VoiceStudio.App/ViewModels/VoiceCloningWizardViewModel.cs`).
  - Wizard job state is persisted via `backend/services/JobStateStore.py` (no longer in-memory only).

## Key enforcement hooks

- **RuleGuard**: `tools/verify_no_stubs_placeholders.py`
- **XAML toolchain**: wrapper/targets under `tools/` + MSBuild targets.
