## VoiceStudio — Project Progression Log (as of 2026-01-11)

**Scope:** “Where are we, how did we get here, what is blocking production, what are we building with, and why did we abandon MSIX.”

**Canonical sources used (in priority order):**

- **Ledger (source of truth):** `Recovery Plan/QUALITY_LEDGER.md`
- **Evidence packets:** `docs/governance/overseer/handoffs/VS-*.md`
- **Architecture decision:** `docs/architecture/ADR_GATE_C_ARTIFACT_CHOICE.md`
- **Build/packaging scripts:** `scripts/gatec-publish-launch.ps1`, `scripts/prepare-release.ps1`, `installer/build-installer.ps1`, `installer/verify-installer.ps1`
- **Build configuration pins:** `global.json`, `Directory.Build.props`, `Directory.Build.targets`, `src/VoiceStudio.App/VoiceStudio.App.csproj`
- **Python stack manifests:** `requirements.txt`, `requirements_engines.txt`, `requirements_missing_libraries.txt`, `version_lock.json`, `docs/design/COMPATIBILITY_MATRIX.md`

---

## Executive summary (broad)

- **What VoiceStudio is**: a WinUI 3 (.NET) desktop app (`src/`) + Python FastAPI backend (`backend/`) + Python engine/runtime layer (`app/`) + engine manifests (`engines/`) with governance gates A–H.
- **Current packaging lane (locked)**: **unpackaged apphost EXE + installer only**. MSIX is archived/removed to eliminate dual-path ambiguity.
- **Current production blockers (broad):**
  - **Gate C (boot stability)**: app boot/activation must be proven end-to-end with deterministic evidence (**VS-0012**).
  - **Gate H (installer readiness)**: installer lifecycle proof (install → launch → upgrade → rollback → uninstall) is still incomplete (**VS-0003**) and is downstream of Gate C.

---

## Major decisions register (what/why/what we expect to achieve)

### Packaging lane: unpackaged EXE + installer only (no MSIX)

- **Decision**: keep **one lane**: unpackaged apphost EXE for Gate C + installer for distribution; **MSIX is not used**.
- **Why**:
  - Removes “dual-path ambiguity” (code/docs/scripts drifting between lanes)
  - Avoids MSIX-specific build complexity (PRI/manifest/signing/tooling)
  - Keeps the Gate C proof artifact deterministic and fast to iterate on
- **What we plan to accomplish with this change**:
  - Faster Gate C iteration and clearer failure diagnosis
  - Single, repeatable production release workflow (installer) with less maintenance overhead
  - No “fallback packaging path” — only deterministic evidence artifacts (logs/dumps) remain
- **Evidence/implementation**:
  - ADR: `docs/architecture/ADR_GATE_C_ARTIFACT_CHOICE.md`
  - MSIX artifacts archived: `docs/archive/msix/`
  - MSIX manifest removed from active project; MSIX packaging script removed from `scripts/`

### Gate C proof is script-driven with deterministic artifacts

- **Decision**: Gate C proof uses `scripts/gatec-publish-launch.ps1` + `.buildlogs/` + crash artifacts under `%LOCALAPPDATA%\VoiceStudio\crashes`.
- **Why**:
  - Gate C failures frequently occur before UI is visible; evidence must survive early crash modes
  - Binlogs and fixed file paths let multiple roles reproduce and reason from the same evidence
- **What we plan to accomplish**:
  - Make “boot stability” measurable and auditable (repeatable proof runs)
  - Reduce “works on my machine” drift and cut debugging time
- **Evidence/implementation**:
  - Script: `scripts/gatec-publish-launch.ps1`
  - Early crash artifacts: `src/VoiceStudio.App/Program.cs` (boot markers + early exception logs)
  - Handoff: `docs/governance/overseer/handoffs/VS-0026.md`

### Toolchain pinning (WinUI / WinAppSDK / .NET)

- **Decision**: pin core WinUI/WinAppSDK versions centrally; pin .NET SDK via `global.json`.
- **Why**: WinUI build pipeline is sensitive to version skew; pinning reduces “random” XAML tool failures.
- **What we plan to accomplish**: stable CI builds + fewer XAML/toolchain regressions.
- **Evidence/implementation**:
  - .NET SDK pin: `global.json` (currently `8.0.416`)
  - WinAppSDK pin: `Directory.Build.props` (currently `MicrosoftWindowsAppSDKVersion=1.8.251106002`)
  - App target framework: `src/VoiceStudio.App/VoiceStudio.App.csproj` (`net8.0-windows10.0.19041.0`)

