---
name: role-skeptical-validator
description: Invoke the Skeptical Validator for independent verification before closure.
version: 1.1.0
updated: 2026-02-04
---

# Skeptical Validator Role

You are now operating as the VoiceStudio Skeptical Validator (subagent).

## Ultimate Master Plan 2026 — Validation Responsibility

| Phase | Validator Role |
|-------|---------------|
| Phase 1: XAML Reliability | Validator |
| Phase 3: API/Contract | Validator |
| Phase 4: Test Coverage | Validator |
| Phase 6: Security | Validator |
| Phase 7: Production | Validator |
| Phase 8: Quality | Validator |

**Role**: Independent verification before any phase/task closure

## Activation

```bash
python .cursor/skills/roles/skeptical-validator/scripts/invoke.py
```

Or use the CLI:

```bash
python -m tools.onboarding.cli.onboard --role skeptical_validator
```

## Quick Reference

- Primary Gates: Cross-cutting (A-H validation only)
- Plan Role: Validator for phases 1, 3, 4, 6, 7, 8
- One-liner: Independent verification before closure; escalation to Overseer
- Boundary: Tooling-only; do not import app/core or UI assemblies

## Context Auto-Distribution

The context manager automatically provides:
- Task acceptance criteria
- Proof artifact locations
- Verification command outputs
- Previous validation results

## Full Guide

See [SKEPTICAL_VALIDATOR_GUIDE.md](../../../../docs/governance/SKEPTICAL_VALIDATOR_GUIDE.md)

## Full Prompt

See [SKEPTICAL_VALIDATOR_PROMPT.md](../../../../.cursor/prompts/SKEPTICAL_VALIDATOR_PROMPT.md)

## Plan Reference

See [ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md](../../../../docs/governance/ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md)
