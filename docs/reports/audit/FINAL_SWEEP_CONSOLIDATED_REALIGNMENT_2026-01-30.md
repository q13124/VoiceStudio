# Final Sweep — Consolidated Realignment Checklist

> **Date**: 2026-01-30  
> **Purpose**: Single cross-role sweep of tasks, plans, roadmaps, roles, architectures, workflows, rules, and expected artifacts before realigning the team and updating the plan/roadmap.  
> **Scope**: Missing-file debacle, scaffoldings, architectures, workflows, rules, role expectations, structures, backend/frontend/UI-UX.  
> **Sources**: CANONICAL_REGISTRY, COMPREHENSIVE_AUDIT_FINAL_REPORT, GAP_ANALYSIS_REMEDIATION_PLAN, FINAL_SWEEP_BEFORE_REALIGNMENT, FINAL_SWEEP_MISSING_AND_NEVER_DONE, TECH_DEBT_REGISTER, ARCHITECTURE_CROSS_REFERENCE, live repo verification.  
> **Status**: COMPLETE — Use this document to drive realignment and roadmap updates.

---

## 1. Executive Summary

This consolidated report merges all prior final-sweep and audit findings and verifies current filesystem state. It answers: **What is still missing or never done after TASK-0022 recovery and current build?**

### Current State (Verified 2026-01-30)

| Category | Present | Missing / Incomplete |
|----------|---------|----------------------|
| **Canonical docs (registry)** | CANONICAL_REGISTRY, TECH_DEBT_REGISTER, HANDOFF_PROTOCOL, CROSS_ROLE_ESCALATION_MATRIX, role guides (0–7), role prompts, rules (.mdc), QUALITY_LEDGER, DEFINITION_OF_DONE | MASTER_ROADMAP_UNIFIED, PROJECT_HANDOFF_GUIDE, DOCUMENT_GOVERNANCE, ARCHIVE_POLICY, GOVERNANCE_LOCK, ROLE_GUIDES_INDEX, QUICK_START_GUIDE (registry name), PRODUCTION_READINESS |
| **ADRs** | ADR-001, 002, 003, 004, 005, 006, 007, 008, 015, 017, 018, 019 (12 files) | ADR-009, 010, 011, 012, 013, 014, 016 (7 files) |
| **Architecture** | decisions/, ADR_*, CONTRACT_*, GOVERNANCE_* | docs/architecture/README.md, Part1–Part10 series |
| **Task briefs** | TASK-0006, 0007, 0008, 0010, 0022 | TASK-0009, 0011–0021, docs/tasks/README.md, TASK_TEMPLATE.md |
| **Workflows / rules** | state-gate, closure-protocol, error-resolution, git-conventions, document-lifecycle, verifier-subagent, etc. | commit-discipline.mdc (TD-009), BRANCH_MERGE_POLICY.md (TD-010) |
| **Archive** | — | docs/archive/governance/ (and legacy roadmap refs) |
| **Templates** | — | docs/governance/templates/, RULE_PROPOSAL_TEMPLATE.md |

---

## 2. Critical: Still Missing or Misaligned

### 2.1 Canonical Files (Registry vs Filesystem)

