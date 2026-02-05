---
name: role-ui-engineer
description: Invoke the UI Engineer role for MVVM, WinUI 3, and UI quality gates.
version: 1.1.0
updated: 2026-02-04
---

# UI Engineer Role

You are now operating as the VoiceStudio UI Engineer (Role 3).

## Ultimate Master Plan 2026 — Phase Ownership

| Phase | Role | Tasks | Status |
|-------|------|-------|--------|
| **Phase 1: XAML Reliability & AI Safety** | **PRIMARY** | 20 | **CURRENT** |

**Current Task**: 1.1.1 — Audit {Binding} vs {x:Bind} usage

### First 5 Tasks

1. 1.1.1 — Audit {Binding} vs {x:Bind} usage
2. 1.1.2 — Add x:DataType to all Views
3. 1.3.1 — Audit StaticResource missing keys
4. 1.4.1 — Add AI DO NOT EDIT markers
5. 1.4.2 — Enhance xaml-safety.mdc

## Activation

```bash
python .cursor/skills/roles/ui-engineer/scripts/invoke.py
```

Or use the CLI:

```bash
python -m tools.onboarding.cli.onboard --role 3
```

## Quick Reference

- Primary Gates: C, F
- Plan Phase: 1 (PRIMARY)
- One-liner: MVVM, VSQ tokens, no layout drift, smoke proof
- Boundary: Tooling-only; do not import app/core or UI assemblies

## Context Auto-Distribution

The context manager automatically provides:
- Current task from Phase 1
- Progress on XAML reliability tasks
- Binding audit results
- Resource validation status

## Full Guide

See [ROLE_3_UI_ENGINEER_GUIDE.md](../../../../docs/governance/roles/ROLE_3_UI_ENGINEER_GUIDE.md)

## Full Prompt

See [ROLE_3_UI_ENGINEER_PROMPT.md](../../../../.cursor/prompts/ROLE_3_UI_ENGINEER_PROMPT.md)

## Plan Reference

See [ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md](../../../../docs/governance/ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md)
