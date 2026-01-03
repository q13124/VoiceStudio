# VoiceStudio — OpenMemory

This file is a **living index** of VoiceStudio’s architecture, contracts, and current recovery gate status.

## Overview

- **Primary goal**: upgrade voice cloning quality + functionality without architectural drift.
- **Architecture**:
  - **Frontend**: WinUI 3 (.NET) app under `src/` (MVVM).
  - **Backend API**: Python FastAPI service under `backend/`.
  - **Engine layer**: Python engine implementations and runtime management under `app/`.
  - **Shared contracts**: JSON/schema artifacts under `shared/` (interop boundary).

## Gate status (A–H)

- **Gate A**: COMPLETE
- **Gate B**: COMPLETE (RuleGuard enforced)
- **Gate C**: BLOCKED by **VS-0012** (WinUI runtime activation / launch environment) and **VS-0020** (Release build configuration)
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
  - Normalizes engine IDs; supports alias `xtts` -> `xtts_v2`.
  - Many engines write to `output_path` and return `None` (or `(None, metrics)`); treat a written file as
    success and still return a playable `audio_url`.
  - `/api/voice/clone` registers the generated file under a new `audio_id` and returns
    `/api/voice/audio/{audio_id}`.
- **Wizard routes**: `backend/api/routes/voice_cloning_wizard.py`
  - Prefix: `/api/voice/clone/wizard` (used by
    `src/VoiceStudio.App/ViewModels/VoiceCloningWizardViewModel.cs`).

## Serialization interoperability

- Frontend `BackendClient` now uses `SnakeCaseJsonNamingPolicy` so C# requests/responses align with FastAPI's
  snake_case fields (`profile_id`, `audio_id`, `word_timestamps`, etc.).
- Backend `/api/engines` route mirrors `/api/engines/list` to support host discovery logic expecting the root path.

## Key enforcement hooks

- **RuleGuard**: `tools/verify_no_stubs_placeholders.py`
- **XAML toolchain**: wrapper/targets under `tools/` + MSBuild targets.
