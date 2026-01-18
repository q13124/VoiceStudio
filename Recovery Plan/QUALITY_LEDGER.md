# Quality Ledger — Single Source of Truth

Last updated: 2026-01-16  
Owner: [OVERSEER]

This file is the canonical ledger for **every** bug, crash, build failure, missing feature, UX regression, rule violation, or architecture drift item.

## Golden rules

- **If it isn’t in this ledger, it doesn’t exist.**
- **One change set ↔ one primary ledger ID** (additional IDs allowed if tightly coupled).
- **Every entry must include a Repro and a Proof Run.**
- **No “close” without evidence** (commands + results).
- **Functionality gates before features** (see Plan gates A–H).

---

## Status states (required)

Use exactly one:

- `OPEN` — acknowledged, not being worked
- `TRIAGE` — reproducing / narrowing scope
- `IN_PROGRESS` — fix underway
- `BLOCKED` — waiting on dependency/decision
- `FIXED_PENDING_PROOF` — code changed, proof not captured yet
- `DONE` — proof captured, regression test added/updated
- `WONT_FIX` — documented rationale (rare)

---

## Severity (required)

- `S0 Blocker` — stops build/boot, data loss, security risk
- `S1 Critical` — feature unusable / frequent crash / major corruption
- `S2 Major` — important feature broken, workaround exists
- `S3 Minor` — cosmetic or edge case
- `S4 Chore` — cleanup/refactor/improvement

---

## Categories (use 1–3 tags)

`BUILD`, `BOOT`, `UI`, `RUNTIME`, `ENGINE`, `AUDIO`, `STORAGE`, `PLUGINS`, `PACKAGING`, `PERF`, `SECURITY`, `DOCS`, `RULES`

---

## Open index (keep this near the top)

| ID      | State               | Sev         | Gate | Owner Role               | Category        | Title                                                                         |
| ------- | ------------------- | ----------- | ---- | ------------------------ | --------------- | ----------------------------------------------------------------------------- |
| VS-0001 | DONE                | S0 Blocker  | B    | Build & Tooling Engineer | BUILD           | XAML compiler false-positive exit code 1 fix                                  |
| VS-0002 | DONE                | S2 Major    | E    | Engine Engineer          | ENGINE          | Replace placeholder ML quality prediction with production implementation      |
| VS-0003 | DONE                | S1 Critical | H    | Release Engineer         | PACKAGING       | Installer package verification and upgrade/rollback path                      |
| VS-0004 | DONE                | S2 Major    | D    | Core Platform Engineer   | STORAGE         | Persist project metadata on disk for cross-restart reliability                |
| VS-0005 | DONE                | S0 Blocker  | B    | Build & Tooling Engineer | BUILD           | XAML Page items disabled causing missing XAML copy failures                   |
| VS-0006 | DONE                | S2 Major    | D    | Core Platform Engineer   | STORAGE,AUDIO   | Content-addressed audio cache to deduplicate waveforms and model artifacts    |
| VS-0007 | DONE                | S2 Major    | E    | Engine Engineer          | ENGINE          | ML quality prediction integration into engine metrics                         |
| VS-0008 | DONE                | S0 Blocker  | B    | Build & Tooling Engineer | BUILD,RULES     | RuleGuard not configured - Gate B requires RuleGuard pass                     |
| VS-0009 | DONE                | S2 Major    | E    | Engine Engineer          | ENGINE          | Enable ML quality prediction in Chatterbox and Tortoise voice cloning engines |
| VS-0010 | DONE                | S2 Major    | C    | Build & Tooling Engineer | TEST,BUILD      | Test runner configuration fix                                                 |
| VS-0011 | DONE                | S0 Blocker  | C    | Core Platform Engineer   | BOOT            | ServiceProvider recursion fix                                                 |
| VS-0012 | DONE                | S0 Blocker  | C    | Release Engineer         | BOOT,PACKAGING  | App crash on startup: 0xE0434352 / 0x80040154 (WinUI class not registered)    |
| VS-0013 | DONE                | S2 Major    | C    | UI Engineer              | TEST,UI         | Unit tests requiring UI thread failing                                        |
| VS-0014 | DONE                | S2 Major    | D    | Core Platform Engineer   | RUNTIME         | Job Runtime hardening                                                         |
| VS-0015 | DONE                | S2 Major    | D    | Core Platform Engineer   | STORAGE         | ProjectStore storage migration verification                                   |
| VS-0016 | DONE                | S2 Major    | E    | Core Platform Engineer   | ENGINE          | Standardize Engine Interface                                                  |
| VS-0017 | DONE                | S2 Major    | E    | Core Platform Engineer   | ENGINE          | Engine Manager Service Implementation                                         |
| VS-0018 | DONE                | S0 Blocker  | B    | System Architect         | BUILD,RULES     | RuleGuard violation in /api/engines stop endpoint (remove pass)               |
| VS-0019 | DONE                | S2 Major    | D    | Core Platform Engineer   | STORAGE,RUNTIME | Backend preflight readiness report (paths + model root)                       |
| VS-0020 | DONE                | S2 Major    | D    | Core Platform Engineer   | STORAGE,AUDIO   | Durable audio artifact registry (audio_id -> file_path)                       |
| VS-0021 | DONE                | S2 Major    | D    | Core Platform Engineer   | RUNTIME,STORAGE | Persist voice cloning wizard job state across restart                         |
| VS-0022 | DONE                | S3 Minor    | D    | Core Platform Engineer   | RUNTIME,PLUGINS | Deterministic ffmpeg discovery (env override + known locations)               |
| VS-0023 | DONE                | S0 Blocker  | C    | Build & Tooling Engineer | BUILD,RUNTIME   | Release build configuration hotfix (Gate C publish+launch)                    |
| VS-0024 | DONE                | S0 Blocker  | C    | UI Engineer              | BUILD,UI        | CS0126 compilation errors in LibraryView.xaml.cs                              |
| VS-0026 | DONE                | S2 Major    | C    | Core Platform Engineer   | BOOT,RUNTIME    | Early crash artifact capture (boot marker + WER LocalDumps helper)            |
| VS-0027 | DONE                | S2 Major    | E    | Engine Engineer          | ENGINE          | So-VITS-SVC engine + quality metrics fixes                                    |
| VS-0028 | DONE                | S2 Major    | F    | UI Engineer              | UI              | Replace UI control stubs with functional visualizations                       |
| VS-0029 | DONE                | S2 Major    | D    | Core Platform Engineer   | RUNTIME,STORAGE | Preflight jobs_root enhancement + durability proof documentation              |

