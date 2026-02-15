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

- V1: `/api/v1/...` (deprecated as of 2026-07-01)
- V2: `/api/v2/...` (supported)
- V3: `/api/v3/...` (**current**, StandardResponse format)

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
# Preferred method - uses dedicated generation script
python scripts/generate_openapi.py

# With validation
python scripts/generate_openapi.py --validate

# Check for drift (CI usage)
python scripts/generate_openapi.py --check-drift

# Alternative - direct export (legacy)
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

1. **Consistent error format** - Use StandardResponse envelope for all errors
2. **Document error codes** - Include in OpenAPI schema
3. **Graceful degradation** - Handle version mismatches

## V3 StandardResponse Format

V3 API uses a consistent response envelope for all responses:

### Success Response

```python
from backend.api.v3.models import StandardResponse, ResponseStatus

# In endpoint implementation
return StandardResponse(
    status=ResponseStatus.SUCCESS,
    data={"items": [...], "count": 42},
    message="Operation completed successfully",
)
```

### Error Response

```python
from backend.api.v3.models import StandardResponse, ResponseStatus, ErrorDetail, ErrorCode

# In exception handler
return StandardResponse(
    status=ResponseStatus.ERROR,
    errors=[
        ErrorDetail(
            code=ErrorCode.INVALID_INPUT,
            message="Invalid audio format",
            field="audio_file",
            recovery_suggestion="Please upload a WAV or MP3 file",
        )
    ],
    message="Validation failed",
)
```

### StandardResponse Structure

| Field | Type | Description |
|-------|------|-------------|
| `status` | `ResponseStatus` | `SUCCESS`, `ERROR`, or `PARTIAL` |
| `data` | `T` | Response payload (success only) |
| `errors` | `List[ErrorDetail]` | Error details (error only) |
| `message` | `str` | Human-readable summary |
| `meta` | `RequestMeta` | Request ID, correlation ID, timestamp |
| `pagination` | `PaginationMeta` | Pagination info (if applicable) |

### ErrorDetail Structure

| Field | Type | Description |
|-------|------|-------------|
| `code` | `ErrorCode` | Machine-readable error code |
| `message` | `str` | Human-readable error message |
| `field` | `str` | Field that caused the error (optional) |
| `details` | `Dict` | Additional context (optional) |
| `recovery_suggestion` | `str` | How to fix the error (optional) |

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Permission denied |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Backend unavailable |

### Legacy Error Migration

All exception handlers now return v3 StandardResponse format. Legacy error codes are automatically mapped:

```python
from backend.api.error_handling import map_legacy_error_code, to_v3_error_response

# Map legacy code
v3_code = map_legacy_error_code(ErrorCodes.INVALID_INPUT)  # → "INVALID_INPUT"

# Create v3 error response
response = to_v3_error_response(
    error_code=ErrorCodes.VALIDATION_ERROR,
    message="Validation failed",
    request_id=request_id,
)
```

## Centralized Upload Service

Phase 2.3 introduced a centralized `UploadService` for handling multipart file uploads with consistent validation.

### Usage

```python
from fastapi import Depends, File, UploadFile
from backend.api.services.upload_service import (
    UploadService,
    UploadResult,
    UploadValidationConfig,
    get_upload_service,
)

@router.post("/upload", response_model=UploadResult)
async def upload_audio(
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(get_upload_service),
) -> UploadResult:
    config = UploadValidationConfig(
        allowed_mime_types=["audio/wav", "audio/mpeg", "audio/ogg"],
        max_size_bytes=100 * 1024 * 1024,  # 100MB
        allowed_categories=["audio"],
    )
    
    return await upload_service.process_upload(file, config)
```

### Features

- **File type detection**: Magic bytes + MIME type validation
- **Size validation**: Configurable min/max limits
- **Category filtering**: audio, video, image, document, model
- **Checksum generation**: SHA-256 for integrity
- **Secure storage**: UUID-based filenames
- **Temp file cleanup**: Automatic cleanup of stale uploads

### UploadResult Model

| Field | Type | Description |
|-------|------|-------------|
| `file_id` | `str` | Unique file identifier (UUID) |
| `filename` | `str` | Original filename |
| `stored_path` | `str` | Storage location path |
| `size_bytes` | `int` | File size |
| `mime_type` | `str` | Detected MIME type |
| `category` | `str` | File category |
| `checksum` | `str` | SHA-256 checksum (optional) |
| `upload_timestamp` | `str` | ISO timestamp |

## Related Documentation

- [API Migration Guide](./API_MIGRATION_GUIDE.md) - Migrating to generated client
- [Serialization Guide](./SERIALIZATION_GUIDE.md) - JSON naming conventions
- [NSwag README](../../tools/nswag/README.md) - Tooling details
- [ADR-007: IPC Boundary](../architecture/decisions/ADR-007-ipc-boundary.md)
