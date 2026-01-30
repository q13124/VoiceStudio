# Final Sweep Before Realignment
## All Roles — Missing, Never Done, and Scaffolding Gaps

> **Date**: 2026-01-30  
> **Purpose**: One last sweep across tasks, plans, roadmaps, roles, architectures, workflows, rules, and expected artifacts before realigning the team and updating the plan/roadmap.  
> **Scope**: File-debacle / missing-file gaps, scaffoldings, architectures, workflows, rules, role expectations, structures, systems, layers, backend, frontend, UI/UX.  
> **Status**: COMPLETE — Use this document to drive realignment and roadmap updates.

---

## 1. Executive Summary

This sweep cross-references:

- **CANONICAL_REGISTRY** (expected canonical sources)
- **Existing audit deliverables** (COMPREHENSIVE_AUDIT_FINAL_REPORT, GAP_ANALYSIS_REMEDIATION_PLAN, DOCUMENTATION_COMPLETENESS_AUDIT, ARCHITECTURE_CROSS_REFERENCE)
- **Filesystem verification** (glob/search for key files)
- **Role guides, prompts, architecture, governance**

**Outcome**: A single list of **missing** (disappeared or never created), **misaligned** (wrong name/location), and **never done** items so the team can realign the plan and roadmap accordingly.

---

## 2. Critical: Missing or Misaligned Canonical Files

### 2.1 Files Referenced in CANONICAL_REGISTRY but NOT on Filesystem

| Expected Path (per Registry) | Status | Notes |
|------------------------------|--------|------|
| `docs/governance/PROJECT_HANDOFF_GUIDE.md` | **MISSING** | Not found in repo. Similar: `PROJECT_HANDOFF_DOCUMENT_2025-01-28.md` exists — may be rename/supersede. |
| `docs/governance/MASTER_ROADMAP_UNIFIED.md` | **MISSING** | Not found in repo (0 files). Registry lists as primary canonical roadmap. |
| `docs/governance/DOCUMENT_GOVERNANCE.md` | **MISSING** | Not found in repo (0 files). |
| `docs/governance/ROLE_GUIDES_INDEX.md` | **MISSING** | Not found in repo (0 files). Role guides (ROLE_0–7) exist; index file missing. |
| `docs/architecture/README.md` | **MISSING** | Not in `docs/architecture/` (only decisions/, ADR_GATE_C_ARTIFACT_CHOICE, CONTRACT_BOUNDARY_STABILITY, GOVERNANCE_RECONCILIATION_REPORT). |
| `docs/architecture/Part*.md` (10-part series) | **MISSING** | 0 Part*.md in docs/architecture. Registry: "System Architecture — 10-part architecture series". |

### 2.2 ADR Files — Missing (File Debacle / Never Restored)

**Referenced in CANONICAL_REGISTRY and in `docs/architecture/decisions/README.md` index, but files do NOT exist:**

| ADR | Title | File Exists? |
|-----|-------|--------------|
| ADR-002 | Document Governance | No |
| ADR-004 | MessagePack IPC | No |
| ADR-005 | Context Management System | No |
| ADR-006 | Enhanced Cursor Rules System | No |
| ADR-007 | IPC Boundary (Control vs Data Plane) | No |
| ADR-008 | Architecture Patterns | No |
| ADR-009 | AI-Native Development Patterns | No |
| ADR-010 | Native Windows Platform | No |
| ADR-011 | Context Manager Architecture | No |
| ADR-012 | Roadmap Integration Scaffolding | No |
| ADR-013 | OpenTelemetry Distributed Tracing | No |
| ADR-014 | Agent Skills Integration | No |
| ADR-016 | Task Classifier and MCP Selector | No |

**Present:** ADR-001, ADR-003, ADR-015, ADR-017, ADR-018, ADR-019 (and decisions/README.md).

**Remediation (from GAP_ANALYSIS_REMEDIATION_PLAN):** Option C — Create placeholder ADRs with TODO status, or restore from backup/TASK-0022 evidence if available.

---

## 3. Scaffolding, Architecture, and Structure Gaps

### 3.1 Architecture Documentation

| Item | Expected | Status |
|------|----------|--------|
| Architecture index | `docs/architecture/README.md` | Missing |
| 10-part architecture series | `docs/architecture/Part1.md` … `Part10.md` (or similar) | Missing (0 Part*.md) |
| Single entry point for “system architecture” | Registry points to Part*.md | No files |

