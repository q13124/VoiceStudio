# Comprehensive Finish Plan - VoiceStudio Quantum+
## Complete Task Distribution Across All Workers

**Date:** 2025-01-28  
**Overseer:** ACTIVE  
**Status:** 🚧 **MASTER PLAN - ALL TASKS DETAILED**

---

## 📋 EXECUTIVE SUMMARY

This document provides **extremely detailed** task breakdowns for completing VoiceStudio Quantum+ to production-ready state. All tasks are distributed across Worker 1 (Backend/Engines), Worker 2 (UI/UX), and Worker 3 (Testing/QA/Documentation).

**Total Tasks:** 50+ detailed tasks across 8 major categories  
**Estimated Completion:** 2-3 weeks with all workers active  
**Current Status:** ~90% code complete, ~85% overall complete

---

## 🎯 WORKER 1: BACKEND / ENGINES / CONTRACTS / SECURITY

### TASK 1.1: OpenAPI Schema Export & Versioning ✅ COMPLETE

**Status:** ✅ **COMPLETE** - Schema exported to `docs/api/openapi.json`

**Completed:**
- ✅ OpenAPI export script created (`scripts/export_openapi_schema.py`)
- ✅ Schema exported (21 paths, version 1.0.0)
- ✅ Schema committed to `docs/api/openapi.json`

**Next Steps:**
- Add versioning strategy documentation
- Add schema validation in CI/CD

---

### TASK 1.2: Strongly Typed C# Client Generation

**Priority:** HIGH  
**Estimated Time:** 4-6 hours  
**Dependencies:** OpenAPI schema (✅ complete)

**Detailed Steps:**

1. **Choose Code Generator:**
   - Option A: NSwag (recommended - .NET native)
   - Option B: AutoRest (Microsoft official)
   - Option C: Swashbuckle + manual client
   - **Decision:** Use NSwag for C# client generation

2. **Install NSwag:**
   ```powershell
   dotnet tool install -g NSwag.ConsoleCore
   ```

3. **Create Generation Script:**
   - File: `scripts/generate_client.ps1`
   - Input: `docs/api/openapi.json`
   - Output: `src/VoiceStudio.Core/Services/BackendClient.generated.cs`
   - Namespace: `VoiceStudio.Core.Services`

4. **Generate Client:**
   ```powershell
   nswag openapi2csclient /input:docs/api/openapi.json /output:src/VoiceStudio.Core/Services/BackendClient.generated.cs /namespace:VoiceStudio.Core.Services /clientClassAccessibility:public
   ```

5. **Wire Generated Client:**
   - Create adapter class that implements `IBackendClient`
   - Map generated client methods to `IBackendClient` interface
   - File: `src/VoiceStudio.App/Services/BackendClientAdapter.cs`

6. **Update ServiceProvider:**
   - Register generated client in DI container
   - Ensure backward compatibility with existing `BackendClient`

7. **Test Integration:**
   - Verify all API calls work with generated client
   - Test error handling
   - Test cancellation tokens

**Files to Create/Modify:**
- `scripts/generate_client.ps1` (create)
- `src/VoiceStudio.Core/Services/BackendClient.generated.cs` (generated)
- `src/VoiceStudio.App/Services/BackendClientAdapter.cs` (create)
- `src/VoiceStudio.App/Services/ServiceProvider.cs` (modify)

**Acceptance Criteria:**
- [ ] Generated client compiles without errors
- [ ] All API endpoints have typed methods
- [ ] Adapter implements `IBackendClient` correctly
- [ ] Existing code works with adapter
- [ ] No breaking changes to existing functionality

---

### TASK 1.3: Contract Tests

**Priority:** HIGH  
**Estimated Time:** 6-8 hours  
**Dependencies:** OpenAPI schema (✅ complete), Generated client (TASK 1.2)

**Detailed Steps:**

1. **Create Contract Test Project:**
   - File: `tests/contract/VoiceStudio.ContractTests.csproj`
   - Framework: .NET 8
   - Test Framework: MSTest or xUnit

2. **Install Required Packages:**
   - `Microsoft.NET.Test.Sdk`
   - `MSTest.TestAdapter` / `xunit`
   - `Newtonsoft.Json` (for schema validation)
   - `JsonSchema.Net` (for JSON schema validation)

3. **Create Schema Validator:**
   - File: `tests/contract/SchemaValidator.cs`
   - Load OpenAPI schema from `docs/api/openapi.json`
   - Validate request/response DTOs against schema
   - Report mismatches

4. **Create Contract Test Base:**
   - File: `tests/contract/ContractTestBase.cs`
   - Setup/teardown for contract tests
   - Helper methods for validation

5. **Create Endpoint Contract Tests:**
   - File: `tests/contract/ProfileContractTests.cs`
   - File: `tests/contract/ProjectContractTests.cs`
   - File: `tests/contract/VoiceContractTests.cs`
   - File: `tests/contract/QualityContractTests.cs`
   - Test each endpoint's request/response schema

6. **Create DTO Contract Tests:**
   - File: `tests/contract/DtoContractTests.cs`
   - Validate all DTOs in `VoiceStudio.Core.Models` match OpenAPI schema
   - Test required fields, types, formats

7. **Add CI/CD Integration:**
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
- [ ] All contract tests pass
- [ ] Tests fail when schema changes
- [ ] Contract diff report generated
- [ ] CI/CD integration complete

---

### TASK 1.4: Python Redaction Helper

**Priority:** MEDIUM  
**Estimated Time:** 2-3 hours  
**Dependencies:** None

**Detailed Steps:**

1. **Create Redaction Helper:**
   - File: `backend/utils/redaction.py`
   - Functions: `redact_message()`, `redact_dict()`, `redact_log_entry()`
   - Patterns: API keys, tokens, passwords, PII, card numbers

