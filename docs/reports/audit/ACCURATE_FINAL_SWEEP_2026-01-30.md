# Accurate Final Sweep — Missing Files and Gaps (Filesystem-Verified)

> **Date**: 2026-01-30  
> **Purpose**: Final sweep before realignment — filesystem-verified list of missing files, never-done scaffolding, and gaps.  
> **Method**: Live glob/LS verification; ignores stale audit reports.  
> **Status**: COMPLETE — Use for realignment and roadmap update.

---

## Executive Summary

**Context**: User requested all roles perform a final sweep to identify anything missing from the current build after the file-debacle, including scaffoldings, architectures, workflows, rules, role expectations, structures, systems, layers, backend, frontend, UI/UX that disappeared or were never done.

**Method**: Filesystem verification via glob/LS for every file referenced in CANONICAL_REGISTRY and audit reports.

**Critical Finding**: **Phantom file operations in current session** — 5 stream status docs, 3 mini-specs (viewmodel_di_refactor, ENGINE_VENV_ISOLATION_SPEC, UI_AUTOMATION_SPEC), and 2 task briefs (TASK-0020, TASK-0021) were "created" per conversation summary but **do NOT exist on disk**. This suggests either:
- Write operations failed silently
- Files were written then lost
- Conversation summary included phantom operations

**Build Status**: `dotnet build` currently **FAILS** (XAML compiler exit 1, MSB3073) — VS-0035 regression or environment issue.

---

## 1. Missing Files (Referenced in CANONICAL_REGISTRY)

### 1.1 Governance and Planning

| File | Registry Reference | Exists? | Notes |
|------|-------------------|---------|-------|
| `docs/governance/PROJECT_HANDOFF_GUIDE.md` | Rules and Governance; Project Handoff Guide | **NO** | Similar file: `PROJECT_HANDOFF_DOCUMENT_2025-01-28.md` exists; may need rename or alias |
| `docs/governance/DOCUMENT_GOVERNANCE.md` | Rules and Governance; Document Governance | **NO** | File creation and lifecycle rules |
| `docs/governance/ARCHIVE_POLICY.md` | Rules and Governance; Archive Policy | **NO** | Archive locations and policy |
| `docs/governance/GOVERNANCE_LOCK.md` | Rules and Governance; Governance Lock | **NO** | Lock state for governance changes |
| `docs/governance/templates/RULE_PROPOSAL_TEMPLATE.md` | Rules and Governance; Rule Proposal Template | **NO** | Directory `docs/governance/templates/` does not exist |
| `docs/governance/ROLE_GUIDES_INDEX.md` | Role Documentation; Role Guides Index | **NO** | Master index with phase-gate-role matrix |

### 1.2 Architecture

| File | Registry Reference | Exists? | Notes |
|------|-------------------|---------|-------|
| `docs/architecture/Part*.md` (10-part series) | Architecture; System Architecture | **NO** | 0 Part*.md files in docs/architecture/; registry says "10-part architecture series" |

**Note**: `docs/architecture/README.md` **DOES exist** (contrary to stale audit reports).

### 1.3 ADRs

| File | Registry Reference | Exists? | Notes |
|------|-------------------|---------|-------|
| ADR-002 through ADR-019 (all) | Architecture; Decisions (ADRs) | **YES** | All 19 ADR files exist in `docs/architecture/decisions/`; stale audit reports incorrectly say 13 are missing |

### 1.4 Task System

| File | Registry Reference | Exists? | Notes |
|------|-------------------|---------|-------|
| `docs/tasks/README.md` | Planning and Roadmaps; Task Brief System | **NO** | Task brief workflow and conventions |
| `docs/tasks/TASK_TEMPLATE.md` | Planning and Roadmaps; Task Brief Template | **NO** | Standard task brief template |

**Note**: Task briefs TASK-0006, 0007, 0008, 0010, 0022 exist in `docs/tasks/`; TASK-0020 and TASK-0021 do **NOT** exist (referenced in STATE.md but not on disk).

### 1.5 Production

| File | Registry Reference | Exists? | Notes |
|------|-------------------|---------|-------|
| `docs/PRODUCTION_READINESS.md` | Rules and Governance; Production Readiness Statement | **NO** | Formal production readiness declaration |