---

### VS-0003 — Installer package verification and upgrade/rollback path (Gate H)

**State:** DONE  
**Severity:** S1 Critical  
**Gate:** H  
**Owner role:** Release Engineer  
**Reviewer role:** Overseer  
**Categories:** PACKAGING  
**Introduced:** 2026-01-13  
**Last verified:** 2026-01-13 (Windows 10.0.26200)

**Summary**

- Installer lifecycle proof PASS: install → launch → upgrade → rollback → uninstall.
- Built Inno Setup installers for v1.0.0 and v1.0.1 from the Gate C publish output.
- Gate C publish ensures required PRI files are present so installed app launch succeeds.

**Proof run**

- Commands executed:
  - `.\installer\build-installer.ps1 -InstallerType InnoSetup -Configuration Release -Version 1.0.0`
  - `.\installer\build-installer.ps1 -InstallerType InnoSetup -Configuration Release -Version 1.0.1`
  - `.\installer\test-installer-lifecycle.ps1 -InstallerV1Path "E:\VoiceStudio\installer\Output\VoiceStudio-Setup-v1.0.0.exe" -InstallerV2Path "E:\VoiceStudio\installer\Output\VoiceStudio-Setup-v1.0.1.exe" -LogDir "C:\logs"`
- Result: ExitCode `0` (PASS)

**Evidence**

- Installers:
  - `installer\Output\VoiceStudio-Setup-v1.0.0.exe`
  - `installer\Output\VoiceStudio-Setup-v1.0.1.exe`
- Lifecycle logs:
  - `C:\logs\voicestudio_lifecycle_20260113-150110.log`
  - `C:\logs\voicestudio_install_1.0.0_initial.log`
  - `C:\logs\voicestudio_install_1.0.1_upgrade.log`
  - `C:\logs\voicestudio_install_1.0.0_rollback.log`
  - `C:\logs\voicestudio_uninstall_1.0.1.log`
  - `C:\logs\voicestudio_uninstall_1.0.0.log`

**Links**

- Handoff: `docs/governance/overseer/handoffs/VS-0003.md`

---

### VS-0012 — App crash on startup: 0xE0434352 / 0x80040154 (WinUI class not registered)