2. **Integrate with Structured Logging:**
   - File: `app/core/monitoring/structured_logging.py` (modify)
   - Apply redaction before writing logs
   - Configurable redaction (enable/disable)

3. **Create Test Data Redaction:**
   - File: `backend/utils/test_data_redaction.py`
   - Redact test data before export
   - Redact demo data in seed scripts

4. **Add Configuration:**
   - Environment variable: `VOICESTUDIO_ENABLE_REDACTION=true`
   - Config file option
   - Default: enabled

**Files to Create/Modify:**
- `backend/utils/redaction.py` (create)
- `app/core/monitoring/structured_logging.py` (modify)
- `backend/utils/test_data_redaction.py` (create)

**Acceptance Criteria:**
- [ ] Redaction helper created
- [ ] Integrated with structured logging
- [ ] Test data redaction works
- [ ] Configuration options available

---

### TASK 1.5: Backend Analytics Instrumentation

**Priority:** MEDIUM  
**Estimated Time:** 4-6 hours  
**Dependencies:** Structured logging (✅ exists)

**Detailed Steps:**

1. **Create Analytics Event Types:**
   - File: `backend/api/models/analytics.py`
   - Event types: ImportStart, ImportComplete, EditStart, EditComplete, SynthesisStart, SynthesisComplete, ExportStart, ExportComplete
   - Event properties: user_id, correlation_id, duration_ms, success, error_code

2. **Add Event Tracking to Routes:**
   - File: `backend/api/routes/voice.py` (modify)
   - File: `backend/api/routes/profiles.py` (modify)
   - File: `backend/api/routes/projects.py` (modify)
   - Track start/complete events for key operations

3. **Create Analytics Service:**
   - File: `app/core/analytics/analytics_service.py`
   - Store events in memory (circular buffer)
   - Export events to structured logs
   - Support querying recent events

4. **Add Analytics Endpoint:**
   - File: `backend/api/routes/analytics.py` (create)
   - Endpoint: `GET /api/analytics/events`
   - Query parameters: limit, event_type, since
   - Return recent events

5. **Integrate with Correlation IDs:**
   - Use request ID middleware correlation IDs
   - Link events to user actions
   - Support breadcrumb tracking

**Files to Create/Modify:**
- `backend/api/models/analytics.py` (create)
- `backend/api/routes/analytics.py` (create)
- `app/core/analytics/analytics_service.py` (create)
- `backend/api/routes/voice.py` (modify)
- `backend/api/routes/profiles.py` (modify)
- `backend/api/routes/projects.py` (modify)

**Acceptance Criteria:**
- [ ] Analytics events tracked for all key flows
- [ ] Events include correlation IDs
- [ ] Analytics endpoint returns events
- [ ] Events exported to structured logs

---

### TASK 1.6: Secrets Handling Service

**Priority:** HIGH  
**Estimated Time:** 4-6 hours  
**Dependencies:** None

**Detailed Steps:**

1. **Create Secrets Service Interface:**
   - File: `src/VoiceStudio.Core/Services/ISecretsService.cs`
   - Methods: `GetSecret(string key)`, `SetSecret(string key, string value)`, `DeleteSecret(string key)`, `HasSecret(string key)`

2. **Implement Windows Credential Manager:**
   - File: `src/VoiceStudio.App/Services/WindowsCredentialManagerSecretsService.cs`
   - Use `Windows.Security.Credentials.PasswordVault`
   - Store secrets in Windows Credential Manager
   - Scope: Application-specific

3. **Implement Dev Vault:**
   - File: `src/VoiceStudio.App/Services/DevVaultSecretsService.cs`
   - File-based secrets for development
   - File: `.dev/secrets.json` (gitignored)
   - JSON format with encryption (optional)

4. **Create Secrets Configuration:**
   - Environment variable: `VOICESTUDIO_SECRETS_PROVIDER=windows|dev`
   - Default: Windows for production, Dev for development
   - Auto-detect based on environment

5. **Migrate Existing Secrets:**
   - Audit codebase for hardcoded secrets
   - Move to secrets service
   - Update all references

6. **Add Secrets Validation:**
   - Check required secrets on startup
   - Provide helpful error messages
   - Document required secrets

**Files to Create:**
- `src/VoiceStudio.Core/Services/ISecretsService.cs`
- `src/VoiceStudio.App/Services/WindowsCredentialManagerSecretsService.cs`
- `src/VoiceStudio.App/Services/DevVaultSecretsService.cs`
- `.dev/secrets.json.example` (template)

**Files to Modify:**
- `src/VoiceStudio.App/Services/ServiceProvider.cs` (register service)
- All files with hardcoded secrets (migrate)

**Acceptance Criteria:**
- [ ] Secrets service interface created
- [ ] Windows Credential Manager implementation complete
- [ ] Dev vault implementation complete
- [ ] All hardcoded secrets migrated
- [ ] Secrets validation on startup
- [ ] Documentation for required secrets

---

### TASK 1.7: Dependency Audit Enhancement

**Priority:** MEDIUM  
**Estimated Time:** 2-3 hours  
**Dependencies:** Audit script (✅ exists)

**Detailed Steps:**

1. **Enhance Audit Script:**
   - File: `scripts/audit_dependencies.ps1` (modify)
   - Add detailed reporting
   - Export to JSON/HTML report
   - Include version information

2. **Add Python Audit Setup:**
   - Install pip-audit in requirements-dev.txt
   - Add installation instructions
   - Auto-install if missing

