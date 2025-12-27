# Worker 2 Prompt - UI/UX/Controls/Localization/Packaging
## Complete Task Instructions

**Date:** 2025-01-28  
**Worker:** Worker 2 (UI/UX Specialist)  
**Status:** 🚧 **READY FOR IMPLEMENTATION**

---

## 🎯 YOUR ROLE

You are **Worker 2**, responsible for:
- UI/UX design and implementation
- Reusable controls and components
- Localization and internationalization
- Release packaging and versioning
- Design system consistency

---

## ✅ COMPLETED WORK (DO NOT REDO)

1. ✅ **Reusable Controls** - VSQButton, VSQCard, VSQFormField, VSQBadge, VSQProgressIndicator created
2. ✅ **Accessibility Helpers** - AccessibilityHelpers.cs created with WCAG compliance
3. ✅ **Performance Budgets** - PerformanceProfiler enhanced with budgets
4. ✅ **DesignTokens Expansion** - Complete spacing, radii, typography, accessibility tokens added
5. ✅ **Launch Profiles** - VS Code and Visual Studio launch profiles created

---

## 📋 YOUR TASKS (6 TASKS - 30-40 HOURS)

### TASK 2.1: Resource Files for Localization

**Priority:** HIGH  
**Estimated Time:** 8-10 hours  
**Status:** ⏳ **PENDING**

**Objective:** Create resource files for all UI strings and migrate hardcoded text from ViewModels and XAML.

**Detailed Steps:**

1. **Create Resource File Structure:**
   - File: `src/VoiceStudio.App/Resources/Resources.resw` (create)
   - File: `src/VoiceStudio.App/Resources/en-US/Resources.resw` (create)
   - File: `src/VoiceStudio.App/Resources/es-ES/Resources.resw` (create - optional, can be empty initially)
   - File: `src/VoiceStudio.App/Resources/fr-FR/Resources.resw` (create - optional, can be empty initially)

2. **Create Resource Key Naming Convention:**
   - Format: `Category.Item.Description`
   - Examples:
     - `Button.Save` - Save button text
     - `Button.Delete` - Delete button text
     - `Error.ProfileNotFound` - Profile not found error
     - `Panel.Profiles.Title` - Profiles panel title
     - `Toast.Success.ProfileCreated` - Success toast message
     - `Tooltip.Search.Help` - Search tooltip text

3. **Create Resource Helper:**
   - File: `src/VoiceStudio.App/Utilities/ResourceHelper.cs`
   - Static class with methods:
     - `GetString(string key, params object[] args) -> string`
     - `GetString(string key, string? defaultValue) -> string`
     - `FormatString(string key, params object[] args) -> string`
   - Load from `Resources.resw` using `ResourceLoader`
   - Support string formatting (e.g., "Profile {0} created")

4. **Audit ViewModels for Hardcoded Strings:**
   - Search pattern: `"text"` or `@"text"` in ViewModels
   - Files to audit (70+ ViewModels):
     - `src/VoiceStudio.App/ViewModels/*.cs`
   - Create list of all hardcoded strings
   - Assign resource keys
   - Document in `docs/developer/RESOURCE_KEYS.md`

5. **Update ViewModels:**
   - Replace hardcoded strings with `ResourceHelper.GetString()`
   - Example:
     ```csharp
     // Before:
     Title = "Voice Profiles";
     
     // After:
     Title = ResourceHelper.GetString("Panel.Profiles.Title", "Voice Profiles");
     ```
   - Update all 70+ ViewModels systematically

6. **Audit XAML Files for Hardcoded Text:**
   - Search pattern: `Text="..."` or `<TextBlock Text="..."/>`
   - Files to audit (150+ XAML files):
     - `src/VoiceStudio.App/Views/**/*.xaml`
     - `src/VoiceStudio.App/Controls/**/*.xaml`
   - Replace with `x:Uid` and resource references
   - Example:
     ```xml
     <!-- Before: -->
     <TextBlock Text="Voice Profiles" />
     
     <!-- After: -->
     <TextBlock x:Uid="ProfilesPanelTitle" />
     <!-- In Resources.resw: ProfilesPanelTitle.Text = "Voice Profiles" -->
     ```

