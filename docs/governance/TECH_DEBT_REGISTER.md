# VoiceStudio Technical Debt Register

> **Last Updated**: 2026-02-02  
> **Owner**: Overseer (Role 0)  
> **Purpose**: Canonical registry of all known technical debt, limitations, and future enhancements

---

## Active Technical Debt

### HIGH Priority

| ID | Title | Description | Impact | Owner | Created | Target |
|----|-------|-------------|--------|-------|---------|--------|
| **TD-001** | Chatterbox torch version | Chatterbox requires torch>=2.6, but venv has 2.2.2+cu121 | Engine unusable | Role 5 | 2026-01-29 | Phase 6+ |
| **TD-002** | Release build suppressions | Release build passes (0 warnings, 0 errors); no suppressions needed | Build clean | Role 2 | 2026-01-29 | CLOSED |
| **TD-013** | VRAM Resource Scheduler | No explicit VRAM budgeting per ChatGPT spec Part 7 | Potential OOM with multi-engine | Role 4/5 | 2026-01-30 | Phase 6+ |
| **TD-014** | Circuit Breaker Pattern | Implemented and wired into voice, image_gen, video_gen, rvc routes | Cascading failures prevented | Role 4 | 2026-01-30 | CLOSED |
| **TD-015** | Venv Families Strategy | Single venv instead of 12 families per ChatGPT spec Part 4 | Dependency conflicts, limits expansion | Role 5 | 2026-01-30 | Phase 6+ |

### MEDIUM Priority

| ID | Title | Description | Impact | Owner | Created | Target |
|----|-------|-------------|--------|-------|---------|--------|
| **TD-003** | Python CVE: protobuf | protobuf 6.33.4 installed (CVE fixed at 5.28.3) | Security RESOLVED | Role 4 | 2026-01-29 | CLOSED |
| **TD-004** | ViewModel DI migration | All 68 ViewModels use IViewModelContext DI; legacy constructor unused | Migration complete | Role 3 | 2026-01-28 | CLOSED |
| **TD-005** | Wizard e2e proof | Wizard flow proof passes (4 PASS, 2 SKIP due to engine deps) | QA complete | Role 3/5 | 2026-01-29 | CLOSED |
| **TD-017** | OpenAPI spec regeneration | docs/api/openapi.json regenerated (508 paths) | Verification complete | Role 4 | 2026-02-02 | CLOSED |

### LOW Priority

| ID | Title | Description | Impact | Owner | Created | Target |
|----|-------|-------------|--------|-------|---------|--------|
| **TD-006** | Ledger warnings | VS-0025 and VS-0032 are expected validation warnings | Documentation only | Role 0 | 2026-01-29 | CLOSED |
| **TD-007** | Warning count | Debug build reduced 4990→2046 (54%); CI budget at 2500 | Code quality | Role 2 | 2026-01-29 | CLOSED |
| **TD-008** | Git History Reconstruction | Documentation-git disconnect from branch divergence | Process failure | Role 0 | 2026-01-29 | CLOSED |
| **TD-009** | Commit Discipline Enforcement | Pre-commit hooks verified (completion_guard, compatibility_matrix) | Process improvement | Role 0 | 2026-01-30 | CLOSED |
| **TD-010** | Branch Merge Policy | Policy created: docs/governance/BRANCH_MERGE_POLICY.md | Complete | Role 0 | 2026-01-30 | CLOSED |
| **TD-011** | Interface Implementations | All interfaces implemented: ViewModelContext, TelemetryServiceStub, JsonProjectRepository | Complete | Role 3/4 | 2026-01-30 | CLOSED |
| **TD-012** | Namespace Cleanup | UseCases namespace correctly defined and used; no issues | Verified correct | Role 2/3 | 2026-01-30 | CLOSED |

---

## Closed Technical Debt

| ID | Title | Closed Date | Resolution | Proof |
|----|-------|-------------|------------|-------|
| **TD-006** | Ledger warnings | 2026-01-29 | Documented as expected warnings | TASK-0018 |
| **TD-007** | Warning count | 2026-02-02 | Reduced 4990→2046 (54%); CI budget added at 2500 | scripts/check_warning_budget.py, build.yml |
| **TD-008** | Git History Reconstruction | 2026-01-30 | 11 recovery commits, 80+ files recovered | TASK-0022 |
| **TD-009** | Commit Discipline Enforcement | 2026-02-02 | Pre-commit hooks verified working | pre-commit run --all-files |
| **TD-014** | Circuit Breaker Pattern | 2026-02-02 | CircuitBreaker wired into image_gen, video_gen, rvc routes | backend/services/circuit_breaker.py |
| **TD-016** | Engine Manifest Schema v2 | 2026-02-02 | verify_engine_tasks_targeted.py 4/4 PASS | ENGINE_ENGINEER_STATUS_2026-02-01 |
| **TD-005** | Wizard e2e proof | 2026-02-02 | Wizard flow proof 4/4 PASS, 2 SKIP (engine deps) | .buildlogs/proof_runs/wizard_flow_20260201-231924 |
| **TD-017** | OpenAPI spec regeneration | 2026-02-02 | docs/api/openapi.json regenerated with 508 paths | curl http://localhost:8002/openapi.json |
| **TD-003** | Python CVE: protobuf | 2026-02-02 | protobuf 6.33.4 installed (CVE fixed at 5.28.3) | pip show protobuf |
| **TD-002** | Release build suppressions | 2026-02-02 | Release build 0 warnings, 0 errors; no suppressions needed | dotnet build -c Release |
| **TD-004** | ViewModel DI migration | 2026-02-02 | All 68 ViewModels use IViewModelContext DI; legacy constructor unused | Grep: IViewModelContext |
| **TD-011** | Interface Implementations | 2026-02-02 | ViewModelContext, TelemetryServiceStub, JsonProjectRepository implemented | Grep: class.*: I*Service |
| **TD-012** | Namespace Cleanup | 2026-02-02 | UseCases namespace correctly defined and used; no issues found | Grep: App.UseCases |
| **TD-010** | Branch Merge Policy | 2026-02-02 | Policy created: docs/governance/BRANCH_MERGE_POLICY.md | BRANCH_MERGE_POLICY.md |

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
| TD-017 | Documentation | Stale OpenAPI spec |

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
| 2026-02-02 | Added TD-017 (OpenAPI spec regeneration); Closed TD-016 (Engine Manifest verified) |
| 2026-02-02 | Closed TD-007 (warning reduction 54%), TD-009 (pre-commit verified), TD-014 (circuit breaker wired) |
| 2026-02-02 | Closed TD-017 (OpenAPI spec regenerated with 508 paths from running backend) |
| 2026-02-02 | Closed TD-005 (Wizard e2e proof 4/4 PASS, 2 SKIP) |
