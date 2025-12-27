E:\VoiceStudio\docs\governance\worker1\WORKER_1_FINAL_PROMPT_2025-01-28.md

**Date:** 2025-01-28  
**Worker:** Worker 2 (UI/UX/Controls/Localization/Packaging Specialist)  
**Status:** 🚧 **READY - 5 TASKS REMAINING**

---

## 🎯 YOUR ROLE

You are **Worker 2**, responsible for:
- UI/UX design and implementation
- Reusable controls and components
- Localization and internationalization
- Release packaging and versioning
- Design system consistency

**IMPORTANT:** Do NOT redo completed work. Focus only on the remaining tasks below.

---

## ✅ ALREADY COMPLETE (DO NOT REDO)

1. ✅ **Reusable Controls** - VSQButton, VSQCard, VSQFormField, VSQBadge, VSQProgressIndicator
2. ✅ **Accessibility Helpers** - AccessibilityHelpers.cs with WCAG compliance
3. ✅ **DesignTokens Expansion** - Complete spacing, radii, typography, accessibility tokens
4. ✅ **Launch Profiles** - VS Code and Visual Studio launch profiles
5. ✅ **Microcopy Guide** - `docs/design/MICROCOPY_GUIDE.md` (395 lines)
6. ✅ **Resource Files Foundation** - Resources.resw (50+ keys), ResourceHelper.cs, en-US/Resources.resw
7. ✅ **Toast Control** - VSQToastNotification.xaml/.cs created, ToastStyles.xaml exists

**DO NOT recreate these. They are complete.**

---

## 📋 YOUR REMAINING TASKS (5 TASKS)

### TASK 2.1: Resource Files Migration (HIGH PRIORITY)

**Status:** 🚧 **FOUNDATION DONE - MIGRATION PENDING**  
**Time:** 6-8 hours  
**Foundation Ready:** ✅ Resources.resw (50+ keys), ✅ ResourceHelper.cs

**What to Do:**

1. **Expand Resource Keys:**
   - Audit 70+ ViewModels for hardcoded strings
   - Audit 150+ XAML files for hardcoded text
   - Add missing keys to both `Resources.resw` and `en-US/Resources.resw`
   - Update `docs/developer/RESOURCE_KEYS.md`

2. **Update High-Priority ViewModels First:**
   - ProfilesViewModel
   - TimelineViewModel
   - VoiceSynthesisViewModel
   - EffectsMixerViewModel
   - QualityDashboardViewModel
   - Example:
     ```csharp
     // Before:
     DisplayName = "Voice Profiles";
     ErrorMessage = "Failed to load profiles";
     
     // After:
     DisplayName = ResourceHelper.GetString("Panel.Profiles.DisplayName", "Voice Profiles");
     ErrorMessage = ResourceHelper.GetString("Error.LoadFailed");
     ```

3. **Update XAML Files:**
   - Replace `Text="..."` with `x:Uid="KeyName"`
   - Add corresponding entries to Resources.resw
   - Example:
     ```xml
     <!-- Before: -->
     <TextBlock Text="Voice Profiles" />
     
     <!-- After: -->
     <TextBlock x:Uid="ProfilesPanelTitle" />
     <!-- In Resources.resw: ProfilesPanelTitle.Text = "Voice Profiles" -->
     ```

4. **Verify Migration:**
   - Search for remaining hardcoded strings: `"text"` or `@"text"`
   - Test all resource keys load
   - Verify fallback values work

**Files to Modify:**
- `src/VoiceStudio.App/Resources/Resources.resw` (expand)
- `src/VoiceStudio.App/Resources/en-US/Resources.resw` (expand)
- 70+ ViewModels (migrate strings)
- 150+ XAML files (migrate text)

**Acceptance Criteria:**
- [ ] All ViewModels use ResourceHelper
- [ ] All XAML uses x:Uid
- [ ] No hardcoded strings in ViewModels
- [ ] No hardcoded text in XAML
- [ ] All resource keys documented

---

### TASK 2.2: Locale Switch Toggle (MEDIUM PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 4-6 hours  
**Dependencies:** TASK 2.1 (Resource Files)

**What to Do:**

1. **Create Localization Service:**
   - File: `src/VoiceStudio.Core/Services/ILocalizationService.cs`
   - Methods: `GetCurrentLocale()`, `SetLocaleAsync()`, `GetString()`, `GetAvailableLocales()`
   - Event: `LocaleChanged`