3. **Create Audit Report Format:**
   - JSON report: `reports/dependency_audit_YYYYMMDD.json`
   - HTML report: `reports/dependency_audit_YYYYMMDD.html`
   - Include: package name, version, vulnerabilities, severity, CVE IDs

4. **Add CI/CD Integration:**
   - Run audit on every PR
   - Fail PR if critical vulnerabilities found
   - Generate report artifact

5. **Create Audit Documentation:**
   - File: `docs/security/DEPENDENCY_AUDIT.md`
   - How to run audit
   - How to interpret results
   - How to fix vulnerabilities

**Files to Create/Modify:**
- `scripts/audit_dependencies.ps1` (enhance)
- `requirements-dev.txt` (add pip-audit)
- `docs/security/DEPENDENCY_AUDIT.md` (create)

**Acceptance Criteria:**
- [ ] Enhanced audit script with reporting
- [ ] pip-audit auto-installation
- [ ] JSON/HTML report generation
- [ ] CI/CD integration
- [ ] Documentation complete

---

### TASK 1.8: Minimal Privileges Documentation

**Priority:** MEDIUM  
**Estimated Time:** 3-4 hours  
**Dependencies:** None

**Detailed Steps:**

1. **Audit Current Privileges:**
   - Review backend service requirements
   - Document file system access needs
   - Document network access needs
   - Document registry access (if any)

2. **Create Privileges Document:**
   - File: `docs/security/MINIMAL_PRIVILEGES.md`
   - Sections: File System, Network, Registry, User Data, System Resources
   - Document required vs. optional privileges

3. **Create Privilege Test Script:**
   - File: `scripts/test_minimal_privileges.ps1`
   - Test running with minimal privileges
   - Verify functionality
   - Report missing privileges

4. **Document Service Account Setup:**
   - Instructions for running as service
   - Required service account permissions
   - Security best practices

**Files to Create:**
- `docs/security/MINIMAL_PRIVILEGES.md`
- `scripts/test_minimal_privileges.ps1`

**Acceptance Criteria:**
- [ ] Privileges documented
- [ ] Test script created
- [ ] Service account setup documented
- [ ] Security best practices included

---

## 🎨 WORKER 2: UI/UX / CONTROLS / LOCALIZATION / PACKAGING

### TASK 2.1: Resource Files for Localization

**Priority:** HIGH  
**Estimated Time:** 8-10 hours  
**Dependencies:** None

**Detailed Steps:**

1. **Create Resource File Structure:**
   - File: `src/VoiceStudio.App/Resources/Resources.resw` (create)
   - File: `src/VoiceStudio.App/Resources/en-US/Resources.resw` (create)
   - File: `src/VoiceStudio.App/Resources/es-ES/Resources.resw` (create - optional)
   - File: `src/VoiceStudio.App/Resources/fr-FR/Resources.resw` (create - optional)

2. **Extract Hardcoded Strings:**
   - Audit all ViewModels for hardcoded strings
   - Audit all XAML files for hardcoded text
   - Create resource keys for all strings
   - Format: `ResourceKey.Description` (e.g., `Button.Save`, `Error.ProfileNotFound`)

3. **Create Resource Helper:**
   - File: `src/VoiceStudio.App/Utilities/ResourceHelper.cs`
   - Method: `GetString(string key, params object[] args)`
   - Load from Resources.resw
   - Support string formatting

4. **Update ViewModels:**
   - Replace hardcoded strings with resource keys
   - Use ResourceHelper.GetString()
   - Test all ViewModels

5. **Update XAML:**
   - Replace hardcoded Text with x:Uid
   - Use resource references
   - Test all XAML files

6. **Create Resource Key Documentation:**
   - File: `docs/developer/RESOURCE_KEYS.md`
   - List all resource keys
   - Usage examples
   - Naming conventions

**Files to Create:**
- `src/VoiceStudio.App/Resources/Resources.resw`
- `src/VoiceStudio.App/Resources/en-US/Resources.resw`
- `src/VoiceStudio.App/Utilities/ResourceHelper.cs`
- `docs/developer/RESOURCE_KEYS.md`

**Files to Modify:**
- All ViewModels with hardcoded strings (50+ files)
- All XAML files with hardcoded text (150+ files)

**Acceptance Criteria:**
- [ ] Resource files created
- [ ] All hardcoded strings extracted
- [ ] ResourceHelper implemented
- [ ] All ViewModels use resources
- [ ] All XAML uses resources
- [ ] Documentation complete

---

### TASK 2.2: Locale Switch Toggle

**Priority:** MEDIUM  
**Estimated Time:** 4-6 hours  
**Dependencies:** Resource files (TASK 2.1)

**Detailed Steps:**

1. **Create Localization Service:**
   - File: `src/VoiceStudio.App/Services/LocalizationService.cs`
   - Interface: `ILocalizationService`
   - Methods: `GetCurrentLocale()`, `SetLocale(string locale)`, `GetString(string key)`
   - Event: `LocaleChanged`

2. **Create Locale Switch Control:**
   - File: `src/VoiceStudio.App/Controls/LocaleSwitchControl.xaml` + `.xaml.cs`
   - Dropdown/ComboBox with available locales
   - Visual indicator of current locale
   - Accessible (keyboard navigation, screen reader support)

3. **Add to Settings Panel:**
   - File: `src/VoiceStudio.App/Views/Panels/SettingsView.xaml` (modify)
   - Add locale switch control
   - Save locale preference
   - Load locale on startup

4. **Implement Locale Persistence:**
   - Save locale to user settings
   - Load locale on app startup
   - Apply locale immediately on change

5. **Test Locale Switching:**
   - Test all supported locales
   - Verify UI updates immediately
   - Test with different resource files