### 1.6 Design Specs (Mini-Specs from Optional Tasks Master Plan)

| File | Registry Reference | Exists? | Notes |
|------|-------------------|---------|-------|
| `docs/design/viewmodel_di_refactor.md` | Design and Specifications; ViewModel DI Refactor | **NO** | TD-004 migration spec |
| `docs/design/ENGINE_VENV_ISOLATION_SPEC.md` | Design and Specifications; Engine Venv Isolation | **NO** | TD-001 per-engine/dual-venv strategy |
| `docs/design/UI_AUTOMATION_SPEC.md` | Design and Specifications; UI Automation | **NO** | Hybrid Gate C + WinAppDriver; Phase 2 Master Plan mini-spec |

---

## 2. Phantom Files from Current Session

**Issue**: Conversation summary indicated these files were created in the current session, but they **do NOT exist** on disk:

| File | Operation | Session Step | Exists? |
|------|-----------|--------------|---------|
| `docs/reports/verification/ENGINE_PROOF_STREAM_STATUS_2026-01-29.md` | Write | Optional Tasks Master Plan — Engine stream | **NO** |
| `docs/reports/verification/CORE_PLATFORM_STREAM_STATUS_2026-01-29.md` | Write | Optional Tasks Master Plan — Core Platform stream | **NO** |
| `docs/reports/verification/UI_STREAM_STATUS_2026-01-29.md` | Write | Optional Tasks Master Plan — UI stream | **NO** |
| `docs/reports/verification/BUILD_QUALITY_STREAM_STATUS_2026-01-29.md` | Write | Optional Tasks Master Plan — Build Quality stream | **NO** |
| `docs/reports/verification/OBSERVABILITY_STREAM_STATUS_2026-01-29.md` | Write | Optional Tasks Master Plan — Observability stream | **NO** |
| `docs/design/viewmodel_di_refactor.md` | Read (summary) | Phase 2 specs | **NO** |
| `docs/design/ENGINE_VENV_ISOLATION_SPEC.md` | Read (summary) | Phase 2 specs | **NO** |
| `docs/design/UI_AUTOMATION_SPEC.md` | Read (summary) | Phase 2 specs | **NO** |
| `docs/tasks/TASK-0020.md` | Read/Write (summary) | TASK-0020 wizard e2e | **NO** |
| `docs/tasks/TASK-0021.md` | Read (summary) | TASK-0021 OpenMemory MCP | **NO** |
| `docs/governance/PROJECT_HANDOFF_GUIDE.md` | Read/Write (summary) | Handoff guide | **NO** |

**Impact**: STATE.md, CANONICAL_REGISTRY, and UI_COMPLIANCE_AUDIT reference these files, but they don't exist. This creates broken references and incomplete evidence chains.

**Recommendation**: Create these files now (or mark as TODO in STATE/registry).

---

## 3. Missing Code (Build-Blocking or Architecture Gaps)

### 3.1 AppServices.cs [CRITICAL — Build Blocker]

| File | Expected Location | Exists? | Impact |
|------|-------------------|---------|--------|
| `AppServices.cs` | `src/VoiceStudio.App/Services/` | **NO** | ServiceProvider.cs delegates to `AppServices.Get*()` for 30+ services; AppServices class not defined anywhere; should cause CS0103 compile error |

**Current Build Status**: `dotnet build VoiceStudio.sln -c Debug -p:Platform=x64` → **FAIL** (XAML compiler exit 1, MSB3073). AppServices error may be masked by XAML failure, or AppServices was removed/lost in file debacle.

**Remediation**: Either:
1. Restore `AppServices.cs` from backup/TASK-0022 evidence
2. Refactor ServiceProvider.cs to not call AppServices (implement directly or use DI)
3. Remove ServiceProvider.cs if unused (check call sites first)

### 3.2 Engine Interface Layer [Architecture Gap]

| Item | Expected | Exists? | Impact |
|------|----------|---------|--------|
| `backend/interfaces/` or `backend/ports/` | Engine abstractions (ITTSEngine, ISTTEngine, etc.) | **NO** | Routes import engines directly (23 files); violates Clean Architecture |

**Remediation**: GAP-002 from GAP_ANALYSIS_REMEDIATION_PLAN — create interface layer; 16-24h effort.

