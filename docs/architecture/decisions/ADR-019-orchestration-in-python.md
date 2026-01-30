# ADR-019: Orchestration in Python (Not C#)

## Status

Accepted

## Context

Original ChatGPT specification had C# handling engine orchestration. This was moved to Python to leverage Python ML ecosystem.

## Options Considered

1. **C# orchestration** - Per original spec
2. **Python orchestration** - Backend handles all engine coordination

## Decision

Moved orchestration to Python backend. The C# frontend is a thin client that calls backend APIs. Engine coordination, job management, and artifact handling are all in Python.

## Consequences

- Simpler C# codebase (MVVM UI only)
- Leverage Python ML libraries directly
- Single language for backend + engines
- Some latency from HTTP calls (acceptable)
