# Overseer — Next task list

## Mission alignment

Run the gated recovery model: every task is reproducible, evidence-backed, and owned by the correct role so the project reaches completion without drift.

## What you do next (ordered)

### 1) Ledger hygiene (single source of truth)

- [ ] Ensure every active work item exists in `Recovery Plan/QUALITY_LEDGER.md` with:
  - repro steps
  - proof run requirement
  - owner + gate + severity
- [ ] Reconcile missing IDs referenced in handoffs (e.g., VS-0020) into the ledger open index.
- **Success**: “If it isn’t in this ledger, it doesn’t exist” is actually true again.

### 2) Role clarity (team alignment)

- [ ] Keep `docs/governance/overseer/role_tasks/` current:
  - each role has a “next actions” list
  - each list references the same invariants (artifact type, model root, offline-first)
- **Success**: no role is blocked on “what do I do next?”

### 3) Evidence packets (handoff discipline)

- [ ] Require that each change set adds/updates a handoff file under `docs/governance/overseer/handoffs/VS-<id>.md`.
- **Success**: every fix can be replayed by another engineer without guesswork.

### 4) Gate progression checkpoints

- [ ] Gate C: confirm deterministic launch proof is captured (VS-0012 + VS-0020 implications).
- [ ] Gate H: once Gate C is green, move installer proofs forward (VS-0003).
- **Success**: gates close in order; voice cloning upgrades land on a stable base.

