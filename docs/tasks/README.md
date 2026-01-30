# Task Brief System

> **Owner**: Overseer (Role 0)  
> **Last Updated**: 2026-01-30  
> **Purpose**: Task brief workflow, conventions, and lifecycle for VoiceStudio.

---

## Overview

Task briefs are formal work units for VoiceStudio. Each task has:
- **Unique ID**: TASK-NNNN (sequential, zero-padded)
- **Objective**: Clear goal and scope
- **Owner**: Assigned role (Overseer, Role 1–7)
- **Lifecycle**: Analyze → Blueprint → Construct → Validate
- **Evidence**: Required proofs and acceptance criteria

---

## Task Brief Workflow

### 1. Task Creation

1. **Identify need**: From roadmap, tech debt, gate failure, or user request.
2. **Assign ID**: Next sequential ID (e.g. TASK-0023). Check `docs/tasks/` for highest existing ID.
3. **Copy template**: Use [TASK_TEMPLATE.md](TASK_TEMPLATE.md).
4. **Fill sections**: Objective, Affected Modules, Constraints, Required Proofs, Acceptance Criteria, Owner, Status.
5. **Register**: Create `docs/tasks/TASK-NNNN.md`; set as Active Task in [.cursor/STATE.md](../../.cursor/STATE.md).

### 2. Task Execution

1. **Analyze**: Understand scope, dependencies, risks.
2. **Blueprint**: Design solution; document approach.
3. **Construct**: Implement changes; capture evidence.
4. **Validate**: Run proofs; verify acceptance criteria.

### 3. Task Closure

1. **Update task brief**: Mark status Complete; add execution summary.
2. **Update STATE.md**: Move to Last Milestone; clear Active Task or set next.
3. **Update CANONICAL_REGISTRY**: If task created canonical docs.
4. **Create ADR**: If task changed architecture or established convention.
5. **Proof Index**: Add proof artifacts to STATE.md Proof Index.

See [.cursor/rules/workflows/closure-protocol.mdc](../../.cursor/rules/workflows/closure-protocol.mdc) for full closure requirements.

---

## Task Brief Conventions

### Naming

- **Format**: `TASK-NNNN.md` (4-digit zero-padded)
- **Location**: `docs/tasks/`
- **Example**: `docs/tasks/TASK-0020.md`

### Status Values

- **Not Started**: Task created but not begun
- **In Progress**: Work underway
- **Blocked**: Waiting on dependency or external factor
- **Complete**: All acceptance criteria met; proofs captured

### Ownership

Tasks are assigned to roles per the 8-role system:
- **Overseer (Role 0)**: Governance, coordination
- **System Architect (Role 1)**: ADRs, boundaries
- **Build & Tooling (Role 2)**: Build, CI/CD
- **UI Engineer (Role 3)**: MVVM, WinUI
- **Core Platform (Role 4)**: Backend, runtime
- **Engine Engineer (Role 5)**: Engines, quality
- **Release Engineer (Role 6)**: Installer, packaging
- **Debug Agent (Role 7)**: Triage, root-cause

See [ROLE_GUIDES_INDEX.md](../governance/ROLE_GUIDES_INDEX.md) for role details.

---

## Active Tasks

Current active task is tracked in [.cursor/STATE.md](../../.cursor/STATE.md) § Active Task.

---

## Task Index

| ID | Title | Owner | Status |
|----|-------|-------|--------|
| TASK-0006 | A/B Testing Panel | Role 3 | Complete |
| TASK-0007 | SLO Dashboard Panel | Role 3 | Complete |
| TASK-0008 | Quality Dashboard Panel | Role 3 | Complete |
| TASK-0010 | Piper/Chatterbox Backend Fix | Role 4/5 | Partial Complete |
| TASK-0020 | Wizard Flow E2E Proof (TD-005) | Role 3/5 | In Progress |
| TASK-0021 | OpenMemory MCP Wiring (Phase 6+) | Role 4/1 | Not Started |
| TASK-0022 | Git History Reconstruction | Role 0 | Complete |

See individual task briefs in `docs/tasks/TASK-*.md`.

---

## References

- [TASK_TEMPLATE.md](TASK_TEMPLATE.md) — Standard task brief template
- [.cursor/STATE.md](../../.cursor/STATE.md) — Current phase, active task
- [CANONICAL_REGISTRY.md](../governance/CANONICAL_REGISTRY.md) — Document registry
- [.cursor/rules/workflows/closure-protocol.mdc](../../.cursor/rules/workflows/closure-protocol.mdc) — Closure requirements
