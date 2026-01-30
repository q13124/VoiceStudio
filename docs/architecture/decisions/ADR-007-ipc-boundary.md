# ADR-007: IPC Boundary (Control vs Data Plane)

## Status

Accepted

## Context

VoiceStudio has a hybrid architecture with a C# WinUI 3 frontend and Python FastAPI backend. A clear IPC boundary is needed to separate control plane (commands, status) from data plane (audio, artifacts).

## Options Considered

1. **Single HTTP API** - All communication via REST
2. **Named Pipes + HTTP** - Control via pipes, data via HTTP
3. **HTTP REST (control) + HTTP Streaming (data)** - Standard protocols

## Decision

Adopted HTTP REST for control plane operations (start job, get status) and HTTP streaming for data plane operations (upload audio, download artifacts). WebSocket used for real-time status updates.

## Consequences

- **Easier debugging** - Standard HTTP tools work
- **Cross-platform ready** - No Windows-specific IPC
- **Moderate latency** - Acceptable for voice synthesis workloads
- **Standard tooling** - OpenAPI, Swagger, httpx all compatible

Implementation evidence:
- `backend/api/routes/` - REST API routes
- `src/VoiceStudio.App/Services/BackendClient.cs` - HTTP client
