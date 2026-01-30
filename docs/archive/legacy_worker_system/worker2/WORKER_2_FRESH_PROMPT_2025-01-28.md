# Worker 2 Fresh Prompt - Focused Implementation

**Date:** 2025-01-28  
**Worker:** Worker 2 (UI/UX/Controls/Localization/Packaging)  
**Status:** 🚧 **READY - FOCUSED TASKS**

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

1. ✅ **Reusable Controls** - VSQButton, VSQCard, VSQFormField, VSQBadge, VSQProgressIndicator created
2. ✅ **Accessibility Helpers** - AccessibilityHelpers.cs created with WCAG compliance
3. ✅ **Performance Budgets** - PerformanceProfiler enhanced with budgets
4. ✅ **DesignTokens Expansion** - Complete spacing, radii, typography, accessibility tokens added
5. ✅ **Launch Profiles** - VS Code and Visual Studio launch profiles created
6. ✅ **Microcopy Guide** - Complete guide created (`docs/design/MICROCOPY_GUIDE.md`)
7. ✅ **Resource Files Foundation** - Resources.resw created with 50+ keys, ResourceHelper exists
8. ✅ **Toast Control** - VSQToastNotification control created, ToastStyles.xaml exists

**DO NOT recreate these. They are complete.**

---

## 📋 YOUR REMAINING TASKS (5 TASKS)

### TASK 2.1: Resource Files Migration (HIGH PRIORITY)

**Status:** 🚧 **FOUNDATION DONE - MIGRATION PENDING**  
**Time:** 6-8 hours  
**Foundation Ready:** ✅ Resources.resw (50+ keys), ✅ ResourceHelper.cs, ✅ en-US/Resources.resw

**What to Do:**

1. **Expand Resource Keys:**

   - Audit ViewModels for additional hardcoded strings (70+ files)
   - Audit XAML files for hardcoded text (150+ files)
   - Add missing keys to `Resources.resw` and `en-US/Resources.resw`
   - Update `docs/developer/RESOURCE_KEYS.md` with new keys

2. **Update ViewModels:**

   - Replace hardcoded strings with `ResourceHelper.GetString()`
   - Focus on high-priority ViewModels first:
     - ProfilesViewModel
     - TimelineViewModel
     - VoiceSynthesisViewModel
     - EffectsMixerViewModel
     - QualityDashboardViewModel
   - Example:

     ```csharp
     // Before:
     Title = "Voice Profiles";
     ErrorMessage = "Failed to load profiles";

     // After:
     Title = ResourceHelper.GetString("Panel.Profiles.Title", "Voice Profiles");
     ErrorMessage = ResourceHelper.GetString("Error.LoadFailed");
     ```

3. **Update XAML Files:**

   - Replace hardcoded `Text` attributes with `x:Uid`
   - Add resource references in Resources.resw
   - Example:

     ```xml
     <!-- Before: -->
     <TextBlock Text="Voice Profiles" />

     <!-- After: -->
     <TextBlock x:Uid="ProfilesPanelTitle" />
     <!-- In Resources.resw: ProfilesPanelTitle.Text = "Voice Profiles" -->
     ```

4. **Verify Migration:**
   - Search codebase for remaining hardcoded strings
   - Test all resource keys load correctly
   - Verify fallback to default values works

**Files to Modify:**

- All ViewModels with hardcoded strings (70+ files)
- All XAML files with hardcoded text (150+ files)
- `src/VoiceStudio.App/Resources/Resources.resw` (expand)
- `src/VoiceStudio.App/Resources/en-US/Resources.resw` (expand)
- `docs/developer/RESOURCE_KEYS.md` (update)

**Acceptance Criteria:**

- [ ] All ViewModels use ResourceHelper
- [ ] All XAML uses x:Uid
- [ ] No hardcoded strings remain
- [ ] All resource keys documented
- [ ] All resources load correctly

---

### TASK 2.3: Toast Styles Enhancement (HIGH PRIORITY)

**Status:** 🚧 **CONTROL CREATED - SERVICE ENHANCEMENT PENDING**  
**Time:** 2-4 hours  
**Foundation Ready:** ✅ VSQToastNotification control, ✅ ToastStyles.xaml

