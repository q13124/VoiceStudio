# VoiceStudio AI Agent Development Guide

> **Last Updated**: 2026-02-02  
> **Owner**: Overseer (Role 0)  
> **Purpose**: Guide for AI-assisted development in VoiceStudio

---

## Overview

This guide explains how AI agents (Cursor Auto mode, ChatGPT-assisted development,
Copilot, etc.) should interact with VoiceStudio's codebase while respecting its
governance framework.

VoiceStudio uses a comprehensive governance system including:
- **Role-based ownership** (8 roles + Skeptical Validator)
- **Quality gates** (B-H)
- **Compatibility matrix** for version control
- **Protected surfaces** requiring elevated review
- **Scaffolding tools** for consistent code generation

---

## Before You Start

### 1. Read the Compatibility Matrix

```bash
python scripts/check_compatibility_matrix.py --list-pins
```

This shows all version constraints. Key locked dependencies:
- `torch==2.2.2+cu121` - Required for XTTS v2
- `numpy==1.26.4` - Bridge for PyTorch/librosa compatibility
- `librosa==0.11.0` - Audio processing (DO NOT UPGRADE)

### 2. Check Current State

Read `.cursor/STATE.md` to understand:
- Current phase and active task
- Recent milestones and blockers
- Context for ongoing work

### 3. Understand Protected Surfaces

These paths require Overseer approval for changes:

| Path | Owner | Reason |
|------|-------|--------|
| `global.json` | Build & Tooling | SDK version |
| `requirements*.txt` | Core Platform | Dependencies |
| `src/VoiceStudio.Core/**` | System Architect | Contracts |
| `.cursor/rules/**` | Overseer | Agent governance |

---

## Creating New Components

### Use Scaffolding Tools

VoiceStudio provides CLI scaffolds that generate correct patterns:

#### New UI Panel

```bash
python tools/scaffolds/generate_panel.py --name QualityMonitor --region Center
```

Generates:
- `src/VoiceStudio.App/Views/Panels/QualityMonitorView.xaml`
- `src/VoiceStudio.App/Views/Panels/QualityMonitorView.xaml.cs`
- `src/VoiceStudio.App/ViewModels/QualityMonitorViewModel.cs`
- `tests/ui/test_quality_monitor.py`

#### New API Route

```bash
python tools/scaffolds/generate_route.py --name quality_metrics
```

Generates:
- `backend/api/routes/quality_metrics.py`
- `backend/api/models/quality_metrics_models.py`
- `tests/unit/backend/api/routes/test_quality_metrics.py`

#### New Engine

```bash
python tools/scaffolds/generate_engine.py --name cosyvoice --type audio --subtype tts
```

Generates:
- `engines/audio/cosyvoice/engine.manifest.json`
- `app/core/engines/cosyvoice_engine.py`
- `tests/unit/engines/test_cosyvoice.py`

### Why Use Scaffolds?

1. **Consistency**: Generated code follows VoiceStudio patterns
2. **Completeness**: Includes tests, code-behind, proper imports
3. **Compliance**: Pre-commit hooks validate scaffold usage
4. **Documentation**: Generated files include TODO markers for customization

---

## Handling Dependency Changes

### Check Matrix First

Before proposing any dependency change:

```bash
python scripts/check_compatibility_matrix.py --list-pins
```

Look for:
- `locked: true` - Cannot change without ADR
- `tech_debt: TD-XXX` - Has known constraints
- `reason` - Why current version is pinned

### Locked Dependencies

If a dependency is locked:
1. **DO NOT propose upgrade** unless user explicitly requests
2. Explain the constraint to the user
3. Suggest workarounds (separate venv, alternative package)

Example response:
```
The requested torch upgrade conflicts with our compatibility matrix:

torch is pinned at 2.2.2+cu121 because XTTS v2 requires it.
Upgrading to 2.6+ would break voice synthesis.

Alternatives:
1. Use a separate venv for the new engine (see TD-015)
2. Wait for Chatterbox compatibility resolution (TD-001)
3. Request an ADR for coordinated upgrade

Which would you prefer?
```

---

## Verification Protocol

### Before Completing Any Task

Run the verification suite:

```bash
python scripts/run_verification.py
```

This checks:
- `gate_status` - All gates B-H
- `ledger_validate` - Quality Ledger consistency
- `completion_guard` - No uncommitted completion markers
- `compatibility_matrix` - Version pins match files

### Expected Output

```
============================================================
VERIFICATION REPORT (automated)
============================================================

  [PASS] gate_status (exit 0, 0.11s)
  [PASS] ledger_validate (exit 0, 0.10s)
  [PASS] completion_guard (exit 0, 0.08s)
  [PASS] compatibility_matrix (exit 0, 0.07s)

  Overall: PASS
```

If any check fails, resolve it before marking work complete.

---

## Common Scenarios

### Scenario 1: User Requests New Panel

```
User: "Add a new Quality Monitor panel"

Correct Response:
1. Generate scaffold: python tools/scaffolds/generate_panel.py --name QualityMonitor
2. Show generated files
3. Explain manual steps (registration, build)
4. Offer to implement panel logic
```

### Scenario 2: User Requests Dependency Upgrade

```
User: "Upgrade numpy to 2.0"

Correct Response:
1. Check matrix: numpy==1.26.4 [LOCKED]
2. Explain: "numpy is locked at 1.26.4 because it bridges PyTorch 2.2.2 and librosa 0.11"
3. Propose alternatives or request ADR
```

### Scenario 3: User Wants to Modify Core Contract

```
User: "Add a new method to IBackendClient"

Correct Response:
1. Note: "This modifies src/VoiceStudio.Core - a protected surface"
2. Explain impact on boundary contract
3. Suggest interface extension pattern
4. Note: Changes will require System Architect review via CODEOWNERS
```

### Scenario 4: Build Fails After Changes

```
Build failed with errors

Correct Response:
1. Analyze error messages
2. Fix errors (don't suppress)
3. Run verification: python scripts/run_verification.py
4. Document resolution
5. Only mark complete when verification PASS
```

---

## Escalation Triggers

Pause and ask the user when:

1. **Protected surface change needed** - Requires approval
2. **Locked dependency conflict** - Need resolution strategy
3. **Scaffold inappropriate** - Explain and get approval
4. **Multiple failures** - After 2 attempts, ask for guidance
5. **Security concern** - Credentials, vulnerabilities, etc.

---

## Reference Files

| File | Purpose |
|------|---------|
| `config/compatibility_matrix.yml` | Version pins and constraints |
| `.cursor/STATE.md` | Current session state |
| `.github/CODEOWNERS` | Protected surface ownership |
| `.cursor/rules/workflows/auto-mode-safety.mdc` | AI agent safety rules |
| `docs/governance/TECH_DEBT_REGISTER.md` | Known constraints |

---

## Quick Checklist

Before completing any AI-assisted task:

- [ ] Used scaffold for new components (if applicable)
- [ ] Checked compatibility matrix before dependency changes
- [ ] Verified protected surfaces not modified without approval
- [ ] Ran `python scripts/run_verification.py` - PASS
- [ ] Build succeeds with no new errors
- [ ] Tests pass for modified code

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-02 | Initial guide created (Phase 4) |
