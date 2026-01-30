# ADR-017: Engine Subprocess Model

## Status

Proposed

## Context

VoiceStudio engines run in isolated processes to prevent VRAM conflicts and enable fault isolation. A subprocess model is needed.

## Options Considered

1. **In-process** - All engines in backend process
2. **Subprocess per-call** - Spawn process for each operation
3. **Subprocess pool** - Persistent worker processes

## Decision

**To be decided.** This ADR is a placeholder.

Implementation evidence:
- `app/core/runtime/` - Runtime engine orchestration
- Circuit breaker pattern (TD-014)

## Consequences

TBD - Document when decision is formally made.
