# Role Coordination & Conflict Prevention

**Last updated:** 2025-01-28  
**Owner:** Overseer  
**Purpose:** Explain how roles coordinate and how conflicts are prevented/resolved

---

## 🛡️ How Conflicts Are Prevented

### 1. Single Owner Per Ledger Entry

**Golden Rule:** Each ledger entry (`VS-XXXX`) has exactly **ONE Owner Role**.

**Enforcement:**
- Ledger format requires explicit `Owner Role` field
- Overseer blocks duplicate ownership claims
- Ledger is the single source of truth for ownership

**Example from ledger:**
```
| VS-0012 | TRIAGE | S0 Blocker | C | Release Engineer | BOOT,PACKAGING | App crash on startup |
```
→ Only **Release Engineer** owns VS-0012. Other roles must coordinate.

**What this prevents:**
- ✅ Two roles working on the same issue without coordination
- ✅ Duplicate work on the same bug/feature
- ✅ Conflicting fixes to the same problem

---

### 2. Clear Role Boundaries (What Each Role Owns)

**Each role has explicit ownership:**

| Role | Owns | Must NOT Change |
|------|------|-----------------|
| **Engine Engineer** | `app/core/engines/*`, `engines/*`, model lifecycle | UI, storage schemas without coordination |
| **UI Engineer** | `src/VoiceStudio.App/*`, XAML, viewmodels | Core storage/runtime contracts without architect signoff |
| **Core Platform Engineer** | `app/core/runtime/*`, `app/core/storage/*` | UI design rules, engine model code without coordination |
| **Build & Tooling Engineer** | MSBuild, CI, RuleGuard | App behavior unless tooling requires it |
| **Release Engineer** | Installer, packaging, upgrades | Core behavior unless affects packaging |
| **System Architect** | Module boundaries, contracts, ADRs | UI details, engine internals unless coordinated |

**What this prevents:**
- ✅ Engine Engineer modifying UI code directly
- ✅ UI Engineer changing storage schemas without approval
- ✅ Build Engineer changing app behavior arbitrarily

---

### 3. Cross-Role Handshake Rules

**Rule:** If a role needs to touch another role's boundary, they MUST:

1. **Open/update an ADR** (if architectural change), OR
2. **Add a ledger entry** (if defect), AND
3. **Request review from that role**

**Example Scenario:**
- Engine Engineer needs to add new model path configuration
- Model paths are stored in `app/core/storage/` (Core Platform owns)
- Engine Engineer must:
  1. Create ledger entry: `VS-XXXX` with Owner: Engine Engineer
  2. Add to ledger: "Requires Core Platform review for storage schema change"
  3. Request review from Core Platform Engineer
  4. Core Platform Engineer reviews and approves/rejects

**What this prevents:**
- ✅ Uncoordinated changes across boundaries
- ✅ Breaking changes without proper review
- ✅ Surprise dependencies between roles

---

### 4. Task Slicing Rules (One Primary Boundary)

**Golden Rule:** Each task touches **ONE primary boundary** (UI, Core, Engine, Build, Release).

**Enforcement:**
- Tasks are "well-sliced" if they touch one primary boundary
- Overseer rejects tasks that mix boundaries without coordination
- Handoff records document boundary changes

**What this prevents:**
- ✅ Tasks that require multiple roles working simultaneously
- ✅ Ambiguous ownership for multi-boundary changes
- ✅ Coordination failures on complex changes

---

### 5. Overseer Blocking Authority

**Overseer blocks:**
- Changes without ledger ID + proof run
- Cross-boundary edits without required reviewer
- "Fixes" without regression prevention
- Moving to next gate until current gate has objective green proof

**What this prevents:**
- ✅ Parallel work on conflicting changes
- ✅ Work without proper evidence/coordination
- ✅ Gate progression with unresolved conflicts

---

## ⚖️ Conflict Resolution (When Conflicts DO Occur)

### Conflict Resolution Hierarchy

If roles conflict, **one role wins based on domain authority:**

| Domain | Winning Role |
|--------|--------------|
| **Boundaries/Contracts** | System Architect |
| **Determinism/Enforcement** | Build & Tooling Engineer |
| **UX + Desktop Correctness** | UI Engineer |
| **Runtime + Storage Correctness** | Core Platform Engineer |
| **Audio/Model Correctness** | Engine Engineer |
| **Installer/Upgrade Safety** | Release Engineer |
| **Gates + Evidence** | Overseer (always) |

**Example Scenario:**
- Engine Engineer wants to add new model path format
- Core Platform Engineer says it breaks storage migration
- **Core Platform wins** on storage correctness
- Solution: Engine Engineer adapts to storage schema, or Core Platform extends schema with approval

