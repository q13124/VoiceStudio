# ADR-018: Named Pipes Replaced with HTTP

## Status

Accepted

## Context

Original ChatGPT specification called for Named Pipes IPC. This was replaced with HTTP for portability and debugging ease.

## Options Considered

1. **Named Pipes** - Windows-specific, low latency
2. **HTTP REST** - Standard, cross-platform

## Decision

HTTP REST replaced Named Pipes. See ADR-007 for the full IPC architecture decision.

## Consequences

- Easier debugging with standard HTTP tools
- Cross-platform compatibility
- Slightly higher latency (acceptable for workload)
