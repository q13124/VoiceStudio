# ADR-031: API Versioning Strategy

**Status:** Accepted
**Date:** 2026-02-10
**Decision Makers:** VoiceStudio Architecture Team

## Context

VoiceStudio exposes a REST API with 520+ endpoints across 119 route files. As the API evolves, we need a clear versioning strategy to:
- Maintain backward compatibility
- Allow deprecation of old endpoints
- Support parallel API versions during migration

## Decision

We adopt URL-based versioning with the following conventions:

### Version Format

```
/api/v{major}[.{minor}]/resource
```

Examples:
- `/api/v1/voice/synthesize` - Current stable API
- `/api/v2/voice/synthesize` - Next major version
- `/api/v3/voice/synthesize` - Future API (experimental)

### Version Lifecycle

| Stage | Description | Duration |
|-------|-------------|----------|
| Current | Active development and support | Indefinite |
| Deprecated | Supported but discouraged | 6 months |
| Sunset | No longer supported | End of life |

### Deprecation Process

1. Announce deprecation in release notes
2. Add `Deprecation` header to responses
3. Log deprecation warnings
4. Remove after sunset period

### Current API Versions

| Version | Status | Notes |
|---------|--------|-------|
| v1 | Current | Production API |
| v2 | Deprecated | Legacy compatibility |
| v3 | Experimental | New features testing |

## Consequences

### Positive
- Clear versioning expectations for API consumers
- Structured deprecation process
- Support for experimental features

### Negative
- Multiple versions to maintain
- Documentation complexity

### Neutral
- Requires version routing middleware

## Implementation

Located in `backend/api/versioning/`:
- `version_router.py` - Version routing logic
- `deprecation.py` - Deprecation middleware

## Related ADRs

- ADR-007: IPC Boundary
- ADR-032: Middleware Stack