7. **Create Resource Key Documentation:**
   - File: `docs/developer/RESOURCE_KEYS.md`
   - List all resource keys organized by category
   - Usage examples
   - Naming conventions
   - How to add new keys

8. **Test Resource Loading:**
   - Test all resource keys load correctly
   - Test fallback to default values
   - Test string formatting
   - Verify no missing keys

**Files to Create:**
- `src/VoiceStudio.App/Resources/Resources.resw`
- `src/VoiceStudio.App/Resources/en-US/Resources.resw`
- `src/VoiceStudio.App/Resources/es-ES/Resources.resw` (optional)
- `src/VoiceStudio.App/Resources/fr-FR/Resources.resw` (optional)
- `src/VoiceStudio.App/Utilities/ResourceHelper.cs`
- `docs/developer/RESOURCE_KEYS.md`

**Files to Modify:**
- All ViewModels with hardcoded strings (70+ files)
- All XAML files with hardcoded text (150+ files)

**Acceptance Criteria:**
- [ ] Resource files created
- [ ] ResourceHelper implemented
- [ ] All ViewModels use resources
- [ ] All XAML uses resources
- [ ] Resource keys documented
- [ ] No hardcoded strings remain
- [ ] All resources load correctly

---

### TASK 2.2: Locale Switch Toggle

**Priority:** MEDIUM  
**Estimated Time:** 4-6 hours  
**Dependencies:** Resource files (TASK 2.1)

**Objective:** Implement locale switching functionality with UI toggle and persistence.

**Detailed Steps:**

1. **Create Localization Service Interface:**
   - File: `src/VoiceStudio.Core/Services/ILocalizationService.cs`
   - Methods:
     - `string GetCurrentLocale()`
     - `Task SetLocaleAsync(string locale)`
     - `string GetString(string key, string? defaultValue = null)`
     - `IReadOnlyList<string> GetAvailableLocales()`
   - Events:
     - `event EventHandler<string> LocaleChanged`

2. **Implement Localization Service:**
   - File: `src/VoiceStudio.App/Services/LocalizationService.cs`
   - Load resource files based on locale
   - Switch `ResourceContext` for locale changes
   - Persist locale to user settings
   - Load locale on app startup
   - Support: en-US, es-ES, fr-FR (at minimum)

3. **Create Locale Switch Control:**
   - File: `src/VoiceStudio.App/Controls/LocaleSwitchControl.xaml`
   - File: `src/VoiceStudio.App/Controls/LocaleSwitchControl.xaml.cs`
   - ComboBox or RadioButtons for locale selection
   - Display locale names in native language:
     - English (en-US)
     - Español (es-ES)
     - Français (fr-FR)
   - Visual indicator of current locale
   - Accessibility:
     - `AutomationProperties.Name`
     - `AutomationProperties.HelpText`
     - Keyboard navigation

4. **Add to Settings Panel:**
   - File: `src/VoiceStudio.App/Views/Panels/SettingsView.xaml` (modify)
   - Add locale switch control in "General" or "Appearance" section
   - Label: "Language" or "Locale"
   - Save locale preference on change

5. **Implement Locale Persistence:**
   - Use `ApplicationData.LocalSettings` to save locale
   - Key: `"AppLocale"` (default: "en-US")
   - Load on app startup in `App.xaml.cs`
   - Apply locale immediately on change

6. **Update ResourceHelper:**
   - File: `src/VoiceStudio.App/Utilities/ResourceHelper.cs` (modify)
   - Use `LocalizationService` instead of direct ResourceLoader
   - Listen to `LocaleChanged` event
   - Update cached resources on locale change

7. **Test Locale Switching:**
   - Test all supported locales
   - Verify UI updates immediately
   - Verify persistence works
   - Test with different resource files
   - Test fallback to en-US if locale missing

