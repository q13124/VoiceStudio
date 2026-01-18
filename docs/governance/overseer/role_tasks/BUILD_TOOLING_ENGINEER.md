# Build & Tooling Engineer — Next task list

## Mission alignment

Keep the build/publish lane deterministic so **voice cloning quality work** can proceed without toolchain drift.

## Current state snapshot (from evidence)

- ✅ Gate C is **DONE**: publish + UI smoke proof is green (VS-0012 DONE).
- ✅ Gate H is **DONE**: installer lifecycle proof captured (VS-0003 DONE).
- Toolchain outputs:
  - Gate C publish folder: `.buildlogs\x64\Release\gatec-publish\`
  - Installer builder: `installer/build-installer.ps1` (Inno/WiX)

## What you do next (ordered)

### 1) Harden engine dependency onboarding (quality + functions focus)

- [x] Provide a one-liner (script or doc) that installs the pinned engine stack so XTTS loads by default:
  - **Production one-liner**: `powershell -NoProfile -Command '& { $log=Join-Path ".\.buildlogs" ("engine-deps-install-" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + $PID + ".log"); New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null; & .\scripts\install-engine-deps.ps1 -VenvDir venv -Profile xtts 2>&1 | Tee-Object -FilePath $log; Write-Host ("LOG_PATH=" + $log) }'`
  - **Usage**: Run from repo root. Creates timestamped log in `.buildlogs/` with full install output and key package versions.
- [x] Clean venv run captured with key package versions logged.
  - **Run**: `.\scripts\install-engine-deps.ps1 -VenvDir venv_xtts_clean_verify6 -Profile xtts`
  - **Log**: `.buildlogs\engine-deps-install-20260115-213116-32948.log`
- **Success**: Engine Engineer can run baseline proof without "Coqui TTS not installed" errors.

### 2) Keep the build/publish/installer lane deterministic

- [ ] Ensure `installer/build-installer.ps1` and publish scripts remain stable (no regressions from Gate H); fix only if drift is detected.
- [ ] Keep Inno Setup discovery working (PATH or `-InnoSetupPath`).
- **Success**: a clean machine can still produce installer EXEs without edits.

### 3) CI lane coverage (build + publish + installer sanity)

- [ ] Add/adjust CI checks to run:
  - RuleGuard
  - `dotnet publish` (Gate C artifact)
  - Basic installer build validation (at least script + prereq detection)
- **Success**: CI fails fast when the ship lane regresses.

### 4) Toolchain pinning guardrails (ongoing)

- [ ] Keep `.NET SDK` + `Windows App SDK` pins stable; do not upgrade without proof + doc updates.

## Hand-off expectation

When you finish, Release Engineer should be able to:

- Build installers without surprises and stay unblocked; Engine Engineer should be unblocked on quality proof by having a ready engine stack.