**Files to Create:**
- `src/VoiceStudio.App/Services/ILocalizationService.cs`
- `src/VoiceStudio.App/Services/LocalizationService.cs`
- `src/VoiceStudio.App/Controls/LocaleSwitchControl.xaml` + `.xaml.cs`

**Files to Modify:**
- `src/VoiceStudio.App/Views/Panels/SettingsView.xaml`
- `src/VoiceStudio.App/Services/ServiceProvider.cs`

**Acceptance Criteria:**
- [ ] LocalizationService implemented
- [ ] Locale switch control created
- [ ] Added to settings panel
- [ ] Locale persistence works
- [ ] UI updates on locale change
- [ ] All locales tested

---

### TASK 2.3: Toast Styles & Standardization

**Priority:** HIGH  
**Estimated Time:** 4-6 hours  
**Dependencies:** DesignTokens (✅ exists)

**Detailed Steps:**

1. **Create Toast Styles Resource:**
   - File: `src/VoiceStudio.App/Resources/ToastStyles.xaml`
   - Styles: SuccessToast, ErrorToast, WarningToast, InfoToast
   - Use VSQ.* design tokens
   - Consistent animations

2. **Enhance ToastNotificationService:**
   - File: `src/VoiceStudio.App/Services/ToastNotificationService.cs` (modify)
   - Add methods: `ShowSuccess()`, `ShowError()`, `ShowWarning()`, `ShowInfo()`
   - Apply toast styles automatically
   - Support custom duration

3. **Create Toast Control:**
   - File: `src/VoiceStudio.App/Controls/ToastNotification.xaml` + `.xaml.cs`
   - Reusable toast component
   - Support icons, messages, actions
   - Accessibility (keyboard dismiss, screen reader)

4. **Update All Toast Calls:**
   - Audit all `ToastNotificationService` usage
   - Replace with typed methods (ShowSuccess, ShowError, etc.)
   - Ensure consistent styling

5. **Add Toast Queue Management:**
   - Limit concurrent toasts
   - Queue overflow handling
   - Dismiss animations

**Files to Create:**
- `src/VoiceStudio.App/Resources/ToastStyles.xaml`
- `src/VoiceStudio.App/Controls/ToastNotification.xaml` + `.xaml.cs`

**Files to Modify:**
- `src/VoiceStudio.App/Services/ToastNotificationService.cs`
- All files using ToastNotificationService (50+ files)

**Acceptance Criteria:**
- [ ] Toast styles created
- [ ] Toast control created
- [ ] ToastNotificationService enhanced
- [ ] All toast calls updated
- [ ] Queue management implemented
- [ ] Accessibility support complete

---

### TASK 2.4: Empty States & Loading Skeletons Standardization

**Priority:** MEDIUM  
**Estimated Time:** 6-8 hours  
**Dependencies:** EmptyState control (✅ exists), SkeletonScreen (✅ exists)

**Detailed Steps:**

1. **Audit Existing Empty States:**
   - Review all panels for empty states
   - Document current implementations
   - Identify inconsistencies

2. **Enhance EmptyState Control:**
   - File: `src/VoiceStudio.App/Controls/EmptyState.xaml` (modify)
   - Standardize props: Title, Message, Icon, ActionButton
   - Use VSQ.* design tokens
   - Accessibility support

3. **Enhance SkeletonScreen Control:**
   - File: `src/VoiceStudio.App/Controls/SkeletonScreen.xaml` (modify)
   - Standardize skeleton patterns
   - Support different content types (list, card, form)
   - Smooth animations

4. **Create Empty State Patterns:**
   - File: `docs/design/EMPTY_STATE_PATTERNS.md`
   - Document patterns for different scenarios
   - Code examples
   - Best practices

5. **Update All Panels:**
   - Replace custom empty states with EmptyState control
   - Replace custom loading with SkeletonScreen
   - Ensure consistency

6. **Test Empty States:**
   - Test all panels with no data
   - Verify empty states display correctly
   - Test loading states

**Files to Create/Modify:**
- `src/VoiceStudio.App/Controls/EmptyState.xaml` (enhance)
- `src/VoiceStudio.App/Controls/SkeletonScreen.xaml` (enhance)
- `docs/design/EMPTY_STATE_PATTERNS.md` (create)

**Files to Modify:**
- All panels with custom empty states (30+ files)
- All panels with custom loading (30+ files)

**Acceptance Criteria:**
- [ ] EmptyState control standardized
- [ ] SkeletonScreen control standardized
- [ ] All panels use standardized controls
- [ ] Patterns documented
- [ ] All empty/loading states tested

---

### TASK 2.5: Microcopy Guide

**Priority:** MEDIUM  
**Estimated Time:** 4-6 hours  
**Dependencies:** None

**Detailed Steps:**

1. **Create Microcopy Guide:**
   - File: `docs/design/MICROCOPY_GUIDE.md`
   - Sections: Button Verbs, Error Messages, Titles, Toast Messages, Tooltips, Help Text

2. **Document Button Verb Patterns:**
   - Action verbs: Save, Delete, Create, Edit, Export, Import
   - Avoid: Click, Press, Use
   - Examples and anti-patterns

3. **Document Error Message Patterns:**
   - User-friendly language
   - Actionable messages
   - Avoid technical jargon
   - Examples and templates

4. **Document Title Conventions:**
   - Panel titles
   - Dialog titles
   - Section headings
   - Consistency rules

5. **Document Toast Message Patterns:**
   - Success messages
   - Error messages
   - Warning messages
   - Info messages
   - Examples

6. **Create Microcopy Checklist:**
   - Checklist for reviewing UI text
   - Common mistakes to avoid
   - Review process

**Files to Create:**
- `docs/design/MICROCOPY_GUIDE.md`

