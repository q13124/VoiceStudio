# Overseer — Next task list

## Mission alignment

Run the gated recovery model: every task is reproducible, evidence-backed, and owned by the correct role so the project reaches completion without drift.

## Current gate status (today)

- **Gate C**: DONE (VS-0012 is DONE; UI smoke exits 0 with 0 binding failures)
- **Gate H**: DONE (VS-0003 lifecycle proof COMPLETE; installer lane proven)

## What you do next (ordered)

### 1) Launch the “quality + functions” tranche (post Gate H)

- [ ] Require **Engine Engineer** to deliver a passing baseline voice workflow proof (XTTS synth → whisper.cpp transcribe) with non-null `audio_id`, metrics, and proof artifacts.
- [ ] Require **Build & Tooling Engineer** to bake the engine dependency install command (coqui-tts, etc.) into onboarding/setup so XTTS loads by default.
- [ ] Require **Release Engineer** to log the passing proof into the ledger + handoff (attach proof_runs path and metrics).
- **Success**: `Recovery Plan/QUALITY_LEDGER.md` contains the baseline quality entry with evidence and owners; engine stack loads cleanly on a fresh machine.

### 2) Ledger hygiene (single source of truth)

- [ ] Ensure every non-DONE item has a **full ledger body entry** (repro + proof + owner + artifacts).
- [ ] Reconcile handoffs that claim work is complete but are not reflected in the ledger.
- **Success**: the ledger index and body are consistent and up to date.

### 3) Role clarity + conflict prevention

- [ ] Keep `docs/governance/overseer/role_tasks/` current and aligned to gate order.
- [ ] Enforce role boundaries: no cross-role edits without coordination.
- **Success**: no one is blocked on “what do I do next?” and work lands without drift.

### 4) Post-Gate-H sequencing

- [ ] Keep the “quality + functions” tranche expressed as explicit ledger items with proof runs; add/assign new IDs only when evidence is defined.
