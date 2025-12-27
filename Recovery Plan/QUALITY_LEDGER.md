# Quality Ledger — Single Source of Truth

Last updated: 2025-12-26  
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

| ID | State | Sev | Gate | Owner Role | Category | Title |
|---|---|---|---|---|---|---|
| (add rows here) |  |  |  |  |  |  |

---

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
- 

**Environment**
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
- 

**Actual**
- 

**Evidence**
- Log excerpt (keep short):
- Screenshot path (if any):
- Crash bundle path (if any):

**Suspected root cause**
- 

**Fix plan (small tasks)**
- [ ] Task 1 (single success condition)
- [ ] Task 2
- [ ] Task 3

**Change set**
- Files changed:
- Notes:

**Proof run (required)**
- Commands executed:
  - 
- Result:
  - 

**Regression / prevention**
- Tests added/updated:
- RuleGuard rule updated (if relevant):
- Any new ADR link (if architecture changed):

**Links**
- Related commits:
- Related entries:
- ADRs:

---