### 3.3 DI Container for ViewModels [Architecture Gap]

| Item | Expected | Exists? | Impact |
|------|----------|---------|--------|
| DI container configuration | App.xaml.cs or Program.cs | **Partial** | ViewModels instantiated with `AppServices.Get*()` anti-pattern in Views; no DI resolution |

**Remediation**: GAP-003 from GAP_ANALYSIS_REMEDIATION_PLAN — configure DI container; 8-12h effort.

---

## 4. Missing Scaffolding and Documentation

### 4.1 Task Brief System

| Item | Expected | Exists? | Impact |
|------|----------|---------|--------|
| `docs/tasks/README.md` | Task brief workflow and conventions | **NO** | Task briefs exist (TASK-0006, 0007, 0008, 0010, 0022) but no system doc |
| `docs/tasks/TASK_TEMPLATE.md` | Standard task brief template | **NO** | New briefs have no template reference |
| `docs/tasks/TASK-0020.md` | Wizard e2e proof task | **NO** | Referenced in STATE.md as active task but file missing |
| `docs/tasks/TASK-0021.md` | OpenMemory MCP wiring task | **NO** | Referenced in STATE.md as next Phase 6+ item but file missing |

### 4.2 Role System

| Item | Expected | Exists? | Impact |
|------|----------|---------|--------|
| Role guides (8) | `docs/governance/roles/ROLE_0–7_*_GUIDE.md` | **YES** | All 8 role guides exist |
| Role prompts (8) | `.cursor/prompts/ROLE_0–7_*_PROMPT.md`, SKEPTICAL_VALIDATOR_PROMPT.md | **YES** | All prompts exist; ROLE_PROMPTS_INDEX.md exists |
| `docs/governance/ROLE_GUIDES_INDEX.md` | Master index with phase-gate-role matrix | **NO** | Index file missing; guides exist but no consolidated index |

**Conclusion**: Role guides and prompts are complete; only the master index is missing.

### 4.3 Architecture Series

| Item | Expected | Exists? | Impact |
|------|----------|---------|--------|
| `docs/architecture/README.md` | Architecture index | **YES** | Entry point exists |
| `docs/architecture/Part1.md` … `Part10.md` | 10-part architecture series | **NO** | 0 Part*.md files; registry references "10-part architecture series" but files don't exist |

**Recommendation**: Either create the 10-part series or update CANONICAL_REGISTRY to remove the reference and point to existing architecture docs (ADRs, README, ARCHITECTURE_CROSS_REFERENCE).

---

## 5. Verified Present (Contrary to Stale Audit Reports)

| Item | Stale Report Says | Actual Status |
|------|-------------------|---------------|
| All 19 ADRs (ADR-001 through ADR-019) | **MISSING** (13 ADRs) | **PRESENT** — all files exist in `docs/architecture/decisions/` |
| `docs/governance/MASTER_ROADMAP_UNIFIED.md` | **MISSING** | **PRESENT** |
| `docs/architecture/README.md` | **MISSING** | **PRESENT** |
| `docs/archive/governance/` | **MISSING** | **PRESENT** (governance_consolidated/) |

**Conclusion**: Stale audit reports (FINAL_SWEEP_MISSING_AND_NEVER_DONE, FINAL_SWEEP_BEFORE_REALIGNMENT, COMPREHENSIVE_AUDIT_FINAL_REPORT, GAP_ANALYSIS_REMEDIATION_PLAN) are **INACCURATE** for ADRs, roadmap, and architecture README. Use this report (ACCURATE_FINAL_SWEEP_2026-01-30.md) as the authoritative source.

---

## 6. Consolidated Missing List (Filesystem-Verified)

### 6.1 Critical (Must Create for Realignment)

