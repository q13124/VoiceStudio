# ADR-013: OpenTelemetry Distributed Tracing

## Status

**Accepted** (2026-02-04)

## Context

VoiceStudio has multiple components:
- WinUI 3 frontend
- FastAPI backend
- Python engine layer
- Subprocess-based engine execution

Distributed tracing is needed for:
- Debugging cross-component issues
- Performance monitoring and optimization
- SLO tracking
- Error correlation

## Options Considered

1. **No tracing** - Rely on logs
   - Pros: Simple, no infrastructure
   - Cons: Hard to correlate cross-component issues

2. **OpenTelemetry** - Standard observability framework
   - Pros: Vendor-neutral, standardized, extensible
   - Cons: Setup complexity, overhead

3. **Vendor-specific** - Datadog, Sentry, etc.
   - Pros: Integrated features, managed infrastructure
   - Cons: Cost, vendor lock-in, cloud dependency

## Decision

**Option 2: OpenTelemetry** with Prometheus backend for metrics.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Observability                         │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Traces    │  │   Metrics   │  │      Logs       │ │
│  │(OpenTelemetry)│ │(Prometheus) │  │  (Structured)   │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│         │                │                  │           │
│         └────────────────┼──────────────────┘           │
│                          │                              │
│                 ┌────────▼────────┐                     │
│                 │  Local Export   │                     │
│                 │ (Jaeger, files) │                     │
│                 └─────────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

### Instrumentation

**Backend (FastAPI)**:
- OpenTelemetry Python SDK
- Auto-instrumentation for HTTP requests
- Custom spans for engine operations

**Metrics (Prometheus)**:
- Request latency histograms
- Synthesis/transcription counters
- GPU utilization gauges
- SLO tracking

### SLO Configuration

| Metric | Target | Threshold |
|--------|--------|-----------|
| Synthesis latency P95 | < 5s | 4.5s warning |
| Transcription latency P95 | < 10s | 9s warning |
| Error rate | < 1% | 0.8% warning |
| Backend availability | 99.9% | 99.5% warning |

### Local-First

Consistent with project principles:
- No cloud-based tracing required
- Jaeger or file-based export
- Prometheus runs locally
- Optional cloud integration

## Implementation Evidence

- `backend/services/telemetry.py` - Prometheus metrics
- `app/core/monitoring/metrics.py` - Engine metrics
- `app/core/monitoring/profiler.py` - Profiling support
- `backend/api/middleware/` - Request tracing

## Consequences

### Positive
- Standardized observability across components
- Vendor-neutral, no lock-in
- Local-first operation
- SLO tracking for quality gates
- Better debugging for distributed issues

### Negative
- Setup and configuration overhead
- Performance overhead (minimal with sampling)
- Need to maintain exporters

### Neutral
- Optional cloud integration
- Trace storage requires disk space
- Learning curve for OpenTelemetry
