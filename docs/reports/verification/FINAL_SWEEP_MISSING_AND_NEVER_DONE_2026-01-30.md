# Final Sweep: Missing and Never-Done Items

> **Date**: 2026-01-30  
> **Purpose**: One-time audit across all roles — identify anything missing from the current build after the TASK-0022 recovery, and items that were supposed to exist but never did or disappeared.  
> **Use**: Realign team, update plan/roadmap, and close gaps before next phase.  
> **Owner**: Overseer (Role 0)

---

## 1. Executive Summary

This report cross-references **CANONICAL_REGISTRY**, **TASK-0022 Evidence Pack**, **GAP_ANALYSIS_REMEDIATION_PLAN**, **TECH_DEBT_REGISTER**, and the live repository to list:

1. **Documents and files that are referenced but missing** (never recovered or never created).
2. **Outstanding work from the missing-file incident** (deferred, not yet done).
3. **Scaffoldings, architectures, workflows, rules, role expectations, and structures** that are incomplete or absent.

**Findings**: The primary canonical **roadmap** and **archive** structure are missing. **13 ADR files** are missing. Several **governance** docs (Document Governance, Archive Policy, Governance Lock, Rule Proposal Template, Project Handoff *Guide*) are either missing or misnamed. The **10-part architecture series** (Part*.md) and **docs/tasks** system (README, TASK_TEMPLATE) are absent. **Production Readiness** and **docs/archive/governance** do not exist. Implementation gaps (engine interface layer, DI container, interface implementations) remain. Role **guides** and **prompts** are present; individualized **expectations/responsibilities** are in the guides but no separate "role expectations" doc set is missing as a category.

---

## 2. Missing Files (Referenced but Not Present)

### 2.1 Critical — Roadmap and Planning

| Referenced In | Path | Status |
|---------------|------|--------|
| CANONICAL_REGISTRY § Planning | `docs/governance/MASTER_ROADMAP_UNIFIED.md` | **MISSING** — Primary canonical roadmap; registry and TASK-0022 reference it |
| CANONICAL_REGISTRY § Planning | `docs/archive/governance/MASTER_ROADMAP.md` | **MISSING** — Directory `docs/archive/governance` does not exist |
| CANONICAL_REGISTRY § Planning | `docs/archive/governance/MASTER_ROADMAP_SUMMARY.md` | **MISSING** |
| CANONICAL_REGISTRY § Planning | `docs/archive/governance/MASTER_ROADMAP_INDEX.md` | **MISSING** |

**Note**: Other roadmap files exist (e.g. `MASTER_ROADMAP_SUMMARY.md`, `ROADMAP_TO_COMPLETION.md`, `MASTER_FEATURE_ROADMAP.md`) in `docs/governance/` but **MASTER_ROADMAP_UNIFIED.md** does not. The **archive** folder for legacy governance is absent.

### 2.2 Critical — Architecture Decision Records (ADRs)

CANONICAL_REGISTRY and GAP_ANALYSIS list 17 ADRs; only **7 files** exist under `docs/architecture/decisions/`.

| ADR | Registry Path | Status |
|-----|--------------|--------|
| ADR-001 | ADR-001-rulebook-integration.md | PRESENT |
| ADR-002 | ADR-002-document-governance.md | **MISSING** |
| ADR-003 | ADR-003-agent-governance-framework.md | PRESENT |
| ADR-004 | ADR-004-messagepack-ipc.md | **MISSING** |
| ADR-005 | ADR-005-context-management-system.md | **MISSING** |
| ADR-006 | ADR-006-enhanced-cursor-rules-system.md | **MISSING** |
| ADR-007 | ADR-007-ipc-boundary.md | **MISSING** |
| ADR-008 | ADR-008-architecture-patterns.md | **MISSING** |
| ADR-009 | ADR-009-ai-native-development-patterns.md | **MISSING** |
| ADR-010 | ADR-010-native-windows-platform.md | **MISSING** |
| ADR-011 | ADR-011-context-manager-architecture.md | **MISSING** |
| ADR-012 | ADR-012-roadmap-integration-scaffolding.md | **MISSING** |
| ADR-013 | ADR-013-opentelemetry-distributed-tracing.md | **MISSING** |
| ADR-014 | ADR-014-agent-skills-integration.md | **MISSING** |
| ADR-015 | ADR-015-architecture-integration-contract.md | PRESENT |
| ADR-016 | ADR-016-task-classifier-and-mcp-selector.md | **MISSING** |
| ADR-017 | ADR-017-debug-role-architecture.md | PRESENT |
| ADR-018 | ADR-018-ipc-architecture-deviation.md | PRESENT |
| ADR-019 | ADR-019-orchestration-architecture.md | PRESENT |

