# VoiceStudio — Project Breakdown, Execution Plan, and Work Summary

**Author role:** System Architect  
**Repo root:** `E:\VoiceStudio`  
**Last updated:** 2026-01-06

This document provides:

- A **component-by-component breakdown** of the VoiceStudio codebase (what exists, where it lives, and how it fits together)
- A **forward execution plan** (gated recovery + voice cloning upgrade track)
- A **detailed summary of work completed** with pointers to canonical evidence

## Canonical sources (use these to verify truth)

- **Single source of truth for status:** `Recovery Plan/QUALITY_LEDGER.md`
- **Evidence packets (proof runs + file lists):** `docs/governance/overseer/handoffs/`
- **Current working architecture notes:** `openmemory.md`
- **Role task lists (what each role does next):** `docs/governance/overseer/role_tasks/INDEX.md`
- **Architecture references:**
  - `C:\Users\Tyler\Downloads\VoiceStudio Project Architecture and Dependency Guide.pdf`
  - `C:\Users\Tyler\Downloads\VoiceStudio – Architecture Blueprint.pdf`
- **Build/publish crash & Gate C scripts:** `docs/governance/overseer/GATE_C_*`
- **Release build unblock work:** `docs/governance/overseer/handoffs/VS-0020.md`
- **Model root defaults:** backend sets `VOICESTUDIO_MODELS_PATH=E:\VoiceStudio\models` (HF/TTS/whisper/piper subfolders expected)

If any statement in this document conflicts with the ledger, the ledger wins.

---

## 1) Product scope (what this system is)

VoiceStudio is a **local-first** Windows desktop application for:

- **Voice synthesis (TTS)** and **voice cloning**
- **Audio production workflows** (timeline/clip-based UI, playback, processing)
- **Quality evaluation** (metrics + scoring) and quality-driven engine selection
- A pluggable **engine system** (TTS, transcription, voice conversion, and other media engines)

The architecture is split into:

- **WinUI 3 frontend** (`src/VoiceStudio.App`) using MVVM
- **FastAPI backend** (`backend/`) exposing REST/WebSocket APIs
- **Python engine/runtime layer** (`app/core/`) that implements engines, quality metrics, and runtime/lifecycle management
- **Manifests** (`engines/`) for dynamic engine discovery/config
- **Shared contracts** (`shared/`) for interop boundaries (JSON schemas)

---

## 2) Architectural principles and constraints (non-negotiables)

### 2.1 Governance / gates

The repo is operated under a gated recovery model (Gates A–H). The current gate status is tracked in the ledger:

- Gate A: deterministic environment
- Gate B: clean compile + RuleGuard enforcement
- Gate C: app boot stability (standard launch artifact + proof run)
- Gate D: storage baseline + job runtime baseline
- Gate E: engine integration baseline
- Gate F: UI stability
- Gate G: testing baseline
- Gate H: packaging + upgrades

### 2.2 Contract boundaries