### Quality discipline: RuleGuard + analyzer warnings (Roslynator)

- **Decision**: enforce “no stubs/placeholders” via RuleGuard; keep Roslynator as **non-blocking warnings**.
- **Why**:
  - RuleGuard prevents shipping TODO/NotImplemented/pass-only logic (hard stop quality gate)
  - Roslynator warnings raise quality steadily without blocking Gate C critical path
- **What we plan to accomplish**:
  - Reduce regressions and “unfinished” behavior making it into release
  - Incrementally reduce warning debt without derailing milestones
- **Evidence/implementation**:
  - RuleGuard wired via `Directory.Build.targets` (`RunRuleGuard` target)
  - Roslynator package: `src/VoiceStudio.App/VoiceStudio.App.csproj` (`Roslynator.Analyzers 4.11.0`)
  - Coordination doc: `docs/governance/overseer/ROSLYNATOR_TEAM_COORDINATION_2026-01-10.md`

---

## Progression timeline (high-signal milestones)

This is the “what changed when” view, stitched from the ledger + handoffs + build docs.

- **2025-01-28**
  - Many foundational governance and plan documents created/updated (worker prompts, roadmaps, tooling plans).
  - Installer tooling and scripts introduced/verified (Inno Setup + WiX) — see `installer/` and `docs/release/INSTALLER_PREPARATION.md`.
- **2025-12-30**
  - Ledger recorded **VS-0012** as Gate C S0 blocker on Windows 10 build `26200` with `0x80040154` (“Class not registered”) evidence.
  - Ledger recorded Gate H installer track as **VS-0003** (but detailed entry is not present in the ledger body; handoff exists).
- **2026-01-05 → 2026-01-10**
  - Gate C publish+launch script matured into a stable, repeatable proof command (`scripts/gatec-publish-launch.ps1`).
  - Early crash artifact capture added (boot markers + startup exception pointers + WER LocalDumps helper) — **VS-0026**.
  - Release build/publish investigations captured in evidence packets — see **VS-0023** and **VS-0012** handoffs.
- **2026-01-11**
  - Packaging lane explicitly locked to **unpackaged EXE + installer only**; MSIX artifacts archived under `docs/archive/msix/` and removed from active paths.

---

## Major blockers stopping progression (broad)

### Blocker class 1: Gate C boot stability isn’t fully proven end-to-end

- **Impact**: without a stable boot + UI smoke proof, we can’t certify the artifact, unblock downstream work, or trust installer verification results.
- **Primary ledger item**: **VS-0012** (Gate C, S0 Blocker).

### Blocker class 2: Gate H installer lifecycle proof is incomplete

- **Impact**: production release requires installer evidence (install/upgrade/rollback/uninstall) — cannot be marked done without Gate C stability.
- **Primary ledger item**: **VS-0003** (Gate H, S1 Critical).

---

## Production-stopping error dossiers (extremely detailed)

### VS-0012 — App crash on startup: 0xE0434352 / 0x80040154 (WinUI class not registered)

- **Ledger status**: `TRIAGE` (Gate C, S0 Blocker) in `Recovery Plan/QUALITY_LEDGER.md`
- **What it blocks**:
  - Gate C DONE criteria (boot stability proof)
  - Gate H installer verification reliability (you can’t validate an installer if the app doesn’t boot deterministically)

#### Symptom

- Process terminates immediately when launching the unpackaged EXE.
- Event Viewer shows:
  - `.NET Runtime` Id 1026: `System.Runtime.InteropServices.COMException (0x80040154): Class not registered`
  - `Application Error` Id 1000: `0xe0434352`

#### Environment (as captured in ledger)

- **OS**: Windows `10.0.26200` (Insider/vNext build)
- **.NET runtime**: `8.0.22`
- **Target framework**: `net8.0-windows10.0.19041.0` (`src/VoiceStudio.App/VoiceStudio.App.csproj`)
- **WinAppSDK**: pinned to `1.8.251106002` (`Directory.Build.props`)

#### Reproduction (canonical)