**Files to Create:**
- `src/VoiceStudio.Core/Services/ILocalizationService.cs`
- `src/VoiceStudio.App/Services/LocalizationService.cs`
- `src/VoiceStudio.App/Controls/LocaleSwitchControl.xaml` + `.xaml.cs`

**Files to Modify:**
- `src/VoiceStudio.App/Views/Panels/SettingsView.xaml`
- `src/VoiceStudio.App/Utilities/ResourceHelper.cs`
- `src/VoiceStudio.App/App.xaml.cs`
- `src/VoiceStudio.App/Services/ServiceProvider.cs`

**Acceptance Criteria:**
- [ ] LocalizationService implemented
- [ ] Locale switch control created
- [ ] Added to settings panel
- [ ] Locale persistence works
- [ ] UI updates on locale change
- [ ] All locales tested
- [ ] Accessibility support complete

---

### TASK 2.3: Toast Styles & Standardization

**Priority:** HIGH  
**Estimated Time:** 4-6 hours  
**Status:** ⏳ **PENDING**

**Objective:** Create standardized toast styles and enhance ToastNotificationService with typed methods.

**Detailed Steps:**

1. **Create Toast Styles Resource:**
   - File: `src/VoiceStudio.App/Resources/ToastStyles.xaml`
   - Styles:
     - `VSQ.Toast.Success` - Green background, checkmark icon
     - `VSQ.Toast.Error` - Red background, error icon
     - `VSQ.Toast.Warning` - Orange background, warning icon
     - `VSQ.Toast.Info` - Blue background, info icon
   - Use VSQ.* design tokens:
     - Colors: `VSQ.Success`, `VSQ.Error`, `VSQ.Warn`, `VSQ.Accent.Cyan`
     - Spacing: `VSQ.Spacing.Medium`, `VSQ.Spacing.Large`
     - Corner radius: `VSQ.CornerRadius.Medium`
     - Typography: `VSQ.FontSize.Body`
   - Animations:
     - Slide-in from top
     - Fade-out on dismiss
     - Duration: 300ms

2. **Create Toast Control:**
   - File: `src/VoiceStudio.App/Controls/ToastNotification.xaml`
   - File: `src/VoiceStudio.App/Controls/ToastNotification.xaml.cs`
   - Properties:
     - `ToastType` (Success, Error, Warning, Info)
     - `Message` (string)
     - `Title` (optional string)
     - `Duration` (TimeSpan, default: 5 seconds)
     - `ActionButton` (optional ICommand)
   - Visual:
     - Icon (based on type)
     - Message text
     - Dismiss button
     - Action button (if provided)
   - Accessibility:
     - `AutomationProperties.Name` (includes type and message)
     - `AutomationProperties.HelpText`
     - Keyboard dismiss (Escape key)
     - Live region for screen readers

3. **Enhance ToastNotificationService:**
   - File: `src/VoiceStudio.App/Services/ToastNotificationService.cs` (modify)
   - Add typed methods:
     - `void ShowSuccess(string message, string? title = null, TimeSpan? duration = null)`
     - `void ShowError(string message, string? title = null, TimeSpan? duration = null)`
     - `void ShowWarning(string message, string? title = null, TimeSpan? duration = null)`
     - `void ShowInfo(string message, string? title = null, TimeSpan? duration = null)`
   - Apply toast styles automatically based on method
   - Support custom duration
   - Support action buttons

4. **Add Toast Queue Management:**
   - Limit concurrent toasts (max 3-5)
   - Queue overflow handling
   - Dismiss oldest when queue full
   - Smooth animations for queue changes

5. **Update All Toast Calls:**
   - Audit all `ToastNotificationService` usage
   - Replace generic `Show()` calls with typed methods
   - Ensure consistent styling
   - Files to update (50+ files):
     - All ViewModels using toast notifications
     - All Services using toast notifications

