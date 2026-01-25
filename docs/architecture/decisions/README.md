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
| - | No ADRs yet | - | - |
