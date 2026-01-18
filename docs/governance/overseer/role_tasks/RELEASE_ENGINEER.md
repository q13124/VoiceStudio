# Release Engineer — Next task list

## Mission alignment

Ship a **local-first** desktop app safely: install → launch → upgrade → rollback → uninstall, with crash bundles and clear prerequisites.

## Current state snapshot (from evidence)

- ✅ Gate C is **DONE** (VS-0012 UI smoke PASS, exit code 0, 0 binding failures).
- ✅ Gate H is **DONE** (VS-0003 installer lifecycle proof captured; installer lane proven).
- Build inputs (for future releases):
  - Gate C publish artifact: `.buildlogs\x64\Release\gatec-publish\VoiceStudio.App.exe`
  - Installer build entrypoint: `installer/build-installer.ps1`
  - Lifecycle test harness (VM): `installer/test-installer-lifecycle.ps1`

## What you do next (ordered)

### 1) Archive Gate H + prep for quality proof

- [x] Ensure the final Gate H artifacts (installer EXEs, lifecycle logs) remain referenced in `handoffs/VS-0003.md` and are hashable/retrievable.
  - Evidence: `docs/governance/overseer/handoffs/VS-0003.md` includes SHA256 for both installers and lifecycle log.
- [ ] Keep the installer lane ready for distribution (no further action unless it regresses).

### 2) When Engine Engineer produces the “quality + functions” baseline proof

- [x] Pull the new `proof_runs/...` directory and archive it in the handoff (attach the path, audio + metrics).
  - **Proof dir**: `proof_runs\\baseline_workflow_20260116-091722_prosody\\`
  - **Handoff**: `docs/governance/overseer/handoffs/VS-0031.md`
- [x] Update `Recovery Plan/QUALITY_LEDGER.md` with the baseline quality entry and artifacts.
- [x] Copy the proof artifacts into `.buildlogs\proof_runs` for release packaging.
  - Evidence: `.buildlogs\proof_runs\baseline_workflow_20260116-091722_prosody`

## Handoff expectation

Overseer should have: Gate H proof retained, plus the baseline quality proof logged and archived for release packaging.