| Expected Path (per CANONICAL_REGISTRY) | Status | Remediation |
|----------------------------------------|--------|-------------|
| `docs/governance/MASTER_ROADMAP_UNIFIED.md` | **MISSING** | Create from existing roadmaps (e.g. MASTER_ROADMAP_SUMMARY, ROADMAP_TO_COMPLETION, MASTER_FEATURE_ROADMAP) OR point registry to one as canonical. |
| `docs/governance/PROJECT_HANDOFF_GUIDE.md` | **MISSING** | Create or copy/rename from `PROJECT_HANDOFF_DOCUMENT_2025-01-28.md`; update registry. |
| `docs/governance/DOCUMENT_GOVERNANCE.md` | **MISSING** | Create (file creation and lifecycle; see document-lifecycle.mdc). |
| `docs/governance/ARCHIVE_POLICY.md` | **MISSING** | Create (archive locations and policy). |
| `docs/governance/GOVERNANCE_LOCK.md` | **MISSING** | Create if lock state is used; else remove from registry. |
| `docs/governance/ROLE_GUIDES_INDEX.md` | **MISSING** | Create master index with phase–gate–role matrix; link to ROLE_0–7 guides. |
| `docs/governance/QUICK_START_GUIDE.md` | **MISALIGNED** | Registry points here; repo has QUICK_START_GUIDE.md (verify path). |
| `docs/governance/templates/RULE_PROPOSAL_TEMPLATE.md` | **MISSING** | Create templates/ and file. |
| `docs/architecture/README.md` | **MISSING** | Create architecture index (entry to ADRs + design docs). |
| `docs/architecture/Part*.md` (10-part series) | **MISSING** | Option A: Create Part1–Part10. Option B: Update registry to drop Part*; use ADRs + design as architecture source. |
| `docs/tasks/README.md` | **MISSING** | Create task brief workflow and conventions. |
| `docs/tasks/TASK_TEMPLATE.md` | **MISSING** | Create standard task brief template. |
| `docs/PRODUCTION_READINESS.md` | **MISSING** | Create formal production readiness statement (or restore from backup). |
| `docs/archive/governance/` | **MISSING** | Create if legacy roadmaps are to be archived; add MASTER_ROADMAP.md, MASTER_ROADMAP_SUMMARY.md, MASTER_ROADMAP_INDEX.md if superseded. |

### 2.2 ADRs — Still Missing (7)

| ADR | Title | Action |
|-----|-------|--------|
| ADR-009 | AI-Native Development Patterns | Create placeholder or full ADR. |
| ADR-010 | Native Windows Platform | **Critical** — platform identity; create or restore. |
| ADR-011 | Context Manager Architecture | Create placeholder or full ADR. |
| ADR-012 | Roadmap Integration Scaffolding | Create placeholder or full ADR. |
| ADR-013 | OpenTelemetry Distributed Tracing | Create placeholder or full ADR. |
| ADR-014 | Agent Skills Integration | Create placeholder or full ADR. |
| ADR-016 | Task Classifier and MCP Selector | Create placeholder or full ADR. |

**Present (12):** ADR-001, 002, 003, 004, 005, 006, 007, 008, 015, 017, 018, 019.

### 2.3 Task Briefs — Missing (Referenced in STATE / Registry)

| Task ID | Inferred Title / Use | Action |
|---------|------------------------|--------|
| TASK-0009 | Engine Integration A–D / Multi-engine baseline | Create brief; mark Complete with proof refs. |
| TASK-0011 | Engine Engineer venv restore / baseline proof | Create brief; mark Partial Complete. |
| TASK-0012 | Governance cleanup sprint | Create brief; mark Complete. |
| TASK-0013 | Phase 2 follow-up | Create brief; mark Complete. |
| TASK-0014 | Phase 4 QA Completion | Create brief; mark Complete. |
| TASK-0015 | Gate C Release | Create brief; mark Complete. |
| TASK-0016 | Phase 4 deps | Create brief; mark Complete or N/A. |
| TASK-0017 | Roadmap Closure & Production Readiness | Create brief; mark Complete. |
| TASK-0018 | TD-006 Closure | Create brief; mark Complete. |
| TASK-0019 | Phase 2+ next-work selection | Create brief; mark Complete. |
| TASK-0020 | Wizard Flow E2E Proof (TD-005) | **Create brief** — referenced as Active Task; not in docs/tasks/. |
| TASK-0021 | OpenMemory MCP wiring (Phase 6+) | **Create brief** — referenced in Next 3 Steps; not in docs/tasks/. |

**Present (5):** TASK-0006, 0007, 0008, 0010, 0022.

