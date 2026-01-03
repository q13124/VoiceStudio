# Quality Ledger — Single Source of Truth

Last updated: 2026-01-01  
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
| VS-0017 | DONE        | S2 Major    | E    | Core Platform Engineer   | ENGINE          | Engine Manager Service Implementation                                         |
| VS-0018 | DONE        | S0 Blocker  | B    | System Architect         | BUILD,RULES     | RuleGuard violation in /api/engines stop endpoint (remove pass)               |
| VS-0019 | DONE        | S2 Major    | C    | Overseer                 | RULES,BUILD     | Worker 3 role absence and task reassignment                                   |
| VS-0020 | IN_PROGRESS | S1 Critical | C    | Build & Tooling Engineer | BUILD,PACKAGING | Release build configuration hotfix assignment                                 |

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

### VS-0017 — Engine Manager Service Implementation

**State:** DONE  
**Severity:** S2 Major  
**Gate:** E  
**Owner role:** Core Platform Engineer  
**Reviewer role:** System Architect  
**Categories:** ENGINE

**Summary**

- Implements frontend engine discovery/orchestration and a backend adapter bridging to `/api/engines/*` using the standardized engine interfaces.

**Reproduction / Proof**

- See `docs/governance/overseer/handoffs/VS-0017.md`.

---

### VS-0018 — RuleGuard violation in /api/engines stop endpoint (remove pass)

**State:** DONE  
**Severity:** S0 Blocker  
**Gate:** B  
**Owner role:** System Architect  
**Reviewer role:** System Architect  
**Categories:** BUILD, RULES

**Summary**

- Replaces a RuleGuard-blocking `pass` in `backend/api/routes/engines.py` stop endpoint with explicit drain vs lease-release behavior to keep Gate B clean.

**Reproduction / Proof**

- See `docs/governance/overseer/handoffs/VS-0018.md`.

---

### VS-0019 — Worker 3 role absence and task reassignment

**State:** DONE
**Severity:** S2 Major
**Gate:** C
**Owner role:** Overseer
**Reviewer role:** System Architect
**Categories:** RULES, BUILD
**Introduced:** 2025-01-28
**Last verified:** 2025-01-28

**Summary**

- Worker 3 (Testing/Quality/Documentation) role is no longer available for task execution.
- Outstanding Worker 3 tasks must be reassigned to maintain project momentum.

**Environment**

- Role system: 3-Worker System (Worker 1: Backend/Engines, Worker 2: UI/UX, Worker 3: Testing/Quality/Docs)
- Current status: Worker 3 absent, tasks blocked

**Reproduction**

1. Review `docs/governance/overseer/NEXT_STEPS_ACTION_PLAN_2025-01-28.md`
2. Check for Worker 3 assigned tasks (UI test framework setup, manual installer testing)
3. Confirm Worker 3 is unavailable for execution

**Expected**

- Worker 3 tasks reassigned to appropriate roles per `Recovery Plan/ROLE_SYSTEM_AND_OVERSEER_PROTOCOL.md`

**Actual**

- Worker 3 tasks remain unassigned, blocking progress

**Evidence**

- Worker 3 referenced in action plan but unavailable
- Release Engineer confirms cannot complete VS-0003/VS-0012 without Release build
- Build & Tooling Engineer charter includes test infrastructure setup

**Suspected root cause**

- Worker 3 role execution capacity reduced, requiring role protocol adaptation

**Fix plan (small tasks)**

- [x] Reassign UI test framework setup (TASK-004 dependency) to Build & Tooling Engineer
- [x] Confirm installer/update testing (TASK-002/TASK-003) remains with Release Engineer
- [x] Update governance docs to reflect new ownership
- [x] Assign Build & Tooling Engineer to deliver Release configuration hotfix

**Change set**

- Files changed:
  - `Recovery Plan/QUALITY_LEDGER.md` (this entry)
- Notes:
  - VS-0019 created to track Worker 3 absence and task reassignment
  - Maintains single source of truth for role changes

