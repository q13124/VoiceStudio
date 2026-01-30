# ADR-011: Context Manager Architecture

## Status

Proposed

## Context

The Context Manager needs a defined architecture for source adapters, budget allocation, and package composition.

## Options Considered

1. **Monolithic** - Single module handles all context
2. **Adapter-based** - Pluggable source adapters
3. **Pipeline-based** - Sequential processing stages

## Decision

**To be decided.** This ADR is a placeholder.

Implementation evidence:
- `tools/context/core/` - Core context management
- `tools/context/sources/` - Source adapters (memory, state, rules, etc.)

## Consequences

TBD - Document when decision is formally made.
