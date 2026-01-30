# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for VoiceStudio.

## What is an ADR?

An ADR documents a significant architectural decision along with its context and consequences.

## When to create an ADR

Per `.cursor/rules/core/architecture.mdc`, an ADR is required when:

- Adding or removing a major dependency
- Changing project structure
- Changing engine integration strategy
- Introducing persistence schemas or migrations

## ADR Format

Use this template:

```markdown
# ADR-NNN: Title

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
What is the issue that we're seeing that is motivating this decision or change?

## Options Considered
1. **Option A**: Description
   - Pros: ...
   - Cons: ...

2. **Option B**: Description
   - Pros: ...
   - Cons: ...

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
```

## Naming Convention

- Format: `ADR-NNN-short-title.md`
- Example: `ADR-001-engine-subprocess-isolation.md`
- Numbers are sequential and never reused

## Index

### Existing ADRs

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-rulebook-integration.md) | Cursor Agent Rulebook Integration | Accepted | 2026-01-25 |
| [ADR-003](ADR-003-agent-governance-framework.md) | Agent Governance Framework | Accepted | 2026-01-25 |
| [ADR-015](ADR-015-architecture-integration-contract.md) | Architecture Integration Contract | Accepted | 2026-01-29 |
| [ADR-016](ADR-016-gate-c-artifact-choice.md) | Gate C Artifact Choice | Accepted | 2026-01-29 |

### Planned ADRs (Not Yet Created)

The following ADRs are planned but have not yet been written. They will be created as architectural decisions are formally made.

| ADR | Planned Title | Status |
|-----|---------------|--------|
| ADR-002 | Document Governance Architecture | Planned |
| ADR-004 | MessagePack IPC Transport | Planned |
| ADR-005 | Context Management System | Planned |
| ADR-006 | Enhanced Cursor Rules System | Planned |
| ADR-007 | IPC Boundary (Control vs Data Plane) | Planned |
| ADR-008 | Architecture Patterns and Enforcement | Planned |
| ADR-009 | AI-Native Development Patterns | Planned |
| ADR-010 | Native Windows Platform | Planned |
| ADR-011 | Context Manager Architecture | Planned |
| ADR-012 | Roadmap Integration Scaffolding | Planned |
| ADR-013 | OpenTelemetry Distributed Tracing | Planned |
| ADR-014 | Agent Skills Integration | Planned |

## Implementation Evidence (audit 2026-01-30)

ADR-001 (Rulebook Integration) is reflected in `.cursor/rules/*.mdc`. ADR-003 (Agent Governance Framework) is reflected in the 8-role system (`docs/governance/roles/ROLE_*_GUIDE.md`). ADR-015 (Architecture Integration Contract) defines boundary stability. Planned ADRs represent decisions implemented in code but not yet formally documented as ADRs.
