# Quality Ledger — Single Source of Truth

Last updated: 2025-12-26  
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

| ID      | State       | Sev         | Gate | Owner Role               | Category        | Title                                                                         |
| ------- | ----------- | ----------- | ---- | ------------------------ | --------------- | ----------------------------------------------------------------------------- |
| VS-0001 | DONE        | S0 Blocker  | B    | Build & Tooling Engineer | BUILD           | XAML compiler false-positive exit code 1 fix                                  |
| VS-0002 | DONE        | S2 Major    | E    | Engine Engineer          | ENGINE          | Replace placeholder ML quality prediction with production implementation      |
| VS-0003 | IN_PROGRESS | S1 Critical | H    | Release Engineer         | PACKAGING       | Installer package verification and upgrade/rollback path                      |
| VS-0004 | DONE        | S2 Major    | D    | Core Platform Engineer   | STORAGE         | Persist project metadata on disk for cross-restart reliability                |
| VS-0005 | DONE        | S0 Blocker  | B    | Build & Tooling Engineer | BUILD           | XAML Page items disabled causing missing XAML copy failures                   |
| VS-0006 | DONE        | S2 Major    | D    | Core Platform Engineer   | STORAGE,AUDIO   | Content-addressed audio cache to deduplicate waveforms and model artifacts    |
| VS-0007 | DONE        | S2 Major    | E    | Engine Engineer          | ENGINE          | ML quality prediction integration into engine metrics                         |
| VS-0008 | DONE        | S0 Blocker  | B    | Build & Tooling Engineer | BUILD,RULES     | RuleGuard not configured - Gate B requires RuleGuard pass                     |
| VS-0009 | DONE        | S2 Major    | E    | Engine Engineer          | ENGINE          | Enable ML quality prediction in Chatterbox and Tortoise voice cloning engines |
| VS-0010 | DONE        | S2 Major    | C    | Build & Tooling Engineer | TEST,BUILD      | Test runner configuration fix                                                 |
| VS-0011 | DONE        | S0 Blocker  | C    | Core Platform Engineer   | BOOT            | ServiceProvider recursion fix                                                 |
| VS-0012 | TRIAGE      | S0 Blocker  | C    | Release Engineer         | BOOT,PACKAGING  | App crash on startup: 0xE0434352 / 0x80040154 (WinUI class not registered)    |
| VS-0013 | DONE        | S2 Major    | C    | UI Engineer              | TEST,UI         | Unit tests requiring UI thread failing                                        |
| VS-0014 | DONE        | S2 Major    | D    | Core Platform Engineer   | RUNTIME         | Job Runtime hardening                                                         |
| VS-0015 | DONE        | S2 Major    | D    | Core Platform Engineer   | STORAGE         | ProjectStore storage migration verification                                   |
| VS-0016 | DONE        | S2 Major    | E    | Core Platform Engineer   | ENGINE          | Standardize Engine Interface                                                  |
| VS-0019 | DONE        | S2 Major    | D    | Core Platform Engineer   | STORAGE,RUNTIME | Backend preflight readiness report (paths + model root)                       |
| VS-0020 | DONE        | S2 Major    | D    | Core Platform Engineer   | STORAGE,AUDIO   | Durable audio artifact registry (audio_id -> file_path)                       |
| VS-0021 | DONE        | S2 Major    | D    | Core Platform Engineer   | RUNTIME,STORAGE | Persist voice cloning wizard job state across restart                         |
| VS-0022 | DONE        | S3 Minor    | D    | Core Platform Engineer   | RUNTIME,PLUGINS | Deterministic ffmpeg discovery (env override + known locations)               |

---

### VS-0012 — App crash on startup: 0xE0434352 / 0x80040154 (WinUI class not registered)

**State:** TRIAGE  
**Severity:** S0 Blocker  
**Gate:** C  
**Owner role:** Release Engineer  
**Reviewer role:** System Architect  
**Categories:** BOOT, PACKAGING  
**Introduced:** 2025-12-30  
**Last verified:** 2025-12-30 (Windows 10.0.26200)

**Summary**

- Launching `VoiceStudio.App.exe` from build output terminates immediately with exit code `-532462766` (0xE0434352).
- Windows Application log shows an unhandled exception during WinUI startup:
  - `System.Runtime.InteropServices.COMException (0x80040154): Class not registered (REGDB_E_CLASSNOTREG)`

**Environment**

- OS: Windows 10.0.26200
- .NET: 8.0.22
- CoreCLR: 8.0.2225.52707
- Launch path:
  - `E:\VoiceStudio\.buildlogs\x64\Debug\net8.0-windows10.0.19041.0\VoiceStudio.App.exe`
- Windows App Runtime packages present on machine (x64/x86), including 1.8.

**Reproduction**

1. Build Debug x64 (producing the exe under `.buildlogs`).
2. Run:
   - `Start-Process "E:\VoiceStudio\.buildlogs\x64\Debug\net8.0-windows10.0.19041.0\VoiceStudio.App.exe"`
3. Observe immediate termination.

**Expected**

- App starts and remains running (window visible).

**Actual**

- Process exits within seconds.

**Evidence**

- Exit code:
  - `-532462766` (0xE0434352)
- Windows Application log events from the same launch window:
  - `.NET Runtime` Id 1026:
    - `System.Runtime.InteropServices.COMException (0x80040154): Class not registered (REGDB_E_CLASSNOTREG)`
    - Stack includes `Microsoft.UI.Xaml.Application.Start(...)` and `VoiceStudio.App.Program.Main(...)` (generated `App.g.i.cs`)
  - `Application Error` Id 1000:
    - Exception code: `0xe0434352`
  - `Windows Error Reporting` Id 1001:
    - Event: `APPCRASH`
    - Report Id: `e9eeca1d-93ca-4668-89c1-3f50c982e451`

**Suspected root cause**

- WinUI activation failure when launching an unpackaged exe directly (WinRT class not registered), despite the Windows App Runtime being installed.
- Gate C requires a deterministic, documented launch method for the desktop app (packaged vs unpackaged) with required runtime prerequisites.

**Fix plan (small tasks)**

- [ ] Record the Gate C proof standard launch method (packaged MSIX vs unpackaged exe).
- [ ] Make the required runtime prerequisites deterministic for that launch method.
- [ ] Capture a successful Gate C proof run where the process stays running and the main window appears.

**Change set**

- Files changed:
  - `Recovery Plan/QUALITY_LEDGER.md`
- Notes:
  - VS-0012 entry created with on-machine repro + event log evidence.

**Proof run (required)**

- Commands executed:
  - `Start-Process "E:\VoiceStudio\.buildlogs\x64\Debug\net8.0-windows10.0.19041.0\VoiceStudio.App.exe"`
- Result:
  - Exits with `-532462766` and logs `.NET Runtime` Id 1026 `0x80040154`.

**Regression / prevention**

- Add a scripted boot smoke check in CI on Windows runners using the Gate C standard launch method.

**Links**

- Related entries:
  - VS-0003 (Installer package verification and upgrade/rollback path for Gate H)

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