**Missing count**: 13 ADR files.

### 2.3 Governance — Rules and Lifecycle

| Referenced In | Path | Status |
|---------------|------|--------|
| CANONICAL_REGISTRY § Rules | `docs/governance/DOCUMENT_GOVERNANCE.md` | **MISSING** |
| CANONICAL_REGISTRY § Rules | `docs/governance/ARCHIVE_POLICY.md` | **MISSING** |
| CANONICAL_REGISTRY § Rules | `docs/governance/GOVERNANCE_LOCK.md` | **MISSING** |
| CANONICAL_REGISTRY § Rules | `docs/governance/templates/RULE_PROPOSAL_TEMPLATE.md` | **MISSING** — `docs/governance/templates/` does not exist |

### 2.4 Handoff and Task System

| Referenced In | Path | Status |
|---------------|------|--------|
| CANONICAL_REGISTRY § Rules | `docs/governance/PROJECT_HANDOFF_GUIDE.md` | **MISSING** — Only `PROJECT_HANDOFF_DOCUMENT_2025-01-28.md` exists |
| CANONICAL_REGISTRY § Planning | `docs/tasks/README.md` | **MISSING** |
| CANONICAL_REGISTRY § Planning | `docs/tasks/TASK_TEMPLATE.md` | **MISSING** |

### 2.5 Architecture Series

| Referenced In | Path | Status |
|---------------|------|--------|
| CANONICAL_REGISTRY § Architecture | `docs/architecture/README.md` | **MISSING** (only `docs/architecture/decisions/README.md` exists) |
| CANONICAL_REGISTRY § Architecture | `docs/architecture/Part*.md` (10-part series) | **MISSING** — No Part1–Part10 or similar in `docs/architecture/` |

### 2.6 Production and API

| Referenced In | Path | Status |
|---------------|------|--------|
| CANONICAL_REGISTRY § Rules | `docs/PRODUCTION_READINESS.md` | **MISSING** |

### 2.7 Build-blocking code: AppServices / ServiceProvider [CRITICAL]

| Item | Status | Impact |
|------|--------|--------|
| **AppServices.cs** | **MISSING or minimal stub** | ServiceProvider.cs (and Views/ViewModels) call `AppServices.Get*` / `AppServices.TryGet*` for 30+ services (BackendClient, AudioPlayerService, ErrorLoggingService, OperationQueueService, PanelRegistry, UndoRedoService, DragDropVisualFeedbackService, ContextMenuService, TelemetryService, ProfilesUseCase, etc.). If AppServices.cs is absent or only defines a few methods, the build fails with many CS0117 errors. |
| **Owner** | Role 2 (Build & Tooling) / Role 3 (UI) / Role 4 (Core Platform) | Restore or implement full AppServices facade, or refactor ServiceProvider + call sites to a proper DI container (GAP-003). |

**Evidence**: ServiceProvider.cs delegates 50+ calls to AppServices; no AppServices.cs in repo (or stub with ~8–10 methods only). This is either a file that disappeared in the missing-file incident or scaffolding that was never completed.

---

## 3. Outstanding from TASK-0022 (Recovery Report)

From **TASK-0022_COMPLETE_RECOVERY_REPORT_2026-01-30.md** § Resolution Summary — **Outstanding**:

