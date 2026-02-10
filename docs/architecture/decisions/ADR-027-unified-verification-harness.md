# ADR-027: Unified Verification Harness

## Status

**Accepted** - 2026-02-09

## Context

VoiceStudio has extensive testing infrastructure that was fragmented across multiple scripts:

- `run-test-pipeline.ps1` - C# tests only
- `run_verification.py` - Gate checks only
- `quick_verify.ps1` - Quick checks only
- Individual scripts for unit/smoke/E2E

This fragmentation led to several problems:

1. **No single source of truth** - Different scripts checked different things
2. **Inconsistent local vs CI** - CI workflows had their own logic
3. **Regression blindness** - Fixing one thing could break another without detection
4. **No fail-fast enforcement** - Changes could be merged despite failing verification
5. **No artifact consolidation** - Logs scattered across multiple locations

## Decision

We will implement a **Unified Verification Harness** (`scripts/verify.ps1`) that:

1. Runs all 8 verification stages in sequence with fail-fast behavior
2. Produces consolidated artifacts in `artifacts/verify/<timestamp>/`
3. Establishes the **Golden Rule**: No changes allowed unless verify.ps1 stays GREEN
4. Supports Quick mode for pre-commit checks
5. Integrates with existing CI workflows

### Verification Stages

| Stage | Description | Dependency |
|-------|-------------|------------|
| 1. Clean Build | Build VoiceStudio.sln | None |
| 2. Python Quality | Ruff lint + mypy type check | None |
| 3. C# Unit Tests | Non-UI C# tests | Stage 1 |
| 4. Python Unit Tests | Python unit tests | Stage 2 |
| 5. Contract Tests | C# ↔ Python API contracts | Stages 1, 2 |
| 6. Backend Integration | API endpoints, engine adapters | Stages 1, 2 |
| 7. UI Smoke Tests | App launch, panels, navigation | Stage 1 |
| 8. Gate/Ledger Validation | Project governance checks | None |

### Quick Mode

Quick mode (`-Quick`) runs stages 1, 2, and 8 only (~30 seconds):
- Build verification
- Python quality checks
- Gate/ledger validation (fast and critical)

### Artifact Structure

```
artifacts/verify/<timestamp>/
├── verification_report.md
├── summary.json
├── logs/
├── screenshots/
└── test-results/
```

## Alternatives Considered

### Alternative 1: Enhanced CI-Only Verification

**Rejected** because:
- Developers need local verification before pushing
- CI feedback loop is too slow
- No unified artifact capture

### Alternative 2: Makefile/Task Runner

**Rejected** because:
- VoiceStudio is Windows-first (PowerShell is native)
- Would add dependency on Make or other tools
- Less readable than explicit PowerShell

### Alternative 3: GitHub Actions as Source of Truth

**Rejected** because:
- Can't run locally easily
- Duplicate logic in multiple workflow files
- No consolidated reporting

## Consequences

### Positive

1. **Single command verification** - `.\scripts\verify.ps1` checks everything
2. **Fail-fast behavior** - Issues caught early, clear failure point
3. **Consolidated artifacts** - All logs/results in one place
4. **Consistent local/CI** - Same verification everywhere
5. **Regression prevention** - Golden Rule enforcement

### Negative

1. **Full run time** - ~5-10 minutes for complete verification
2. **Windows dependency** - PowerShell script (but project is Windows-first)
3. **Prerequisite requirements** - Must have Python, dotnet, ruff, mypy installed

### Mitigations

1. `-Quick` mode for pre-commit (~30 seconds)
2. Skip flags for stages not relevant to current work
3. Prerequisite validation at script start
4. Clear error messages for missing tools

## Related Documents

- [verify.ps1](../../../scripts/verify.ps1) - Implementation
- [CHANGE_CONTROL_RULES.md](../../governance/CHANGE_CONTROL_RULES.md) - Governance rules
- [verification-harness.mdc](../../../.cursor/rules/workflows/verification-harness.mdc) - Agent rule
- [AUTOMATION_ID_REGISTRY.md](../../developer/AUTOMATION_ID_REGISTRY.md) - UI test identifiers

## Compliance

This decision aligns with:
- ADR-008 Architecture Patterns (verification as first-class concern)
- ADR-024 Completion Evidence Guard (proof-before-closure)
- Project rule: `anti-drift.mdc` (proof over promises)
