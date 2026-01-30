# Build Quality Stream Status (Master Plan Phase 4)

**Date:** 2026-01-29  
**Owner:** Role 2 (Build & Tooling)  
**Traceability:** Optional & Available Tasks Master Plan — Phase 4 Build/Tooling Stream; [OPTIONAL_TASK_INVENTORY](../../governance/OPTIONAL_TASK_INVENTORY.md) §3.4; [TECH_DEBT_REGISTER](../../governance/TECH_DEBT_REGISTER.md) TD-002, TD-007

This document records the **reduce warnings and remove Release suppressions** stream status for the optional tasks master plan.

---

## 1. Current State

| Item | Status | Evidence |
|------|--------|----------|
| Release build | **Unblocked** | TASK-0015 Complete — [VoiceStudio.App.csproj](../../../src/VoiceStudio.App/VoiceStudio.App.csproj): `NoWarn` (CS0436, CS0618), `TreatWarningsAsErrors=false` for Release; Gate C UI smoke PASS |
| Gate C publish | **PASS** | Publish 0 errors; ~4990 warnings (TD-007); UI smoke exit 0 |
| App.Tests Release | **Fails** | Full-solution Release with App.Tests still fails; not required for Gate C |
| Warning count | **~4990** | Mostly C# language version, nullability (CS8618), obsolete (CS0618); zero errors |

---

## 2. Release Suppressions (TD-002)

| Suppression | Location | Reason | Removal Blocked By |
|-------------|----------|--------|--------------------|
| NoWarn CS0436 | VoiceStudio.App.csproj (Release) | Type conflicts (generated/duplicate types) | Resolve type conflicts |
| NoWarn CS0618 | VoiceStudio.App.csproj (Release) | Obsolete API usage (AppServices, BaseViewModel) | TD-004 (ViewModel DI migration) |
| TreatWarningsAsErrors false | VoiceStudio.App.csproj (Release) | Prevents Release from failing on warnings above | Same as above |

**Strategy:** Do **not** remove suppressions until (a) TD-004 ViewModel DI migration is complete, and (b) CS0436 type conflicts are resolved. Then revert NoWarn and TreatWarningsAsErrors in phases; fix App.Tests Release separately. See [TECH_DEBT_REGISTER](../../governance/TECH_DEBT_REGISTER.md) TD-002, TD-004.

---

## 3. Warning Reduction (TD-007)

| Action | Effort | Owner | Target |
|--------|--------|-------|--------|
| Incremental reduction | Code quality sprints | Role 2/3 | Phase 6+ (optional) |
| CS0618 migration | 16–24h (obsolete usage) | Role 3 | Per viewmodel_di_refactor.md |
| CS8618 migration | 4–8h (nullable init) | Role 3 | Low priority |
| Accept baseline | Warnings do not block | — | Current state acceptable |

**Conclusion:** Warning reduction is optional; stream deliverable is status and strategy, not removal of suppressions (which would break Release until TD-004 is done).

---

## 4. Stream Completion Criteria (Plan Phase 4)

- [x] Current build quality state documented (Release unblocked; suppressions and rationale captured).
- [x] Strategy for removing Release suppressions documented (blocked by TD-004; revert in phases when safe).
- [x] Warning reduction approach documented (incremental sprints or accept baseline; TD-007).

---

## 5. References

- [TECH_DEBT_REGISTER](../../governance/TECH_DEBT_REGISTER.md) TD-002, TD-004, TD-007
- [TASK-0015](../../tasks/TASK-0015.md) — Gate C Release (unblocked)
- [viewmodel_di_refactor.md](../../design/viewmodel_di_refactor.md)
