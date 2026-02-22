# Role System & [OVERSEER] Protocol (VoiceStudio)

This document is the practical runbook for **how work is allowed to happen** in this repo.
It is intentionally strict: the goal is to prevent drift, thrash, and “it kind-of works” engineering.

> If a rule here conflicts with a one-off request, the [OVERSEER] must log an exception in `QUALITY_LEDGER.md`
> (category: RULES) explaining why, and how we’ll revert to standard.

---

## The [OVERSEER] mandate

### What [OVERSEER] blocks (always)
- Building while Gate A/B is red.
- Feature PRs without a ledger ID + proof run.
- Architecture changes without an ADR.
- Cross-boundary edits without the required reviewer.
- “Fixes” that don’t include a regression prevention step.

### The [OVERSEER] loop
1) Create or update a ledger entry  
2) Reproduce on a clean-ish environment  
3) Implement the smallest fix that can be proven  
4) Run proof commands  
5) Add prevention (tests/RuleGuard/ADR)  
6) Close the entry + update gate status

---

## Roles & rules

(These are identical to the Plan’s Role section, duplicated here for quick reference.)

## 2) Roles (by responsibility)

These roles describe **responsibility boundaries**; one person can cover multiple roles.  
Every change must have **one primary Owner role** and **one Reviewer role** (can be the same person only for trivial doc-only changes).

### 2.1 The [OVERSEER] function (governance + drift prevention)

**Purpose:** Keep the project “by the book” — enforce architecture boundaries, rule compliance, and quality gates *before* features move forward.

**Non‑negotiable rules the Overseer enforces**
- **Functionality before features:** No “advanced” work while build/boot gates are red.
- **Single source of truth:** all bugs/issues go into `QUALITY_LEDGER.md` first (or at the same time), with a reproducible trigger.
- **Evidence-based progress:** each fix requires a *Proof Run* (commands + output summary).
- **No architectural drift:** dependency direction stays one-way; stable contracts only change via ADR.
- **Native desktop only:** no web UI, no “must-use cloud” dependencies; offline-first default.

**Overseer responsibilities (checklist)**
1. **Start-of-work sanity**
   - Confirm the current active gate (A→H) and which items are blocking it.
   - Confirm RuleGuard policy exists and is enabled in the build/CI.
2. **Intake**
   - Ensure any new bug/error is logged in `QUALITY_LEDGER.md` with Severity + Repro + Expected/Actual.
3. **Task slicing**
   - Break work into **≤ 1 day** tasks with a single success condition each.
   - Reject tasks that mix “fix build” + “add features” in the same change set.
4. **Gate enforcement**
   - Block moving to the next gate until the current gate has objective green proof.
5. **Merge discipline**
   - Require: ledger ID, passing RuleGuard, passing tests, and a short upgrade note.
6. **Release discipline**
   - Require: installer verify/repair, rollback note, crash-bundle export path verified.

**Overseer cadence**
- Works in cycles: **Log → Repro → Fix → Proof → Close**.
- Produces `[OVERSEER]` updates at the end of each cycle:
  - Gate status (A–H), top blockers, what changed, and next 1–3 actions.

---

### 2.2 Role playbooks (each role has its own “do / don’t”)

#### Role 0 — Overseer (Quality + Governance)
- **Owns:** gating, drift prevention, quality ledger hygiene, rule compliance.
- **May change:** docs, RuleGuard policy, CI gating configuration.
- **Must not change:** engine logic/UI logic unless acting as a temporary Owner role.
- **Definition of Done:** gates updated, ledger updated, RuleGuard enforced, proof attached.

#### Role 1 — System Architect
- **Owns:** module boundaries, dependency direction, public contracts, ADRs.
- **May change:** `core/api/*`, architectural interfaces, folder layout, plugin contracts (with ADR).
- **Must not change:** UI details or engine internals unless coordinated.
- **Required artifacts:**
  - ADR for any breaking change or new subsystem.
  - Contract tests updated when interfaces change.
- **DoD:** dependency graph unchanged or updated intentionally; contract tests green.