6. **Test Toast System:**
   - Test all toast types
   - Test queue management
   - Test dismiss functionality
   - Test accessibility
   - Test animations

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
- [ ] All toast types tested

---

### TASK 2.4: Empty States & Loading Skeletons Standardization

**Priority:** MEDIUM  
**Estimated Time:** 6-8 hours  
**Status:** ⏳ **PENDING**

**Objective:** Standardize empty states and loading skeletons across all panels using existing controls.

**Detailed Steps:**

1. **Audit Existing Empty States:**
   - Review all panels for empty states
   - Document current implementations
   - Identify inconsistencies
   - Files to review (30+ panels):
     - `src/VoiceStudio.App/Views/Panels/*.xaml`

2. **Enhance EmptyState Control:**
   - File: `src/VoiceStudio.App/Controls/EmptyState.xaml` (modify)
   - Properties:
     - `Title` (string) - Main title
     - `Message` (string) - Description message
     - `Icon` (IconElement) - Optional icon
     - `ActionButtonText` (string) - Optional action button
     - `ActionButtonCommand` (ICommand) - Action command
   - Use VSQ.* design tokens
   - Accessibility:
     - `AutomationProperties.Name`
     - `AutomationProperties.HelpText`
     - Keyboard navigation for action button

3. **Enhance SkeletonScreen Control:**
   - File: `src/VoiceStudio.App/Controls/SkeletonScreen.xaml` (modify)
   - Properties:
     - `SkeletonType` (List, Card, Form, Table)
     - `ItemCount` (int) - Number of skeleton items
   - Standardize skeleton patterns:
     - List skeleton: Rounded rectangles for items
     - Card skeleton: Card shape with lines
     - Form skeleton: Input field shapes
     - Table skeleton: Row/column structure
   - Smooth shimmer animation
   - Use VSQ.* design tokens

4. **Create Empty State Patterns:**
   - File: `docs/design/EMPTY_STATE_PATTERNS.md`
   - Document patterns for different scenarios:
     - No data (e.g., "No profiles yet")
     - Error state (e.g., "Failed to load")
     - Empty search results
     - No permissions
   - Code examples
   - Best practices
   - When to use each pattern

5. **Update All Panels:**
   - Replace custom empty states with `EmptyState` control
   - Replace custom loading with `SkeletonScreen` control
   - Ensure consistency
   - Files to update (30+ panels):
     - ProfilesView, TimelineView, EffectsMixerView, etc.

6. **Test Empty States:**
   - Test all panels with no data
   - Verify empty states display correctly
   - Test loading states
   - Test accessibility

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
- [ ] Consistency achieved

---

### TASK 2.5: Microcopy Guide

**Priority:** MEDIUM  
**Estimated Time:** 4-6 hours  
**Status:** ⏳ **PENDING**

**Objective:** Create comprehensive microcopy guide for consistent UI text across the application.

**Detailed Steps:**

1. **Create Microcopy Guide:**
   - File: `docs/design/MICROCOPY_GUIDE.md`
   - Sections:
     - Button Verbs
     - Error Messages
     - Titles
     - Toast Messages
     - Tooltips
     - Help Text
     - Empty States
     - Loading Messages

2. **Document Button Verb Patterns:**
   - Action verbs: Save, Delete, Create, Edit, Export, Import, Apply, Cancel, Close
   - Avoid: Click, Press, Use, Do
   - Examples:
     - ✅ "Save Profile"
     - ❌ "Click to Save Profile"
     - ✅ "Delete Selected"
     - ❌ "Press Delete Button"
   - Guidelines:
     - Use imperative mood
     - Be concise (1-2 words)
     - Be action-oriented

3. **Document Error Message Patterns:**
   - User-friendly language
   - Actionable messages
   - Avoid technical jargon
   - Examples:
     - ✅ "Profile not found. Please check the profile ID and try again."
     - ❌ "HTTP 404: ProfileNotFoundException"
     - ✅ "Unable to connect to backend. Please check your connection and try again."
     - ❌ "ConnectionError: Failed to establish connection"
   - Templates:
     - "Unable to [action]. [Reason]. [Action user can take]."
     - "[What happened]. [What user can do]."

