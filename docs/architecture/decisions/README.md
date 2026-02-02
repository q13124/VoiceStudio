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

### ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-rulebook-integration.md) | Cursor Agent Rulebook Integration | Accepted | 2026-01-25 |
| [ADR-002](ADR-002-document-governance.md) | Document Governance Architecture | Proposed | 2026-01-30 |
| [ADR-003](ADR-003-agent-governance-framework.md) | Agent Governance Framework | Accepted | 2026-01-25 |
| [ADR-004](ADR-004-messagepack-ipc.md) | MessagePack IPC Transport | Superseded | 2026-01-30 |
| [ADR-005](ADR-005-context-management.md) | Context Management System | Proposed | 2026-01-30 |
| [ADR-006](ADR-006-cursor-rules-system.md) | Enhanced Cursor Rules System | Proposed | 2026-01-30 |
| [ADR-007](ADR-007-ipc-boundary.md) | IPC Boundary (Control vs Data Plane) | Accepted | 2026-01-30 |
| [ADR-008](ADR-008-architecture-patterns.md) | Architecture Patterns and Enforcement | Proposed | 2026-01-30 |
| [ADR-009](ADR-009-ai-native-development.md) | AI-Native Development Patterns | Proposed | 2026-01-30 |
| [ADR-010](ADR-010-native-windows-platform.md) | Native Windows Platform | Accepted | 2026-01-30 |
| [ADR-011](ADR-011-context-manager-architecture.md) | Context Manager Architecture | Proposed | 2026-01-30 |
| [ADR-012](ADR-012-roadmap-integration.md) | Roadmap Integration Scaffolding | Proposed | 2026-01-30 |
| [ADR-013](ADR-013-opentelemetry-tracing.md) | OpenTelemetry Distributed Tracing | Proposed | 2026-01-30 |
| [ADR-014](ADR-014-agent-skills.md) | Agent Skills Integration | Proposed | 2026-01-30 |
| [ADR-015](ADR-015-architecture-integration-contract.md) | Architecture Integration Contract | Accepted | 2026-01-29 |
| [ADR-016](ADR-016-gate-c-artifact-choice.md) | Gate C Artifact Choice | Accepted | 2026-01-29 |
| [ADR-017](ADR-017-engine-subprocess-model.md) | Engine Subprocess Model | Proposed | 2026-01-30 |
| [ADR-018](ADR-018-named-pipes-http.md) | Named Pipes Replaced with HTTP | Accepted | 2026-01-30 |
| [ADR-019](ADR-019-orchestration-in-python.md) | Orchestration in Python | Accepted | 2026-01-30 |
| [ADR-023](ADR-023-ui-assembly-split.md) | UI Assembly Split into Feature Modules | Accepted | 2026-02-01 |
| [ADR-024](ADR-024-completion-evidence-guard.md) | Completion Evidence Guard | Accepted | 2026-02-01 |

## Status Legend

- **Accepted** - Decision made and implemented
- **Proposed** - Placeholder for decision to be formally documented
- **Superseded** - Replaced by another ADR

## Implementation Evidence (audit 2026-01-30)

ADR-001 (Rulebook Integration) is reflected in `.cursor/rules/*.mdc`. ADR-003 (Agent Governance Framework) is reflected in the 8-role system (`docs/governance/roles/ROLE_*_GUIDE.md`). ADR-015 (Architecture Integration Contract) defines boundary stability. Proposed ADRs represent decisions implemented in code but needing formal documentation.