### 3.2 Governance Documentation

| Item | Expected | Status |
|------|----------|--------|
| Document lifecycle / file creation | DOCUMENT_GOVERNANCE.md | Missing |
| Primary roadmap | MASTER_ROADMAP_UNIFIED.md | Missing |
| Maintainer entry point | PROJECT_HANDOFF_GUIDE.md | Missing (similar: PROJECT_HANDOFF_DOCUMENT_2025-01-28.md) |
| Role guides index | ROLE_GUIDES_INDEX.md (phase–gate–role matrix) | Missing |

### 3.3 Role System — What Exists vs What’s Missing

**Present:**

- Role guides: `docs/governance/roles/ROLE_0_OVERSEER_GUIDE.md` … `ROLE_7_DEBUG_AGENT_GUIDE.md`
- Role prompts: `.cursor/prompts/ROLE_0_OVERSEER_PROMPT.md` … `ROLE_7_DEBUG_AGENT_PROMPT.md`, SKEPTICAL_VALIDATOR_PROMPT.md, ROLE_PROMPTS_INDEX.md
- CANONICAL_REGISTRY rows for Role Documentation and Role System Prompts

**Missing:**

- `docs/governance/ROLE_GUIDES_INDEX.md` — master index with phase–gate–role matrix (per registry).

---

## 4. Workflows, Rules, and Guidelines

### 4.1 Rules and Guidelines

- **Agent rules:** `.cursor/rules/*.mdc` — present (referenced; not re-verified in this sweep).
- **Human reference:** `docs/governance/MASTER_RULES_COMPLETE.md` — referenced in registry; existence not re-verified here.
- **Document governance:** DOCUMENT_GOVERNANCE.md — **missing** (governance and lifecycle rules).

### 4.2 Workflows

- **Overseer:** Daily workflow, gate enforcement, handoff process — registry points to `docs/governance/overseer/`; directory exists (many files).
- **Handoff protocol:** Registry lists HANDOFF_PROTOCOL.md, CROSS_ROLE_ESCALATION_MATRIX — existence not re-verified here.
- **Verification:** run_verification.py, gate status, ledger — present and used.

---

## 5. Backend, Frontend, UI/UX — From Audits

From **COMPREHENSIVE_AUDIT_FINAL_REPORT** and **GAP_ANALYSIS_REMEDIATION_PLAN** (no re-audit in this sweep):

- **Backend:** 23 route files import engine implementations directly (architecture violation); FastAPI in services layer; route utility imports.
- **Frontend / UI:** 5 ViewModels don’t inherit BaseViewModel; business logic in View code-behind; direct HttpClient/WebSocket instantiation; AppServices anti-pattern; DI container missing.
- **UI/UX specs:** UI_IMPLEMENTATION_SPEC, VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC — referenced in registry; not re-verified here.

---

## 6. Systems, Layers, and Structures