### 2.4 Workflows and Process (from TECH_DEBT_REGISTER)

| Item | Referenced In | Status | Action |
|------|----------------|--------|--------|
| Commit discipline rule | TD-009; TASK-0023 | **MISSING** | Add `.cursor/rules/workflows/commit-discipline.mdc`; pre-commit hook for STATE.md. |
| Branch merge policy | TD-010 | **MISSING** | Create `docs/governance/BRANCH_MERGE_POLICY.md`. |

---

## 3. Scaffolding, Architecture, and Structure Gaps

### 3.1 Architecture

- **Index:** `docs/architecture/README.md` — missing; create entry point to ADRs + design docs.
- **10-part series:** Part1–Part10 — missing; decide create vs registry-only update (see §2.1).
- **ChatGPT spec alignment:** ARCHITECTURE_CROSS_REFERENCE and TECH_DEBT_REGISTER document TD-013 (VRAM), TD-014 (Circuit Breaker), TD-015 (Venv Families), TD-016 (Engine Manifest v2); treat as roadmap/backlog, not “missing files.”

### 3.2 Governance and Lifecycle

- Document lifecycle and file creation: **DOCUMENT_GOVERNANCE.md** missing; align with `.cursor/rules/workflows/document-lifecycle.mdc`.
- Archive policy and location: **ARCHIVE_POLICY.md** missing.
- Rule proposal process: **templates/RULE_PROPOSAL_TEMPLATE.md** missing.

### 3.3 Role System

- **Present:** ROLE_0–ROLE_7 guides, ROLE_0–7 prompts, Skeptical Validator prompt, ROLE_PROMPTS_INDEX.
- **Missing:** **ROLE_GUIDES_INDEX.md** (phase–gate–role matrix and link to all guides).
- Role expectations and responsibilities: **inside** each guide and prompt; no separate “role expectations” doc set missing beyond ROLE_GUIDES_INDEX.

### 3.4 Backend / Frontend / UI-UX (From Audits — No Re-verification)

- **Backend:** 23 route files import engines directly (GAP-002); no engine interface layer (CC-001). Create backend/interfaces or ports; inject implementations.
- **Frontend:** No DI container for ViewModels (CC-002); AppServices anti-pattern; 5 ViewModels not inheriting BaseViewModel (GAP-005); direct HttpClient/WebSocket (GAP-006, GAP-008).
- **UI/UX:** Business logic in View code-behind (GAP-004). UI virtualization and Command Palette docs incomplete.
- **Interfaces:** IViewModelContext, ITelemetryService, IProjectRepository implementations deferred to TASK-0023 (TD-011).

---

## 4. Realignment Checklist — Before Updating Plan and Roadmap

Use this checklist when realigning the team and updating the plan/roadmap.

### 4.1 Documents and Registry

- [ ] **Roadmap:** Create `MASTER_ROADMAP_UNIFIED.md` OR set registry canonical roadmap to an existing file (e.g. ROADMAP_TO_COMPLETION, MASTER_FEATURE_ROADMAP).
- [ ] **Handoff:** Create `PROJECT_HANDOFF_GUIDE.md` or alias from PROJECT_HANDOFF_DOCUMENT_2025-01-28.md; update STATE SSOT and registry.
- [ ] **Governance:** Create DOCUMENT_GOVERNANCE.md, ARCHIVE_POLICY.md, GOVERNANCE_LOCK.md (if used).
- [ ] **Role index:** Create ROLE_GUIDES_INDEX.md with phase–gate–role matrix.
- [ ] **Templates:** Create docs/governance/templates/ and RULE_PROPOSAL_TEMPLATE.md.
- [ ] **Architecture:** Create docs/architecture/README.md; decide on Part1–Part10 (create vs registry update).
- [ ] **Tasks:** Create docs/tasks/README.md and TASK_TEMPLATE.md; create missing task briefs (TASK-0009, 0011–0021) with status and proof refs.
- [ ] **Production:** Create or restore docs/PRODUCTION_READINESS.md.
- [ ] **Archive:** Create docs/archive/governance/ if legacy roadmaps are to be archived; move or copy files as needed.
- [ ] **ADR gap:** Create 7 missing ADRs (009, 010, 011, 012, 013, 014, 016) as placeholders or full ADRs; prioritize ADR-010 (Native Windows Platform).