**What to Do:**

1. **Enhance ToastNotificationService:**

   - File: `src/VoiceStudio.App/Services/ToastNotificationService.cs` (modify)
   - Optionally use VSQToastNotification control instead of programmatic creation
   - Ensure all toast types use styles from ToastStyles.xaml
   - Verify typed methods (ShowSuccess, ShowError, ShowWarning, ShowInfo) apply correct styles

2. **Verify Toast Styles Applied:**

   - Check that all toast types use VSQ.\* design tokens
   - Verify animations work correctly
   - Test queue management (max 3-5 toasts)

3. **Update Toast Calls (if needed):**
   - Audit all `ToastNotificationService` usage (50+ files)
   - Ensure all calls use typed methods (ShowSuccess, ShowError, etc.)
   - Verify consistent styling

**Files to Modify:**

- `src/VoiceStudio.App/Services/ToastNotificationService.cs`
- Any files using generic `Show()` method (if any)

**Acceptance Criteria:**

- [ ] ToastNotificationService uses VSQToastNotification or applies styles correctly
- [ ] All toast types styled consistently
- [ ] All toast calls use typed methods
- [ ] Queue management works
- [ ] Animations smooth

---

### TASK 2.6: Installer Release Prep & Smoke Checklist (HIGH PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 6-8 hours

**What to Do:**

1. **Release prep (single lane: installer only):**

   - Use: `scripts/prepare-release.ps1` + `installer/build-installer.ps1`
   - Steps:
     - Update version + changelog
     - Build in Release mode
     - Create installer (Inno Setup / WiX)
     - Create distribution package under `release/dist`
   - **Note:** MSIX is not used; historical MSIX artifacts live under `docs/archive/msix/`

2. **Create Smoke Checklist:**

   - File: `docs/release/SMOKE_CHECKLIST.md`
   - Pre-release verification steps:
     - All tests pass
     - Performance budgets met
     - Accessibility checks pass
     - Installer works on clean systems
     - All key panels functional
     - Backend integration works
     - Version displayed correctly

3. **Add Version Stamping:**
   - File: `src/VoiceStudio.App/Views/Dialogs/AboutDialog.xaml` (create or modify)
   - Display: App version, build date, .NET version, Windows SDK version
   - Use VersionService for version info

**Files to Create:**

- `docs/release/SMOKE_CHECKLIST.md`
- `src/VoiceStudio.App/Views/Dialogs/AboutDialog.xaml` (if not exists)

**Files to Modify:**

- `src/VoiceStudio.App/Services/VersionService.cs` (if needs enhancement)

**Acceptance Criteria:**

- [ ] Installer-based release prep works end-to-end
- [ ] Smoke checklist comprehensive
- [ ] Version stamping in About dialog
- [ ] All packaging steps work

---

### TASK 2.2: Locale Switch Toggle (MEDIUM PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 4-6 hours  
**Dependencies:** TASK 2.1 (Resource Files) - Can start after resource migration begins

**What to Do:**

1. **Create Localization Service:**

   - File: `src/VoiceStudio.Core/Services/ILocalizationService.cs`
   - File: `src/VoiceStudio.App/Services/LocalizationService.cs`
   - Methods: `GetCurrentLocale()`, `SetLocaleAsync()`, `GetString()`, `GetAvailableLocales()`
   - Event: `LocaleChanged`
   - Persist locale to user settings

2. **Create Locale Switch Control:**

   - File: `src/VoiceStudio.App/Controls/LocaleSwitchControl.xaml` + `.xaml.cs`
   - ComboBox for locale selection
   - Display locale names in native language
   - Accessibility support

3. **Add to Settings Panel:**

   - File: `src/VoiceStudio.App/Views/Panels/SettingsView.xaml` (modify)
   - Add locale switch control
   - Save locale preference on change

4. **Update ResourceHelper:**
   - File: `src/VoiceStudio.App/Utilities/ResourceHelper.cs` (modify)
   - Use LocalizationService instead of direct ResourceLoader
   - Listen to LocaleChanged event

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

---

### TASK 2.4: Empty States & Loading Skeletons (MEDIUM PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 6-8 hours