4. **Document Title Conventions:**
   - Panel titles: Use noun phrases
     - ✅ "Voice Profiles"
     - ❌ "Manage Voice Profiles"
   - Dialog titles: Use action phrases
     - ✅ "Create Profile"
     - ❌ "Profile Creation"
   - Section headings: Use noun phrases
     - ✅ "Quality Metrics"
     - ❌ "View Quality Metrics"

5. **Document Toast Message Patterns:**
   - Success messages:
     - ✅ "Profile created successfully"
     - ❌ "Success!"
   - Error messages:
     - ✅ "Failed to save profile. Please try again."
     - ❌ "Error occurred"
   - Warning messages:
     - ✅ "Profile will be deleted. This action cannot be undone."
     - ❌ "Warning!"
   - Info messages:
     - ✅ "Synthesis in progress. This may take a few moments."
     - ❌ "Processing..."

6. **Document Tooltip Patterns:**
   - Be concise (1 sentence)
   - Explain what the control does
   - Include keyboard shortcut if available
   - Examples:
     - ✅ "Save the current profile (Ctrl+S)"
     - ❌ "This button saves the profile"

7. **Create Microcopy Checklist:**
   - Checklist for reviewing UI text
   - Common mistakes to avoid
   - Review process
   - Examples of good vs bad microcopy

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
**Status:** ⏳ **PENDING**

**Objective:** Create repeatable packaging script and comprehensive smoke checklist for release candidates.

**Detailed Steps:**

1. **Create Packaging Script:**
   - File: `scripts/package_release.ps1`
   - Script steps:
     ```powershell
     # 1. Clean build directories
     Remove-Item -Recurse -Force bin, obj -ErrorAction SilentlyContinue
     
     # 2. Restore NuGet packages
     dotnet restore
     
     # 3. Build in Release mode
     dotnet build -c Release
     
     # 4. Run tests
     dotnet test
     
     # 5. Create MSIX package
     # (MSIX packaging steps)
     
     # 6. Sign package (if certificate available)
     # (Code signing steps)
     
     # 7. Generate release notes
     # (Extract from changelog)
     
     # 8. Create installer
     # (NSIS or similar)
     ```
   - Parameters:
     - `-Version` - Version number
     - `-Configuration` - Release/Debug (default: Release)
     - `-SkipTests` - Skip test execution
     - `-Sign` - Sign package (requires certificate)

2. **Create MSIX Package Configuration:**
   - File: `src/VoiceStudio.App/Package.appxmanifest` (create or modify)
   - App identity:
     - Name: VoiceStudio Quantum+
     - Publisher: (your publisher)
     - Version: (from VersionService)
   - Capabilities:
     - Internet (for backend API)
     - Private Networks (for localhost)
     - Documents Library (for file access)
   - Visual assets:
     - Logo images
     - Splash screen
     - Tile images

3. **Create Installer Script:**
   - File: `installer/create_installer.ps1` (or enhance existing)
   - Use NSIS or WiX Toolset
   - Include:
     - All dependencies
     - Create shortcuts
     - Add to Start Menu
     - Register file associations
     - Add uninstaller

4. **Create Smoke Checklist:**
   - File: `docs/release/SMOKE_CHECKLIST.md`
   - Pre-release verification steps:
     - [ ] All unit tests pass
     - [ ] All integration tests pass
     - [ ] No critical bugs in issue tracker
     - [ ] Performance budgets met (startup <3s, panel load <500ms)
     - [ ] Accessibility checks pass (keyboard navigation, screen reader)
     - [ ] Installer works on clean Windows 10 system
     - [ ] Installer works on clean Windows 11 system
     - [ ] Update mechanism works (if applicable)
     - [ ] All key panels functional:
       - [ ] Profiles panel
       - [ ] Timeline panel
       - [ ] Effects panel
       - [ ] Quality dashboard
     - [ ] Backend integration works
     - [ ] No console errors on startup
     - [ ] Version displayed correctly in About dialog
     - [ ] Release notes generated

