# VoiceStudio Technical Debt Register

> **Last Updated**: 2026-01-30  
> **Owner**: Overseer (Role 0)  
> **Purpose**: Canonical registry of all known technical debt, limitations, and future enhancements

---

## Active Technical Debt

### HIGH Priority

| ID | Title | Description | Impact | Owner | Created | Target |
|----|-------|-------------|--------|-------|---------|--------|
| **TD-001** | Chatterbox torch version | Chatterbox requires torch>=2.6, but venv has 2.2.2+cu121 | Engine unusable | Role 5 | 2026-01-29 | Phase 6+ |
| **TD-002** | Release build suppressions | Release build uses NoWarn for CS0436, CS0618 | Technical debt in build | Role 2 | 2026-01-29 | Sprint 2 |
| **TD-013** | VRAM Resource Scheduler | No explicit VRAM budgeting per ChatGPT spec Part 7 | Potential OOM with multi-engine | Role 4/5 | 2026-01-30 | Phase 6+ |
| **TD-014** | Circuit Breaker Pattern | No failure isolation for engines per ChatGPT spec Part 3.6 | Cascading failures possible | Role 4 | 2026-01-30 | Sprint 2 |
| **TD-015** | Venv Families Strategy | Single venv instead of 12 families per ChatGPT spec Part 4 | Dependency conflicts, limits expansion | Role 5 | 2026-01-30 | Phase 6+ |

### MEDIUM Priority

| ID | Title | Description | Impact | Owner | Created | Target |
|----|-------|-------------|--------|-------|---------|--------|
| **TD-003** | Python CVE: protobuf | protobuf <5.28.3 has CVE-2024-7254 | Security vulnerability | Role 4 | 2026-01-29 | Sprint 2 |
| **TD-004** | ViewModel DI migration | TD-004 DI migration incomplete, some commented imports | Code cleanup needed | Role 3 | 2026-01-28 | Sprint 2 |
| **TD-005** | Wizard e2e proof incomplete | Wizard flow e2e proof run blocked on reference audio | QA incomplete | Role 3/5 | 2026-01-29 | TASK-0020 |
| **TD-016** | Engine Manifest Schema v2 | Current engine configs lack capability declarations per spec | Limited metadata | Role 5 | 2026-01-30 | Phase 6+ |

### LOW Priority

| ID | Title | Description | Impact | Owner | Created | Target |
|----|-------|-------------|--------|-------|---------|--------|
| **TD-006** | Ledger warnings | VS-0025 and VS-0032 are expected validation warnings | Documentation only | Role 0 | 2026-01-29 | CLOSED |
| **TD-007** | Warning count | Debug build has 4990 warnings (Release has 504) | Code quality | Role 2 | 2026-01-29 | Phase 6+ |
| **TD-008** | Git History Reconstruction | Documentation-git disconnect from branch divergence | Process failure | Role 0 | 2026-01-29 | CLOSED |
| **TD-009** | Commit Discipline Enforcement | Need pre-commit hooks to prevent uncommitted work | Process improvement | Role 0 | 2026-01-30 | TASK-0023 |
| **TD-010** | Branch Merge Policy | Need policy for max branch divergence | Process improvement | Role 0 | 2026-01-30 | Sprint 2 |
| **TD-011** | Interface Implementations | IViewModelContext, ITelemetryService, IProjectRepository need implementations | Functionality incomplete | Role 3/4 | 2026-01-30 | TASK-0023 |
| **TD-012** | Namespace Cleanup | Some consumers still use wrong namespaces (App.UseCases) | Code cleanup | Role 2/3 | 2026-01-30 | TD-004 |

---

## Closed Technical Debt

| ID | Title | Closed Date | Resolution | Proof |
|----|-------|-------------|------------|-------|
| **TD-006** | Ledger warnings | 2026-01-29 | Documented as expected warnings | TASK-0018 |
| **TD-008** | Git History Reconstruction | 2026-01-30 | 11 recovery commits, 80+ files recovered | TASK-0022 |

---

## Technical Debt by Category

### Architecture Gaps (from ChatGPT Spec Cross-Reference)