From the ledger:

- Build Debug x64 and run:
  - `Start-Process "E:\VoiceStudio\.buildlogs\x64\Debug\net8.0-windows10.0.19041.0\VoiceStudio.App.exe"`

#### Evidence artifacts (what to attach to the proof packet)

- **Ledger evidence**: see VS-0012 section in `Recovery Plan/QUALITY_LEDGER.md`
- **Gate C publish+launch logs** (if using the proof script):
  - `.buildlogs/gatec-latest.txt`
  - `.buildlogs/x64/Release/gatec-publish/gatec-launch.log`
  - `.buildlogs/gatec-publish-<timestamp>-<pid>.binlog`
- **Early crash artifacts** (even if WinUI never constructs `App`):
  - `%LOCALAPPDATA%\VoiceStudio\crashes\boot_latest.json`
  - `%LOCALAPPDATA%\VoiceStudio\crashes\latest_startup_exception.log`
  - `%LOCALAPPDATA%\VoiceStudio\crashes\latest.log`
  - Native dumps (if enabled): `%LOCALAPPDATA%\VoiceStudio\dumps\*.dmp` (enable via `scripts/enable-wer-localdumps.ps1`)

#### Root cause analysis (high confidence vs hypotheses)

- **High confidence**:
  - `0x80040154` at WinUI startup is a runtime activation/registration failure. For unpackaged WinUI 3 apps this most commonly indicates the Windows App SDK runtime is not being loaded/initialized early enough or is mismatched to the environment.
- **Key complicating factor**:
  - **OS build 26200 (Insider)** + **WinAppSDK 1.8** is a higher-risk combo; regressions are plausible even if “runtime packages are installed.”
- **Mitigations already implemented in code/tooling**:
  - `src/VoiceStudio.App/Program.cs` explicitly calls `Bootstrap.Initialize(0x00010008)` for unpackaged runs before WinUI activation.
  - Publish output is scrubbed of OS-adjacent DLLs to avoid fail-fast / wrong-DLL-loaded modes (see `ExcludeSystemDllsFromPublish` target in `VoiceStudio.App.csproj`).
  - Deterministic crash artifacts were added (VS-0026) to make failures actionable.

#### Related failure mode (historical but important for production proof)

- `docs/governance/overseer/handoffs/VS-0023.md` captures an additional Release publish crash mode:
  - Exit code `0xC0000602` with **faulting module `CoreMessagingXP.dll`** (no package identity).
- The current publish approach intentionally avoids shipping certain OS-adjacent runtime DLLs loose in the publish folder to reduce these fail-fast modes.

#### Current “state of the world” vs what still must be proven

- **We can produce a Gate C publish artifact and keep it running for N seconds** via:
  - `scripts/gatec-publish-launch.ps1`
  - Evidence packet: `docs/governance/overseer/handoffs/VS-0012.md`
- **Still missing for Gate C closure**:
  - **UI smoke proof** (navigation + “no binding errors” capture) on the Gate C artifact.

#### Required next action (to close VS-0012 for production)

- Run the Gate C publish+launch script, then do UI smoke using that exact artifact:
  - `.\scripts\gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64 -SmokeSeconds 10`
  - Launch: `E:\VoiceStudio\.buildlogs\x64\Release\gatec-publish\VoiceStudio.App.exe`
  - Capture: navigation evidence + binding error output + exit code

---

### VS-0003 — Installer package verification and upgrade/rollback path (Gate H)

- **Ledger status**: `IN_PROGRESS` (Gate H, S1 Critical) in `Recovery Plan/QUALITY_LEDGER.md` (index row)
- **Handoff evidence**: `docs/governance/overseer/handoffs/VS-0003.md`
- **Why it halts production**:
  - This is the “ship it” gate: without installer lifecycle proofs, production release can’t be certified.

#### What “DONE” means for VS-0003 (production-grade definition)

- A clean, repeatable workflow for:
  - Install → launch → upgrade → rollback → uninstall
- On **clean Windows 10/11 profiles** (VMs preferred), with:
  - Deterministic logs/proof artifacts (installer logs + app logs + backend logs)
  - Explicit prereq story (what is bundled vs required vs detected)

#### Current implementation status (what exists today)