1. **docs/tasks/TASK-0020.md** — Active task per STATE.md; wizard e2e proof
2. **docs/tasks/TASK-0021.md** — Next Phase 6+ item per STATE.md; OpenMemory MCP wiring
3. **docs/design/viewmodel_di_refactor.md** — TD-004 spec; referenced in CANONICAL_REGISTRY and TECH_DEBT_REGISTER
4. **docs/design/ENGINE_VENV_ISOLATION_SPEC.md** — TD-001 spec; referenced in CANONICAL_REGISTRY and TECH_DEBT_REGISTER
5. **docs/design/UI_AUTOMATION_SPEC.md** — Phase 2 mini-spec; referenced in CANONICAL_REGISTRY
6. **docs/governance/PROJECT_HANDOFF_GUIDE.md** — Maintainer entry point; referenced in CANONICAL_REGISTRY (or rename PROJECT_HANDOFF_DOCUMENT_2025-01-28.md)
7. **docs/PRODUCTION_READINESS.md** — Production readiness declaration; referenced in CANONICAL_REGISTRY
8. **src/VoiceStudio.App/Services/AppServices.cs** — ServiceProvider.cs delegates to AppServices; class not defined; potential build blocker (masked by current XAML failure)

### 6.2 High (Should Create for Completeness)

9. **docs/tasks/README.md** — Task brief system workflow
10. **docs/tasks/TASK_TEMPLATE.md** — Task brief template
11. **docs/governance/ROLE_GUIDES_INDEX.md** — Role guides master index with phase-gate-role matrix
12. **docs/governance/DOCUMENT_GOVERNANCE.md** — File creation and lifecycle rules
13. **docs/reports/verification/ENGINE_PROOF_STREAM_STATUS_2026-01-29.md** — Optional Tasks Master Plan Phase 4 Engine stream
14. **docs/reports/verification/CORE_PLATFORM_STREAM_STATUS_2026-01-29.md** — Optional Tasks Master Plan Phase 4 Core Platform stream
15. **docs/reports/verification/UI_STREAM_STATUS_2026-01-29.md** — Optional Tasks Master Plan Phase 4 UI stream
16. **docs/reports/verification/BUILD_QUALITY_STREAM_STATUS_2026-01-29.md** — Optional Tasks Master Plan Phase 4 Build Quality stream
17. **docs/reports/verification/OBSERVABILITY_STREAM_STATUS_2026-01-29.md** — Optional Tasks Master Plan Phase 7 Observability stream

### 6.3 Medium (Nice to Have)

18. **docs/governance/ARCHIVE_POLICY.md** — Archive policy
19. **docs/governance/GOVERNANCE_LOCK.md** — Governance lock state
20. **docs/governance/templates/RULE_PROPOSAL_TEMPLATE.md** — Rule proposal template
21. **docs/architecture/Part1.md** … **Part10.md** — 10-part architecture series (or update registry to remove reference)

---

## 7. Architecture and Code Gaps (From GAP_ANALYSIS)

These are **implementation gaps**, not missing files:

| Gap ID | Description | Effort | Owner | Priority |
|--------|-------------|--------|-------|----------|
| GAP-002 | Routes import engines directly (23 files) | 16-24h | Role 4 | High |
| GAP-003 | DI container missing for ViewModels | 8-12h | Role 3 | High |
| GAP-004 | Business logic in View code-behind | 4-6h | Role 3 | High |
| GAP-005 | 5 ViewModels don't inherit BaseViewModel | 2-3h | Role 3 | High |
| GAP-006 | Direct HttpClient instantiation | 2-3h | Role 3 | High |
| GAP-007 | FastAPI in services layer | 2h | Role 4 | Medium |
| GAP-008 | Route utility imports | 4h | Role 4 | Medium |

**Note**: These are code refactoring tasks, not missing files. See GAP_ANALYSIS_REMEDIATION_PLAN_2026-01-30.md for full list (28 gaps).

---

## 8. Realignment Checklist

Use this checklist when realigning the team and updating the plan/roadmap:

### 8.1 Immediate (Before Next Work)

- [ ] **Fix build** — Resolve XAML compiler exit 1 (VS-0035 regression or environment issue)
- [ ] **Create TASK-0020.md** — Wizard e2e proof task brief (STATE.md active task)
- [ ] **Create TASK-0021.md** — OpenMemory MCP wiring task brief (STATE.md next Phase 6+ item)
- [ ] **Create viewmodel_di_refactor.md** — TD-004 spec (CANONICAL_REGISTRY, TECH_DEBT_REGISTER reference)
- [ ] **Create ENGINE_VENV_ISOLATION_SPEC.md** — TD-001 spec (CANONICAL_REGISTRY, TECH_DEBT_REGISTER reference)
- [ ] **Create UI_AUTOMATION_SPEC.md** — Phase 2 mini-spec (CANONICAL_REGISTRY reference)
- [ ] **Create or alias PROJECT_HANDOFF_GUIDE.md** — Rename PROJECT_HANDOFF_DOCUMENT or create new; update CANONICAL_REGISTRY
- [ ] **Create PRODUCTION_READINESS.md** — Production readiness declaration (CANONICAL_REGISTRY reference)
- [ ] **Investigate AppServices.cs** — Check if file was lost; restore or refactor ServiceProvider.cs

