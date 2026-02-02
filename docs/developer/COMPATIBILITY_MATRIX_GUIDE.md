# VoiceStudio Compatibility Matrix Guide

> **Last Updated**: 2026-02-02  
> **Owner**: Overseer (Role 0)  
> **Purpose**: Guide for using and maintaining the compatibility matrix

---

## Overview

The **Compatibility Matrix** (`config/compatibility_matrix.yml`) is VoiceStudio's single source of truth for version pins, dependency constraints, and protected surfaces. It centralizes scattered version knowledge and enables automated validation.

### Why We Have a Compatibility Matrix

1. **Prevent Drift**: Ensures versions don't change without explicit review
2. **Document Constraints**: Captures why specific versions are locked (e.g., TD-001 torch constraint)
3. **Enable Validation**: Automated checks in pre-commit and CI
4. **Protect Critical Paths**: Defines protected surfaces requiring Overseer approval

---

## Matrix Structure

The matrix has six main sections:

### 1. Platform Requirements

```yaml
platform:
  dotnet_sdk: "8.0.417"
  python_runtime: ">=3.10.15,<3.13"
  python_recommended: "3.11.9"
```

Defines OS, SDK, and runtime constraints.

### 2. Python Dependencies

```yaml
dependencies:
  python:
    torch:
      version: "2.2.2+cu121"
      reason: "Baseline for XTTS v2"
      tech_debt: null
    librosa:
      version: "0.11.0"
      locked: true  # DO NOT UPGRADE
```

Each dependency includes:
- `version`: Required version or range
- `reason`: Why this version
- `locked`: If true, version is frozen
- `tech_debt`: Reference to TD-XXX if applicable

### 3. .NET Dependencies

```yaml
dependencies:
  dotnet:
    windows_app_sdk:
      version: "1.8.251106002"
```

### 4. API Contracts

```yaml
contracts:
  api:
    endpoints:
      health_preflight:
        path: "/api/health/preflight"
```

Documents API contract expectations.

### 5. UI Invariants

```yaml
ui_invariants:
  design_tokens: "src/VoiceStudio.App/Resources/DesignTokens.xaml"
  panel_registry: "src/VoiceStudio.App/Services/PanelRegistry.cs"
```

Patterns and files that must remain stable.

### 6. Protected Surfaces

```yaml
protected_surfaces:
  - path: "global.json"
    owner: "Role 2 (Build & Tooling)"
    reason: ".NET SDK version"
```

Paths requiring elevated review.

---

## Validation

### Local Validation (Pre-commit)

The matrix validator runs automatically on commit:

```bash
python scripts/check_compatibility_matrix.py --local
```

### Manual Validation

```bash
# Run full validation
python scripts/check_compatibility_matrix.py

# Show all version pins
python scripts/check_compatibility_matrix.py --list-pins

# JSON output for CI
python scripts/check_compatibility_matrix.py --json

# Verbose output
python scripts/check_compatibility_matrix.py --verbose
```

### What Gets Validated

| Source File | Checks |
|-------------|--------|
| `global.json` | .NET SDK version matches `platform.dotnet_sdk` |
| `version_lock.json` | Critical Python packages match matrix |
| `Directory.Build.props` | WindowsAppSDK version matches |

---

## Making Changes

### Proposing a Version Change

1. **Check for constraints**: Review matrix for `locked: true` or `tech_debt` references
2. **Test locally**: Ensure build/tests pass with new version
3. **Update matrix**: Edit `config/compatibility_matrix.yml`
4. **Update lock files**: Edit `version_lock.json`, `requirements*.txt` as needed
5. **Run validation**: `python scripts/check_compatibility_matrix.py`
6. **Create PR**: Protected surface changes auto-assign Overseer

### Adding a New Dependency

```yaml
dependencies:
  python:
    new_package:
      version: "1.0.0"
      reason: "Purpose of this package"
      tech_debt: null  # or "TD-XXX" if constrained
```

### Marking a Dependency as Locked

```yaml
librosa:
  version: "0.11.0"
  reason: "librosa >0.11.0 breaks PyTorch 2.2.2"
  locked: true
```

**LOCKED dependencies require ADR or Tech Debt resolution before changing.**

---

## Protected Surfaces

Protected surfaces require Overseer approval via CODEOWNERS:

| Path | Owner | Reason |
|------|-------|--------|
| `global.json` | Build & Tooling | SDK version |
| `requirements*.txt` | Core Platform / Engine | Dependencies |
| `version_lock.json` | Overseer | Canonical pins |
| `src/VoiceStudio.Core/**` | System Architect | Contracts |
| `.cursor/rules/**` | Overseer | Agent governance |

When modifying these paths:
1. GitHub auto-assigns owners for review
2. CI validates matrix compliance
3. PR requires owner approval

---

## Integration Points

### Pre-commit Hook

Added to `.pre-commit-config.yaml`:

```yaml
- id: compatibility-matrix-check
  name: Compatibility Matrix Validation
  entry: python scripts/check_compatibility_matrix.py --local
  language: system
  files: ^(global\.json|requirements.*\.txt|version_lock\.json|Directory\.Build\.props)$
```

### CI Pipeline (Phase 3)

A dedicated job validates matrix compliance on every PR.

### run_verification.py (Phase 3)

Matrix validation integrates with existing verification:

```bash
python scripts/run_verification.py
# Runs: gate_status, ledger_validate, completion_guard, compatibility_matrix
```

---

## Tech Debt References

The matrix documents constraints tied to Tech Debt:

| TD ID | Package | Constraint |
|-------|---------|------------|
| TD-001 | torch | Must stay at 2.2.2+cu121 for Chatterbox |
| TD-003 | protobuf | >=5.28.3 for CVE fix |

When resolving Tech Debt, update the corresponding matrix entries.

---

## Troubleshooting

### Validation Fails on global.json

```
[FAIL]: global.json
  Expected: 8.0.417
  Actual:   8.0.500
```

**Fix**: Either update `global.json` to match matrix, or update matrix with Overseer approval.

### Validation Fails on version_lock.json

```
[FAIL]: version_lock.json:torch
  Expected: 2.2.2+cu121
  Actual:   2.5.0+cu124
```

**Fix**: Check if change is intentional. If not, revert. If yes, update matrix and get approval.

### Pre-commit Hook Blocks Commit

The hook runs on files matching version-related paths. Either:
1. Fix the version mismatch
2. Use `--no-verify` (requires justification)

---

## References

- **Matrix File**: `config/compatibility_matrix.yml`
- **Validator Script**: `scripts/check_compatibility_matrix.py`
- **CODEOWNERS**: `.github/CODEOWNERS`
- **Tech Debt Register**: `docs/governance/TECH_DEBT_REGISTER.md`
- **ADR-025**: `docs/architecture/decisions/ADR-025-compatibility-matrix-and-scaffolding.md` (Phase 5)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-02 | Initial guide created (Phase 1) |
