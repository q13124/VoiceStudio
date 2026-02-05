# NSwag Client Generation

This directory contains tooling for generating C# API clients from the VoiceStudio backend OpenAPI specification.

## Overview

The VoiceStudio backend exposes an OpenAPI 3.1.0 specification that documents all available API endpoints. We use NSwag to automatically generate a typed C# HTTP client from this specification, ensuring the frontend always has up-to-date type definitions.

## Files

| File | Purpose |
|------|---------|
| `nswag.json` | NSwag configuration file |
| `generate-client.ps1` | PowerShell script to run client generation |
| `verify-client.ps1` | PowerShell script to verify generated client |
| `validate-contract.py` | Python script for contract validation |
| `detect-breaking-changes.py` | Breaking change detection between API versions |

## Prerequisites

- .NET SDK 8.0+
- NSwag CLI (`dotnet tool install -g NSwag.ConsoleCore`)
- Valid OpenAPI schema at `docs/api/openapi.json`

## Usage

### Generate Client

```powershell
# Standard generation
.\tools\nswag\generate-client.ps1

# Force regeneration even if up-to-date
.\tools\nswag\generate-client.ps1 -Force

# Verbose output
.\tools\nswag\generate-client.ps1 -Verbose

# Validate only (check if regeneration needed)
.\tools\nswag\generate-client.ps1 -ValidateOnly
```

### Verify Client

```powershell
# Full verification (includes build)
.\tools\nswag\verify-client.ps1

# Quick verification (skip build)
.\tools\nswag\verify-client.ps1 -Quick
```

### Validate Contract

```bash
# Basic validation - verify C# client matches OpenAPI schema
python tools/nswag/validate-contract.py

# Include breaking change detection
python tools/nswag/validate-contract.py --check-breaking

# JSON output for CI integration
python tools/nswag/validate-contract.py --json
```

### Detect Breaking Changes

```bash
# Compare current schema against last git commit
python tools/nswag/detect-breaking-changes.py

# Compare against specific baseline
python tools/nswag/detect-breaking-changes.py --baseline path/to/old-schema.json

# JSON output
python tools/nswag/detect-breaking-changes.py --json
```

Breaking change detection catches:
- Removed endpoints
- Removed HTTP methods
- Removed required parameters
- New required parameters (breaks existing clients)
- Removed success response codes

### Run Contract Tests

Contract tests validate that the OpenAPI schema and generated client are correct and consistent.

```bash
# Python contract tests (schema structure validation)
python -m pytest tests/contract/test_openapi_contract.py -v

# C# contract tests (client/schema alignment)
dotnet test tests/contract/VoiceStudio.ContractTests.csproj
```

Contract tests verify:
- Schema structure (required fields, valid version)
- Endpoint definitions (operationId, responses)
- Critical endpoints exist (health, metrics)
- Schema definitions have types
- OperationIds are valid C# identifiers
- Generated client methods match schema endpoints
- Request/response models match schema

## Generated Output

The generated client is output to:
```
src/VoiceStudio.App/Services/Generated/BackendClient.g.cs
```

This file contains:
- `GeneratedBackendClient` class - HTTP client with typed methods
- `IGeneratedBackendClient` interface - Interface for dependency injection
- DTO classes - Request/response types matching Pydantic models

## Configuration Details

Key settings in `nswag.json`:

| Setting | Value | Description |
|---------|-------|-------------|
| `className` | `GeneratedBackendClient` | Generated client class name |
| `namespace` | `VoiceStudio.App.Services.Generated` | C# namespace |
| `jsonLibrary` | `SystemTextJson` | JSON serializer (matches WinUI) |
| `generateNullableReferenceTypes` | `true` | C# nullable reference types |
| `dateTimeType` | `System.DateTimeOffset` | DateTime handling |

## Integration with CI

The client generation is integrated into the CI pipeline:

1. Backend starts and exports OpenAPI schema
2. Schema is validated for completeness
3. NSwag generates C# client
4. Build verifies generated code compiles
5. Drift detection checks for uncommitted changes
6. Breaking change detection runs
7. Python contract tests validate schema structure
8. C# contract tests validate client/schema alignment

## Pre-commit Hook

Contract validation runs as a pre-commit hook to catch issues early:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run contract-validation --all-files
```

The hook validates:
- OpenAPI schema is valid JSON
- Schema has required fields
- All endpoints have operationIds
- Schema and client are in sync (warns if schema changed but client not updated)

## Troubleshooting

### NSwag not found

```powershell
dotnet tool install -g NSwag.ConsoleCore
```

### OpenAPI schema not found

Ensure the backend has exported the schema:
```powershell
cd backend
python -c "from api.main import app; import json; print(json.dumps(app.openapi()))" > ../docs/api/openapi.json
```

### Build errors in generated code

If the generated code has compile errors:
1. Check OpenAPI schema is valid
2. Verify Pydantic models have complete type annotations
3. Check for circular references in models

## Related Documentation

- [API Contract Guide](../../docs/developer/API_CONTRACT_GUIDE.md)
- [Serialization Guide](../../docs/developer/SERIALIZATION_GUIDE.md)
- [ADR-007: IPC Architecture](../../docs/architecture/decisions/ADR-007-ipc-architecture.md)