- The frontend should treat the backend as a **network boundary** (even on localhost).
- JSON request/response shapes must remain stable; changes should be versioned or made backward compatible.
- Engine integration is governed by **stable interface contracts** (C# engine interfaces + backend endpoints).

### 2.3 “Local-first” runtime assumptions

- Processing happens locally; packaging must ensure the WinUI runtime and dependencies are present in the chosen launch mode (packaged vs unpackaged).

---

## 3) High-level system diagram

```
[WinUI 3 App (C#/.NET 8)]
      |
      | JSON over HTTP/WebSocket
      v
[FastAPI Backend (Python)]
      |
      | internal calls
      v
[Engine Layer / Runtime (Python)]
      |
      +--> Engine implementations (XTTS/Chatterbox/Tortoise/RVC/...)
      +--> Quality metrics + scoring + optimization
      +--> Engine lifecycle management (start/stop/status/voices)
```

---

## 4) Component breakdown (by repo area)

This section is intentionally “where to look + what it owns” so engineers can navigate quickly without guessing.

### 4.1 Governance & recovery controls

**Location**

- `Recovery Plan/QUALITY_LEDGER.md` (canonical status)
- `docs/governance/overseer/` (gate scripts, policies, status snapshots)
- `docs/governance/overseer/handoffs/` (evidence packets per ledger item)

**Responsibilities**

- Define what “done” means per gate (proof runs)
- Track blockers (e.g., Gate C boot stability)
- Record role/ownership changes (e.g., VS-0019)

### 4.2 Build & tooling system (MSBuild + RuleGuard + XAML)

**Core files**

- `Directory.Build.props`
  - Centralizes `MicrosoftWindowsAppSDKVersion`
  - Allows ad-hoc override via `WinAppSdkVersionOverride`
- `Directory.Build.targets`
  - Runs RuleGuard before build: target `RunRuleGuard`
  - Manages XAML source copying into `obj` to prevent MSB3030 failures
  - Contains a `MarkupCompilePass2` workaround target for the WinUI app project
- `tools/verify_no_stubs_placeholders.py`
  - RuleGuard: blocks TODO/FIXME/HACK/XXX, NotImplemented\*, and Python `pass`-only lines
- `tools/xaml-compiler-wrapper.cmd`
  - Wraps WinUI XAML compiler selection/logging
- `.buildlogs/` (build outputs + logs)

**Packaging defaults (current)**

- `src/VoiceStudio.App/VoiceStudio.App.csproj` is configured for **unpackaged apphost EXE by default**:
  - `WindowsPackageType=None`
  - MSIX lane removed/archived (do not re-enable MSIX tooling)

**Why this matters**

- Gate C depends on a deterministic “standard launch artifact” (the thing we launch for proof).
- VS-0020 is explicitly about getting a reliable **Release** artifact to unblock packaging and launch verification.

### 4.3 Frontend: WinUI 3 desktop application

**Location**

- `src/VoiceStudio.App/`

**Key architectural pattern**

- MVVM:
  - Views in XAML (`Views/`)
  - ViewModels in C# (`ViewModels/`)
  - Services for cross-cutting concerns (`Services/`)

**Startup + service initialization**

- `App.xaml.cs` → `ServiceProvider.Initialize()`
- Services are described in `docs/developer/SERVICE_ARCHITECTURE.md`

**Backend communication**

- `src/VoiceStudio.App/Services/BackendClient.cs`
  - Uses `SnakeCaseJsonNamingPolicy` so frontend JSON aligns with backend snake_case fields
  - Provides typed request helpers (`SendRequestAsync<,>`, `SynthesizeVoiceAsync`, etc.)

**Voice cloning UI**

- `src/VoiceStudio.App/ViewModels/VoiceCloningWizardViewModel.cs`
  - Implements step-based wizard:
    - Upload → Validate → Configure → Process → Review/Finalize
  - Talks to backend wizard endpoints under `/api/voice/clone/wizard/*`

### 4.4 Frontend: shared contracts / core library

**Location**

- `src/VoiceStudio.Core/`

**Purpose**

- Shared models/contracts used by the WinUI application and service layer.
- The engine interface contract used by the app lives under `VoiceStudio.Core.Engines` (see Gate E).

### 4.5 Backend: FastAPI HTTP API + WebSockets

**Location**

- `backend/api/`

**Routing**

- `backend/api/routes/voice.py`
  - Voice synthesis and voice cloning endpoints
  - Manages `_audio_storage` (`audio_id -> file_path`) and serves `/api/voice/audio/{audio_id}`
  - Normalizes engine IDs (example: `xtts` aliasing to `xtts_v2`)
- `backend/api/routes/voice_cloning_wizard.py`
  - Wizard endpoints under `/api/voice/clone/wizard`
  - Performs audio validation using `app.core.audio.audio_utils` and uses `_audio_storage` from voice routes
- `backend/api/routes/engines.py`
  - Engine list/recommendation endpoints
  - Engine lifecycle endpoints used by the app adapter:
    - `POST /api/engines/{engine_id}/start`
    - `POST /api/engines/{engine_id}/stop`
    - `GET  /api/engines/{engine_id}/status`
    - `GET  /api/engines/{engine_id}/voices`

**Cross-cutting backend infrastructure**

- `backend/api/middleware/` (validation, auth, etc.)
- `backend/api/optimization.py`, `backend/api/response_cache.py` (caching and perf)
- `backend/api/ws/` (realtime WebSocket services)

### 4.6 Engine layer + runtime (Python)

**Location**

- `app/core/`

**Engines**

- `app/core/engines/`
  - Engine protocol: `protocols.py` (`EngineProtocol`)
  - Engine router/registry: `router.py`
  - Engine implementations (examples):
    - `xtts_engine.py`
    - `chatterbox_engine.py`
    - `tortoise_engine.py`
    - `rvc_engine.py`
    - `openvoice_engine.py`
    - `gpt_sovits_engine.py`
    - `mockingbird_engine.py`
  - `__init__.py` now uses **lazy loading** to avoid importing heavy optional dependencies (e.g., Deforum’s Diffusers stack) when importing unrelated engines.

**Quality metrics**

- `app/core/engines/quality_metrics.py`
  - Central metric computation (MOS, similarity, naturalness, SNR, artifact detection)
  - Gate E requires voice cloning engines to enable ML quality prediction in this pipeline (VS-0009)

**Runtime/lifecycle management**

- `app/core/runtime/engine_lifecycle.py`
  - State machine for engine instances
  - Lease handling (`acquire_engine` / `release_engine`)
  - Health checks and draining behavior

**Audio utilities**

- `app/core/audio/audio_utils.py`, `enhanced_preprocessing.py`, etc.
  - Loading/analysis utilities used by voice cloning validation and quality enhancement.

### 4.7 Engine manifests (dynamic discovery)

**Location**

- `engines/` (JSON manifests per engine)

**Purpose**

- Declare engine metadata, capabilities, dependencies, entrypoint, and configuration schema.
- Used by router/discovery to enumerate available engines.

### 4.8 Shared contracts (interop boundary)

**Location**

- `shared/contracts/`

**Purpose**

- JSON schemas for frontend-backend contracts and MCP-style operation routing.
- See `docs/design/ARCHITECTURE_DATA_FLOW.md` for contract patterns and examples.

### 4.9 Installer + release packaging

**Location**

- `installer/` (installer scripts/specs)
- `docs/release/` (runtime prerequisites, packaging notes)

**Purpose**

- Make the chosen Gate C artifact reproducible on clean systems.
- Enable Gate H: installer verification + upgrade/rollback proofs (VS-0003).

### 4.10 Test suites

**Python tests**

- `tests/` (unit/integration/performance/quality/ui)

**C# tests**

- `src/VoiceStudio.App.Tests/` (MSTest-based tests and UI smoke test infrastructure)

### 4.11 Component inventories (file-level “what exists”)

This section is a navigational inventory. It is intentionally concrete (file names) so work can be assigned without guesswork.

#### 4.11.1 Backend route modules (`backend/api/routes/`)

Below is the current module inventory (one module per file), grouped by domain. Each file contains FastAPI route decorators defining endpoint paths.

**Core / platform**

- `__init__.py`
- `models.py`
- `docs.py`
- `health.py`
- `gpu_status.py`
- `settings.py`
- `advanced_settings.py`
- `shortcuts.py`
- `help.py`
- `pdf.py`
- `adr.py`
- `huggingface_fix.py`
- `repair.py`
- `monitoring.py`

**Auth / security**

- `auth.py`
- `api_key_manager.py`
- `safety.py`

**Voice / speech / cloning**

- `voice.py`
- `voice_cloning_wizard.py`
- `voice_speech.py`
- `voice_morph.py`
- `voice_browser.py`
- `dubbing.py`
- `rvc.py`
- `prosody.py`
- `emotion.py`
- `emotion_style.py`
- `articulation.py`
- `formant.py`
- `ssml.py`
- `text_speech_editor.py`
- `text_highlighting.py`
- `lexicon.py`
- `multilingual.py`

**Engine management**

- `engines.py`
- `engine.py`
- `engine_audit.py`
- `model_inspect.py`
- `presets.py`

**Projects / profiles / content organization**

- `projects.py`
- `profiles.py`
- `library.py`
- `tags.py`
- `markers.py`
- `templates.py`
- `scenes.py`
- `tracks.py`
- `search.py`

**Audio processing / analysis**

- `audio.py`
- `audio_analysis.py`
- `audio_audit.py`
- `effects.py`
- `mixer.py`
- `mix_scene.py`
- `mix_assistant.py`
- `ensemble.py`
- `spectrogram.py`
- `advanced_spectrogram.py`
- `waveform.py`
- `sonography.py`
- `spatial_audio.py`
- `spectral.py`
- `granular.py`
- `nr.py`
- `recording.py`
- `realtime_converter.py`
- `realtime_visualizer.py`

**Automation / workflows / jobs**

- `automation.py`
- `workflows.py`
- `macros.py`
- `batch.py`
- `jobs.py`
- `todo_panel.py`
- `plugins.py`
- `backup.py`

**Quality / evaluation / ML optimization**

- `quality.py`
- `quality_pipelines.py`
- `eval_abx.py`
- `analytics.py`
- `reward.py`
- `ml_optimization.py`

**Training + datasets**

- `training.py`
- `training_audit.py`
- `dataset.py`
- `dataset_editor.py`

**Media generation / enhancement (non-audio)**

- `image_gen.py`
- `image_search.py`
- `img_sampler.py`
- `upscaling.py`
- `video_gen.py`
- `video_edit.py`
- `deepfake_creator.py`

**Assistants / dashboards**

- `assistant.py`
- `assistant_run.py`
- `ai_production_assistant.py`
- `embedding_explorer.py`
- `mcp_dashboard.py`
- `ultimate_dashboard.py`
- `multi_voice_generator.py`

> Note: this inventory lists modules; endpoint shapes are defined inside each module via FastAPI route decorators.

#### 4.11.2 Engine implementations (`app/core/engines/`)

**Voice synthesis / voice cloning / voice conversion (audio)**

- `xtts_engine.py`
- `chatterbox_engine.py`
- `tortoise_engine.py`
- `openvoice_engine.py`
- `gpt_sovits_engine.py`
- `mockingbird_engine.py`
- `rvc_engine.py`
- `rhvoice_engine.py`
- `piper_engine.py`
- `espeak_ng_engine.py`
- `marytts_engine.py`
- `festival_flite_engine.py`
- `openai_tts_engine.py`
- `bark_engine.py`
- `f5_tts_engine.py`
- `parakeet_engine.py`
- `higgs_audio_engine.py`
- `speaker_encoder_engine.py`
- `streaming_engine.py`

**Transcription (ASR)**

- `whisper_engine.py`
- `whisper_cpp_engine.py`
- `whisper_ui_engine.py`
- `vosk_engine.py`

**Media engines (image/video and related tooling)**

- `deforum_engine.py`
- `automatic1111_engine.py`
- `comfyui_engine.py`
- `invokeai_engine.py`
- `sd_cpu_engine.py`
- `fastsd_cpu_engine.py`
- `sdxl_engine.py`
- `sdxl_comfy_engine.py`
- `sdnext_engine.py`
- `fooocus_engine.py`
- `openjourney_engine.py`
- `realistic_vision_engine.py`
- `realesrgan_engine.py`
- `svd_engine.py`
- `video_creator_engine.py`
- `moviepy_engine.py`
- `ffmpeg_ai_engine.py`
- `fomm_engine.py`
- `sadtalker_engine.py`
- `deepfacelab_engine.py`

**Core engine framework + quality system**

- `protocols.py` (EngineProtocol)
- `router.py` / `router_optimized.py` (discovery + dispatch)
- `manifest_loader.py` (manifest ingestion)
- `quality_metrics.py` (metrics + ML prediction hook)
- `quality_optimizer.py` / `quality_presets.py` / `quality_comparison.py`

#### 4.11.3 Shared contract schemas (`shared/contracts/`)

- `mcp_operation.schema.json`
- `mcp_operation_response.schema.json`
- `analyze_voice_request.schema.json`
- `layout_state.schema.json`

#### 4.11.4 Frontend panels inventory (`src/VoiceStudio.App/Views/Panels/`)

The WinUI panel system is large; each panel is generally represented by:

- `PanelNameView.xaml`
- `PanelNameView.xaml.cs`
- `PanelNameViewModel.cs` (sometimes in `src/VoiceStudio.App/ViewModels/` and sometimes adjacent to the view files)

Voice-cloning critical panels to understand first:

- `VoiceSynthesisView.xaml`
- `VoiceQuickCloneView.xaml`
- `VoiceCloningWizardView.xaml`
- `TrainingView.xaml`
- `QualityControlView.xaml`
- `EngineRecommendationView.xaml`

---

## 5) Key end-to-end flows (what calls what)

### 5.1 Engine discovery (frontend host side)

- Frontend `EngineManager` queries backend engine list (see `backend/api/routes/engines.py`).
- Frontend creates adapters (`BackendEngineAdapter`) that translate UI calls to `/api/engines/*`.

### 5.2 Voice synthesis (TTS)

1. UI collects synthesis request (text + engine + parameters)
2. Frontend calls `POST /api/voice/synthesize`
3. Backend dispatches to selected engine
4. Backend registers output audio in `_audio_storage` and returns `audio_id` + `audio_url`
5. UI plays audio from `/api/voice/audio/{audio_id}`

### 5.3 Voice cloning wizard (step-based)

- Backend endpoints: `backend/api/routes/voice_cloning_wizard.py`
- Frontend ViewModel: `src/VoiceStudio.App/ViewModels/VoiceCloningWizardViewModel.cs`

Core steps:

- Upload reference audio
- Validate audio (duration, sample rate, channels, SNR/clipping checks)
- Configure engine + quality mode + profile metadata
- Process cloning job
- Review metrics + finalize profile

### 5.4 Quality metrics (engine-side)

- Engines (e.g., Chatterbox, Tortoise) call:
  - `calculate_all_metrics(..., include_ml_prediction=True)`
- ML prediction enablement across major voice cloning engines is tracked as VS-0009 with regression tests in Python.

---

## 6) Current system status (gates + ledger)

### 6.1 Gate status snapshot

- **Gate A:** complete
- **Gate B:** complete (RuleGuard enforced; XAML build stabilized)
- **Gate C:** blocked by:
  - **VS-0012** (WinUI activation failure / class-not-registered in unpackaged launch path)
  - **VS-0020** (Release build configuration + publish/launch artifact reliability)
- **Gate D:** baseline complete per entries in ledger
- **Gate E:** baseline complete per entries in ledger
- **Gate F/G:** blocked until Gate C is closed
- **Gate H:** blocked until Release/packaging prerequisites are unblocked

### 6.2 Ledger index (authoritative)

See `Recovery Plan/QUALITY_LEDGER.md` for the full index and each entry’s repro/proof.

---

## 7) Detailed summary of work completed (what has been done and why it matters)

This section is a consolidated narrative built from the ledger and handoffs. For exact proof commands and file diffs, use the relevant handoff document.

### 7.1 Gate B — build stability + enforcement

- **VS-0001:** XAML compiler false-positive exit code handling
- **VS-0005:** restored XAML file inclusion/copy semantics to prevent missing XAML artifacts
- **VS-0008:** RuleGuard wired into MSBuild (`RunRuleGuard`) to enforce “no stubs/placeholders” policy
- **VS-0018:** removed a RuleGuard-blocking `pass` from backend engine stop endpoint and replaced it with explicit drain/lease-release behavior

### 7.2 Gate C — boot stability (partial)

Completed items that removed internal boot/test blockers:

- **VS-0010:** test runner configuration fix
- **VS-0011:** ServiceProvider recursion fix
- **VS-0013:** UI-thread test execution support

Remaining blockers:

- **VS-0012:** unpackaged WinUI activation failure (`0x80040154`) requires deterministic “Gate C artifact” and runtime prerequisites
- **VS-0020:** Release publish/launch reliability, including apphost creation and launch crashes (see VS-0020 handoff for latest evidence including publish binlog + CoreMessagingXP.dll crash)

### 7.3 Gate D — storage + runtime baseline

Ledger entries indicate storage/runtime foundations required for reliable projects and repeatable processing.
See: VS-0004, VS-0006, VS-0014, VS-0015.

### 7.4 Gate E — engine integration baseline (voice cloning oriented)

Key architectural outcomes:

- Standard engine contract established (interfaces + capability flags)
- Host-side orchestration added (EngineManager + adapter)
- Backend engine lifecycle endpoints exist (`/api/engines/{id}/*`)
- ML quality prediction is enabled across major voice cloning engines (VS-0009), backed by tests

See: VS-0002, VS-0007, VS-0009, VS-0016, VS-0017.

---

## 8) Forward execution plan (what to add next)

This plan is intentionally **gate-driven** so voice cloning upgrades are built on a stable launch + packaging baseline.

### 8.0 Immediate integrated actions (role-assigned)

- **Build & Tooling Engineer**
  - Default model root: `VOICESTUDIO_MODELS_PATH=E:\VoiceStudio\models` (HF/TTS/whisper/piper subfolders).
  - Publish/launch is green for unpackaged apphost; binlogs under `.buildlogs/` per VS-0020.
- **Release Engineer**
  - Use the unpackaged EXE artifact for Gate C proof; note model root expectation above.
- **UI Engineer**
  - Continue UI warning cleanup; no backend defaults changed UI contracts.
- **Engine Engineer**
  - XTTS default `coqui/XTTS-v2`; Piper `en_US-amy-medium`; STT default whisper_cpp (whisper-medium.en.gguf under models\whisper); So-VITS checkpoints under models\checkpoints\<project>.
- **Core Platform Engineer**
  - Model path fallback resolves to `E:\VoiceStudio\models` when engine-specific paths absent; add pre-flight model existence checks and clear errors if missing.
- **UI Test/Infra**

  - No change; keep UI smoke/VM setup work.

- **Build & Tooling Engineer**
  - Pin WinAppSDK/WinUI/CommunityToolkit/NAudio to one stable line (1.8.x) and purge experimental WinUI bits.
  - Add publish-time extraction/copy of WinAppSDK runtime (CoreMessagingXP/bootstrap DLLs) into unpackaged apphost publish output (align with VS-0020/Gate C).
  - Keep unpackaged EXE as the only supported lane; remove MSIX/dual-path ambiguity in docs/scripts.
- **Release Engineer**
  - Run Release publish with new runtime copy; launch apphost EXE and capture proof/dump if failure (VS-0012/VS-0020 linkage).
  - Own installer/upgrade proofs once Gate C launch is green (VS-0003).
- **UI Engineer**
  - Implement all converter stubs (NullToVisibility, BooleanToBrush, StringFormat, NumberFormat, StringToBrush, NullToBoolean, DictionaryValue).
  - Add missing ViewModel properties/commands used by XAML; clean high-signal warnings in touched panels (nullability/async-without-await/hidden members).
- **Engine Engineer**
  - Replace placeholder backend routes with real engines, starting with TTS (Coqui/XTTS or Tortoise + a lightweight Piper/eSpeak path) and Transcription (Whisper/WhisperX or whisper.cpp) returning real artifacts.
  - Bring one VC path (RVC or So-VITS-SVC) to working output; ensure model loading and audio return.
  - Implement quality metrics with real computation (PESQ/STOI/embedding similarity) instead of dummy values.
- **Core Platform Engineer**
  - Ensure ffmpeg/native assets are bundled and discoverable for backend engines; stabilize audio artifact storage and job tracking where placeholder data exists.
- **UI Test/Infra (Build & Tooling + UI)**
  - Stand up WinUI UI test framework (Appium/WinAppDriver/WinUI test framework) and add a smoke suite for launch/navigation.
  - Prepare clean VM profiles for installer/update testing; script environment prep.

### 8.1 Gate C closure plan (boot stability)

**Goal:** produce one deterministic “Gate C artifact” and prove it launches reliably.

Deliverables:

1. **Choose and codify the Gate C artifact**

   - **Unpackaged self-contained apphost EXE** (single supported lane; distribution via installer; MSIX not used)

2. **Make Release publish deterministic (VS-0020)**

   - Publish must produce an apphost EXE + required runtime components
   - Capture and retain binlog and publish log in `.buildlogs/` (per VS-0020 handoff)

3. **Resolve launch crash modes**

   - WinUI activation: COMException `0x80040154` (VS-0012)
   - Release publish launch crash: CoreMessagingXP.dll `0xC0000602` (see VS-0020 evidence)

4. **Run the Gate C proof checklist**
   - Use `docs/governance/overseer/GATE_C_UI_SMOKE_TEST.md` and related Gate C scripts
   - Record success evidence (process stays running, MainWindow visible)

### 8.2 Gate F (UI stability) and Gate G (testing baseline)

These gates are downstream of Gate C.

Once Gate C is closed:

- Run UI smoke checklist end-to-end
- Execute UI stability pass (binding errors, navigation, crash-free flows)
- Establish CI verification coverage for both Debug and Release builds

### 8.3 Gate H (packaging + upgrade/rollback)

Once Release artifact is stable:

- Build installer artifacts and run clean install/upgrade/rollback proofs (VS-0003)
- Ensure runtime prerequisites are deterministically satisfied for the chosen artifact type

### 8.4 Voice cloning upgrade track (quality + functionality)

This is the product’s primary trajectory. Execution should remain behind gates so quality improvements land on a stable base.

High-leverage additions (voice cloning focused):

1. **Strengthen quality-driven engine selection**

   - Ensure engine manifests expose quality features consistently
   - Integrate recommendation endpoints with engine capabilities metadata

2. **Expand/upgrade voice cloning engines**

   - Deepen RVC/OpenVoice/GPT-SoVITS/MockingBird integrations where incomplete
   - Ensure each engine:
     - Emits consistent quality metrics
     - Supports reference audio workflows robustly
     - Is isolated from heavy optional deps via lazy-load patterns (keep this property)

3. **Training workflows**

   - Improve local training pipelines (dataset management, job tracking, reproducible outputs)
   - Integrate training artifacts into profile management

4. **Quality regression coverage**
   - Add targeted regression tests for:
     - ML prediction enablement
     - Wizard validation rules (audio constraints)
     - Contract/serialization alignment (snake_case)
     - Engine lifecycle endpoints (start/stop/status)

Reference for extended backlog ideas:

- `docs/governance/NEW_COMPREHENSIVE_ROADMAP_2025-01-28.md` (broad backlog; treat as input, not status)
- `docs/developer/QUALITY_FEATURES_ARCHITECTURE.md` (quality comparison features and endpoints)

### 8.5 Planned additions by component (voice cloning upgrade centered)

This is the “what to add next” mapping by subsystem. It is derived from the ledger blockers + existing architecture documents; it is not a substitute for the ledger.

**Build & tooling**

- Make Release publish deterministic for the Gate C artifact (VS-0020):
  - apphost EXE consistently emitted
  - runtime prerequisites reliably present in the publish output (or a packaged path adopted)
  - binlog retained under `.buildlogs/` for reproducibility
- Add CI checks that cover both Debug and Release builds and publish output sanity (presence of apphost, required DLLs).

**Frontend (WinUI)**

- Harden the voice cloning workflow UX around failure modes already present in backend/engines:
  - clear reporting when an engine writes to `output_path` but returns `None`
  - surfaced quality metrics and reference-audio validation feedback
- Integrate engine capabilities metadata into UI so the UI doesn’t rely on name heuristics.

**Backend API**

- Convert wizard job tracking from in-memory (`_wizard_jobs`) to a persistent store (so wizard survives restarts and supports long jobs).
- Expand engine metadata endpoints so the frontend can discover:
  - capabilities (TTS / voice cloning / transcription)
  - voice list availability
  - quality feature flags (e.g., ML prediction support)

**Engine layer**

- Continue tightening “import isolation” so optional heavy engines do not break voice cloning usage paths (preserve the lazy-load strategy in `app/core/engines/__init__.py`).
- Bring voice cloning engines to consistent quality-metric behavior:
  - consistent keys/units returned across engines
  - consistent `include_ml_prediction` enablement where supported (VS-0009 pattern)

**Storage**

- Ensure audio artifact storage is deterministic and resilient:
  - stable `audio_id -> file_path` mapping behavior
  - consistent cleanup and project association of generated audio

**Testing**

- Add targeted regression tests for voice cloning invariants:
  - wizard validation invariants
  - ML prediction enablement invariants
  - engine lifecycle endpoint invariants

---

## 9) Architectural risks and watchpoints

- **Packaged vs unpackaged WinUI activation semantics**: some runtime failures only appear without package identity.
- **Release artifact drift**: Debug success does not prove Release publish correctness; Gate C should standardize the proof artifact.
- **Eager imports / optional dependencies**: preserve the lazy-load pattern in `app/core/engines/__init__.py` to avoid cascading dependency failures.
- **Contract drift**: keep snake_case interop stable (frontend naming policy + backend expectations).
- **RuleGuard scope**: keep build green by preventing `pass`/NotImplemented/TODO patterns from entering scanned code.

---

## Appendix A — High-signal proof commands

### RuleGuard

```powershell
python tools\verify_no_stubs_placeholders.py
```

### Voice cloning ML prediction regressions (Gate E)

```powershell
pytest -q tests/unit/core/engines/test_chatterbox_engine.py tests/unit/core/engines/test_tortoise_engine.py
```

### Release publish experiment (Gate C / VS-0020)

Use the property set captured in `docs/governance/overseer/handoffs/VS-0020.md` and keep binlogs under `.buildlogs/`.