| Item | Owner | Status |
|------|-------|--------|
| XAML compiler issue (VS-0035) | Role 2/3 | Pre-existing; not from incident |
| Gate/ledger data files need population | Role 0 | Not done |
| Interface implementations (IViewModelContext, ITelemetryService, IProjectRepository) | Role 3/4 | Deferred to TASK-0023 |
| Namespace cleanup (TD-004 continuation) | Role 2/3 | TD-012 in TECH_DEBT_REGISTER |

These were explicitly left incomplete after recovery and require follow-up.

---

## 4. Scaffoldings, Architectures, Workflows, Rules, Role Expectations

### 4.1 Recovered and Present

- **tools/overseer/** — 60+ files, gate/ledger CLI, agent/domain/issues/workflows (RESTORED).
- **.cursor/** — prompts (all 7 roles + Skeptical Validator), rules (core, domains, languages, mcp, quality, security, workflows), skills, hooks, commands, STATE.md (RESTORED).
- **docs/governance/roles/** — ROLE_0 through ROLE_7 guides (8 files) (PRESENT).
- **.cursor/prompts/** — ROLE_0–7 prompts, SKEPTICAL_VALIDATOR_PROMPT, ROLE_PROMPTS_INDEX (PRESENT).
- **Recovery Plan/QUALITY_LEDGER.md**, **openmemory.md**, **DEFINITION_OF_DONE.md**, **MASTER_RULES_COMPLETE.md**, **TECH_DEBT_REGISTER.md** (PRESENT).

### 4.2 Missing or Incomplete

- **Unified roadmap**: MASTER_ROADMAP_UNIFIED.md is the single source for "plan and roadmap"; it is missing. Other roadmaps (ROADMAP_TO_COMPLETION, MASTER_FEATURE_ROADMAP, etc.) exist but are not the canonical one.
- **Archive structure**: No `docs/archive/governance/`; legacy roadmap references are broken.
- **Document lifecycle**: DOCUMENT_GOVERNANCE.md and ARCHIVE_POLICY.md define file creation and archive policy; both missing.
- **Rule proposal process**: RULE_PROPOSAL_TEMPLATE and templates/ directory missing.
- **Project handoff**: PROJECT_HANDOFF_GUIDE.md is the maintainer entry point in the registry; only PROJECT_HANDOFF_DOCUMENT_2025-01-28.md exists — either rename/link or create the Guide.
- **Task brief system**: docs/tasks/README.md and TASK_TEMPLATE.md are the canonical task workflow; both missing. Task briefs (TASK-0006, 0007, 0008, 0010, 0022) exist but without the system doc and template.
- **Architecture narrative**: 10-part architecture series (Part*.md) and docs/architecture/README.md are missing; only ADRs and a few other docs exist under docs/architecture/.
- **Production readiness**: docs/PRODUCTION_READINESS.md is referenced; missing.

### 4.3 Role Expectations and Individualized Guidelines

- **Role expectations and responsibilities**: Defined **inside** each ROLE_X_*_GUIDE.md and ROLE_X_*_PROMPT.md. There is no separate "Role Expectations" document set; the guides and prompts are the source. No additional missing "individualized guidelines" set was found beyond the missing governance/roadmap docs above.
- **GUIDE vs PROMPT**: Each role has both a Guide (docs/governance/roles/) and a Prompt (.cursor/prompts/). All 8 role guides and 7 role prompts + Skeptical Validator are present.

### 4.4 Backend / Frontend / UI-UX / Layers

- **Backend**: Engine interface layer is **missing** (GAP-002, CC-001) — routes import engines directly; no backend/interfaces or ports layer.
- **Frontend**: DI container for ViewModels is **missing** (GAP-003, CC-002); AppServices.Get…() anti-pattern in Views. Some ViewModels do not inherit BaseViewModel (GAP-005). Direct HttpClient/WebSocket instantiation (GAP-006, GAP-008).
- **UI/UX**: Business logic in View code-behind (GAP-004). UI virtualization and Command Palette docs incomplete (GAP-014, GAP-015).
- **Structures/systems/layers**: Documented in ADRs and rules; many ADRs are missing, so the written "structures, systems, layers" narrative is incomplete.

---

## 5. Summary: What to Restore or Create for Realignment

### 5.1 Fix Registry vs Reality (Choose One Strategy)

- **Option A — Create missing artifacts**: Add MASTER_ROADMAP_UNIFIED.md (or consolidate from existing roadmaps), create 13 ADR placeholders or full ADRs, add DOCUMENT_GOVERNANCE.md, ARCHIVE_POLICY.md, GOVERNANCE_LOCK.md, templates/RULE_PROPOSAL_TEMPLATE.md, PROJECT_HANDOFF_GUIDE.md (or alias from PROJECT_HANDOFF_DOCUMENT), docs/tasks/README.md, docs/tasks/TASK_TEMPLATE.md, docs/architecture/README.md, Part1–Part10 or equivalent, docs/PRODUCTION_READINESS.md, and docs/archive/governance/ with legacy roadmap files if desired.
- **Option B — Update registry to match reality**: Point roadmap to an existing file (e.g. ROADMAP_TO_COMPLETION.md or MASTER_FEATURE_ROADMAP.md), remove or mark as "not yet created" the 13 ADRs, remove or update references to missing governance docs, point Handoff to PROJECT_HANDOFF_DOCUMENT_2025-01-28.md, and document that task brief system and architecture series are to be added later.

### 5.2 Recommended Immediate Actions

1. **Roadmap**: Create or designate one canonical roadmap (e.g. merge MASTER_FEATURE_ROADMAP + ROADMAP_TO_COMPLETION into MASTER_ROADMAP_UNIFIED.md) and update CANONICAL_REGISTRY.
2. **Handoff**: Add PROJECT_HANDOFF_GUIDE.md as a redirect/symlink or copy of PROJECT_HANDOFF_DOCUMENT_2025-01-28.md and ensure it contains gate status, build/test, structure, roles, and task brief creation.
3. **Task brief system**: Add docs/tasks/README.md and docs/tasks/TASK_TEMPLATE.md so new briefs (e.g. TASK-0023+) have a defined workflow.
4. **ADRs**: Either create 13 placeholder ADRs (GAP-001 Option C) or update the registry to list only existing ADRs and add a "Pending ADRs" section.
5. **Governance**: Create DOCUMENT_GOVERNANCE.md (file creation and lifecycle) and ARCHIVE_POLICY.md; create docs/governance/templates/ and RULE_PROPOSAL_TEMPLATE.md if the rule proposal process is required.
6. **Plan/roadmap realignment**: Update MASTER_TASK_CHECKLIST and any phase gates to reflect post–TASK-0022 state and the missing-file debacle (what was recovered, what is still deferred).
7. **Role expectations**: No new doc set required; ensure each ROLE_X_*_GUIDE.md is updated to reflect current responsibilities and boundaries post-recovery (optional consistency pass).

---

## 6. Checklist for All Roles (Final Sweep)

| Area | Check | Status |
|------|-------|--------|
| Roadmap | Single canonical roadmap file exists and is linked in registry | MISSING |
| ADRs | All registry ADRs exist on disk | 13 MISSING |
| Governance | DOCUMENT_GOVERNANCE, ARCHIVE_POLICY, GOVERNANCE_LOCK, RULE_PROPOSAL_TEMPLATE | MISSING |
| Handoff | PROJECT_HANDOFF_GUIDE exists | MISSING (alternate doc exists) |
| Task system | docs/tasks/README.md, TASK_TEMPLATE.md | MISSING |
| Architecture | docs/architecture/README.md, Part*.md series | MISSING |
| Production | PRODUCTION_READINESS.md | MISSING |
| Archive | docs/archive/governance/ and legacy roadmaps | MISSING |
| TASK-0022 | Interface implementations, gate/ledger data, namespace cleanup | OUTSTANDING |
| Backend | Engine interface layer (CC-001) | NOT DONE |
| Frontend | DI for ViewModels (CC-002), BaseViewModel, HttpClient/WS | NOT DONE |
| Role guides/prompts | 8 guides, 7 prompts + Validator | PRESENT |
| **AppServices.cs** | Full facade or DI refactor (GAP-003) | **BUILD BLOCKER** |

---

## 7. Addendum: Final Verification Pass (All Roles)

> **Date**: 2026-01-30 (final pass)  
> **Request**: Review all work tasks, plans, roadmaps; identify anything missing from current build; capture missing-file debacle, scaffoldings, architectures, workflows, rules, role expectations/responsibilities, structures, backend/frontend/UI-UX that disappeared or were never done.

### 7.1 Additional Missing Items (This Pass)

| Item | Referenced In | Status |
|------|---------------|--------|
| **ROLE_GUIDES_INDEX.md** | Each ROLE_X_*_GUIDE.md § "Parent Document" | **MISSING** — `docs/governance/ROLE_GUIDES_INDEX.md` does not exist |
| **QUALITY_LEDGER** | STATE.md SSOT, Overseer guide | **PRESENT** at `Recovery Plan/QUALITY_LEDGER.md` (not under docs/) |
| **PRODUCTION_READINESS.md** | CANONICAL_REGISTRY, TASK-0022 | **MISSING** — not in repo root or docs/ |
| **docs/tasks/README.md** | CANONICAL_REGISTRY § Task Brief System | **MISSING** |
| **docs/tasks/TASK_TEMPLATE.md** | CANONICAL_REGISTRY § Task Brief Template | **MISSING** |
| **docs/architecture/README.md** | CANONICAL_REGISTRY § Architecture Index | **MISSING** |
| **UI_AUTOMATION_SPEC.md** | CANONICAL_REGISTRY § Design | **MISSING** — `docs/design/UI_AUTOMATION_SPEC.md` not found |
| **AppServices.cs** | ServiceProvider.cs + Views/ViewModels | **MISSING or stub** — 50+ AppServices.Get*/TryGet* calls; file absent or minimal; **build blocker** (Role 2/3/4) |

