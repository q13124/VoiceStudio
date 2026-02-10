# ADR-032: Middleware Stack Architecture

**Status:** Accepted
**Date:** 2026-02-10
**Decision Makers:** VoiceStudio Architecture Team

## Context

VoiceStudio's FastAPI backend requires several cross-cutting concerns:
- Request/response compression
- Rate limiting
- Authentication
- Request logging
- Error handling
- CORS

We need a consistent middleware stack architecture.

## Decision

We adopt a layered middleware stack with explicit ordering:

### Middleware Order (Outer to Inner)

```
Request → [Compression] → [RateLimit] → [Auth] → [Logging] → Route Handler
                                                                    ↓
Response ← [Compression] ← [RateLimit] ← [Auth] ← [Logging] ← Response
```

### Middleware Components

| Order | Middleware | Location | Purpose |
|-------|------------|----------|---------|
| 1 | Compression | `middleware/compression.py` | Gzip/Brotli response compression |
| 2 | Rate Limiter | `middleware/rate_limiter.py` | Token bucket rate limiting |
| 3 | Auth | `middleware/auth_middleware.py` | API key and session validation |
| 4 | Logging | `middleware/logging.py` | Request/response logging |
| 5 | Error Handler | `middleware/error_handler.py` | Exception to HTTP response |

### Configuration

Middleware is configured in `backend/api/main.py`:

```python
# Order matters - outer middleware first
app.add_middleware(CompressionMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware, rate="100/minute")
app.add_middleware(AuthMiddleware, optional=True)
app.add_middleware(LoggingMiddleware)
```

### Rate Limiting Strategy

| Endpoint Type | Rate Limit |
|---------------|------------|
| Synthesis | 10 req/min |
| Transcription | 30 req/min |
| General API | 100 req/min |
| WebSocket | 5 connections |

### Compression Strategy

- Minimum response size: 1KB
- Algorithms: Gzip (default), Brotli (if supported)
- Excluded: Audio/video streams, binary uploads

## Consequences

### Positive
- Consistent cross-cutting concern handling
- Clear middleware ordering
- Configurable per-endpoint behavior

### Negative
- Middleware overhead on every request
- Debugging complexity with multiple layers

### Neutral
- Requires careful ordering to avoid conflicts

## Implementation

All middleware in `backend/api/middleware/`:
- `__init__.py` - Middleware exports
- `compression.py` - Response compression
- `rate_limiter.py` - Rate limiting
- `auth_middleware.py` - Authentication

## Related ADRs

- ADR-031: API Versioning Strategy
- ADR-007: IPC Boundary