2. **Implement Localization Service:**
   - File: `src/VoiceStudio.App/Services/LocalizationService.cs`
   - Load resource files based on locale
   - Switch ResourceContext on locale change
   - Persist locale to ApplicationData.LocalSettings
   - Support: en-US, es-ES, fr-FR (at minimum)

3. **Create Locale Switch Control:**
   - File: `src/VoiceStudio.App/Controls/LocaleSwitchControl.xaml` + `.xaml.cs`
   - ComboBox with locale selection
   - Display names: "English", "Español", "Français"
   - Accessibility: AutomationProperties.Name, HelpText

4. **Add to Settings Panel:**
   - File: `src/VoiceStudio.App/Views/Panels/SettingsView.xaml`
   - Add locale switch in "General" section
   - Save preference on change

5. **Update ResourceHelper:**
   - Use LocalizationService instead of direct ResourceLoader
   - Listen to LocaleChanged event
   - Reload resources on locale change

**Files to Create:**
- `src/VoiceStudio.Core/Services/ILocalizationService.cs`
- `src/VoiceStudio.App/Services/LocalizationService.cs`
- `src/VoiceStudio.App/Controls/LocaleSwitchControl.xaml` + `.xaml.cs`

**Files to Modify:**
- `src/VoiceStudio.App/Views/Panels/SettingsView.xaml`
- `src/VoiceStudio.App/Utilities/ResourceHelper.cs`
- `src/VoiceStudio.App/Services/ServiceProvider.cs`

**Acceptance Criteria:**
- [ ] LocalizationService implemented
- [ ] Locale switch control created
- [ ] Added to settings panel
- [ ] Locale persistence works
- [ ] UI updates on locale change
- [ ] All locales tested

---

### TASK 2.3: Toast Styles & Standardization (HIGH PRIORITY)

**Status:** 🚧 **CONTROL CREATED - INTEGRATION PENDING**  
**Time:** 2-4 hours  
**Foundation Ready:** ✅ VSQToastNotification control, ✅ ToastStyles.xaml

**What to Do:**

1. **Enhance ToastNotificationService:**
   - File: `src/VoiceStudio.App/Services/ToastNotificationService.cs`
   - Optionally use VSQToastNotification control
   - Ensure styles from ToastStyles.xaml are applied
   - Verify typed methods (ShowSuccess, ShowError, etc.) work correctly

2. **Update Toast Calls:**
   - Audit all `ToastNotificationService` usage (50+ files)
   - Ensure all calls use typed methods
   - Verify consistent styling
   - Example:
     ```csharp
     // Good:
     _toastService?.ShowSuccess("Profile created", "Success");
     _toastService?.ShowError("Failed to save", "Error");
     
     // Avoid:
     _toastService?.Show("Profile created", ToastType.Success);
     ```

3. **Test Toast System:**
   - Test all toast types (Success, Error, Warning, Info, Progress)
   - Test queue management (max 3-5 concurrent)
   - Test dismiss functionality
   - Test accessibility

**Files to Modify:**
- `src/VoiceStudio.App/Services/ToastNotificationService.cs` (enhance)
- 50+ files using ToastNotificationService (verify typed methods)

**Acceptance Criteria:**
- [ ] ToastNotificationService uses VSQToastNotification or applies styles correctly
- [ ] All toast calls use typed methods
- [ ] Queue management works
- [ ] All toast types tested
- [ ] Accessibility verified

---

### TASK 2.4: Empty States & Loading Skeletons (MEDIUM PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 6-8 hours

**What to Do:**

1. **Audit Existing Empty States:**
   - Review 30+ panels for empty state implementations
   - Document current patterns
   - Identify inconsistencies

2. **Enhance EmptyState Control:**
   - File: `src/VoiceStudio.App/Controls/EmptyState.xaml` (enhance if exists)
   - Properties: Title, Message, Icon, ActionButtonText, ActionButtonCommand
   - Use VSQ.* design tokens
   - Accessibility: AutomationProperties

3. **Enhance SkeletonScreen Control:**
   - File: `src/VoiceStudio.App/Controls/SkeletonScreen.xaml` (enhance if exists)
   - Properties: SkeletonType (List, Card, Form, Table), ItemCount
   - Smooth shimmer animation
   - Use VSQ.* design tokens

4. **Update All Panels:**
   - Replace custom empty states with EmptyState control
   - Replace custom loading with SkeletonScreen control
   - Focus on high-priority panels first