- **Installer build**: `installer/build-installer.ps1`
  - Supports `-InstallerType InnoSetup` or `WiX`
  - Requires external tooling installed:
    - Inno Setup: `ISCC.exe` (default path `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`)
    - WiX: `candle.exe` + `light.exe` in PATH
- **Installer verification helper**: `installer/verify-installer.ps1`
- **Release prep**: `scripts/prepare-release.ps1` (builds frontend + builds installer + assembles `release/dist`)
- **Documentation**: `docs/release/INSTALLER_PREPARATION.md` + `docs/release/UPGRADE_ROLLBACK_NOTES.md`

#### Why it’s not done yet

- Gate H is **downstream of Gate C**. Until VS-0012 is closed with a real UI smoke proof, installer proofs are not trustworthy.
- Historical note from the VS-0003 handoff: installer build was previously blocked by frontend compilation errors at the time of that proof run.

#### Required next action (to close VS-0003 for production)

Once Gate C is green:

- Build installer:
  - `.\installer\build-installer.ps1 -InstallerType InnoSetup -Configuration Release -Version 1.0.0`
- Verify the installer artifact exists and is sane:
  - `.\installer\verify-installer.ps1 -ExpectedVersion 1.0.0`
- Run clean-machine lifecycle proofs (VMs):
  - install → launch → upgrade → rollback → uninstall
- Capture evidence packet:
  - commands, outputs, installer logs, resulting file layout, app boot logs, and any crash bundles.

---

## Full tooling + dependency inventory (what we use to build and run)

### Windows/.NET frontend (WinUI 3)

- **SDK pinned**: .NET SDK `8.0.416` (`global.json`)
- **Target framework**: `net8.0-windows10.0.19041.0` (`src/VoiceStudio.App/VoiceStudio.App.csproj`)
- **Min Windows target**: `TargetPlatformMinVersion=10.0.17763.0` (`VoiceStudio.App.csproj`)
- **Key NuGet packages (core)**:
  - `Microsoft.WindowsAppSDK` = `1.8.251106002` (pinned in `Directory.Build.props`)
  - `Microsoft.Windows.SDK.BuildTools` = `10.0.26100.4654` (pinned)
  - `Microsoft.Graphics.Win2D` = `1.3.2`
  - `CommunityToolkit.WinUI.UI.Controls` = `7.1.2`
  - `CommunityToolkit.Mvvm` = `8.2.2`
  - `NAudio` = `2.2.1`
  - `Roslynator.Analyzers` = `4.11.0` (warnings; non-blocking)

### WinUI build pipeline / XAML tooling

- **XAML compiler wrapper**: `tools/xaml-compiler-wrapper.cmd`
  - Locates `XamlCompiler.exe` from NuGet (`microsoft.windowsappsdk.winui`)
  - Handles “false-positive exit code 1” (VS-0001) by validating output.json and generated code
  - Retries if output.json missing due to file locks
- **MSBuild targets**: `Directory.Build.targets`
  - Runs RuleGuard before build
  - Copies XAML files into `obj/` deterministically to prevent MSB3030

### RuleGuard (no placeholders)

- **Script**: `tools/verify_no_stubs_placeholders.py`
- **Invocation**: via `Directory.Build.targets` (`RunRuleGuard`) and in CI lanes
- **Purpose**: blocks TODO/FIXME/NotImplemented/pass-only stub behavior

### Python backend + engines

- **Backend/dev deps**: `requirements.txt`
  - FastAPI/uvicorn/pydantic/httpx/websockets
  - pytest tooling + docs tooling (Sphinx)
- **Engine deps**: `requirements_engines.txt`
  - Declares pinned ML/audio stack (Torch, transformers, librosa, numpy, etc.)
- **Engine “missing libraries” list**: `requirements_missing_libraries.txt`
  - Additional audio quality libs (PESQ/STOI, spleeter, etc.) referenced from older projects
- **Version reference**: `version_lock.json` (note: see compatibility drift section below)

### Installer toolchain

- **Installer build**: `installer/build-installer.ps1`
- **Installer verification**: `installer/verify-installer.ps1`
- **Installer tech choices**: Inno Setup (`installer/VoiceStudio.iss`) and/or WiX (`installer/VoiceStudio.wxs`)
- **Prereqs**: Inno Setup 6.2+ and/or WiX 3.11+

---