**State:** DONE  
**Severity:** S0 Blocker  
**Gate:** C  
**Owner role:** Release Engineer  
**Reviewer role:** System Architect  
**Categories:** BOOT, PACKAGING  
**Introduced:** 2025-12-30  
**Last verified:** 2026-01-13 (Windows 10.0.26200)

**Summary**

- Gate C publish+launch + UI smoke proof **passes** on unpackaged apphost EXE (Release, `win-x64`, `WindowsPackageType=None`).
- Key fix: remove problematic system DLLs (`CoreMessagingXP.dll`, `dcompi.dll`, `dwmcorei.dll`, `marshal.dll`) from publish output via `ExcludeSystemDllsFromPublish` target in `VoiceStudio.App.csproj`.
- UI smoke proof: `scripts/gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64 -UiSmoke` → `exit_code 0`, `binding_failure_count 0`.

**Proof run (latest)**

- Command: `.\scripts\gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64 -UiSmoke`
- Artifacts:
  - Binlog: `.buildlogs\gatec-publish-*.binlog` (see `.buildlogs\gatec-latest.txt`)
  - PublishDir: `.buildlogs\x64\Release\gatec-publish\`
  - UI smoke summary: `%LOCALAPPDATA%\VoiceStudio\crashes\ui_smoke_summary.json`
  - UI smoke steps: `%LOCALAPPDATA%\VoiceStudio\crashes\ui_smoke_steps_latest.log`
  - Binding failures: `%LOCALAPPDATA%\VoiceStudio\crashes\binding_failures_latest.log`
- Result: `UiSmokeExitCode 0`, `binding_failure_count 0`

**Links**

- Handoff: `docs/governance/overseer/handoffs/VS-0012.md`
- Related entries:
  - VS-0023 (Release build configuration hotfix)
  - VS-0024 (CS0126 fix)
  - VS-0026 (crash artifact capture)

---

### VS-0019 — Backend preflight readiness report (paths + model root)

**State:** DONE  
**Severity:** S2 Major  
**Gate:** D  
**Owner role:** Core Platform Engineer  
**Reviewer role:** System Architect  
**Categories:** STORAGE, RUNTIME  
**Introduced:** 2026-01-07  
**Last verified:** 2026-01-07 (Windows 10.0.26200)

**Summary**

- Added `/api/health/preflight` to report operator-readable readiness for local-first operation:
  - projects root
  - cache root
  - model root (`VOICESTUDIO_MODELS_PATH`)
  - audio registry directory
  - ffmpeg presence (report-only)
- Hardened `/api/health/*` to be **safe-by-default** (avoid importing native ML stacks unless explicitly enabled).

**Change set**

- Files changed:
  - `backend/api/routes/health.py`
  - `tests/unit/backend/api/routes/test_health.py`

**Proof run**

- Commands executed:
  - `python -m pytest "e:\\VoiceStudio\\tests\\unit\\backend\\api\\routes\\test_health.py" -q`
- Result:
  - ✅ `16 passed`

---

### VS-0020 — Durable audio artifact registry (audio_id -> file_path)

**State:** DONE  
**Severity:** S2 Major  
**Gate:** D  
**Owner role:** Core Platform Engineer  
**Reviewer role:** System Architect  
**Categories:** STORAGE, AUDIO  
**Introduced:** 2026-01-07  
**Last verified:** 2026-01-07 (Windows 10.0.26200)

**Summary**

- Implemented a disk-backed audio artifact registry that persists `audio_id -> cached_file_path` under the cache root.
- Updated `backend/api/routes/voice.py` to register synthesized outputs via the content-addressed audio cache and persist the mapping.
- Updated `backend/api/routes/rvc.py` to register outputs via the shared voice registry (durable across restart).

**Change set**

- Files changed:
  - `backend/services/AudioArtifactRegistry.py`
  - `backend/api/routes/voice.py`
  - `backend/api/routes/rvc.py`
  - `tests/unit/backend/services/test_audio_artifact_registry.py`

**Proof run**

- Commands executed:
  - `python -m pytest "e:\\VoiceStudio\\tests\\unit\\backend\\services\\test_audio_artifact_registry.py" -q`
- Result:
  - ✅ `1 passed`

---

### VS-0021 — Persist voice cloning wizard job state across restart

**State:** DONE  
**Severity:** S2 Major  
**Gate:** D  
**Owner role:** Core Platform Engineer  
**Reviewer role:** System Architect  
**Categories:** RUNTIME, STORAGE  
**Introduced:** 2026-01-07  
**Last verified:** 2026-01-07 (Windows 10.0.26200)

**Summary**

- Replaced in-memory-only wizard job tracking with a disk-backed store:
  - `backend/services/JobStateStore.py` persists `job_id -> job_payload` under the cache root (`VOICESTUDIO_CACHE_DIR/jobs/...`).
  - `backend/api/routes/voice_cloning_wizard.py` now persists updates on every state/progress mutation.
- On backend restart, any wizard jobs left in `processing` are marked `failed` with a deterministic error message.

**Change set**

- Files changed:
  - `backend/services/JobStateStore.py`
  - `backend/api/routes/voice_cloning_wizard.py`
  - `tests/unit/backend/services/test_job_state_store.py`

**Proof run**

- Commands executed:
  - `python -m pytest "e:\\VoiceStudio\\tests\\unit\\backend\\services\\test_job_state_store.py" -q`
  - `python -m pytest "e:\\VoiceStudio\\tests\\unit\\backend\\api\\routes\\test_voice_cloning_wizard.py" -q`
- Result:
  - ✅ `1 passed`
  - ✅ `4 passed`

---

### VS-0022 — Deterministic ffmpeg discovery (env override + known locations)

**State:** DONE  
**Severity:** S3 Minor  
**Gate:** D  
**Owner role:** Core Platform Engineer  
**Reviewer role:** System Architect  
**Categories:** RUNTIME, PLUGINS  
**Introduced:** 2026-01-07  
**Last verified:** 2026-01-07 (Windows 10.0.26200)

**Summary**

- Centralized ffmpeg discovery in `app/core/utils/native_tools.py`:
  - Supports explicit override via `VOICESTUDIO_FFMPEG_PATH`.
  - Falls back to PATH and common Windows install locations.
- Updated call sites to use the centralized lookup:
  - `app/core/engines/ffmpeg_ai_engine.py`
  - `plugins/audio_tools/plugin.py`
- Updated backend preflight to surface `VOICESTUDIO_FFMPEG_PATH` if set.

**Change set**

- Files changed:
  - `app/core/utils/native_tools.py`
  - `app/core/engines/ffmpeg_ai_engine.py`
  - `plugins/audio_tools/plugin.py`
  - `backend/api/routes/health.py`
  - `tests/unit/core/utils/test_native_tools.py`

**Proof run**

- Commands executed:
  - `python -m pytest "e:\\VoiceStudio\\tests\\unit\\core\\utils\\test_native_tools.py" -q`
- Result:
  - ✅ `1 passed`

---

### VS-0024 — CS0126 compilation errors in LibraryView.xaml.cs

**State:** DONE  
**Severity:** S0 Blocker  
**Gate:** C  
**Owner role:** UI Engineer  
**Reviewer role:** System Architect  
**Categories:** BUILD, UI  
**Introduced:** 2025-01-28  
**Last verified:** 2025-12-30 (Windows 10.0.26200)

**Summary**

- CS0126 compilation errors in `src/VoiceStudio.App/Views/Panels/LibraryView.xaml.cs` prevented Release builds from completing.
- Three Task-returning methods (`AnalyzeAssetAsync`, `ApplyEffectsToAssetAsync`, `AddAssetToTimelineAsync`) had code paths that could complete without returning a value.
- The XAML compiler was failing during build, blocking Gate C publish-launch script execution.

**Reproduction**

1. Run: `dotnet build src/VoiceStudio.App/VoiceStudio.App.csproj -c Release`
2. Observe CS0126 errors for missing return statements in LibraryView.xaml.cs
3. Run Gate C script: `.\scripts\gatec-publish-launch.ps1 -NoLaunch`
4. Build fails with XAML compiler exit code 1

**Expected**

- Build succeeds with 0 errors
- Gate C publish-launch script completes successfully

**Actual**

- Build failed with CS0126 errors
- XAML compiler failed, preventing publish

**Fix plan**

- [x] Move early return checks outside try blocks in Task-returning methods
- [x] Ensure all code paths in `AnalyzeAssetAsync` return `Task.CompletedTask`
- [x] Ensure all code paths in `ApplyEffectsToAssetAsync` return `Task.CompletedTask`
- [x] Ensure all code paths in `AddAssetToTimelineAsync` return `Task.CompletedTask`
- [x] Verify build succeeds with no CS0126 errors
- [x] Verify Gate C script completes successfully

**Change set**

- Files changed:
  - `src/VoiceStudio.App/Views/Panels/LibraryView.xaml.cs`
    - `AnalyzeAssetAsync`: Moved early return check outside try block
    - `ApplyEffectsToAssetAsync`: Moved early return check outside try block
    - `AddAssetToTimelineAsync`: Moved early return check outside try block

**Proof run**

- Commands executed:
  - `dotnet build src/VoiceStudio.App/VoiceStudio.App.csproj -c Release --no-incremental`
  - `.\scripts\gatec-publish-launch.ps1 -NoLaunch`
- Result:
  - ✅ Build succeeded with 0 errors, 0 CS0126 errors
  - ✅ Gate C publish-launch script completed successfully
  - ✅ XAML compiler exit code: 0 (both passes)
  - ✅ Publish completed: `VoiceStudio.App.exe` produced at `E:\VoiceStudio\.buildlogs\x64\Release\gatec-publish\VoiceStudio.App.exe`

**Regression / prevention**

- Build verification: CS0126 errors will be caught by C# compiler during build
- Gate C script will fail if build errors are reintroduced

**Links**

- Related entries:
  - VS-0023 (Release build configuration - blocked by this)
  - VS-0012 (App crash on startup - indirectly blocked by this)

---

### VS-0026 — Early crash artifact capture (boot marker + WER LocalDumps helper)

**State:** DONE  
**Severity:** S2 Major  
**Gate:** C  
**Owner role:** Core Platform Engineer  
**Reviewer role:** Release Engineer  
**Categories:** BOOT, RUNTIME  
**Introduced:** 2026-01-09  
**Last verified:** 2026-01-09 (Windows 10.0.26200)

**Summary**

- Added an **early boot marker** and **pre-App exception logging** so Gate C failures leave deterministic artifacts even if WinUI never reaches `App.xaml.cs`.
- Added a helper script to enable **Windows Error Reporting (WER) LocalDumps** for native fail-fast crashes (e.g. `0xC0000602`).
- Updated the Gate C publish+launch script to always print/store actionable crash artifact paths.

**Artifacts**

- Managed crash logs (existing): `%LOCALAPPDATA%\VoiceStudio\crashes\crash_*.log` + `latest.log`
- Boot marker: `%LOCALAPPDATA%\VoiceStudio\crashes\boot_latest.json`
- Startup exception pointer: `%LOCALAPPDATA%\VoiceStudio\crashes\latest_startup_exception.log`
- Native dumps (when enabled): `%LOCALAPPDATA%\VoiceStudio\dumps\*.dmp`

**Change set**

- Files changed:
  - `src/VoiceStudio.App/Program.cs`
  - `scripts/gatec-publish-launch.ps1`
  - `scripts/enable-wer-localdumps.ps1`
  - `docs/governance/overseer/GATE_C_CRASH_LOG_INSTRUMENTATION.md`

**Proof run**

- Commands executed:
  - `powershell -ExecutionPolicy Bypass -File "e:\\VoiceStudio\\scripts\\enable-wer-localdumps.ps1" -Mode Status`
- Result:
  - ✅ Script executes and reports current LocalDumps configuration state

---

### VS-0017 — Engine Manager Service Implementation

**State:** DONE  
**Severity:** S2 Major  
**Gate:** E  
**Owner role:** Core Platform Engineer  
**Reviewer role:** System Architect  
**Categories:** ENGINE  
**Introduced:** 2025-01-28  
**Last verified:** 2025-01-28

**Summary**

- Adds `EngineManager` service plus `BackendEngineAdapter` to expose backend engines through standardized `IEngine` interfaces and lifecycle calls. Frontend discovers engines via `/api/engines` and proxies `start/stop/status/voices` to backend.

**Change set**

- `src/VoiceStudio.App/Services/EngineManager.cs`
- `src/VoiceStudio.App/Core/Engines/BackendEngineAdapter.cs`
- DI/store wiring; backend lifecycle endpoints under `/api/engines/*`.

**Proof run**

- `dotnet build "E:\VoiceStudio\VoiceStudio.sln" -c Debug -p:Platform=x64`
- `dotnet test "E:\VoiceStudio\src\VoiceStudio.App.Tests\VoiceStudio.App.Tests.csproj" -c Debug -p:Platform=x64`

---

### VS-0018 — RuleGuard violation in /api/engines stop endpoint (remove pass)

**State:** DONE  
**Severity:** S0 Blocker  
**Gate:** B  
**Owner role:** System Architect  
**Reviewer role:** System Architect  
**Categories:** BUILD, RULES  
**Introduced:** 2026-01-01  
**Last verified:** 2026-01-01

**Summary**

- Removed `pass` in `POST /api/engines/{engine_id}/stop`; implemented lease release vs drain semantics to satisfy RuleGuard.

**Change set**

- `backend/api/routes/engines.py`

**Proof run**

- `python tools\verify_no_stubs_placeholders.py` → ✅ No violations

---

### VS-0023 — Release build configuration hotfix (Gate C publish+launch)

**State:** DONE  
**Severity:** S0 Blocker  
**Gate:** C  
**Owner role:** Build & Tooling Engineer  
**Reviewer role:** Overseer  
**Categories:** BUILD, RUNTIME  
**Introduced:** 2025-01-28  
**Last verified:** 2026-01-10

**Summary**

- Release configuration fixed; Gate C publish+launch script now passes on unpackaged apphost EXE and is wired into CI.

**Change set**

- Build/publish settings in `VoiceStudio.App.csproj`, supporting targets/scripts.

**Proof run**

- `python tools\verify_no_stubs_placeholders.py`
- `dotnet build VoiceStudio.sln -c Debug/Release -p:Platform=x64`
- `.\scripts\gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64 -SmokeSeconds 10` → ✅ running_after_timeout

---

### VS-0027 — So-VITS-SVC engine + quality metrics fixes

**State:** DONE  
**Severity:** S2 Major  
**Gate:** E  
**Owner role:** Engine Engineer  
**Reviewer role:** Release Engineer  
**Categories:** ENGINE  
**Introduced:** 2026-01-10  
**Last verified:** 2026-01-10

**Summary**

- Added So-VITS-SVC 4.0 engine structure with manifest discovery (45 engines); improved quality metrics error handling and confidence (normalized features); verified default engine selection fallback chain.

**Change set**

- `app/core/engines/sovits_svc_engine.py`
- `app/core/engines/quality_metrics.py`
- `engines/audio/sovits/engine.manifest.json`
- `scripts/verify_engine_tasks_targeted.py`

**Proof run**

- `python scripts/verify_engine_tasks_targeted.py` → ✅ All targeted checks pass

---

### VS-0028 — Replace UI control stubs with functional visualizations

**State:** DONE  
**Severity:** S2 Major  
**Gate:** F  
**Owner role:** UI Engineer  
**Reviewer role:** Overseer  
**Categories:** UI  
**Introduced:** 2026-01-10  
**Last verified:** 2026-01-10

**Summary**

- Replaced Analyzer controls with functional Path/Canvas implementations (waveform, spectrogram, loudness, radar, phase, VU meter, audio orbs); removed UI stubs.

**Change set**

- `src/VoiceStudio.App/Controls/*Control.xaml` and `.xaml.cs` implementations (Waveform, Spectrogram, LoudnessChart, RadarChart, PhaseAnalysis, VUMeter, AudioOrbs).

**Proof run**

- `python tools\verify_no_stubs_placeholders.py` → ✅
- `dotnet build src/VoiceStudio.App/VoiceStudio.App.csproj -c Debug` → ✅

## Entry template (copy/paste)

### VS-0000 — <short title>

**State:** OPEN  
**Severity:** S2 Major  
**Gate:** (A–H)  
**Owner role:** (Overseer / Architect / Build / UI / Core / Engine / Release)  
**Reviewer role:** (required)  
**Categories:** BUILD, UI  
**Introduced:** (date or commit)  
**Last verified:** (date + machine)

**Summary**

- **Environment**

- OS:
- .NET SDK:
- Visual Studio:
- Repo path:
- Configuration:
- Any required optional components:

**Reproduction**

1.
2.
3.

**Expected**

- **Actual**

- **Evidence**

- Log excerpt (keep short):
- Screenshot path (if any):
- Crash bundle path (if any):

**Suspected root cause**

- **Fix plan (small tasks)**

- [ ] Task 1 (single success condition)
- [ ] Task 2
- [ ] Task 3

**Change set**

- Files changed:
- Notes:

**Proof run (required)**

- ## Commands executed:
- ## Result:

**Regression / prevention**

- Tests added/updated:
- RuleGuard rule updated (if relevant):
- Any new ADR link (if architecture changed):

**Links**

- Related commits:
- Related entries:
- ADRs:

---
