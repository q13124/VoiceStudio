# Worker 1 Prompt - Backend/Engines/Contracts/Security
## Complete Task Instructions

**Date:** 2025-01-28  
**Worker:** Worker 1 (Backend/Engines/Audio Processing Specialist)  
**Status:** 🚧 **READY FOR IMPLEMENTATION**

---

## 🎯 YOUR ROLE

You are **Worker 1**, responsible for:
- Backend API development and optimization
- Engine integrations and audio processing
- Data contracts and API schemas
- Security and dependency management
- Backend analytics and observability

---

## ✅ COMPLETED WORK (DO NOT REDO)

1. ✅ **OpenAPI Schema Export** - `scripts/export_openapi_schema.py` created, schema exported to `docs/api/openapi.json` (21 paths, version 1.0.0)
2. ✅ **HTTP Seed Data Script** - `scripts/seed_data_http.py` created for demo data via API
3. ✅ **C# Log Redaction Helper** - `src/VoiceStudio.App/Utilities/LogRedactionHelper.cs` created and integrated
4. ✅ **Dependency Audit Script** - `scripts/audit_dependencies.ps1` created (NuGet audit working, pip-audit needs installation)

---

## 📋 YOUR TASKS (8 TASKS - 30-40 HOURS)

### TASK 1.2: Strongly Typed C# Client Generation

**Priority:** HIGH  
**Estimated Time:** 4-6 hours  
**Status:** ⏳ **PENDING**

**Objective:** Generate strongly typed C# client from OpenAPI schema to ensure type safety and prevent API contract drift.

**Detailed Steps:**

1. **Install NSwag Tool:**
   ```powershell
   dotnet tool install -g NSwag.ConsoleCore
   ```

2. **Create Client Generation Script:**
   - File: `scripts/generate_client.ps1`
   - Script should:
     - Read `docs/api/openapi.json`
     - Generate C# client using NSwag
     - Output to `src/VoiceStudio.Core/Services/BackendClient.generated.cs`
     - Namespace: `VoiceStudio.Core.Services`
     - Client class name: `GeneratedBackendClient`
     - Use async/await patterns
     - Include XML documentation from OpenAPI