### 7.2 Role Expectations and Individualized Guidelines — Status

| Role | Guide | Prompt | Individualized expectations |
|------|-------|--------|----------------------------|
| 0 Overseer | ROLE_0_OVERSEER_GUIDE.md | ROLE_0_OVERSEER_PROMPT.md | In guide: gate enforcement, ledger, evidence, coordination |
| 1 System Architect | ROLE_1_SYSTEM_ARCHITECT_GUIDE.md | ROLE_1_SYSTEM_ARCHIT_PROMPT.md | In guide: boundaries, ADRs, contracts |
| 2 Build & Tooling | ROLE_2_BUILD_TOOLING_GUIDE.md | ROLE_2_BUILD_TOOLING_PROMPT.md | In guide: deterministic builds, CI/CD |
| 3 UI Engineer | ROLE_3_UI_ENGINEER_GUIDE.md | ROLE_3_UI_ENGINEER_PROMPT.md | In guide: MVVM, VSQ tokens, WinUI 3 |
| 4 Core Platform | ROLE_4_CORE_PLATFORM_GUIDE.md | ROLE_4_CORE_PLATFORM_PROMPT.md | In guide: runtime, storage, preflight |
| 5 Engine Engineer | ROLE_5_ENGINE_ENGINEER_GUIDE.md | ROLE_5_ENGINE_ENGINEER_PROMPT.md | In guide: quality metrics, adapters |
| 6 Release Engineer | ROLE_6_RELEASE_ENGINEER_GUIDE.md | ROLE_6_RELEASE_ENGINEER_PROMPT.md | In guide: installer, Gate H, lifecycle |
| 7 Debug Agent | ROLE_7_DEBUG_AGENT_GUIDE.md | ROLE_7_DEBUG_AGENT_PROMPT.md | In guide: triage, escalation, validation |
| Skeptical Validator | SKEPTICAL_VALIDATOR_GUIDE.md | SKEPTICAL_VALIDATOR_PROMPT.md | Subagent; cross-cutting validation |