- **ADR-007 (IPC Boundary):** Referenced everywhere but **ADR file missing** — control/data plane and two-lane strategy may be documented only in rules/other docs until ADR is restored.
- **ADR-010 (Native Windows Platform):** **ADR file missing** — platform identity and installer-first distribution are in rules/registry but not in an ADR file.
- **ChatGPT spec alignment:** ARCHITECTURE_CROSS_REFERENCE_2026-01-30 and TECH_DEBT_REGISTER document intentional deviations (HTTP vs Named Pipes, Python vs C# orchestration) and gaps (VRAM scheduler, venv families, circuit breaker, etc.).

---

## 7. Consolidation: What to Do Before Realignment

### 7.1 Must Address (Critical for Plan/Roadmap)

1. **Restore or recreate primary plan/roadmap**
   - Either restore `MASTER_ROADMAP_UNIFIED.md` from backup/TASK-0022 evidence or recreate from MASTER_ROADMAP_SUMMARY / OPTIONAL_TASK_INVENTORY / STATE and then repoint registry.

2. **Restore or recreate maintainer entry point**
   - Either restore `PROJECT_HANDOFF_GUIDE.md` or adopt `PROJECT_HANDOFF_DOCUMENT_2025-01-28.md` as canonical and update CANONICAL_REGISTRY.

3. **Fix ADR gap**
   - Restore 12 missing ADR files (ADR-002, 004, 005, 006, 007, 008, 009, 010, 011, 012, 013, 014, 016) from backup/TASK-0022, or create placeholders (per GAP_ANALYSIS_REMEDIATION_PLAN Option C).

4. **Document governance**
   - Restore or recreate `DOCUMENT_GOVERNANCE.md` so file lifecycle and doc creation rules are canonical again.

### 7.2 Should Address (Scaffolding and Clarity)

5. **Architecture entry point**
   - Add `docs/architecture/README.md` and, if desired, restore or recreate the 10-part architecture series (or explicitly retire and update registry).

6. **Role guides index**
   - Create `docs/governance/ROLE_GUIDES_INDEX.md` with phase–gate–role matrix and links to each role guide (per registry).

7. **Registry accuracy**
   - After restoring/creating files, update CANONICAL_REGISTRY so every row points to an existing path (or mark “PLACEHOLDER” / “ARCHIVED” where appropriate).

### 7.3 Already Documented (Use Existing Deliverables)

- **Gaps and remediation:** GAP_ANALYSIS_REMEDIATION_PLAN_2026-01-30.md (28 gaps, effort, owners).
- **Compliance and scorecard:** COMPREHENSIVE_AUDIT_FINAL_REPORT_2026-01-30.md (compliance by category, certification).
- **ChatGPT spec vs implementation:** ARCHITECTURE_CROSS_REFERENCE_2026-01-30.md (9 domains, deviations, TD-013–TD-016).
- **Evidence and recovery:** TASK-0022_EVIDENCE_PACK, TASK-0022_COMPLETE_RECOVERY_REPORT (if applicable), FORENSIC_SYSTEM_REPORT.

---

## 8. Checklist for Realignment and Roadmap Update

Use this when realigning the team and updating the plan/roadmap:

- [ ] Decide canonical roadmap file (restore MASTER_ROADMAP_UNIFIED vs recreate vs use MASTER_ROADMAP_SUMMARY/OPTIONAL_TASK_INVENTORY) and update registry.
- [ ] Decide canonical handoff/maintainer doc (restore PROJECT_HANDOFF_GUIDE vs adopt PROJECT_HANDOFF_DOCUMENT) and update registry.
- [ ] Restore or create 12 missing ADRs; update decisions/README.md index.
- [ ] Restore or create DOCUMENT_GOVERNANCE.md.
- [ ] Add docs/architecture/README.md; decide fate of 10-part Part*.md series and update registry.
- [ ] Create ROLE_GUIDES_INDEX.md and link from registry.
- [ ] Run a full registry pass: every canonical path exists or is marked ARCHIVED/PLACEHOLDER.
- [ ] Align roadmap and STATE with: file-debacle recovery, missing scaffoldings, and GAP_ANALYSIS + ARCHITECTURE_CROSS_REFERENCE + TECH_DEBT_REGISTER.
- [ ] Update role expectations and individualized guidelines if any role docs assumed the missing files (e.g. “see PROJECT_HANDOFF_GUIDE” or “see ADR-007”).

---

## 9. References

| Document | Location |
|----------|----------|
| Canonical Document Registry | docs/governance/CANONICAL_REGISTRY.md |
| Comprehensive Audit Final Report | docs/reports/audit/COMPREHENSIVE_AUDIT_FINAL_REPORT_2026-01-30.md |
| Gap Analysis & Remediation Plan | docs/reports/audit/GAP_ANALYSIS_REMEDIATION_PLAN_2026-01-30.md |
| Documentation Completeness Audit | docs/reports/audit/DOCUMENTATION_COMPLETENESS_AUDIT_2026-01-30.md |
| Architecture Cross-Reference | docs/reports/verification/ARCHITECTURE_CROSS_REFERENCE_2026-01-30.md |
| Tech Debt Register | docs/governance/TECH_DEBT_REGISTER.md |
| TASK-0022 Evidence Pack | docs/reports/post_mortem/TASK-0022_EVIDENCE_PACK_2026-01-30.md |
| Session State | .cursor/STATE.md |

---

**End of Final Sweep.** Use this report together with the existing audit and gap remediation deliverables to drive the realignment and roadmap update.