**Acceptance Criteria:**
- [ ] Microcopy guide complete
- [ ] All patterns documented
- [ ] Examples provided
- [ ] Checklist created
- [ ] Review process defined

---

### TASK 2.6: Packaging Script & Smoke Checklist

**Priority:** HIGH  
**Estimated Time:** 6-8 hours  
**Dependencies:** None

**Detailed Steps:**

1. **Create Packaging Script:**
   - File: `scripts/package_release.ps1`
   - Steps:
     - Clean build directories
     - Restore NuGet packages
     - Build in Release mode
     - Run tests
     - Create MSIX package
     - Sign package (if certificate available)
     - Generate release notes
     - Create installer (NSIS or similar)

2. **Create MSIX Package Configuration:**
   - File: `src/VoiceStudio.App/Package.appxmanifest` (create/modify)
   - App identity
   - Capabilities
   - Visual assets

3. **Create Installer Script:**
   - File: `installer/VoiceStudio.iss` (NSIS script)
   - Or: `installer/create_installer.ps1` (PowerShell)
   - Include all dependencies
   - Create shortcuts
   - Add to Start Menu

4. **Create Smoke Checklist:**
   - File: `docs/release/SMOKE_CHECKLIST.md`
   - Pre-release verification steps:
     - [ ] All tests pass
     - [ ] No critical bugs
     - [ ] Performance budgets met
     - [ ] Accessibility checks pass
     - [ ] Installer works on clean system
     - [ ] Update mechanism works
     - [ ] All key panels functional
     - [ ] Backend integration works

5. **Add Version Stamping:**
   - File: `src/VoiceStudio.App/Views/Dialogs/AboutDialog.xaml` (modify)
   - Display version from assembly
   - Display build date
   - Display commit hash (if available)
   - Display .NET version
   - Display Windows SDK version

6. **Create Release Notes Template:**
   - File: `docs/release/RELEASE_NOTES_TEMPLATE.md`
   - Sections: New Features, Bug Fixes, Improvements, Breaking Changes
   - Format for changelog

**Files to Create:**
- `scripts/package_release.ps1`
- `src/VoiceStudio.App/Package.appxmanifest` (if not exists)
- `installer/create_installer.ps1` (or enhance existing)
- `docs/release/SMOKE_CHECKLIST.md`
- `docs/release/RELEASE_NOTES_TEMPLATE.md`

**Files to Modify:**
- `src/VoiceStudio.App/Views/Dialogs/AboutDialog.xaml`
- `src/VoiceStudio.App/Services/VersionService.cs` (enhance)

**Acceptance Criteria:**
- [ ] Packaging script complete
- [ ] MSIX package configuration complete
- [ ] Installer script complete
- [ ] Smoke checklist complete
- [ ] Version stamping in About dialog
- [ ] Release notes template created

---

## 🧪 WORKER 3: TESTING / QA / DOCUMENTATION / NAVIGATION

### TASK 3.1: NavigationService Implementation

**Priority:** HIGH  
**Estimated Time:** 6-8 hours  
**Dependencies:** PanelStateService (✅ exists)

**Detailed Steps:**

1. **Create NavigationService Interface:**
   - File: `src/VoiceStudio.Core/Services/INavigationService.cs`
   - Methods: `NavigateToPanel(string panelId)`, `NavigateBack()`, `CanNavigateBack()`, `GetCurrentPanel()`, `GetBackStack()`
   - Events: `NavigationChanged`, `BackStackChanged`

2. **Implement NavigationService:**
   - File: `src/VoiceStudio.App/Services/NavigationService.cs`
   - Integrate with PanelStateService
   - Manage backstack
   - Support deep-links (panelId?param=value)
   - Persist navigation state

3. **Add Deep-Link Support:**
   - Parse deep-link parameters
   - Navigate to panel with parameters
   - Support query string parameters
   - Example: `voicestudio://profiles?profileId=123`

4. **Integrate with MainWindow:**
   - File: `src/VoiceStudio.App/MainWindow.xaml.cs` (modify)
   - Use NavigationService for panel navigation
   - Handle back button (if available)
   - Update UI based on navigation state

5. **Add Navigation Breadcrumbs:**
   - Display navigation path
   - Support clicking breadcrumbs to navigate
   - Visual indicator of current location

6. **Test Navigation:**
   - Test panel navigation
   - Test back navigation
   - Test deep-links
   - Test navigation persistence

**Files to Create:**
- `src/VoiceStudio.Core/Services/INavigationService.cs`
- `src/VoiceStudio.App/Services/NavigationService.cs`

**Files to Modify:**
- `src/VoiceStudio.App/MainWindow.xaml.cs`
- `src/VoiceStudio.App/Services/ServiceProvider.cs`

**Acceptance Criteria:**
- [ ] NavigationService interface created
- [ ] NavigationService implemented
- [ ] Deep-link support added
- [ ] Integrated with MainWindow
- [ ] Breadcrumbs implemented
- [ ] All navigation scenarios tested

---

### TASK 3.2: Panel Lifecycle Documentation

**Priority:** MEDIUM  
**Estimated Time:** 4-6 hours  
**Dependencies:** IPanelView (✅ exists)

**Detailed Steps:**

1. **Extend IPanelView Interface:**
   - File: `src/VoiceStudio.Core/Panels/IPanelView.cs` (modify)
   - Add lifecycle methods: `OnInitialize()`, `OnActivate()`, `OnDeactivate()`, `OnPersist()`, `OnRestore()`

2. **Create Panel Lifecycle Helper:**
   - File: `src/VoiceStudio.App/Utilities/PanelLifecycleHelper.cs`
   - Helper methods for lifecycle management
   - Common patterns

