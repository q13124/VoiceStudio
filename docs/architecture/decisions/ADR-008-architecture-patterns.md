# ADR-008: Architecture Patterns and Enforcement

## Status

Proposed

## Context

VoiceStudio uses sacred boundaries (UI ↔ Core ↔ Engines) to enable independent evolution of each layer. Patterns are needed to enforce these boundaries.

## Options Considered

1. **Convention-based** - Rely on code review
2. **Interface-enforced** - Contracts via interfaces
3. **Automated enforcement** - Linting/build-time checks

## Decision

**To be decided.** This ADR is a placeholder.

Implementation evidence:
- `src/VoiceStudio.Core/` - Core contracts and interfaces
- `.cursor/rules/core/architecture.mdc` - Boundary rules

## Consequences

TBD - Document when decision is formally made.