## Compatibility cross-reference (what matches / what conflicts)

### “As implemented” (source-of-truth config files)

- **.NET SDK**: `8.0.416` (`global.json`)
- **WinAppSDK**: `1.8.251106002` (`Directory.Build.props`)
- **Windows SDK BuildTools**: `10.0.26100.4654` (`Directory.Build.props`, `VoiceStudio.App.csproj`)
- **Target**: Windows 10 1809+ (`TargetPlatformMinVersion=10.0.17763.0`)

### “As documented” (potential drift)

The repo contains older compatibility docs that don’t perfectly match the current pins.

- **Windows UI stack drift**:
  - `docs/design/COMPATIBILITY_MATRIX.md` references WinAppSDK `1.5.0`, while the build pins WinAppSDK `1.8.251106002`.
- **Python ML stack drift**:
  - `docs/design/COMPATIBILITY_MATRIX.md` targets Torch `2.9.0+cu128`, while `requirements_engines.txt` pins Torch `2.2.2+cu121`.
  - `version_lock.json` currently matches `requirements_engines.txt` (Torch `2.2.2+cu121`) but conflicts with the matrix doc.
- **Python version drift for tooling**:
  - `backend/mcp_servers/mcp-unlock-pdf/pyproject.toml` requires Python `>=3.12` while engines/docs often refer to Python `3.11.x`.
  - Recommendation: isolate MCP tooling into its own venv; do not force the whole engine stack to 3.12 without verification.

**Practical implication:** there is a _documentation vs implementation_ mismatch. This is not currently listed as a “production blocker” in the ledger, but it is a real compatibility risk that can stall progress if different roles follow different version sources.

---

## MSIX build history (what failed and why we stopped)

### What we attempted

- An MSIX lane existed via:
  - `scripts/package_release.ps1` (now archived at `docs/archive/msix/package_release.ps1`)
  - `src/VoiceStudio.App/Package.appxmanifest` (now archived at `docs/archive/msix/Package.appxmanifest`)
  - MSBuild properties like `GenerateAppxPackageOnBuild=true` / Appx tooling
  - Windows SDK packaging tools (e.g., `makeappx.exe`) for MSIX creation (the archived script attempted to locate this under Windows Kits)

### What broke (high-level)

- **PRI resource conflicts / build pipeline friction** (documented in ADR)
- **Higher build complexity**:
  - manifest/signing/tooling requirements
  - dependence on Windows SDK packaging tools (e.g., `makeappx.exe`)
- **Runtime/activation complexity**:
  - The core failure mode (WinUI runtime activation) did not become simpler under MSIX in this repo’s evidence; debugging was slower due to packaging overhead.

### Why unpackaged EXE won (and why we doubled down)

- **ADR conclusion**: `docs/architecture/ADR_GATE_C_ARTIFACT_CHOICE.md` explicitly rejects MSIX as the Gate C primary artifact due to encountered build complexity and PRI issues.
- **Gate discipline**: Gate C needs one deterministic launch artifact; unpackaged EXE is faster to iterate, easier to instrument, and easier to attach evidence to.
- **Single-lane cleanup**: MSIX artifacts were archived/removed to prevent drift:
  - archived under `docs/archive/msix/`
  - removed from `scripts/` and `src/VoiceStudio.App` project item wiring

---

## What we plan to accomplish next (critical path)

1. **Close VS-0012 with real UI smoke proof**
   - Run the Gate C artifact
   - Navigate panels
   - Capture binding error output + screenshots/logs
2. **Immediately execute Gate H proofs (VS-0003)**
   - Build installer (Inno/WiX)
   - Validate lifecycle on clean VMs
   - Produce a complete evidence packet

---

## Appendix: “Where is the evidence?”

- **Ledger**: `Recovery Plan/QUALITY_LEDGER.md`
- **Handoffs**: `docs/governance/overseer/handoffs/VS-*.md`
- **Gate C script**: `scripts/gatec-publish-launch.ps1`
- **Build logs**: `.buildlogs/` (binlogs + `gatec-latest.txt`)
- **Crash artifacts**: `%LOCALAPPDATA%\VoiceStudio\crashes\*` and `%LOCALAPPDATA%\VoiceStudio\dumps\*`
- **Installer**: `installer/` + `docs/release/INSTALLER_PREPARATION.md`
