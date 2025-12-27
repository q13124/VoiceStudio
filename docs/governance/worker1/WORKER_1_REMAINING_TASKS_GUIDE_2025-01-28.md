# Worker 1: Remaining Tasks Guide
## Step-by-Step Implementation Guide

**Date:** 2025-01-28  
**Worker:** Worker 1 (Backend/Engines/Audio Processing Specialist)  
**Status:** ✅ **6/8 TASKS COMPLETE - 2 REMAINING**

---

## ✅ CURRENT STATUS

### Completed: 6/8 Tasks (75%)
- ✅ TASK 1.1: OpenAPI Schema Export
- ✅ TASK 1.4: Python Redaction Helper
- ✅ TASK 1.5: Backend Analytics Instrumentation
- ✅ TASK 1.6: Secrets Handling Service
- ✅ TASK 1.7: Dependency Audit Enhancement
- ✅ TASK 1.8: Minimal Privileges Documentation

### Remaining: 2/8 Tasks (25%)
- ⏳ TASK 1.2: C# Client Generation (script ready)
- ⏳ TASK 1.3: Contract Tests (depends on 1.2)

---

## 📋 TASK 1.2: C# Client Generation

### Status: ✅ Script Ready
**File:** `scripts/generate_csharp_client.ps1`

### Step-by-Step Execution:

#### Step 1: Verify Prerequisites
```powershell
# Check if OpenAPI schema exists
Test-Path "docs\api\openapi.json"

# If not, export it first
python scripts\export_openapi_schema.py
```

#### Step 2: Execute Script
```powershell
# Using NSwag (recommended)
.\scripts\generate_csharp_client.ps1 -Tool nswag

# Or using openapi-generator
.\scripts\generate_csharp_client.ps1 -Tool openapi-generator
```

**Expected Output:**
- `src/VoiceStudio.Core/Services/Generated/BackendClient.generated.cs`
- Typed client with all API endpoints
- Request/response models
- Exception classes

#### Step 3: Review Generated Code
- Check that all endpoints are included
- Verify model generation
- Check namespace: `VoiceStudio.Core.Services.Generated`
- Verify class name: `BackendClient`

#### Step 4: Create Adapter Wrapper
**File:** `src/VoiceStudio.Core/Services/BackendClientAdapter.cs`

**Purpose:**
- Wrap generated client
- Implement `IBackendClient` interface
- Add custom logic (retry, circuit breaker, logging)
- Maintain backward compatibility

**Template:**
```csharp
using System;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Services;
using VoiceStudio.Core.Services.Generated; // Generated namespace

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Adapter that wraps the generated BackendClient and implements IBackendClient.
    /// </summary>
    public class BackendClientAdapter : IBackendClient
    {
        private readonly BackendClient _generatedClient;
        private readonly IErrorLoggingService? _errorLoggingService;

        public BackendClientAdapter(
            BackendClient generatedClient,
            IErrorLoggingService? errorLoggingService = null)
        {
            _generatedClient = generatedClient ?? throw new ArgumentNullException(nameof(generatedClient));
            _errorLoggingService = errorLoggingService;
        }

        // Implement IBackendClient methods by delegating to generated client
        // Add retry logic, circuit breaker, logging as needed
    }
}
```

#### Step 5: Update ServiceProvider
**File:** `src/VoiceStudio.App/Services/ServiceProvider.cs`

**Changes Needed:**
1. Add field: `private static BackendClientAdapter? _backendClientAdapter;`
2. Initialize in `Initialize()` method
3. Update `GetBackendClient()` to return adapter
4. Maintain backward compatibility

---

## 📋 TASK 1.3: Contract Tests

### Status: ⏳ Pending (depends on TASK 1.2)

### Step-by-Step Implementation:

#### Step 1: Create Test Project
**File:** `tests/contract/VoiceStudio.ContractTests.csproj`

**Template:**
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
    <PackageReference Include="xunit" Version="2.6.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.3" />
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\VoiceStudio.Core\VoiceStudio.Core.csproj" />
    <ProjectReference Include="..\..\src\VoiceStudio.App\VoiceStudio.App.csproj" />
  </ItemGroup>