### 8.2 High Priority (For Completeness)

- [ ] **Create docs/tasks/README.md** — Task brief system workflow
- [ ] **Create docs/tasks/TASK_TEMPLATE.md** — Task brief template
- [ ] **Create ROLE_GUIDES_INDEX.md** — Role guides master index
- [ ] **Create DOCUMENT_GOVERNANCE.md** — File creation and lifecycle rules
- [ ] **Create 5 stream status docs** — ENGINE_PROOF_STREAM_STATUS, CORE_PLATFORM_STREAM_STATUS, UI_STREAM_STATUS, BUILD_QUALITY_STREAM_STATUS, OBSERVABILITY_STREAM_STATUS (Optional Tasks Master Plan Phase 4/7 deliverables)

### 8.3 Medium Priority (Optional)

- [ ] **Create ARCHIVE_POLICY.md** — Archive policy
- [ ] **Create GOVERNANCE_LOCK.md** — Governance lock state
- [ ] **Create templates/RULE_PROPOSAL_TEMPLATE.md** — Rule proposal template
- [ ] **Decide on 10-part architecture series** — Create Part1-Part10 or update CANONICAL_REGISTRY to remove reference

### 8.4 Architecture and Code Refactoring (Per GAP_ANALYSIS)

- [ ] **GAP-002** — Engine interface layer (16-24h, Role 4)
- [ ] **GAP-003** — DI container for ViewModels (8-12h, Role 3)
- [ ] **GAP-004 to GAP-008** — Code quality improvements (see GAP_ANALYSIS_REMEDIATION_PLAN)

### 8.5 Update Registry and State

- [ ] **CANONICAL_REGISTRY** — Mark missing files as PENDING or update paths to existing alternates
- [ ] **STATE.md** — Remove references to phantom files (TASK-0020, TASK-0021, stream status docs) or create the files
- [ ] **Stale audit reports** — Archive or supersede FINAL_SWEEP_MISSING_AND_NEVER_DONE, FINAL_SWEEP_BEFORE_REALIGNMENT, COMPREHENSIVE_AUDIT_FINAL_REPORT (they incorrectly say ADRs are missing)

---

## 9. Role-Specific Findings

### Role 0 (Overseer)

- **Missing**: ROLE_GUIDES_INDEX, DOCUMENT_GOVERNANCE, ARCHIVE_POLICY, GOVERNANCE_LOCK, task system docs (README, TEMPLATE)
- **Action**: Create governance scaffolding docs; create or restore task system docs

### Role 1 (System Architect)

- **Missing**: 10-part architecture series (Part*.md)
- **Present**: All 19 ADRs exist (contrary to audit reports)
- **Action**: Decide fate of Part*.md series; update CANONICAL_REGISTRY if not creating

### Role 2 (Build & Tooling)

- **Missing**: AppServices.cs (potential build blocker)
- **Current**: Build FAILS (XAML compiler exit 1)
- **Action**: Fix XAML compiler issue; investigate AppServices.cs absence

### Role 3 (UI Engineer)

- **Missing**: UI_AUTOMATION_SPEC, viewmodel_di_refactor.md (TD-004 spec)
- **Gaps**: DI container, BaseViewModel compliance, business logic in code-behind
- **Action**: Create missing specs; address GAP-003, GAP-004, GAP-005

### Role 4 (Core Platform)

- **Missing**: ENGINE_VENV_ISOLATION_SPEC (TD-001 spec), stream status docs
- **Gaps**: Engine interface layer (GAP-002), FastAPI in services (GAP-007)
- **Action**: Create missing specs; address GAP-002

### Role 5 (Engine Engineer)

- **Missing**: ENGINE_VENV_ISOLATION_SPEC (TD-001 spec), ENGINE_PROOF_STREAM_STATUS
- **Action**: Create missing docs; TD-001 implementation when prioritized