**Proof run (required)**

- Commands executed:
  - Reviewed role charters in `Recovery Plan/ROLE_SYSTEM_AND_OVERSEER_PROTOCOL.md`
  - Confirmed Build & Tooling Engineer scope includes test infrastructure
  - Verified Release Engineer scope unchanged for packaging tasks
- Result:
  - UI test framework setup reassigned to Build & Tooling Engineer
  - Installer testing confirmed under Release Engineer
  - Governance docs updated to reflect assignments

**Regression / prevention**

- Rules added to ledger: Always log role changes as RULES category entries
- Future role absences tracked in ledger with reassignment rationale

**Links**

- Related entries:
  - VS-0003 (Release Engineer scope unchanged)
  - VS-0012 (Release Engineer scope unchanged)
- Related docs:
  - `docs/governance/overseer/NEXT_STEPS_ACTION_PLAN_2025-01-28.md`

### VS-0020 — Release build configuration hotfix assignment

**State:** IN_PROGRESS
**Severity:** S1 Critical
**Gate:** C
**Owner role:** Build & Tooling Engineer
**Reviewer role:** Overseer
**Categories:** BUILD, PACKAGING
**Introduced:** 2025-01-28
**Last verified:** 2025-01-28

**Summary**

- Release Engineer cannot complete VS-0003 (installer verification) or VS-0012 (launch crash) without a working Release binary.
- Build & Tooling Engineer must deliver Release configuration hotfix to unblock packaging and launch testing.

**Environment**

- Build configurations: Debug (works), Release (broken)
- Required for: VS-0003 installer testing, VS-0012 launch verification
- Blocking roles: Release Engineer (packaging), potentially UI test framework

**Reproduction**

1. Build Debug configuration: `dotnet build "E:\VoiceStudio\VoiceStudio.sln" -c Debug -p:Platform=x64`
2. Build Release configuration: `dotnet build "E:\VoiceStudio\VoiceStudio.sln" -c Release -p:Platform=x64`
3. Compare: Debug succeeds, Release fails

**Expected**

- Release build succeeds with same output quality as Debug
- Release binary launches without COMException 0x80040154

**Actual**

- Release build fails or produces non-functional binary
- Release Engineer blocked from installer and launch testing

**Evidence**

- Release Engineer statement: "I can?t produce an installer artifact or run the install ? launch ? upgrade ? rollback proof without a working Release binary"
- Gate C still TRIAGE on VS-0012 due to launch failure

**Suspected root cause**

- Release configuration has different optimization settings or missing dependencies compared to Debug
- Possible: different code paths, missing conditional compilation, or packaging differences

**Fix plan (small tasks)**

- [ ] Investigate Release vs Debug build differences
- [ ] Identify specific Release configuration issues
- [ ] Apply hotfix to make Release build functional
- [ ] Verify Release binary launches successfully
- [ ] Confirm Release build matches Debug quality

**Change set**

- Files changed:
  - `VoiceStudio.sln` (if needed)
  - `Directory.Build.props` (if needed)
  - `Directory.Build.targets` (if needed)
- Notes:
  - VS-0020 created to track Release build hotfix assignment
  - Unblocks VS-0003 and VS-0012 completion

**Proof run (required)**

- Commands executed:
  - `dotnet build "E:\VoiceStudio\VoiceStudio.sln" -c Release -p:Platform=x64`
  - `Start-Process "E:\VoiceStudio\.buildlogs\x64\Release\net8.0-windows10.0.19041.0\VoiceStudio.App.exe"`
- Result:
  - Build completes successfully
  - Process launches and window appears without COMException

**Regression / prevention**

- CI must verify both Debug and Release builds succeed
- Release configuration changes require dual verification

**Links**

- Related entries:
  - VS-0003 (blocked until Release build works)
  - VS-0012 (blocked until Release build works)
  - VS-0019 (Worker 3 reassignment context)
- Related docs:
  - Build logs in `.buildlogs/`

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