</Project>
```

#### Step 2: Create Test Base Class
**File:** `tests/contract/ContractTestBase.cs`

**Purpose:**
- Load OpenAPI schema
- Validate request/response models
- Compare with generated client

#### Step 3: Implement Schema Validation Tests
**File:** `tests/contract/SchemaValidationTests.cs`

**Tests to Implement:**
- Schema structure validation
- Endpoint path validation
- Request model validation
- Response model validation
- Parameter validation

#### Step 4: Implement Contract Tests
**File:** `tests/contract/ApiContractTests.cs`

**Tests to Implement:**
- All endpoints have corresponding methods in generated client
- Request models match OpenAPI schema
- Response models match OpenAPI schema
- Error responses match schema
- Required fields validation

#### Step 5: Integrate with CI/CD
**File:** `.github/workflows/contract-tests.yml`

**Purpose:**
- Run contract tests on API changes
- Fail build on contract drift
- Generate reports

---

## ✅ VERIFICATION CHECKLIST

### TASK 1.2 Verification:
- [ ] Script executed successfully
- [ ] Generated file exists
- [ ] All endpoints included
- [ ] Models generated correctly
- [ ] No compilation errors
- [ ] Adapter created
- [ ] ServiceProvider updated
- [ ] Backward compatibility maintained

### TASK 1.3 Verification:
- [ ] Test project created
- [ ] Tests compile
- [ ] All tests pass
- [ ] Schema validation works
- [ ] Contract drift detection works
- [ ] CI/CD integration complete

---

## 🎯 ESTIMATED TIME

### TASK 1.2: C# Client Generation
- **Script Execution:** ~15 minutes
- **Code Review:** ~30 minutes
- **Adapter Creation:** ~2-3 hours
- **ServiceProvider Update:** ~1 hour
- **Testing:** ~1 hour
- **Total:** ~4-6 hours

### TASK 1.3: Contract Tests
- **Test Project Setup:** ~1 hour
- **Test Implementation:** ~4-5 hours
- **CI/CD Integration:** ~1-2 hours
- **Total:** ~6-8 hours

**Combined Total:** ~10-14 hours

---

## 📝 NOTES

### TASK 1.2 Dependencies:
- ✅ OpenAPI schema exported
- ✅ Script created
- ⏳ NSwag or openapi-generator installation (script handles this)

### TASK 1.3 Dependencies:
- ⏳ TASK 1.2 complete (generated client needed)
- ✅ OpenAPI schema exported
- ✅ Python contract tests exist (reference)

### Potential Issues:
1. **NSwag Installation:** May require admin rights
2. **Generated Code:** May need manual adjustments
3. **Adapter Complexity:** May need custom logic for some endpoints
4. **Test Coverage:** Need to ensure all endpoints tested

---

## 🚀 QUICK START

### For TASK 1.2:
```powershell
# 1. Export OpenAPI schema (if not done)
python scripts\export_openapi_schema.py

# 2. Generate C# client
.\scripts\generate_csharp_client.ps1

# 3. Review generated code
# 4. Create adapter
# 5. Update ServiceProvider
```

### For TASK 1.3:
```powershell
# 1. Create test project
dotnet new xunit -n VoiceStudio.ContractTests -o tests\contract

# 2. Add project references
# 3. Implement tests
# 4. Run tests
dotnet test tests\contract
```

---

## ✅ CONCLUSION

**Status:** ✅ **GUIDE READY**

**Summary:**
- ✅ Step-by-step instructions provided
- ✅ Templates and examples included
- ✅ Verification checklists created
- ✅ Time estimates provided
- ✅ Quick start guides included

**Next Actions:**
1. Execute TASK 1.2 script
2. Follow step-by-step guide
3. Implement TASK 1.3 after 1.2 complete

---

**Status:** ✅ **GUIDE COMPLETE**  
**Last Updated:** 2025-01-28  
**Note:** All instructions and templates ready for implementation.
