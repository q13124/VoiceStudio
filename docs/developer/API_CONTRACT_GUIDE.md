# API Contract Evolution Guide

This guide documents the policies and procedures for evolving the VoiceStudio API contract between the Python backend and C# frontend.

## Overview

VoiceStudio uses a contract-first approach to API development:

1. **OpenAPI Schema** (`docs/api/openapi.json`) - Single source of truth
2. **Python Backend** - FastAPI generates schema from Pydantic models
3. **C# Client** - NSwag generates typed client from OpenAPI schema
4. **Validation** - Automated tools ensure alignment

## Contract Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Backend Change (Pydantic models, routes)                 │
├─────────────────────────────────────────────────────────────┤
│ 2. Export OpenAPI Schema                                    │
│    python -c "from api.main import app; ..."                │
├─────────────────────────────────────────────────────────────┤
│ 3. Breaking Change Detection                                │
│    python tools/nswag/detect-breaking-changes.py            │
├─────────────────────────────────────────────────────────────┤
│ 4. Client Regeneration                                      │
│    powershell tools/nswag/generate-client.ps1 -Force        │
├─────────────────────────────────────────────────────────────┤
│ 5. Contract Validation                                      │
│    python tools/nswag/validate-contract.py                  │
├─────────────────────────────────────────────────────────────┤
│ 6. Contract Tests                                           │
│    python -m pytest tests/contract/                         │
│    dotnet test tests/contract/                              │
├─────────────────────────────────────────────────────────────┤
│ 7. Commit Changes                                           │
│    git add docs/api/openapi.json                            │
│    git add src/VoiceStudio.App/Services/Generated/          │
└─────────────────────────────────────────────────────────────┘
```

## Breaking vs Non-Breaking Changes

### Non-Breaking Changes (Safe)

These changes are backward-compatible:

| Change Type | Example | Action Required |
|-------------|---------|-----------------|
| Add new endpoint | `POST /api/v1/new-feature` | Regenerate client |
| Add optional parameter | `?limit=10` | Regenerate client |
| Add response field | `{"new_field": "value"}` | Regenerate client |
| Add new status code | `202 Accepted` | Regenerate client |

### Breaking Changes (Dangerous)

These changes require migration planning:

| Change Type | Example | Migration Required |
|-------------|---------|-------------------|
| Remove endpoint | Delete `GET /api/v1/old` | Deprecation period |
| Remove required parameter | Remove `name` param | Version bump |
| Change parameter type | `int` → `string` | Version bump |
| Rename field | `user_id` → `userId` | Version bump |
| Remove response field | Remove `metadata` | Deprecation period |
| Change HTTP method | `GET` → `POST` | Version bump |

## Breaking Change Workflow

When a breaking change is necessary:

### 1. Assess Impact

```bash
# Run breaking change detection
python tools/nswag/detect-breaking-changes.py

# Review changes
git diff docs/api/openapi.json
```

### 2. Choose Strategy

| Strategy | When to Use |
|----------|-------------|
| **Deprecation** | Phased removal over multiple releases |
| **Version Bump** | Clean break to new API version |
| **Feature Flag** | Gradual rollout with fallback |

### 3. Implement Deprecation (Preferred)

```python
# Add deprecation header to endpoint
@app.get("/api/v1/old-endpoint")
@deprecated(sunset="2026-03-01", alternative="/api/v2/new-endpoint")
async def old_endpoint():
    ...
```

### 4. Document Migration

Update this guide with specific migration steps for the change.

## Versioning Strategy

VoiceStudio uses **URL-based versioning**:

- Current: `/api/v1/...`
- Next: `/api/v2/...` (when breaking changes accumulate)

### When to Version

- **Minor updates**: Stay on current version
- **Single breaking change**: Deprecate with sunset date
- **Multiple breaking changes**: Bump to next version

### Version Coexistence

Both versions run simultaneously during transition:

```
/api/v1/... → Legacy endpoints (deprecated)
/api/v2/... → New endpoints (current)
```

## Tools Reference

### Export OpenAPI Schema

```bash
cd backend
python -c "from api.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > ../docs/api/openapi.json
```

### Detect Breaking Changes

```bash
# Against last commit
python tools/nswag/detect-breaking-changes.py

# Against specific baseline
python tools/nswag/detect-breaking-changes.py --baseline path/to/old.json

# JSON output
python tools/nswag/detect-breaking-changes.py --json > changes.json
```

### Regenerate Client

```bash
# Standard regeneration
powershell tools/nswag/generate-client.ps1

# Force regeneration
powershell tools/nswag/generate-client.ps1 -Force
```

### Validate Contract

```bash
# Basic validation
python tools/nswag/validate-contract.py

# With breaking change check
python tools/nswag/validate-contract.py --check-breaking

# JSON output
python tools/nswag/validate-contract.py --json
```

### Run Contract Tests

```bash
# Python tests
python -m pytest tests/contract/test_openapi_contract.py -v

# C# tests
dotnet test tests/contract/VoiceStudio.ContractTests.csproj
```

## CI Integration

The GitHub Actions pipeline validates contracts automatically:

1. **build.yml** → `validate-contracts` job
   - Regenerates client from schema
   - Detects drift (uncommitted changes)
   - Detects breaking changes
   - Runs contract tests

### Handling CI Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| Drift detected | Schema changed, client not updated | Run `generate-client.ps1`, commit |
| Breaking change | API incompatibility | Add deprecation or version bump |
| Contract test fail | Schema structure issue | Fix Pydantic models |

## Pre-commit Hooks

Contract validation runs before each commit:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run contract-validation --all-files
```

## Best Practices

### Schema Design

1. **Always include operationId** - Required for client generation
2. **Use consistent naming** - snake_case for all identifiers
3. **Document all endpoints** - Include description and examples
4. **Version early** - Plan for evolution from the start

### Change Management

1. **Small, incremental changes** - Easier to review and roll back
2. **Announce deprecations** - Give consumers time to migrate
3. **Test both versions** - During coexistence period
4. **Monitor usage** - Track which versions are in use

### Error Handling

1. **Consistent error format** - Use standard error response schema
2. **Document error codes** - Include in OpenAPI schema
3. **Graceful degradation** - Handle version mismatches

## Related Documentation

- [API Migration Guide](./API_MIGRATION_GUIDE.md) - Migrating to generated client
- [Serialization Guide](./SERIALIZATION_GUIDE.md) - JSON naming conventions
- [NSwag README](../../tools/nswag/README.md) - Tooling details
- [ADR-007: IPC Architecture](../architecture/decisions/ADR-007-ipc-architecture.md)