3. **Create Panel Cookbook:**
   - File: `docs/developer/PANEL_COOKBOOK.md`
   - Sections:
     - Panel Lifecycle (init, activate, deactivate, persist, restore)
     - Command Patterns
     - Validation Patterns
     - Async Operation Patterns
     - State Management Patterns
     - Error Handling Patterns

4. **Document Persist/Restore Rules:**
   - What state to persist
   - When to persist
   - How to restore
   - Best practices

5. **Create Panel Template:**
   - File: `docs/developer/templates/PanelTemplate/` (directory)
   - XAML template
   - ViewModel template
   - Registration example
   - Lifecycle implementation example

6. **Update Existing Panels:**
   - Add lifecycle methods to key panels
   - Implement persist/restore
   - Test lifecycle

**Files to Create:**
- `src/VoiceStudio.App/Utilities/PanelLifecycleHelper.cs`
- `docs/developer/PANEL_COOKBOOK.md`
- `docs/developer/templates/PanelTemplate/` (directory with templates)

**Files to Modify:**
- `src/VoiceStudio.Core/Panels/IPanelView.cs`
- Key panels (add lifecycle methods)

**Acceptance Criteria:**
- [ ] IPanelView extended with lifecycle
- [ ] PanelLifecycleHelper created
- [ ] Panel Cookbook complete
- [ ] Persist/restore rules documented
- [ ] Panel template created
- [ ] Key panels updated

---

### TASK 3.3: Async/UX Safety Patterns

**Priority:** HIGH  
**Estimated Time:** 8-10 hours  
**Dependencies:** None

**Detailed Steps:**

1. **Create AsyncCommand Base Class:**
   - File: `src/VoiceStudio.App/Utilities/AsyncRelayCommand.cs` (enhance existing or create)
   - Support CancellationToken
   - In-flight guard (prevent duplicate execution)
   - Progress reporting
   - Error handling

2. **Create Command Guard Helper:**
   - File: `src/VoiceStudio.App/Utilities/CommandGuard.cs`
   - Helper for checking command state
   - Prevent duplicate operations
   - Track in-flight operations

3. **Audit All ViewModels:**
   - Review all async operations
   - Add CancellationToken support
   - Add in-flight guards
   - Add progress indicators

4. **Standardize Error Presentation:**
   - File: `src/VoiceStudio.App/Services/ErrorPresentationService.cs` (create)
   - Centralized error presentation logic
   - Decide: toast vs inline vs dialog
   - Consistent error styling

5. **Update All Commands:**
   - Replace fire-and-forget with proper async
   - Add cancellation support
   - Add progress indicators
   - Add error handling

6. **Create Async Patterns Guide:**
   - File: `docs/developer/ASYNC_PATTERNS.md`
   - Best practices
   - Common patterns
   - Anti-patterns to avoid

**Files to Create:**
- `src/VoiceStudio.App/Utilities/CommandGuard.cs`
- `src/VoiceStudio.App/Services/ErrorPresentationService.cs`
- `docs/developer/ASYNC_PATTERNS.md`

**Files to Modify:**
- `src/VoiceStudio.App/Utilities/AsyncRelayCommand.cs` (enhance)
- All ViewModels with async operations (70+ files)

**Acceptance Criteria:**
- [ ] AsyncCommand enhanced
- [ ] CommandGuard created
- [ ] All ViewModels audited
- [ ] ErrorPresentationService created
- [ ] All commands updated
- [ ] Async patterns guide complete

---

### TASK 3.4: Diagnostics Pane Enhancements

**Priority:** MEDIUM  
**Estimated Time:** 6-8 hours  
**Dependencies:** DiagnosticsView (✅ exists), AnalyticsService (✅ exists), FeatureFlagsService (pending)

**Detailed Steps:**

1. **Create FeatureFlagsService:**
   - File: `src/VoiceStudio.App/Services/FeatureFlagsService.cs`
   - Interface: `IFeatureFlagsService`
   - Methods: `IsEnabled(string flag)`, `SetFlag(string flag, bool enabled)`, `GetAllFlags()`
   - Persist flags to settings

2. **Enhance DiagnosticsView:**
   - File: `src/VoiceStudio.App/Views/Panels/DiagnosticsView.xaml` (modify)
   - Add tabs: Errors, Analytics, Performance, Feature Flags, Environment
   - Add filtering and search
   - Add export functionality

3. **Add Analytics Events Display:**
   - Show recent analytics events
   - Filter by event type
   - Timeline visualization
   - Correlation ID linking

4. **Add Performance Metrics Display:**
   - Show performance budgets
   - Show budget violations
   - Show panel load times
   - Show command execution times

5. **Add Feature Flags Display:**
   - List all feature flags
   - Toggle flags
   - Show flag descriptions
   - Persist changes

6. **Add Environment Info Display:**
   - App version
   - .NET version
   - Windows version
   - Backend URL
   - Log level
   - Performance profiling enabled

7. **Add Log Viewer:**
   - Display recent log entries
   - Filter by level
   - Search functionality
   - Export logs

**Files to Create:**
- `src/VoiceStudio.App/Services/IFeatureFlagsService.cs`
- `src/VoiceStudio.App/Services/FeatureFlagsService.cs`

**Files to Modify:**
- `src/VoiceStudio.App/Views/Panels/DiagnosticsView.xaml`
- `src/VoiceStudio.App/ViewModels/DiagnosticsViewModel.cs`
- `src/VoiceStudio.App/Services/ServiceProvider.cs`

**Acceptance Criteria:**
- [ ] FeatureFlagsService created
- [ ] DiagnosticsView enhanced with tabs
- [ ] Analytics events displayed
- [ ] Performance metrics displayed
- [ ] Feature flags displayed
- [ ] Environment info displayed
- [ ] Log viewer functional