3. **Generate Client:**
   ```powershell
   nswag openapi2csclient `
     /input:docs/api/openapi.json `
     /output:src/VoiceStudio.Core/Services/BackendClient.generated.cs `
     /namespace:VoiceStudio.Core.Services `
     /clientClassAccessibility:public `
     /generateClientClasses:true `
     /generateClientInterfaces:false `
     /useHttpClientCreationMethod:true `
     /httpClientType:System.Net.Http.HttpClient `
     /useBaseUrl:true `
     /generateExceptionClasses:true `
     /exceptionClass:VoiceStudioException
   ```

4. **Create Adapter Class:**
   - File: `src/VoiceStudio.App/Services/BackendClientAdapter.cs`
   - Implements `IBackendClient` interface
   - Wraps `GeneratedBackendClient`
   - Maps generated methods to `IBackendClient` methods
   - Handles error conversion
   - Maintains backward compatibility

5. **Update ServiceProvider:**
   - File: `src/VoiceStudio.App/Services/ServiceProvider.cs`
   - Register `BackendClientAdapter` as `IBackendClient`
   - Ensure existing code continues to work

6. **Test Integration:**
   - Verify all API calls work
   - Test error handling
   - Test cancellation tokens
   - Test all endpoint methods

**Files to Create:**
- `scripts/generate_client.ps1`
- `src/VoiceStudio.Core/Services/BackendClient.generated.cs` (generated)
- `src/VoiceStudio.App/Services/BackendClientAdapter.cs`

**Files to Modify:**
- `src/VoiceStudio.App/Services/ServiceProvider.cs`

**Acceptance Criteria:**
- [ ] NSwag installed
- [ ] Generation script created
- [ ] Client generated successfully
- [ ] Adapter implements IBackendClient
- [ ] All existing code works
- [ ] All API endpoints have typed methods
- [ ] Error handling works correctly

---

### TASK 1.3: Contract Tests

**Priority:** HIGH  
**Estimated Time:** 6-8 hours  
**Dependencies:** OpenAPI schema (✅), Generated client (TASK 1.2)

**Objective:** Create contract tests that validate API contracts match OpenAPI schema and fail fast on breaking changes.

**Detailed Steps:**

1. **Create Contract Test Project:**
   - File: `tests/contract/VoiceStudio.ContractTests.csproj`
   - Target Framework: `net8.0`
   - Test Framework: MSTest
   - References: `VoiceStudio.Core`, `VoiceStudio.App`

2. **Install Required Packages:**
   ```xml
   <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.12.0" />
   <PackageReference Include="MSTest.TestAdapter" Version="3.4.3" />
   <PackageReference Include="MSTest.TestFramework" Version="3.4.3" />
   <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
   <PackageReference Include="JsonSchema.Net" Version="4.0.0" />
   ```

3. **Create Schema Validator:**
   - File: `tests/contract/SchemaValidator.cs`
   - Load OpenAPI schema from `docs/api/openapi.json`
   - Validate request DTOs against schema
   - Validate response DTOs against schema
   - Report mismatches with detailed errors

4. **Create Contract Test Base:**
   - File: `tests/contract/ContractTestBase.cs`
   - Setup: Load OpenAPI schema
   - Helper methods for validation
   - Common test utilities

5. **Create Endpoint Contract Tests:**
   - File: `tests/contract/ProfileContractTests.cs`
     - Test: `POST /api/profiles` request schema
     - Test: `GET /api/profiles` response schema
     - Test: `GET /api/profiles/{id}` response schema
     - Test: `PUT /api/profiles/{id}` request schema
     - Test: `DELETE /api/profiles/{id}` response schema
   
   - File: `tests/contract/ProjectContractTests.cs`
     - Test all project endpoint schemas
   
   - File: `tests/contract/VoiceContractTests.cs`
     - Test all voice synthesis endpoint schemas
   
   - File: `tests/contract/QualityContractTests.cs`
     - Test all quality endpoint schemas

6. **Create DTO Contract Tests:**
   - File: `tests/contract/DtoContractTests.cs`
   - For each DTO in `VoiceStudio.Core.Models`:
     - Validate structure matches OpenAPI schema
     - Validate required fields
     - Validate types
     - Validate formats (dates, UUIDs, etc.)

7. **Add CI/CD Integration:**
   - Update `.github/workflows/*.yml` (if exists)
   - Run contract tests on every PR
   - Fail PR if contracts don't match
   - Generate contract diff report

**Files to Create:**
- `tests/contract/VoiceStudio.ContractTests.csproj`
- `tests/contract/SchemaValidator.cs`
- `tests/contract/ContractTestBase.cs`
- `tests/contract/ProfileContractTests.cs`
- `tests/contract/ProjectContractTests.cs`
- `tests/contract/VoiceContractTests.cs`
- `tests/contract/QualityContractTests.cs`
- `tests/contract/DtoContractTests.cs`

**Acceptance Criteria:**
- [ ] Contract test project created
- [ ] Schema validator implemented
- [ ] All endpoint contracts tested
- [ ] All DTO contracts tested
- [ ] Tests fail when schema changes
- [ ] Contract diff report generated
- [ ] CI/CD integration complete

---

### TASK 1.4: Python Redaction Helper

**Priority:** MEDIUM  
**Estimated Time:** 2-3 hours  
**Status:** ⏳ **PENDING**

**Objective:** Create Python redaction helper for backend logs and test data, matching C# implementation.

**Detailed Steps:**

1. **Create Redaction Helper:**
   - File: `backend/utils/redaction.py`
   - Functions:
     - `redact_message(message: str) -> str` - Redact sensitive patterns in message
     - `redact_dict(data: dict) -> dict` - Redact sensitive values in dictionary
     - `redact_log_entry(entry: dict) -> dict` - Redact structured log entry
   - Patterns to redact:
     - API keys, tokens, secrets (regex: `(?i)(api[_-]?key|token|secret)\s*[:=]\s*([A-Za-z0-9-_]+)`)
     - Passwords (regex: `(?i)(password|passwd)\s*[:=]\s*([^\s]+)`)
     - SSN-like numbers (regex: `\b\d{3}[- ]?\d{2}[- ]?\d{4}\b`)
     - Card numbers (regex: `\b\d{16}\b`)
     - Email addresses (optional, configurable)
     - IP addresses (optional, configurable)

2. **Integrate with Structured Logging:**
   - File: `app/core/monitoring/structured_logging.py` (modify)
   - Apply redaction before writing logs
   - Add redaction flag: `redact_sensitive=True` (default: True)
   - Redact message, metadata, and exception details

3. **Create Test Data Redaction:**
   - File: `backend/utils/test_data_redaction.py`
   - Function: `redact_test_data(data: dict) -> dict`
   - Redact test data before export
   - Redact demo data in seed scripts
   - Support nested dictionaries

4. **Add Configuration:**
   - Environment variable: `VOICESTUDIO_ENABLE_REDACTION=true` (default: true)
   - Config file option in `backend/config.py` (if exists)
   - Disable redaction for debugging (if needed)

5. **Add Unit Tests:**
   - File: `tests/unit/backend/utils/test_redaction.py`
   - Test all redaction patterns
   - Test nested dictionaries
   - Test edge cases

**Files to Create:**
- `backend/utils/redaction.py`
- `backend/utils/test_data_redaction.py`
- `tests/unit/backend/utils/test_redaction.py`

**Files to Modify:**
- `app/core/monitoring/structured_logging.py`

**Acceptance Criteria:**
- [ ] Redaction helper created
- [ ] All patterns implemented
- [ ] Integrated with structured logging
- [ ] Test data redaction works
- [ ] Configuration options available
- [ ] Unit tests complete

---

### TASK 1.5: Backend Analytics Instrumentation

**Priority:** MEDIUM  
**Estimated Time:** 4-6 hours  
**Status:** ⏳ **PENDING**

**Objective:** Instrument key backend flows (import, editing, synthesis, export) with structured analytics events and correlation IDs.

**Detailed Steps:**

1. **Create Analytics Event Models:**
   - File: `backend/api/models/analytics.py`
   - Event types enum:
     - `ImportStart`, `ImportComplete`, `ImportFailed`
     - `EditStart`, `EditComplete`, `EditFailed`
     - `SynthesisStart`, `SynthesisComplete`, `SynthesisFailed`
     - `ExportStart`, `ExportComplete`, `ExportFailed`
   - Event model class:
     - `event_type: str`
     - `correlation_id: str`
     - `user_id: Optional[str]`
     - `timestamp: datetime`
     - `duration_ms: Optional[float]`
     - `success: bool`
     - `error_code: Optional[str]`
     - `properties: Dict[str, Any]`

2. **Create Analytics Service:**
   - File: `app/core/analytics/analytics_service.py`
   - Class: `AnalyticsService`
   - Methods:
     - `track_event(event_type: str, correlation_id: str, properties: dict) -> None`
     - `get_recent_events(limit: int = 100) -> List[AnalyticsEvent]`
     - `get_events_by_correlation(correlation_id: str) -> List[AnalyticsEvent]`
   - Store events in memory (circular buffer, max 1000 events)
   - Export events to structured logs
   - Thread-safe implementation

3. **Add Event Tracking to Routes:**
   - File: `backend/api/routes/voice.py` (modify)
     - Track `SynthesisStart` at route entry
     - Track `SynthesisComplete` or `SynthesisFailed` at route exit
     - Include correlation ID from request
     - Include duration, success, error_code
   
   - File: `backend/api/routes/profiles.py` (modify)
     - Track profile operations (create, update, delete)
   
   - File: `backend/api/routes/projects.py` (modify)
     - Track project operations
   
   - File: `backend/api/routes/audio.py` (if exists, modify)
     - Track import/export operations

4. **Create Analytics Endpoint:**
   - File: `backend/api/routes/analytics.py` (create)
   - Endpoint: `GET /api/analytics/events`
   - Query parameters:
     - `limit: int = 100` - Number of events to return
     - `event_type: Optional[str]` - Filter by event type
     - `since: Optional[datetime]` - Filter by timestamp
     - `correlation_id: Optional[str]` - Filter by correlation ID
   - Return: List of analytics events (JSON)

5. **Integrate with Correlation IDs:**
   - Use request ID middleware correlation IDs
   - Link analytics events to user actions
   - Support breadcrumb tracking
   - Export correlation IDs to structured logs

6. **Add Analytics to Main App:**
   - File: `backend/api/main.py` (modify)
   - Initialize AnalyticsService on startup
   - Register analytics endpoint
   - Export analytics events to structured logs

**Files to Create:**
- `backend/api/models/analytics.py`
- `backend/api/routes/analytics.py`
- `app/core/analytics/analytics_service.py`

**Files to Modify:**
- `backend/api/routes/voice.py`
- `backend/api/routes/profiles.py`
- `backend/api/routes/projects.py`
- `backend/api/main.py`

**Acceptance Criteria:**
- [ ] Analytics event models created
- [ ] AnalyticsService implemented
- [ ] Events tracked for all key flows
- [ ] Analytics endpoint created
- [ ] Events include correlation IDs
- [ ] Events exported to structured logs
- [ ] Thread-safe implementation

---

### TASK 1.6: Secrets Handling Service

**Priority:** HIGH  
**Estimated Time:** 4-6 hours  
**Status:** ⏳ **PENDING**

**Objective:** Centralize secrets handling using Windows Credential Manager for production and dev vault for development.

**Detailed Steps:**

1. **Create Secrets Service Interface:**
   - File: `src/VoiceStudio.Core/Services/ISecretsService.cs`
   - Methods:
     - `Task<string?> GetSecretAsync(string key, CancellationToken cancellationToken = default)`
     - `Task SetSecretAsync(string key, string value, CancellationToken cancellationToken = default)`
     - `Task DeleteSecretAsync(string key, CancellationToken cancellationToken = default)`
     - `Task<bool> HasSecretAsync(string key, CancellationToken cancellationToken = default)`
     - `Task<IReadOnlyDictionary<string, string>> GetAllSecretsAsync(CancellationToken cancellationToken = default)`

2. **Implement Windows Credential Manager:**
   - File: `src/VoiceStudio.App/Services/WindowsCredentialManagerSecretsService.cs`
   - Use `Windows.Security.Credentials.PasswordVault`
   - Resource name: `VoiceStudio.Secrets`
   - Username: secret key
   - Password: secret value
   - Scope: Application-specific
   - Handle exceptions gracefully

3. **Implement Dev Vault:**
   - File: `src/VoiceStudio.App/Services/DevVaultSecretsService.cs`
   - File-based secrets for development
   - File: `.dev/secrets.json` (gitignored)
   - JSON format: `{ "key1": "value1", "key2": "value2" }`
   - Optional encryption (AES, if needed)
   - Create `.dev/secrets.json.example` template

4. **Create Secrets Configuration:**
   - Environment variable: `VOICESTUDIO_SECRETS_PROVIDER=windows|dev`
   - Default: Windows for production, Dev for development
   - Auto-detect based on environment (Debug vs Release)
   - File: `src/VoiceStudio.App/Services/SecretsServiceFactory.cs`

5. **Audit Codebase for Hardcoded Secrets:**
   - Search for: API keys, tokens, passwords, connection strings
   - Files to check:
     - `src/VoiceStudio.App/Services/BackendClient.cs`
     - All ViewModels with API calls
     - Configuration files
   - Document findings

6. **Migrate Existing Secrets:**
   - Move hardcoded secrets to secrets service
   - Update all references
   - Test secret retrieval

7. **Add Secrets Validation:**
   - File: `src/VoiceStudio.App/Utilities/SecretsValidator.cs`
   - Check required secrets on app startup
   - Provide helpful error messages
   - List missing secrets

8. **Create Secrets Documentation:**
   - File: `docs/security/SECRETS_MANAGEMENT.md`
   - How to use secrets service
   - Required secrets list
   - How to set secrets (Windows Credential Manager)
   - How to set secrets (Dev vault)
   - Security best practices

**Files to Create:**
- `src/VoiceStudio.Core/Services/ISecretsService.cs`
- `src/VoiceStudio.App/Services/WindowsCredentialManagerSecretsService.cs`
- `src/VoiceStudio.App/Services/DevVaultSecretsService.cs`
- `src/VoiceStudio.App/Services/SecretsServiceFactory.cs`
- `src/VoiceStudio.App/Utilities/SecretsValidator.cs`
- `.dev/secrets.json.example`
- `docs/security/SECRETS_MANAGEMENT.md`

**Files to Modify:**
- `src/VoiceStudio.App/Services/ServiceProvider.cs` (register service)
- `src/VoiceStudio.App/App.xaml.cs` (validate secrets on startup)
- All files with hardcoded secrets (migrate)

**Acceptance Criteria:**
- [ ] Secrets service interface created
- [ ] Windows Credential Manager implementation complete
- [ ] Dev vault implementation complete
- [ ] Secrets factory created
- [ ] All hardcoded secrets migrated
- [ ] Secrets validation on startup
- [ ] Documentation complete

---

### TASK 1.7: Dependency Audit Enhancement

**Priority:** MEDIUM  
**Estimated Time:** 2-3 hours  
**Status:** ⏳ **PENDING** (Script exists, needs enhancement)

**Objective:** Enhance dependency audit script with detailed reporting and CI/CD integration.

**Detailed Steps:**

1. **Enhance Audit Script:**
   - File: `scripts/audit_dependencies.ps1` (modify)
   - Add detailed reporting:
     - Package name, version, vulnerabilities, severity, CVE IDs
     - Summary statistics
     - Color-coded output (green=safe, yellow=warning, red=critical)
   
   - Add export options:
     - JSON report: `reports/dependency_audit_YYYYMMDD.json`
     - HTML report: `reports/dependency_audit_YYYYMMDD.html`
     - CSV report: `reports/dependency_audit_YYYYMMDD.csv`

2. **Add Python Audit Setup:**
   - File: `requirements-dev.txt` (create or modify)
   - Add: `pip-audit>=2.6.0`
   - Add installation instructions in script
   - Auto-install if missing (with user confirmation)

3. **Create Report Generator:**
   - File: `scripts/generate_audit_report.ps1`
   - Generate HTML report from JSON
   - Include charts/graphs (if possible)
   - Include recommendations

4. **Add CI/CD Integration:**
   - Update `.github/workflows/*.yml` (if exists)
   - Run audit on every PR
   - Fail PR if critical vulnerabilities found
   - Generate report artifact
   - Comment on PR with summary

5. **Create Audit Documentation:**
   - File: `docs/security/DEPENDENCY_AUDIT.md`
   - How to run audit
   - How to interpret results
   - How to fix vulnerabilities
   - CI/CD integration details

**Files to Create/Modify:**
- `scripts/audit_dependencies.ps1` (enhance)
- `scripts/generate_audit_report.ps1` (create)
- `requirements-dev.txt` (create or modify)
- `docs/security/DEPENDENCY_AUDIT.md` (create)

**Acceptance Criteria:**
- [ ] Enhanced audit script with reporting
- [ ] pip-audit auto-installation
- [ ] JSON/HTML/CSV report generation
- [ ] CI/CD integration
- [ ] Documentation complete

---

### TASK 1.8: Minimal Privileges Documentation

**Priority:** MEDIUM  
**Estimated Time:** 3-4 hours  
**Status:** ⏳ **PENDING**

**Objective:** Document minimal privileges required for backend services and create test script.

**Detailed Steps:**

1. **Audit Current Privileges:**
   - Review backend service requirements
   - Document file system access needs:
     - Read: models directory, engines directory, config files
     - Write: logs directory, temp directory, cache directory
     - Execute: engine executables, Python scripts
   
   - Document network access needs:
     - Localhost: 8000 (FastAPI server)
     - Outbound: Hugging Face API (optional), model downloads
   
   - Document registry access (if any):
     - Windows registry keys accessed
     - Read vs write access

2. **Create Privileges Document:**
   - File: `docs/security/MINIMAL_PRIVILEGES.md`
   - Sections:
     - **File System Access:**
       - Required directories (read)
       - Required directories (write)
       - Required executables
     - **Network Access:**
       - Required ports
       - Required outbound connections
     - **Registry Access:**
       - Required keys (if any)
     - **User Data Access:**
       - AppData directories
       - User documents
     - **System Resources:**
       - CPU, memory limits
       - GPU access (if needed)

3. **Create Privilege Test Script:**
   - File: `scripts/test_minimal_privileges.ps1`
   - Test running with minimal privileges
   - Verify file system access
   - Verify network access
   - Verify functionality
   - Report missing privileges

4. **Document Service Account Setup:**
   - Instructions for running as Windows service
   - Required service account permissions
   - Security best practices
   - Least privilege principle

5. **Create Security Checklist:**
   - File: `docs/security/SECURITY_CHECKLIST.md`
   - Pre-deployment security checks
   - Privilege review
   - Access control review

**Files to Create:**
- `docs/security/MINIMAL_PRIVILEGES.md`
- `scripts/test_minimal_privileges.ps1`
- `docs/security/SECURITY_CHECKLIST.md`

**Acceptance Criteria:**
- [ ] Privileges audited and documented
- [ ] Test script created
- [ ] Service account setup documented
- [ ] Security checklist created
- [ ] Best practices included

---

## 📊 TASK SUMMARY

**Total Tasks:** 8  
**Estimated Time:** 30-40 hours  
**Priority Breakdown:**
- HIGH: 3 tasks (Client generation, Contract tests, Secrets handling)
- MEDIUM: 5 tasks (Redaction, Analytics, Audit, Privileges)

**Dependencies:**
- TASK 1.2 (Client generation) → TASK 1.3 (Contract tests)
- All other tasks are independent

---

## ✅ COMPLETION CRITERIA

### Code Complete
- [ ] All 8 tasks implemented
- [ ] All code compiles
- [ ] All tests passing
- [ ] No hardcoded secrets
- [ ] All API contracts validated

### Documentation Complete
- [ ] Secrets management documented
- [ ] Dependency audit documented
- [ ] Minimal privileges documented
- [ ] Security checklist created

### Integration Complete
- [ ] Generated client integrated
- [ ] Contract tests in CI/CD
- [ ] Analytics events tracked
- [ ] Redaction applied to all logs

---

## 🚀 START HERE

**Immediate Next Steps:**

1. **TASK 1.2: Client Generation** (Start here - unblocks contract tests)
   - Install NSwag
   - Create generation script
   - Generate client
   - Create adapter
   - Test integration

2. **TASK 1.6: Secrets Handling** (High priority - security)
   - Create interfaces
   - Implement Windows Credential Manager
   - Implement Dev vault
   - Audit and migrate secrets

3. **TASK 1.3: Contract Tests** (After client generation)
   - Create test project
   - Implement schema validator
   - Create contract tests
   - Add CI/CD integration

---

**Last Updated:** 2025-01-28  
**Status:** 🚧 **READY FOR IMPLEMENTATION**