| TD ID | ChatGPT Spec Section | Gap Description | ADR Reference |
|-------|---------------------|-----------------|---------------|
| TD-013 | Part 7: Resource Management | VRAM Resource Scheduler not implemented | — |
| TD-014 | Part 3: Orchestration | Circuit Breaker pattern missing | — |
| TD-015 | Part 4: Engine Layer | Venv Families not implemented | — |
| TD-016 | Part 4: Engine Layer | Engine Manifest Schema v2 not adopted | — |
| — | Part 5: IPC | Named Pipes replaced with HTTP | ADR-018 |
| — | Part 3: Orchestration | C# orchestration in Python instead | ADR-019 |

### Build & Process

| TD ID | Category | Description |
|-------|----------|-------------|
| TD-002 | Build | Release NoWarn suppressions |
| TD-007 | Build | High warning count |
| TD-009 | Process | Commit discipline enforcement |
| TD-010 | Process | Branch merge policy |

### Code Quality

| TD ID | Category | Description |
|-------|----------|-------------|
| TD-004 | DI Migration | ViewModel DI incomplete |
| TD-011 | Interfaces | Missing implementations |
| TD-012 | Namespaces | Wrong namespace references |

### Dependencies

| TD ID | Category | Description |
|-------|----------|-------------|
| TD-001 | Engine Deps | Chatterbox torch version |
| TD-003 | Security | protobuf CVE |

---

## Tech Debt to Task Mapping

| TD ID | TASK ID | Status |
|-------|---------|--------|
| TD-005 | TASK-0020 | In Progress |
| TD-006 | TASK-0018 | Complete |
| TD-008 | TASK-0022 | Complete |
| TD-009 | TASK-0023 | Pending |
| TD-011 | TASK-0023 | Pending |
| TD-013 | TASK-0028 | Proposed |
| TD-015 | TASK-0029 | Proposed |

---

## Mitigation Strategies

### TD-001: Chatterbox torch version

**Options:**
1. Upgrade venv torch to 2.6 (risk: breaks XTTS)
2. Separate venv for Chatterbox (aligns with TD-015)
3. Defer until TD-015 venv families implemented

**Recommendation:** Option 3 — defer until venv families strategy resolved

### TD-013: VRAM Resource Scheduler

**Implementation Plan:**
1. Create `ResourceScheduler` class in backend
2. Track VRAM allocation per engine
3. Implement priority queue for jobs
4. Add eviction policy for low-priority allocations
5. Wire into engine lifecycle

**Effort:** 16-24 hours

### TD-014: Circuit Breaker Pattern

**Implementation Plan:**
1. Create `CircuitBreaker` class with states (Closed, Open, HalfOpen)
2. Track failure counts per engine
3. Open circuit after 3 failures
4. Auto-reset after recovery timeout
5. Wire into engine manager

**Effort:** 8-12 hours

### TD-015: Venv Families Strategy

**Implementation Plan:**
1. Analyze 49 engines for dependency compatibility
2. Group into 10-12 families
3. Create per-family requirements.txt
4. Update engine manager to use family venvs
5. Update installer to bundle venvs

**Effort:** 40-60 hours (major initiative)

---

## Process Improvements (from TASK-0022 Lessons Learned)

### Commit Discipline Rule (TD-009)

**Rule:** Tasks are NOT complete until committed to git.

**Enforcement:**
- Pre-commit hook validates STATE.md changes
- Rule file: `.cursor/rules/workflows/commit-discipline.mdc`
- Weekly audit for uncommitted work

### Branch Merge Policy (TD-010)

**Policy:**
- Max divergence: 10 commits OR 2 weeks
- Mandatory review at 20 commits
- Process violation at 50 commits

**Enforcement:**
- Weekly `git log master..branches` audit
- Document: `docs/governance/BRANCH_MERGE_POLICY.md`

---

## References

- [ARCHITECTURE_CROSS_REFERENCE_2026-01-30.md](../reports/verification/ARCHITECTURE_CROSS_REFERENCE_2026-01-30.md)
- [TASK-0022_COMPLETE_RECOVERY_REPORT_2026-01-30.md](../reports/post_mortem/TASK-0022_COMPLETE_RECOVERY_REPORT_2026-01-30.md)
- [ADR-018](../architecture/decisions/ADR-018-ipc-architecture-deviation.md) (IPC Deviation)
- [ADR-019](../architecture/decisions/ADR-019-orchestration-architecture.md) (Orchestration Deviation)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-30 | Created register; added TD-001 through TD-016 |
| 2026-01-30 | Added Architecture Gaps from cross-reference analysis |
| 2026-01-30 | Closed TD-006 (TASK-0018) and TD-008 (TASK-0022) |