**Conclusion**: All 8 role guides and 7 role prompts + Validator exist. Expectations and responsibilities are **inside** the guides; no separate "role expectations" doc set is missing. The only missing piece is **ROLE_GUIDES_INDEX.md** (master index with phase-gate-role matrix).

### 7.3 Realignment Checklist for Plan, Roadmap, and Team

Use this when updating the plan, roadmap, and role assignments after the missing-file debacle.

| # | Area | Action | Owner |
|---|------|--------|-------|
| 1 | **Roadmap** | Create or designate `MASTER_ROADMAP_UNIFIED.md`; update CANONICAL_REGISTRY | Role 0 / Role 1 |
| 2 | **Plan** | Update MASTER_TASK_CHECKLIST / phase gates for post–TASK-0022 state; document what was recovered vs deferred | Role 0 |
| 3 | **ADRs** | Create 13 placeholder ADRs (GAP-001 Option C) or update registry to list only existing ADRs | Role 1 |
| 4 | **Governance** | Add DOCUMENT_GOVERNANCE.md, ARCHIVE_POLICY.md; optionally GOVERNANCE_LOCK.md, templates/RULE_PROPOSAL_TEMPLATE.md | Role 0 |
| 5 | **Handoff** | Add PROJECT_HANDOFF_GUIDE.md (or alias PROJECT_HANDOFF_DOCUMENT_2025-01-28.md); ensure gate status, build/test, roles, task brief creation | Role 0 |
| 6 | **Task system** | Add docs/tasks/README.md, docs/tasks/TASK_TEMPLATE.md | Role 0 / Role 2 |
| 7 | **Role index** | Create docs/governance/ROLE_GUIDES_INDEX.md (phase-gate-role matrix) | Role 0 |
| 8 | **Architecture** | Add docs/architecture/README.md; optionally 10-part Part*.md series or equivalent | Role 1 |
| 9 | **Production** | Create docs/PRODUCTION_READINESS.md (or restore from TASK-0017 evidence) | Role 0 / Role 6 |
| 10 | **Archive** | Create docs/archive/governance/ and move/alias legacy roadmaps if desired | Role 0 |
| 11 | **Backend** | Engine interface layer (GAP-002, CC-001); routes use abstractions | Role 4 / Role 5 |
| 12 | **Frontend** | DI for ViewModels (GAP-003); BaseViewModel compliance; reduce AppServices in Views | Role 3 / Role 4 |
| 13 | **UI/UX** | Reduce business logic in code-behind; document UI virtualization and Command Palette | Role 3 |
| 14 | **TASK-0022 outstanding** | Interface implementations (TASK-0023), gate/ledger data population, namespace cleanup (TD-004) | Per task owners |
| 15 | **AppServices build blocker** | Restore full AppServices.cs or refactor to DI (GAP-003); unblock build | Role 2 / Role 3 / Role 4 |