5. **Add Version Stamping:**
   - File: `src/VoiceStudio.App/Views/Dialogs/AboutDialog.xaml` (modify or create)
   - Display:
     - App version (from VersionService)
     - Build date (from VersionService)
     - Commit hash (if available from build)
     - .NET version (from VersionService)
     - Windows SDK version
     - Backend version (if available)
   - Format:
     ```
     VoiceStudio Quantum+
     Version 1.0.0
     Build Date: 2025-01-28
     .NET Runtime: 8.0.416
     Windows SDK: 10.0.26100.0
     ```

6. **Enhance VersionService:**
   - File: `src/VoiceStudio.App/Services/VersionService.cs` (modify)
   - Add methods:
     - `GetCommitHash()` - Get Git commit hash (if available)
     - `GetBuildConfiguration()` - Debug/Release
     - `GetBackendVersion()` - Backend API version (if available)

7. **Create Release Notes Template:**
   - File: `docs/release/RELEASE_NOTES_TEMPLATE.md`
   - Sections:
     - New Features
     - Bug Fixes
     - Improvements
     - Breaking Changes
     - Known Issues
     - Upgrade Notes
   - Format for changelog

**Files to Create:**
- `scripts/package_release.ps1`
- `src/VoiceStudio.App/Package.appxmanifest` (if not exists)
- `installer/create_installer.ps1` (or enhance existing)
- `docs/release/SMOKE_CHECKLIST.md`
- `docs/release/RELEASE_NOTES_TEMPLATE.md`

**Files to Modify:**
- `src/VoiceStudio.App/Views/Dialogs/AboutDialog.xaml` (or create)
- `src/VoiceStudio.App/Services/VersionService.cs`

**Acceptance Criteria:**
- [ ] Packaging script complete
- [ ] MSIX package configuration complete
- [ ] Installer script complete
- [ ] Smoke checklist complete
- [ ] Version stamping in About dialog
- [ ] Release notes template created
- [ ] All packaging steps tested

---

## 📊 TASK SUMMARY

**Total Tasks:** 6  
**Estimated Time:** 30-40 hours  
**Priority Breakdown:**
- HIGH: 3 tasks (Resources, Toast styles, Packaging)
- MEDIUM: 3 tasks (Locale switch, Empty states, Microcopy)

**Dependencies:**
- TASK 2.2 (Locale switch) → TASK 2.1 (Resources)
- All other tasks are independent

---

## ✅ COMPLETION CRITERIA

### Code Complete
- [ ] All 6 tasks implemented
- [ ] All hardcoded strings migrated to resources
- [ ] All toast calls use typed methods
- [ ] All panels use standardized empty/loading states
- [ ] Packaging script works
- [ ] Version stamping complete

### Documentation Complete
- [ ] Resource keys documented
- [ ] Microcopy guide complete
- [ ] Empty state patterns documented
- [ ] Smoke checklist complete
- [ ] Release notes template created

### Consistency Achieved
- [ ] All UI text follows microcopy guide
- [ ] All toasts use standardized styles
- [ ] All empty states consistent
- [ ] All loading states consistent

---

## 🚀 START HERE

**Immediate Next Steps:**

1. **TASK 2.1: Resource Files** (Start here - foundation for localization)
   - Create resource files
   - Create ResourceHelper
   - Audit and extract hardcoded strings
   - Update ViewModels and XAML

2. **TASK 2.3: Toast Styles** (High priority - UX consistency)
   - Create toast styles
   - Create toast control
   - Enhance ToastNotificationService
   - Update all toast calls

3. **TASK 2.6: Packaging Script** (High priority - release readiness)
   - Create packaging script
   - Create MSIX configuration
   - Create installer script
   - Create smoke checklist

---

**Last Updated:** 2025-01-28  
**Status:** 🚧 **READY FOR IMPLEMENTATION**