5. **Create Patterns Documentation:**
   - File: `docs/design/EMPTY_STATE_PATTERNS.md`
   - Document patterns for different scenarios
   - Code examples and best practices

**Files to Create/Modify:**
- `src/VoiceStudio.App/Controls/EmptyState.xaml` (enhance)
- `src/VoiceStudio.App/Controls/SkeletonScreen.xaml` (enhance)
- `docs/design/EMPTY_STATE_PATTERNS.md` (create)
- 30+ panels (standardize)

**Acceptance Criteria:**
- [ ] EmptyState control standardized
- [ ] SkeletonScreen control standardized
- [ ] All panels use standardized controls
- [ ] Patterns documented
- [ ] Consistency achieved

---

### TASK 2.6: Packaging Script & Smoke Checklist (HIGH PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 6-8 hours

**What to Do:**

1. **Create Packaging Script:**
   - File: `scripts/package_release.ps1`
   - Steps:
     - Clean build directories
     - Restore packages
     - Build in Release mode
     - Run tests
     - Create MSIX package
     - Sign package (if certificate available)
     - Generate release notes
   - Parameters: `-Version`, `-Configuration`, `-SkipTests`, `-Sign`

2. **Create MSIX Package Configuration:**
   - File: `src/VoiceStudio.App/Package.appxmanifest` (create or modify)
   - App identity: Name, Publisher, Version
   - Capabilities: Internet, Private Networks, Documents Library
   - Visual assets: Logo, splash screen, tile images

3. **Create Installer Script:**
   - File: `installer/create_installer.ps1` (enhance existing)
   - Use NSIS or WiX Toolset
   - Include dependencies, shortcuts, file associations

4. **Create Smoke Checklist:**
   - File: `docs/release/SMOKE_CHECKLIST.md`
   - Pre-release verification steps:
     - All tests pass
     - No critical bugs
     - Performance budgets met
     - Accessibility checks pass
     - Installer works on clean Windows 10/11
     - All key panels functional
     - Version displayed correctly

5. **Add Version Stamping:**
   - File: `src/VoiceStudio.App/Views/Dialogs/AboutDialog.xaml` (create or modify)
   - Display: App version, build date, .NET version, Windows SDK version
   - Use VersionService if available

6. **Create Release Notes Template:**
   - File: `docs/release/RELEASE_NOTES_TEMPLATE.md`
   - Sections: New Features, Bug Fixes, Improvements, Breaking Changes, Known Issues

**Files to Create:**
- `scripts/package_release.ps1`
- `src/VoiceStudio.App/Package.appxmanifest` (if not exists)
- `docs/release/SMOKE_CHECKLIST.md`
- `docs/release/RELEASE_NOTES_TEMPLATE.md`

**Files to Modify:**
- `src/VoiceStudio.App/Views/Dialogs/AboutDialog.xaml` (or create)
- `installer/create_installer.ps1` (enhance)

**Acceptance Criteria:**
- [ ] Packaging script complete and tested
- [ ] MSIX package configuration complete
- [ ] Installer script complete
- [ ] Smoke checklist comprehensive
- [ ] Version stamping in About dialog
- [ ] Release notes template created

---

## 🚀 START HERE

**Immediate Next Steps:**

1. **TASK 2.1: Resource Files Migration** (Start here - foundation for localization)
   - Expand resource keys
   - Update high-priority ViewModels
   - Update XAML files

2. **TASK 2.3: Toast Standardization** (High priority - UX consistency)
   - Enhance ToastNotificationService
   - Update all toast calls

3. **TASK 2.6: Packaging Script** (High priority - release readiness)
   - Create packaging script
   - Create MSIX config
   - Create smoke checklist

---

## 📊 CURRENT STATUS

**Worker 2 Progress:** 1/6 tasks complete (17%)  
**Remaining:** 5 tasks (26-34 hours estimated)

**Foundation Complete:**
- Resource files structure ready
- Toast control created
- Design system ready

**Next:** Migration and integration work

---

## ⚠️ IMPORTANT NOTES

1. **Do NOT recreate foundation** - Resource files, toast control, design tokens all exist
2. **Focus on migration** - Move hardcoded strings to resources
3. **Test as you go** - Verify resources load, toasts display correctly
4. **Use VSQ.* tokens** - Never hardcode colors, spacing, etc.

---

**Last Updated:** 2025-01-28  
**Status:** 🚧 **5 TASKS REMAINING - START WITH RESOURCE MIGRATION**
