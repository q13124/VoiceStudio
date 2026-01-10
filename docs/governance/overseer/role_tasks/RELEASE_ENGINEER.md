# Release Engineer — Next task list

## Mission alignment

Ship a **local-first** desktop app safely: install → launch → upgrade → rollback → uninstall, with crash bundles and clear prerequisites.

## Current state snapshot (from evidence)

- Gate C artifact default: **unpackaged self-contained apphost EXE**
- Publish/binlogs: see `docs/governance/overseer/handoffs/VS-0020.md`
- Model root default: `E:\VoiceStudio\models` (set by `backend/api/main.py` unless overridden)
- Known open packaging lane: `VS-0003` (installer verification) is downstream of Gate C stability.

## What you do next (ordered)

### 1) Gate C proof run (launch stability)

- [ ] Run the Gate C launch method on the current Release artifact:
  - Use the published apphost output under `.buildlogs/` (see VS-0020 handoff)
  - Verify the process stays running and the main window becomes visible
  - If it fails: capture exit code + Windows Application log events + crash bundle (if available)
- **Success**: you can attach proof (commands + outcome) that satisfies Gate C.

### 2) Resolve VS-0012 (WinUI activation / class not registered) if it still reproduces

- [ ] Reproduce VS-0012 using the exact launch method recorded in the ledger.
- [ ] If the Gate C artifact is unpackaged and still hits WinUI activation issues:
  - Work with Build & Tooling Engineer to make prerequisites deterministic (runtime/bootstrap)
  - If needed, switch Gate C artifact to MSIX (only if unpackaged cannot meet activation constraints)
- **Success**: app launches reliably on the chosen Gate C artifact; ledger updated with proof.

### 3) Gate H packaging proofs (VS-0003)

- [ ] Once Gate C is green, run the installer build and verification workflow:
  - Build installer (Inno/WiX scripts) using the Release artifact
  - Test on clean Windows profiles (VMs): install → launch → upgrade → rollback → uninstall
  - Confirm the install includes/prereqs:
    - .NET runtime approach (self-contained already preferred)
    - `E:\VoiceStudio\models` expectations (or allow configuring via env/config in installer)
    - ffmpeg/native tools as required by backend engines
- **Success**: VS-0003 evidence packet with logs + commands + outcomes; installer can be built and verified end-to-end.

## Handoff expectation

When you finish, Overseer should be able to mark Gate C and Gate H deliverables DONE with evidence:

- Gate C proof: launch stable
- Gate H proof: installer lifecycle stable
