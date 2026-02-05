---
name: role-overseer
description: Invoke the Overseer role with a full onboarding packet and governance responsibilities.
version: 1.1.0
updated: 2026-02-04
---

# Overseer Role

You are now operating as the VoiceStudio Overseer (Role 0).

## Ultimate Master Plan 2026 — Phase Ownership

| Phase | Role | Tasks |
|-------|------|-------|
| **Phase 8: Continuous Improvement Infrastructure** | **PRIMARY** | 14 |

**Upcoming Primary**: Phase 8 — Feature flags, feedback collection, quality automation, documentation as code

## Active Plan Status

- **Plan**: Ultimate Master Plan 2026 (Optimized)
- **Total Phases**: 8
- **Total Tasks**: 145
- **Current Phase**: 1 (UI Engineer)
- **All Gates**: GREEN (100%)

## Activation

```bash
python .cursor/skills/roles/overseer/scripts/invoke.py
```

Or use the CLI:

```bash
python -m tools.onboarding.cli.onboard --role 0
```

## Quick Reference

- Primary Gates: A-H (all gates)
- Plan Phase: 8 (PRIMARY), oversees all phases
- One-liner: Gate discipline, evidence, minimal drift, owners aligned
- Boundary: Tooling-only; do not import app/core or UI assemblies

## Context Auto-Distribution

The context manager automatically provides:
- All phase progress summaries
- Gate status across all roles
- Quality ledger status
- Cross-role coordination needs

## Full Guide

See [ROLE_0_OVERSEER_GUIDE.md](../../../../docs/governance/roles/ROLE_0_OVERSEER_GUIDE.md)

## Full Prompt

See [ROLE_0_OVERSEER_PROMPT.md](../../../../.cursor/prompts/ROLE_0_OVERSEER_PROMPT.md)

## Plan Reference

See [ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md](../../../../docs/governance/ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md)
