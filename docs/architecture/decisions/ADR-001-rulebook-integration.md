# ADR-001: Cursor Agent Rulebook Integration

## Status
Accepted

## Context
VoiceStudio had multiple overlapping governance documents defining agent behavior:
- `docs/governance/MASTER_RULES_COMPLETE.md`
- `docs/COMPLETE_RULESET.md`
- `docs/REFERENCE/MASTER_COMPREHENSIVE_RULES_DESIGNS_GUIDELINES.md`
- `docs/MASTER_RULES_COMPLETE_EMBEDDED.md`
- `docs/design/CURSOR_OPERATIONAL_RULESET.md`

A new comprehensive rulebook (`VoiceStudio_Cursor_Agent_Rulebook_Opus45.md`) was created to establish stricter operational discipline, including proof requirements, atomic changes, ADRs, and repository hygiene.

The challenge: integrate the new rulebook without creating yet another duplicate document.

## Options Considered

1. **Create a new master rules file**
   - Pros: Clean slate, comprehensive
   - Cons: Adds to document sprawl, violates new "one canonical doc" rule

2. **Update existing `.cursor/rules/*.mdc` files**
   - Pros: Rules are where Cursor actually reads them, no new docs
   - Cons: Requires careful merging

3. **Replace all docs with single canonical file**
   - Pros: Maximum simplicity
   - Cons: Loses historical context, high-risk change

## Decision
Option 2: Update the existing `.cursor/rules/*.mdc` files to incorporate the new rulebook requirements, then archive the duplicate governance docs.

Changes made:
- Updated `.cursor/rules/core/anti-drift.mdc` → "Operational Discipline" with response format, atomic changes, DoR/DoD
- Updated `.cursor/rules/core/architecture.mdc` → Added sacred boundaries, plugin-first mindset, ADR requirement
- Updated `.cursor/rules/security/secure-coding.mdc` → Added privacy defaults, telemetry rule
- Updated `.cursor/rules/workflows/git-conventions.mdc` → Added workaround labeling, proof in commits
- Created `.cursor/rules/quality/repo-hygiene.mdc` → Doc hygiene, file creation rules, diagnostics-first

## Consequences

### Easier
- Single source of truth for agent behavior (`.cursor/rules/`)
- Clear operational discipline with structured response format
- ADR requirement ensures decision traceability
- Repository hygiene rules prevent future document sprawl

### Harder
- Agents must follow more structured response format for significant changes
- More process overhead for major architectural decisions (ADRs required)
- Legacy governance docs need to be archived/consolidated (separate task)

## Date
2026-01-25
