# System Architect — Next task list

## Mission alignment

Keep the project on the **architecture blueprint rails**: compatibility, boundaries, and gate discipline so voice cloning upgrades don’t break the system.

## Architecture references in force

- `C:\Users\Tyler\Downloads\VoiceStudio – Architecture Blueprint.pdf`
- `C:\Users\Tyler\Downloads\VoiceStudio Project Architecture and Dependency Guide.pdf`

## What you do next (ordered)

### 0) Gate status sanity (today)

- Gate C is **DONE** (VS-0012 DONE; UI smoke PASS).
- Gate H is **DONE** (VS-0003 lifecycle proof captured).

### 1) Align governance artifacts (ledger ↔ plan ↔ handoffs)

- [ ] Ensure `Recovery Plan/QUALITY_LEDGER.md` reflects the active “quality + functions” tranche and owners.
- [ ] Ensure `PROJECT_BREAKDOWN_AND_EXECUTION_PLAN.md` remains consistent with the ledger (ledger wins).
- **Success**: no “missing work items” exist outside the ledger; roles can navigate by IDs.

### 2) Lock the “platform invariants” (compatibility guardrails)

- [ ] Reconfirm and document these as non-negotiables:
  - Local-first/offline-first
  - Gate C artifact lane: unpackaged apphost EXE only (installer distribution; MSIX not used)
  - Model root default: `E:\VoiceStudio\models` via `VOICESTUDIO_MODELS_PATH`
- **Success**: every role’s tasks reference the same invariants.

### 3) Resolve compatibility drift (docs vs pinned reality)

- [ ] Reconcile `docs/design/COMPATIBILITY_MATRIX.md` with actual pinned versions:
  - `Directory.Build.props` (WinAppSDK / Windows SDK build tools / toolchain pins)
  - `requirements_engines.txt` + `version_lock.json` (engine stack pins)
- **Success**: every role follows **one** compatibility source-of-truth (no more “docs say X, repo pins Y” drift).

### 3) Contract boundary checks

- [ ] Validate frontend/backend contract shapes remain stable (snake_case, endpoints, artifact URLs).
- [ ] If changes are needed, require a gate-safe migration plan and update `shared/` schemas as appropriate.
- **Success**: no silent breaking changes across the network boundary.

### 4) ADR hygiene (only when architecture changes)

- [ ] If the packaging lane changes (requires explicit Overseer approval) or model storage strategy changes, record an ADR and update the blueprint alignment notes.
- **Success**: future contributors can understand “why” decisions were made.