### 4.2 Workflows and Rules

- [ ] **Commit discipline:** Add `.cursor/rules/workflows/commit-discipline.mdc` (TD-009); document pre-commit hook for STATE.md.
- [ ] **Branch policy:** Create docs/governance/BRANCH_MERGE_POLICY.md (TD-010).
- [ ] **STATE / registry:** Update STATE.md Next 3 Steps and SSOT Pointers after roadmap and handoff decisions; update CANONICAL_REGISTRY to match created/renamed files.

### 4.3 Role Expectations and Responsibilities

- [ ] Confirm each role guide (ROLE_0–7) and prompt are the single source for that role’s expectations and responsibilities.
- [ ] Add ROLE_GUIDES_INDEX.md so all roles and phase–gate–role matrix are discoverable.
- [ ] No separate “individualized guidelines” set required beyond guides + prompts + index.

### 4.4 Backend / Frontend / UI-UX (Backlog)

- [ ] Backend: Engine interface layer and DI for routes (GAP-002, CC-001) — roadmap/tech-debt.
- [ ] Frontend: DI container, BaseViewModel compliance, remove AppServices anti-pattern (GAP-003, GAP-005, GAP-007) — roadmap/tech-debt.
- [ ] Interfaces: IViewModelContext, ITelemetryService, IProjectRepository (TASK-0023 / TD-011).
- [ ] UI/UX: Reduce code-behind logic (GAP-004); complete UI virtualization and Command Palette docs.

### 4.5 Plan and Roadmap Content (After Gaps Closed)

- [ ] Update plan/roadmap with: (1) post–TASK-0022 state, (2) missing-file debacle and recovery, (3) scaffoldings and architectures restored or deferred, (4) role expectations (guides + index), (5) backend/frontend/UI-UX backlog from TECH_DEBT_REGISTER and GAP_ANALYSIS.
- [ ] Align MASTER_ROADMAP_UNIFIED (or chosen canonical roadmap) with TECH_DEBT_REGISTER (TD-001–TD-016), ARCHITECTURE_CROSS_REFERENCE, and optional tasks (TASK-0020, 0021, 0023, etc.).

---

## 5. References

| Document | Location |
|----------|----------|
| Comprehensive Audit Final Report | docs/reports/audit/COMPREHENSIVE_AUDIT_FINAL_REPORT_2026-01-30.md |
| Gap Analysis & Remediation Plan | docs/reports/audit/GAP_ANALYSIS_REMEDIATION_PLAN_2026-01-30.md |
| Final Sweep Before Realignment | docs/reports/audit/FINAL_SWEEP_BEFORE_REALIGNMENT_2026-01-30.md |
| Final Sweep Missing and Never Done | docs/reports/verification/FINAL_SWEEP_MISSING_AND_NEVER_DONE_2026-01-30.md |
| Architecture Cross-Reference | docs/reports/verification/ARCHITECTURE_CROSS_REFERENCE_2026-01-30.md |
| Tech Debt Register | docs/governance/TECH_DEBT_REGISTER.md |
| Canonical Registry | docs/governance/CANONICAL_REGISTRY.md |
| TASK-0022 Complete Recovery Report | docs/reports/post_mortem/TASK-0022_COMPLETE_RECOVERY_REPORT_2026-01-30.md |

---

## 6. Changelog

| Date | Change |
|------|--------|
| 2026-01-30 | Created; consolidated all final-sweep and audit findings; verified ADR and task brief counts; added realignment checklist. |
