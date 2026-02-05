# API Client Migration Guide

This guide documents the migration from manual HTTP client code to the NSwag-generated client.

## Overview

VoiceStudio uses two API client implementations:

| Client | Path | Purpose |
|--------|------|---------|
| Manual Client | `src/VoiceStudio.App/Services/BackendClient.cs` | Production client with retry logic, circuit breaker |
| Generated Client | `src/VoiceStudio.App/Services/Generated/BackendClient.g.cs` | Auto-generated from OpenAPI spec |

## Current State

The **manual client** (`BackendClient`) is the primary implementation used in production. It includes:
- Retry logic with exponential backoff
- Circuit breaker pattern for fault tolerance
- Custom error handling and logging
- WebSocket integration

The **generated client** (`GeneratedBackendClient`) is auto-generated from the OpenAPI specification using NSwag. It provides:
- Type-safe API calls matching the backend schema
- Auto-generated DTOs for request/response types
- Interface for dependency injection (`IGeneratedBackendClient`)

## Migration Strategy

### Phase 1: Coexistence (Current)

Both clients exist side-by-side. The manual client remains the production implementation while the generated client provides type reference.

```csharp
using Generated = VoiceStudio.App.Services.Generated;

// Manual client continues to work
await _backendClient.GetHealthAsync();

// Generated client available for reference
// var generatedClient = new Generated.GeneratedBackendClient(baseUrl, httpClient);
```

### Phase 2: DTO Migration

Replace hand-written DTOs with generated ones where the OpenAPI schema provides proper type definitions.

**Before:**
```csharp
public class EngineInfo
{
    public string Name { get; set; }
    public string Status { get; set; }
}
```

**After:**
```csharp
// Use generated type if available in Generated namespace
using EngineInfo = Generated.EngineInfo;
```

### Phase 3: Full Migration (Future)

Eventually, the generated client can replace the manual client entirely:

1. Extend generated client with retry/circuit breaker via partial class
2. Add WebSocket handling via extension methods
3. Deprecate manual client

## Using the Generated Client

### Initialization

```csharp
using VoiceStudio.App.Services.Generated;

var httpClient = new HttpClient();
var client = new GeneratedBackendClient("http://localhost:8000", httpClient);

// Configure JSON serialization (snake_case)
GeneratedBackendClient.UpdateJsonSerializerSettings = (settings) =>
{
    settings.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
};
```

### Type-Safe API Calls

```csharp
// Health check
var health = await client.Health_health_getAsync();

// Engine list
var engines = await client.List_engines_api_engines_getAsync();
```

## Serialization Consistency

Both clients must use the same serialization settings:

| Setting | Value | Notes |
|---------|-------|-------|
| Property Naming | snake_case | `PropertyNamingPolicy.SnakeCaseLower` |
| DateTime | ISO 8601 | `DateTimeOffset` with UTC |
| Null Handling | Include | Explicit null values preserved |

See `docs/developer/SERIALIZATION_GUIDE.md` for details.

## Regenerating the Client

When the OpenAPI schema changes:

```powershell
# Regenerate client
.\tools\nswag\generate-client.ps1 -Force

# Verify compilation
dotnet build src/VoiceStudio.App/VoiceStudio.App.csproj

# Verify no breaking changes
.\tools\nswag\verify-client.ps1
```

## Known Limitations

### OpenAPI 3.1 Nullable Types

The backend uses OpenAPI 3.1 which represents nullable types as:
```json
"schema": {
  "anyOf": [{ "type": "string" }, { "type": "null" }]
}
```

NSwag sometimes generates wrapper classes for these (e.g., `Engine_name`). These are safe to use but may look unusual.

### Empty Schemas

Many endpoints in the current OpenAPI spec return `{}` (empty schema), which generates as `object` return type. As the backend adds proper schema definitions, regenerate to get typed responses.

## Troubleshooting

### Build Errors After Regeneration

1. Check for breaking API changes in the schema
2. Verify namespace references are correct
3. Run `dotnet clean` then rebuild

### Type Mismatches

If generated types don't match expected format:
1. Check OpenAPI schema has proper type definitions
2. Verify NSwag configuration in `tools/nswag/nswag.json`
3. Review post-processing in `generate-client.ps1`

## Related Documentation

- [NSwag Tooling](../../tools/nswag/README.md)
- [Serialization Guide](./SERIALIZATION_GUIDE.md)
- [API Contract Guide](./API_CONTRACT_GUIDE.md)
- [ADR-007: IPC Architecture](../architecture/decisions/ADR-007-ipc-architecture.md)