**What to Do:**

1. **Audit Existing Empty States:**

   - Review all panels (30+ files)
   - Document current implementations
   - Identify inconsistencies

2. **Enhance EmptyState Control:**

   - File: `src/VoiceStudio.App/Controls/EmptyState.xaml` (modify or create)
   - Properties: Title, Message, Icon, ActionButtonText, ActionButtonCommand
   - Use VSQ.\* design tokens
   - Accessibility support

3. **Enhance SkeletonScreen Control:**

   - File: `src/VoiceStudio.App/Controls/SkeletonScreen.xaml` (modify or create)
   - Properties: SkeletonType, ItemCount
   - Standardize skeleton patterns (List, Card, Form, Table)
   - Smooth shimmer animation

4. **Update All Panels:**
   - Replace custom empty states with `EmptyState` control
   - Replace custom loading with `SkeletonScreen` control
   - Ensure consistency (30+ panels)

**Files to Create/Modify:**

- `src/VoiceStudio.App/Controls/EmptyState.xaml` (enhance or create)
- `src/VoiceStudio.App/Controls/SkeletonScreen.xaml` (enhance or create)
- `docs/design/EMPTY_STATE_PATTERNS.md` (create)

**Files to Modify:**

- All panels with custom empty/loading states (30+ files)

**Acceptance Criteria:**

- [ ] EmptyState control standardized
- [ ] SkeletonScreen control standardized
- [ ] All panels use standardized controls
- [ ] Patterns documented
- [ ] Consistency achieved

---

## 🚀 START HERE - RECOMMENDED ORDER

**Start with TASK 2.1 (Resource Files Migration)** - It's the foundation:

1. Expand resource keys (audit ViewModels and XAML)
2. Update 5-10 high-priority ViewModels first
3. Update high-priority XAML files
4. Continue with remaining files

**Then TASK 2.3 (Toast Enhancement)** - Quick win:

1. Enhance ToastNotificationService to use VSQToastNotification or ensure styles applied
2. Verify all toast types styled correctly
3. Test queue management

**Then TASK 2.6 (Packaging)** - Release readiness:

1. Verify installer-only release prep (`scripts/prepare-release.ps1`)
2. Create smoke checklist
3. Add version stamping

**Then TASK 2.2 (Locale Switch)** - After resources migrated:

1. Create LocalizationService
2. Create locale switch control
3. Add to settings panel

**Finally TASK 2.4 (Empty States)** - Polish:

1. Enhance controls
2. Update panels one at a time
3. Document patterns

---

## ⚠️ IMPORTANT NOTES

1. **Do NOT recreate completed controls/services** - They already exist
2. **Focus on migration** - TASK 2.1 is the biggest task (70+ ViewModels, 150+ XAML)
3. **Use existing patterns** - Look at ResourceHelper and VSQToastNotification for examples
4. **Test as you go** - Verify resources load correctly after each batch
5. **Ask for help if stuck** - Don't freeze, ask the Overseer for clarification

---

## 📊 PROGRESS TRACKING

After completing each task, update:

- `docs/governance/overseer/REMAINING_TASKS_SUMMARY_2025-01-28.md`
- Mark task as complete
- Document what was created/modified

---

## 🎯 QUICK REFERENCE

### ResourceHelper Usage

```csharp
// Basic usage
Title = ResourceHelper.GetString("Panel.Profiles.Title", "Voice Profiles");

// With formatting
var message = ResourceHelper.FormatString("Success.ProfileCreated", profileName);
```

### Toast Usage

```csharp
// Use typed methods
_toastNotificationService?.ShowSuccess("Profile created", "Success");
_toastNotificationService?.ShowError("Failed to load", "Error");
```

### VSQ Design Tokens

- Colors: `VSQ.Success`, `VSQ.Error`, `VSQ.Warn`, `VSQ.Accent.Cyan`
- Spacing: `VSQ.Spacing.Medium`, `VSQ.Spacing.Large`
- Typography: `VSQ.FontSize.Body`, `VSQ.FontSize.Subheading`

---

**Last Updated:** 2025-01-28  
**Status:** 🚧 **READY - FOCUSED ON 5 REMAINING TASKS**