### 7.4 Key references for realignment

| Purpose | Document |
|--------|----------|
| Full missing/never-done list | This file (FINAL_SWEEP_MISSING_AND_NEVER_DONE_2026-01-30.md) |
| 28 gaps with remediation | docs/reports/audit/GAP_ANALYSIS_REMEDIATION_PLAN_2026-01-30.md |
| Audit summary | docs/reports/audit/COMPREHENSIVE_AUDIT_FINAL_REPORT_2026-01-30.md |
| Recovery narrative | docs/reports/post_mortem/TASK-0022_COMPLETE_RECOVERY_REPORT_2026-01-30.md |
| Evidence pack | docs/reports/post_mortem/TASK-0022_EVIDENCE_PACK_2026-01-30.md |
| Role system | Recovery Plan/ROLE_SYSTEM_AND_OVERSEER_PROTOCOL.md |
| Recovery plan | Recovery Plan/VoiceStudio_Architectural_Recovery_and_Completion_Plan.md |

---

**END OF FINAL SWEEP**

This document should be used to realign the team, update the plan and roadmap, and prioritize restoration or registry updates before the next phase. It reflects the state of the repository and canonical references as of 2026-01-30. Section 7 adds a final verification pass and a concise realignment checklist for plan, roadmap, and role expectations.
