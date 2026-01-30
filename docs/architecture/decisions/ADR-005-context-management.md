# ADR-005: Context Management System

## Status

Proposed

## Context

AI agents require structured context injection for effective operation. A context management system is needed to allocate context budget, select relevant sources, and compose context packages.

## Options Considered

1. **Static context** - Fixed context per role
2. **Dynamic context manager** - Adaptive context based on task and role
3. **External context service** - Separate MCP-based context service

## Decision

**To be decided.** This ADR is a placeholder.

Implementation evidence:
- `tools/context/` - Context management module
- `tools/context/core/allocator.py` - Budget allocation
- `tools/context/sources/` - Source adapters

## Consequences

TBD - Document when decision is formally made.