---

### TASK 3.5: Analytics Events Integration

**Priority:** MEDIUM  
**Estimated Time:** 6-8 hours  
**Dependencies:** AnalyticsService (✅ exists), ErrorLoggingService (✅ exists)

**Detailed Steps:**

1. **Integrate Analytics into Key Flows:**
   - File: `src/VoiceStudio.App/ViewModels/ProfilesViewModel.cs` (modify)
   - File: `src/VoiceStudio.App/ViewModels/TimelineViewModel.cs` (modify)
   - File: `src/VoiceStudio.App/ViewModels/EffectsMixerViewModel.cs` (modify)
   - Track: Import, Edit, Synthesis, Export flows

2. **Add Correlation IDs to Flows:**
   - Use ErrorLoggingService.StartCorrelation()
   - Link analytics events to correlations
   - Track flow duration
   - Track success/failure

3. **Add Breadcrumbs to Critical Flows:**
   - Recording flow
   - Editing flow
   - Export flow
   - Add breadcrumbs at key points

4. **Create Analytics Event Constants:**
   - File: `src/VoiceStudio.Core/Models/AnalyticsEvents.cs`
   - Constants for all event names
   - Event property definitions
   - Documentation

5. **Test Analytics Integration:**
   - Test all key flows
   - Verify events tracked
   - Verify correlation IDs
   - Verify breadcrumbs

**Files to Create:**
- `src/VoiceStudio.Core/Models/AnalyticsEvents.cs`

**Files to Modify:**
- `src/VoiceStudio.App/ViewModels/ProfilesViewModel.cs`
- `src/VoiceStudio.App/ViewModels/TimelineViewModel.cs`
- `src/VoiceStudio.App/ViewModels/EffectsMixerViewModel.cs`
- Other ViewModels with key flows (20+ files)

**Acceptance Criteria:**
- [ ] Analytics integrated into all key flows
- [ ] Correlation IDs linked
- [ ] Breadcrumbs added
- [ ] Event constants created
- [ ] All flows tested

---

### TASK 3.6: UI Smoke Tests

**Priority:** HIGH  
**Estimated Time:** 8-10 hours  
**Dependencies:** C# test framework (✅ exists)

**Detailed Steps:**

1. **Create Smoke Test Base:**
   - File: `src/VoiceStudio.App.Tests/UI/SmokeTestBase.cs`
   - Setup/teardown for UI tests
   - Helper methods for UI interaction
   - App initialization

2. **Create Launch Test:**
   - File: `src/VoiceStudio.App.Tests/UI/LaunchSmokeTests.cs`
   - Test: Application launches
   - Test: MainWindow displays
   - Test: No crashes on startup

3. **Create Panel Navigation Tests:**
   - File: `src/VoiceStudio.App.Tests/UI/PanelNavigationSmokeTests.cs`
   - Test: Open Profiles panel
   - Test: Open Timeline panel
   - Test: Open Effects panel
   - Test: Open Quality panel
   - Test: Panel switching

4. **Create Common Action Tests:**
   - File: `src/VoiceStudio.App.Tests/UI/CommonActionsSmokeTests.cs`
   - Test: Create profile
   - Test: Synthesize voice
   - Test: Apply effect
   - Test: Export audio

5. **Create Critical Path Tests:**
   - File: `src/VoiceStudio.App.Tests/UI/CriticalPathSmokeTests.cs`
   - Test: Full workflow (create profile → synthesize → export)
   - Test: Error handling
   - Test: Backend connectivity

6. **Add Test Data Setup:**
   - Use seed data for tests
   - Clean up after tests
   - Isolated test data

**Files to Create:**
- `src/VoiceStudio.App.Tests/UI/SmokeTestBase.cs`
- `src/VoiceStudio.App.Tests/UI/LaunchSmokeTests.cs`
- `src/VoiceStudio.App.Tests/UI/PanelNavigationSmokeTests.cs`
- `src/VoiceStudio.App.Tests/UI/CommonActionsSmokeTests.cs`
- `src/VoiceStudio.App.Tests/UI/CriticalPathSmokeTests.cs`

**Acceptance Criteria:**
- [ ] Smoke test base created
- [ ] Launch tests complete
- [ ] Panel navigation tests complete
- [ ] Common action tests complete
- [ ] Critical path tests complete
- [ ] All tests passing

---

### TASK 3.7: ViewModel Contract Tests

**Priority:** HIGH  
**Estimated Time:** 8-10 hours  
**Dependencies:** C# test framework (✅ exists), MockBackendClient (✅ exists)

**Detailed Steps:**

1. **Create Mock Services:**
   - File: `src/VoiceStudio.App.Tests/Services/MockAnalyticsService.cs`
   - File: `src/VoiceStudio.App.Tests/Services/MockStateService.cs`
   - File: `src/VoiceStudio.App.Tests/Services/MockNavigationService.cs`
   - Implement interfaces with test doubles

2. **Create ViewModel Test Base:**
   - File: `src/VoiceStudio.App.Tests/ViewModels/ViewModelTestBase.cs`
   - Setup mocks
   - Common test utilities
   - Assertion helpers

3. **Expand Existing ViewModel Tests:**
   - File: `src/VoiceStudio.App.Tests/ViewModels/GlobalSearchViewModelTests.cs` (enhance)
   - File: `src/VoiceStudio.App.Tests/ViewModels/MultiSelectServiceTests.cs` (enhance)
   - Add more test coverage
   - Test error scenarios
   - Test edge cases

4. **Create New ViewModel Tests:**
   - Test all major ViewModels
   - Test business logic
   - Test command execution
   - Test state management

