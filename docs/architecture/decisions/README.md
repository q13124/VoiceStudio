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

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-rulebook-integration.md) | Cursor Agent Rulebook Integration | Accepted | 2026-01-25 |
| [ADR-002](ADR-002-document-governance.md) | Document Governance Architecture | Accepted | 2026-01-25 |
| [ADR-003](ADR-003-agent-governance-framework.md) | Agent Governance Framework | Accepted | 2026-01-25 |
| [ADR-004](ADR-004-messagepack-ipc.md) | MessagePack IPC Transport | Accepted | 2026-01-25 |
| [ADR-005](ADR-005-context-management-system.md) | Context Management System | Accepted | 2026-01-25 |
| [ADR-006](ADR-006-enhanced-cursor-rules-system.md) | Enhanced Cursor Rules System | Accepted | 2026-01-25 |
| [ADR-007](ADR-007-ipc-boundary.md) | IPC Boundary (Control vs Data Plane) | Accepted | 2026-01-25 |
| [ADR-008](ADR-008-architecture-patterns.md) | Architecture Patterns and Enforcement | Accepted | 2026-01-25 |
| [ADR-009](ADR-009-ai-native-development-patterns.md) | AI-Native Development Patterns | Accepted | 2026-01-25 |
| [ADR-010](ADR-010-native-windows-platform.md) | Native Windows Platform | Accepted | 2026-01-25 |
