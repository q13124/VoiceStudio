# Contract Tests

This directory contains contract tests that validate API contracts match the OpenAPI schema.

## Purpose

Contract tests ensure that:
- API responses match the documented OpenAPI schema
- The generated C# client matches the OpenAPI schema
- API changes don't break client compatibility
- Request/response models are correctly generated
- Required fields are properly handled
- Schema drift is detected before deployment

## Test Files

| File | Description |
|------|-------------|
| `test_openapi_schema_drift.py` | Schema hash and drift detection tests |
| `test_api_contracts.py` | API response contract validation tests |
| `conftest.py` | Contract test fixtures and validators |
| `ApiContractTests.cs` | C# contract tests |
| `SchemaValidationTests.cs` | C# schema validation tests |

## Setup

### Prerequisites

1. **OpenAPI Schema:** Must be exported first
   ```powershell
   python scripts\export_openapi_schema.py
   ```

2. **Generated C# Client:** Must be generated first (TASK 1.2)
   ```powershell
   .\scripts\generate_csharp_client.ps1
   ```

3. **Test Project:** Create test project
   ```powershell
   dotnet new xunit -n VoiceStudio.ContractTests -o tests\contract
   ```

### Installation

1. Add project references:
   ```xml
   <ItemGroup>
     <ProjectReference Include="..\..\src\VoiceStudio.Core\VoiceStudio.Core.csproj" />
     <ProjectReference Include="..\..\src\VoiceStudio.App\VoiceStudio.App.csproj" />
   </ItemGroup>
   ```

2. Add NuGet packages:
   ```xml
   <ItemGroup>
     <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
     <PackageReference Include="xunit" Version="2.6.2" />
     <PackageReference Include="xunit.runner.visualstudio" Version="2.5.3" />
     <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
   </ItemGroup>
   ```

3. Copy template files:
   - `ContractTestBase.cs.template` → `ContractTestBase.cs`
   - `SchemaValidationTests.cs.template` → `SchemaValidationTests.cs`
   - `ApiContractTests.cs.template` → `ApiContractTests.cs`

4. Update namespaces and types as needed

## Running Tests

```powershell
# Run all contract tests
dotnet test tests\contract

# Run specific test class
dotnet test tests\contract --filter "FullyQualifiedName~SchemaValidationTests"

# Run with detailed output
dotnet test tests\contract --logger "console;verbosity=detailed"
```

## Test Structure

### ContractTestBase
Base class providing:
- OpenAPI schema loading
- Schema navigation helpers
- Property validation helpers

### SchemaValidationTests
Tests that validate:
- Schema structure and format
- Required sections exist
- Paths and operations are valid
- Components and schemas are properly defined

### ApiContractTests
Tests that validate:
- Generated client matches OpenAPI schema
- All endpoints have corresponding methods
- Request models match schema
- Response models match schema
- Required fields are properly handled

## CI/CD Integration

Add to `.github/workflows/test.yml`:

```yaml
- name: Run Contract Tests
  run: dotnet test tests/contract --logger "trx;LogFileName=contract-tests.trx"
```

## Updating Tests

When the OpenAPI schema changes:
1. Export updated schema: `python scripts\export_openapi_schema.py`
2. Regenerate client: `.\scripts\generate_csharp_client.ps1`
3. Run tests: `dotnet test tests\contract`
4. Fix any contract drift issues

## Troubleshooting

### Schema Not Found
- Ensure OpenAPI schema is exported: `python scripts\export_openapi_schema.py`
- Check path in `ContractTestBase.cs`

### Generated Client Not Found
- Ensure client is generated: `.\scripts\generate_csharp_client.ps1`
- Check namespace matches: `VoiceStudio.Core.Services.Generated`

### Tests Failing
- Review test output for specific failures
- Check that generated client matches schema
- Verify model property names match (snake_case vs PascalCase)
