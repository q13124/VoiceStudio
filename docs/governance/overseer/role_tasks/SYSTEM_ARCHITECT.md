# System Architect — Next task list

## Mission alignment

Keep the project on the **architecture blueprint rails**: compatibility, boundaries, and gate discipline so voice cloning upgrades don’t break the system.

## Architecture references in force

- `C:\Users\Tyler\Downloads\VoiceStudio – Architecture Blueprint.pdf`
- `C:\Users\Tyler\Downloads\VoiceStudio Project Architecture and Dependency Guide.pdf`

## What you do next (ordered)

### 1) Align governance artifacts (ledger ↔ plan ↔ handoffs)

- [ ] Ensure `Recovery Plan/QUALITY_LEDGER.md` reflects the active work items and owners (including VS-0017/VS-0018/VS-0020 from handoffs).
- [ ] Ensure `PROJECT_BREAKDOWN_AND_EXECUTION_PLAN.md` remains consistent with the ledger (ledger wins).
- **Success**: no “missing work items” exist outside the ledger; roles can navigate by IDs.

### 2) Lock the “platform invariants” (compatibility guardrails)

- [ ] Reconfirm and document these as non-negotiables:
  - Local-first/offline-first
  - Gate C artifact default: unpackaged apphost EXE (MSIX optional)
  - Model root default: `E:\VoiceStudio\models` via `VOICESTUDIO_MODELS_PATH`
- **Success**: every role’s tasks reference the same invariants.

### 3) Contract boundary checks

- [ ] Validate frontend/backend contract shapes remain stable (snake_case, endpoints, artifact URLs).
- [ ] If changes are needed, require a gate-safe migration plan and update `shared/` schemas as appropriate.
- **Success**: no silent breaking changes across the network boundary.

### 4) ADR hygiene (only when architecture changes)

- [ ] If the Gate C artifact choice changes (unpackaged ↔ MSIX) or model storage strategy changes, record an ADR and update the blueprint alignment notes.
- **Success**: future contributors can understand “why” decisions were made.

