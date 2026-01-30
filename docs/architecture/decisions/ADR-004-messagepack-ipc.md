# ADR-004: MessagePack IPC Transport

## Status

Superseded by ADR-007

## Context

Originally considered MessagePack for high-performance IPC between C# frontend and Python backend. This was superseded by the HTTP REST + WebSocket approach documented in ADR-007.

## Options Considered

1. **MessagePack over Named Pipes** - Binary serialization, low latency
2. **HTTP REST + WebSocket** - Standard protocols, easier debugging
3. **gRPC** - Strongly typed, requires protobuf

## Decision

This ADR is superseded by ADR-007 (IPC Boundary - Control vs Data Plane). The project uses HTTP REST for control plane and HTTP streaming for data plane.

## Consequences

See ADR-007 for current IPC architecture consequences.