**Fallback:** If unclear, log a `RULES` entry in the ledger and decide via ADR.

---

## ⚠️ Potential Gaps & Mitigations

### Gap 1: Git Conflicts (Same File, Different Boundaries)

**Scenario:** Engine Engineer modifies `backend/api/routes/voice.py` for engine defaults, while UI Engineer modifies same file for API response format.

**Mitigation:**
- **Ledger coordination:** Both ledger entries must reference the same file
- **Review requirement:** Changes must be reviewed by affected role
- **Sequential work:** If conflicts are likely, Overseer blocks one until the other completes

**Best Practice:** Communicate in ledger comments if you're touching a shared file.

---

### Gap 2: Parallel Work on Related Issues

**Scenario:** VS-0012 (boot crash) is owned by Release Engineer, but it affects engine initialization that Engine Engineer needs to fix.

**Mitigation:**
- **Dependency tracking:** Ledger entries can be `BLOCKED` with dependency: `VS-XXXX`
- **Coordinated handoff:** Release Engineer fixes boot, then hands off to Engine Engineer for engine init fix
- **Separate ledger entries:** Engine init becomes separate `VS-YYYY` with dependency on VS-0012

**Example:**
```
VS-0012: Release Engineer fixes boot crash → DONE
VS-0013: Engine Engineer fixes engine init (depends on VS-0012) → IN_PROGRESS
```

---

### Gap 3: Same File, Same Boundary (No Conflict Resolution)

**Scenario:** Two Engine Engineers both want to modify `xtts_engine.py` simultaneously.

**Mitigation:**
- **Ledger ownership:** Only ONE ledger entry per change, ONE owner per entry
- **Sequential work:** Second Engineer waits or creates separate ledger entry for different change
- **Git merge:** Standard Git conflict resolution if changes are independent

**Best Practice:** Check ledger for active work on files you're modifying.

---

## 📋 Coordination Checklist (Before Starting Work)

**Before you start working on ANY change:**

1. ✅ **Check the ledger** (`Recovery Plan/QUALITY_LEDGER.md`) for:
   - Existing entries on the same issue/file
   - Active `IN_PROGRESS` work on related files
   - `BLOCKED` entries that might affect your work

2. ✅ **Check role boundaries** (`Recovery Plan/ROLE_SYSTEM_AND_OVERSEER_PROTOCOL.md`):
   - Are you modifying files in your role's domain?
   - If crossing boundaries, do you need review?

3. ✅ **Create/claim ledger entry**:
   - One entry per change
   - Set `Owner Role` to your role
   - Set `State` to `TRIAGE` or `IN_PROGRESS`

4. ✅ **Declare dependencies**:
   - If your work depends on another ledger entry, set `State` to `BLOCKED`
   - Add dependency reference in ledger entry

5. ✅ **Check handoffs** (`docs/governance/overseer/handoffs/`):
   - See if related work has been completed
   - Review proof runs for similar issues

---

## 🚦 Red Flags (Stop and Coordinate)

**STOP if you see:**

- ❌ Another ledger entry (`VS-XXXX`) already addresses the same issue
- ❌ File you're modifying has active `IN_PROGRESS` work by another role
- ❌ Your change crosses role boundaries without review
- ❌ Your change requires multiple roles working simultaneously
- ❌ Overseer has blocked related work

**Action:** Coordinate via ledger comments, or create `RULES` entry for Overseer decision.

---

## 📚 References

- **Role boundaries:** `Recovery Plan/ROLE_SYSTEM_AND_OVERSEER_PROTOCOL.md`
- **Conflict resolution:** `Recovery Plan/ROLE_SYSTEM_AND_OVERSEER_PROTOCOL.md` (section: "When roles conflict")
- **Ledger ownership:** `Recovery Plan/QUALITY_LEDGER.md` (format: Owner Role field)
- **Overseer authority:** `docs/governance/overseer/roles/OVERSEER.md`

---

## 🎯 Summary

**Conflicts are prevented by:**
1. ✅ Single owner per ledger entry (enforced by format)
2. ✅ Clear role boundaries (what each role owns)
3. ✅ Cross-role handshake rules (review requirement)
4. ✅ Task slicing (one primary boundary per task)
5. ✅ Overseer blocking (gates + evidence enforcement)

**Conflicts are resolved by:**
1. ✅ Domain authority hierarchy (who wins on what)
2. ✅ Dependency tracking (BLOCKED state)
3. ✅ Sequential handoffs (coordinated work)
4. ✅ Fallback: RULES entry + ADR decision

**Bottom line:** The system is designed to prevent conflicts through clear ownership and boundaries. If conflicts do occur, there's a clear resolution hierarchy. The Overseer acts as the final authority on gates and evidence, ensuring coordination even when conflicts arise.