#### Role 2 — Build & Tooling Engineer
- **Owns:** deterministic builds, local setup, CI pipelines, RuleGuard integration.
- **May change:** MSBuild/solution settings, analyzers, `.editorconfig`, scripts, CI YAML.
- **Must not change:** app behavior unless tooling requires it.
- **Required artifacts:**
  - “Clean machine” build instructions (one command).
  - CI job that runs RuleGuard + tests + packaging smoke.
- **DoD:** `git clean -xfd` → build succeeds; CI green; RuleGuard green.

#### Role 3 — UI Engineer (Native Desktop)
- **Owns:** WinUI navigation, MVVM binding correctness, visual fidelity, accessibility, performance.
- **May change:** `ui/*`, XAML, viewmodels, design tokens/theme resources.
- **Must not change:** core storage/runtime contracts without architect signoff.
- **Required artifacts:**
  - UI smoke: app boots, navigation works, no binding errors in output.
  - Performance budget respected (no blocking calls on UI thread).
- **DoD:** UI gate passes; no XAML compiler errors; no runtime binding spam.

#### Role 4 — Core Platform Engineer
- **Owns:** orchestration, job runtime, storage, plugin host, domain models.
- **May change:** `core/runtime/*`, `core/storage/*`, `core/plugins/*`, serialization, migrations.
- **Must not change:** UI design rules or engine model code unless coordinated.
- **Required artifacts:**
  - Storage migrations idempotent, versioned, and tested.
  - Runtime job cancellation + error propagation proven.
- **DoD:** storage + runtime tests green; crash-safe writes; plugin host loads sample plugins.

#### Role 5 — Engine Engineer (TTS/Cloning/Audio)
- **Owns:** engine adapters, model lifecycle, GPU/CPU execution, audio IO consistency.
- **May change:** `engines/*`, adapter layer, DSP pipeline nodes, model caching.
- **Must not change:** UI or storage schemas without coordination.
- **Required artifacts:**
  - Golden audio test(s) for each engine integration.
  - Deterministic inference settings (seed/config) where possible.
- **DoD:** engine smoke works; latency/VRAM within budget; errors mapped to user-readable faults.

#### Role 6 — Release Engineer
- **Owns:** packaging, installer, upgrades, rollback, crash bundle export.
- **May change:** installer scripts, app manifest, signing pipeline (if any), versioning.
- **Must not change:** core behavior unless it affects packaging.
- **Required artifacts:**
  - Verify/Repair mode, uninstall clean, data folder preserved.
  - Upgrade/rollback notes and migration steps.
- **DoD:** installed app runs; upgrade works; rollback works; crash bundle exports.

---

### 2.3 Cross-role handshake rules (prevents “everyone edits everything”)

**Any change must declare:**
- Owner role
- Reviewer role
- Gate impacted (A–H)
- Ledger ID(s)

**Role escalation rule:**  
If a role needs to touch another role’s boundary, it must:
1) open/update an ADR (if architectural), or  
2) add a ledger entry (if defect), and  
3) request review from that role.

**What can ship without review?**
- Docs-only changes that do not alter behavior (still require ledger if addressing a defect).
- Formatting and comment changes (no functional diffs).


---

## Required metadata for every PR / change set

At minimum, include this at the top of the PR description (or commit message if solo):

- Ledger: VS-XXXX
- Gate: (A–H)
- Owner role:
- Reviewer role:
- Proof run commands:
- Result summary (1–3 lines)

---

## How we slice tasks (non-negotiable)

A task is “well-sliced” if:
- It has **one** success condition.
- It can be proven with **one** proof run.
- It does not mix bugfix + new features.
- It touches **one** primary boundary (UI, Core, Engine, Build, Release).

If it can’t be proven, it’s not a task yet — it’s a hypothesis.

---

## When roles conflict

- Architect wins on **boundaries/contracts**.
- Build wins on **determinism/enforcement**.
- UI wins on **UX + desktop correctness**.
- Core wins on **runtime + storage correctness**.
- Engine wins on **audio/model correctness**.
- Release wins on **installer/upgrade safety**.
- [OVERSEER] wins on **gates + evidence**.

If still unclear: log a RULES entry in the ledger and decide via ADR.