### Role 6 (Release Engineer)

- **Missing**: PRODUCTION_READINESS.md
- **Action**: Create production readiness declaration (or restore from TASK-0017 evidence)

### Role 7 (Debug Agent)

- **Missing**: None identified
- **Present**: Debug Role integration complete per STATE.md; ADR-017 exists

---

## 10. Summary and Recommendations

### 10.1 What's Actually Missing (Filesystem-Verified)

**Documents (11):**
1. PROJECT_HANDOFF_GUIDE.md (or rename existing DOCUMENT)
2. DOCUMENT_GOVERNANCE.md
3. ROLE_GUIDES_INDEX.md
4. ARCHIVE_POLICY.md
5. GOVERNANCE_LOCK.md
6. templates/RULE_PROPOSAL_TEMPLATE.md
7. docs/tasks/README.md
8. docs/tasks/TASK_TEMPLATE.md
9. docs/architecture/Part*.md (10 files)
10. PRODUCTION_READINESS.md
11. docs/tasks/TASK-0020.md, TASK-0021.md

**Specs (3):**
12. viewmodel_di_refactor.md
13. ENGINE_VENV_ISOLATION_SPEC.md
14. UI_AUTOMATION_SPEC.md

**Stream Status (5):**
15. ENGINE_PROOF_STREAM_STATUS_2026-01-29.md
16. CORE_PLATFORM_STREAM_STATUS_2026-01-29.md
17. UI_STREAM_STATUS_2026-01-29.md
18. BUILD_QUALITY_STREAM_STATUS_2026-01-29.md
19. OBSERVABILITY_STREAM_STATUS_2026-01-29.md

**Code (1):**
20. AppServices.cs

**Total**: 20+ missing items (some are 10-file sets like Part*.md).

### 10.2 What's Present (Contrary to Stale Reports)

- All 19 ADRs (ADR-001 through ADR-019)
- MASTER_ROADMAP_UNIFIED.md
- docs/architecture/README.md
- docs/archive/governance/ (governance_consolidated/)
- All 8 role guides and 8 role prompts

### 10.3 Recommended Order of Operations

1. **Fix build** (XAML compiler) — unblocks verification
2. **Create critical task briefs** (TASK-0020, TASK-0021) — unblocks STATE references
3. **Create TD specs** (viewmodel_di_refactor, ENGINE_VENV_ISOLATION_SPEC, UI_AUTOMATION_SPEC) — unblocks TD-001, TD-004 work
4. **Create or alias PROJECT_HANDOFF_GUIDE** — maintainer entry point
5. **Create PRODUCTION_READINESS** — production declaration
6. **Create task system docs** (README, TEMPLATE) — task brief workflow
7. **Create ROLE_GUIDES_INDEX** — role system master index
8. **Create governance docs** (DOCUMENT_GOVERNANCE, ARCHIVE_POLICY, etc.) — file lifecycle
9. **Create stream status docs** (5 files) — Optional Tasks Master Plan evidence
10. **Decide on Part*.md series** — create or remove from registry
11. **Investigate AppServices.cs** — restore or refactor
12. **Address architecture gaps** (GAP-002, GAP-003) — when prioritized

---

## 11. References

| Document | Location | Status |
|----------|----------|--------|
| CANONICAL_REGISTRY | docs/governance/CANONICAL_REGISTRY.md | Present (but has broken references) |
| STATE.md | .cursor/STATE.md | Present (but references phantom files) |
| TECH_DEBT_REGISTER | docs/governance/TECH_DEBT_REGISTER.md | Present |
| GAP_ANALYSIS (stale) | docs/reports/audit/GAP_ANALYSIS_REMEDIATION_PLAN_2026-01-30.md | Present but inaccurate (says ADRs missing) |
| COMPREHENSIVE_AUDIT (stale) | docs/reports/audit/COMPREHENSIVE_AUDIT_FINAL_REPORT_2026-01-30.md | Present but inaccurate |

---

**END OF ACCURATE FINAL SWEEP**

This report supersedes stale audit reports and provides a filesystem-verified list of missing items for realignment. Use §8 Realignment Checklist and §10.3 Recommended Order of Operations to drive the next phase.