5. **Create Contract Test Suite:**
   - Test IBackendClient contract
   - Test IAnalyticsService contract
   - Test state service contracts
   - Verify interface compliance

**Files to Create:**
- `src/VoiceStudio.App.Tests/Services/MockAnalyticsService.cs`
- `src/VoiceStudio.App.Tests/Services/MockStateService.cs`
- `src/VoiceStudio.App.Tests/Services/MockNavigationService.cs`
- `src/VoiceStudio.App.Tests/ViewModels/ViewModelTestBase.cs`

**Files to Enhance:**
- Existing ViewModel test files (10+ files)
- Create new ViewModel tests (30+ files)

**Acceptance Criteria:**
- [ ] Mock services created
- [ ] ViewModel test base created
- [ ] All major ViewModels tested
- [ ] Contract tests complete
- [ ] Test coverage >80%

---

### TASK 3.8: Snapshot Tests

**Priority:** MEDIUM  
**Estimated Time:** 6-8 hours  
**Dependencies:** C# test framework (✅ exists)

**Detailed Steps:**

1. **Create Snapshot Test Framework:**
   - File: `src/VoiceStudio.App.Tests/Snapshot/SnapshotTestBase.cs`
   - Snapshot comparison logic
   - Snapshot storage
   - Diff generation

2. **Create Analytics Snapshot Tests:**
   - File: `src/VoiceStudio.App.Tests/Snapshot/AnalyticsSnapshotTests.cs`
   - Snapshot analytics outputs
   - Verify consistency
   - Detect regressions

3. **Create Visualization Snapshot Tests:**
   - File: `src/VoiceStudio.App.Tests/Snapshot/VisualizationSnapshotTests.cs`
   - Snapshot chart data
   - Snapshot quality metrics
   - Snapshot waveform data

4. **Create XAML Layout Snapshot Tests:**
   - File: `src/VoiceStudio.App.Tests/Snapshot/XamlLayoutSnapshotTests.cs`
   - Snapshot critical XAML layouts
   - Verify structure
   - Detect layout changes

5. **Add Snapshot Update Command:**
   - CLI command to update snapshots
   - Document update process
   - CI/CD integration

**Files to Create:**
- `src/VoiceStudio.App.Tests/Snapshot/SnapshotTestBase.cs`
- `src/VoiceStudio.App.Tests/Snapshot/AnalyticsSnapshotTests.cs`
- `src/VoiceStudio.App.Tests/Snapshot/VisualizationSnapshotTests.cs`
- `src/VoiceStudio.App.Tests/Snapshot/XamlLayoutSnapshotTests.cs`

**Acceptance Criteria:**
- [ ] Snapshot test framework created
- [ ] Analytics snapshots working
- [ ] Visualization snapshots working
- [ ] XAML layout snapshots working
- [ ] Update process documented

---

## 📊 TASK SUMMARY BY WORKER

### Worker 1 Tasks (8 tasks)
1. ✅ OpenAPI Schema Export (COMPLETE)
2. ⏳ Strongly Typed C# Client Generation
3. ⏳ Contract Tests
4. ⏳ Python Redaction Helper
5. ⏳ Backend Analytics Instrumentation
6. ⏳ Secrets Handling Service
7. ⏳ Dependency Audit Enhancement
8. ⏳ Minimal Privileges Documentation

**Estimated Total Time:** 30-40 hours

---

### Worker 2 Tasks (6 tasks)
1. ⏳ Resource Files for Localization
2. ⏳ Locale Switch Toggle
3. ⏳ Toast Styles & Standardization
4. ⏳ Empty States & Loading Skeletons
5. ⏳ Microcopy Guide
6. ⏳ Packaging Script & Smoke Checklist

**Estimated Total Time:** 30-40 hours

---

### Worker 3 Tasks (8 tasks)
1. ⏳ NavigationService Implementation
2. ⏳ Panel Lifecycle Documentation
3. ⏳ Async/UX Safety Patterns
4. ⏳ Diagnostics Pane Enhancements
5. ⏳ Analytics Events Integration
6. ⏳ UI Smoke Tests
7. ⏳ ViewModel Contract Tests
8. ⏳ Snapshot Tests

**Estimated Total Time:** 50-60 hours

---

## 🎯 IMPLEMENTATION PRIORITY

### Phase 1: Critical Foundation (Week 1)
- Worker 1: OpenAPI client generation, Contract tests, Secrets handling
- Worker 2: Resource files, Toast styles, Packaging script
- Worker 3: NavigationService, Async safety, UI smoke tests

### Phase 2: Polish & Testing (Week 2)
- Worker 1: Backend analytics, Python redaction, Dependency audit
- Worker 2: Localization toggle, Empty states, Microcopy guide
- Worker 3: Panel lifecycle docs, Diagnostics enhancements, ViewModel tests

### Phase 3: Final QA (Week 3)
- Worker 1: Minimal privileges docs
- Worker 2: Smoke checklist finalization
- Worker 3: Snapshot tests, Analytics integration, Final testing

---

## ✅ COMPLETION CRITERIA

### Code Complete
- [ ] All tasks implemented
- [ ] All tests passing
- [ ] No critical bugs
- [ ] Performance budgets met
- [ ] Accessibility compliance

### Documentation Complete
- [ ] All guides written
- [ ] API documentation complete
- [ ] User documentation updated
- [ ] Developer documentation complete

### Release Ready
- [ ] Packaging script works
- [ ] Installer tested
- [ ] Smoke checklist passed
- [ ] Version stamping complete
- [ ] Release notes prepared

---

**Last Updated:** 2025-01-28  
**Status:** 🚧 **MASTER PLAN COMPLETE - READY FOR IMPLEMENTATION**
