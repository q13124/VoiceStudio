# Worker 3 Fresh Prompt - Focused Implementation

**Date:** 2025-01-28  
**Worker:** Worker 3 (Testing/QA/Documentation/Navigation)  
**Status:** 🚧 **READY - FOCUSED TASKS**

---

## 🎯 YOUR ROLE

You are **Worker 3**, responsible for:
- Testing infrastructure and test implementation
- Quality assurance and verification
- Documentation and guides
- Navigation and state management
- Diagnostics and observability

**IMPORTANT:** Do NOT redo completed work. Focus only on the remaining tasks below.

---

## ✅ ALREADY COMPLETE (DO NOT REDO)

1. ✅ **C# Test Framework** - MSTest framework set up, test project exists
2. ✅ **Example Tests** - MultiSelectServiceTests, GlobalSearchViewModelTests, etc. exist
3. ✅ **ErrorLoggingService Enhancement** - Correlation IDs and breadcrumbs added
4. ✅ **AnalyticsService** - Created with flow tracking
5. ✅ **FeatureFlagsService** - Created and registered in ServiceProvider
6. ✅ **ErrorPresentationService** - Created and registered
7. ✅ **EnhancedAsyncRelayCommand** - Created with in-flight guards
8. ✅ **CommandGuard** - Created for duplicate execution prevention
9. ✅ **NavigationService** - INavigationService, NavigationService, NavigationModels all exist and registered
10. ✅ **PanelLifecycleHelper** - Created with reflection-based lifecycle invocation
11. ✅ **PerformanceProfiler** - Enhanced with budgets
12. ✅ **Debouncer** - Created for expensive operations

**DO NOT recreate these. They are complete.**

---

## 📋 YOUR REMAINING TASKS (4 HIGH PRIORITY)

Based on the latest status, you have **4 high-priority tasks** remaining:

### TASK 3.3: Async/UX Safety Patterns (HIGH PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 8-10 hours  
**Foundation Ready:** ✅ ErrorPresentationService, ✅ EnhancedAsyncRelayCommand, ✅ CommandGuard

**What to Do:**

1. **Audit ViewModels for Async Safety:**
   - Review all ViewModels (70+ files in `src/VoiceStudio.App/ViewModels/`)
   - For each ViewModel with async commands, check:
     - [ ] Uses `CancellationToken` in async methods
     - [ ] Has in-flight guard (prevents duplicate execution)
     - [ ] Shows progress indicator during execution
     - [ ] Uses `ErrorPresentationService` for errors
     - [ ] Uses `EnhancedAsyncRelayCommand` or wraps with CommandGuard

2. **Update ViewModels to Use EnhancedAsyncRelayCommand:**
   - Replace `AsyncRelayCommand` with `EnhancedAsyncRelayCommand` where needed
   - Add progress reporting for long operations
   - Add cancellation support
   - Example:
     ```csharp
     // Before:
     SaveCommand = new AsyncRelayCommand(SaveAsync);
     
     // After:
     SaveCommand = new EnhancedAsyncRelayCommand(async (ct) => 
     {
         using var profiler = PerformanceProfiler.StartCommand("Save");
         await SaveAsync(ct);
     });
     ```

3. **Add Error Handling:**
   - Wrap async operations in try-catch
   - Use `ErrorPresentationService.ShowError()` for user-facing errors
   - Log errors with `ErrorLoggingService`
   - Example:
     ```csharp
     try
     {
         await operationAsync(ct);
     }
     catch (Exception ex)
     {
         var errorService = ServiceProvider.TryGetErrorPresentationService();
         errorService?.ShowError(ex, "Operation failed");
         var logService = ServiceProvider.TryGetErrorLoggingService();
         logService?.LogError(ex, "Operation context");
     }
     ```

4. **Create Async Patterns Documentation:**
   - File: `docs/developer/ASYNC_PATTERNS.md`
   - Document:
     - Best practices (always use CancellationToken, show progress, handle errors)
     - Common patterns (async command with progress, cancellation, error handling)
     - Anti-patterns to avoid (fire-and-forget, ignoring cancellation, no progress)

**Files to Modify:**
- All ViewModels with async operations (70+ files)
- Focus on high-traffic ViewModels first:
  - `ProfilesViewModel.cs`
  - `TimelineViewModel.cs`
  - `VoiceSynthesisViewModel.cs`
  - `EffectsMixerViewModel.cs`
  - `QualityDashboardViewModel.cs`

**Files to Create:**
- `docs/developer/ASYNC_PATTERNS.md`

**Acceptance Criteria:**
- [ ] All ViewModels audited
- [ ] All async commands use EnhancedAsyncRelayCommand or CommandGuard
- [ ] All async operations have error handling
- [ ] Progress indicators added for long operations
- [ ] Async patterns guide created
- [ ] No fire-and-forget operations remain

---

### TASK 3.6: UI Smoke Tests (HIGH PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 8-10 hours  
**Foundation Ready:** ✅ C# Test Framework exists

**What to Do:**

1. **Create Smoke Test Base:**
   - File: `src/VoiceStudio.App.Tests/UI/SmokeTestBase.cs`
   - Inherit from `TestBase` (already exists)
   - Add helper methods:
     ```csharp
     protected async Task WaitForPanelAsync(string panelId);
     protected async Task ClickButtonAsync(string buttonName);
     protected async Task EnterTextAsync(string controlName, string text);
     protected async Task WaitForElementAsync(string elementName);
     ```

2. **Create Launch Tests:**
   - File: `src/VoiceStudio.App.Tests/UI/LaunchSmokeTests.cs`
   - Test: `[UITestMethod] ApplicationLaunches()`
     - Verify app launches without crash
     - Verify MainWindow displays
     - Verify startup time < 3 seconds
   - Test: `[UITestMethod] MainWindowDisplaysCorrectly()`
     - Verify 3-row grid structure exists
     - Verify panel hosts visible
     - Verify navigation rail visible

3. **Create Panel Navigation Tests:**
   - File: `src/VoiceStudio.App.Tests/UI/PanelNavigationSmokeTests.cs`
   - Test: `[UITestMethod] NavigateToProfilesPanel()`
     - Navigate to Profiles panel
     - Verify ProfilesView displays
     - Verify panel loads < 500ms
   - Test: `[UITestMethod] NavigateToTimelinePanel()`
   - Test: `[UITestMethod] PanelSwitchingWorks()`
     - Switch between multiple panels
     - Verify each loads correctly

4. **Create Common Action Tests:**
   - File: `src/VoiceStudio.App.Tests/UI/CommonActionsSmokeTests.cs`
   - Test: `[UITestMethod] CreateProfile()`
     - Navigate to Profiles panel
     - Click "Create Profile" button
     - Enter profile name
     - Click "Save"
     - Verify success toast displayed
   - Test: `[UITestMethod] SynthesizeVoice()`
     - Navigate to synthesis panel
     - Enter text
     - Click synthesize
     - Verify synthesis completes

5. **Create Critical Path Test:**
   - File: `src/VoiceStudio.App.Tests/UI/CriticalPathSmokeTests.cs`
   - Test: `[UITestMethod] FullWorkflow()`
     - Create profile → Synthesize voice → Apply effect → Export
     - Verify all steps complete without errors

**Files to Create:**
- `src/VoiceStudio.App.Tests/UI/SmokeTestBase.cs`
- `src/VoiceStudio.App.Tests/UI/LaunchSmokeTests.cs`
- `src/VoiceStudio.App.Tests/UI/PanelNavigationSmokeTests.cs`
- `src/VoiceStudio.App.Tests/UI/CommonActionsSmokeTests.cs`
- `src/VoiceStudio.App.Tests/UI/CriticalPathSmokeTests.cs`

**Acceptance Criteria:**
- [ ] Smoke test base created
- [ ] Launch tests pass
- [ ] Panel navigation tests pass
- [ ] Common action tests pass
- [ ] Critical path test passes
- [ ] All tests run in < 2 minutes total

---

### TASK 3.7: ViewModel Contract Tests (HIGH PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 8-10 hours  
**Foundation Ready:** ✅ C# Test Framework, ✅ MockBackendClient exists

**What to Do:**

1. **Create Mock Services:**
   - File: `src/VoiceStudio.App.Tests/Services/MockAnalyticsService.cs`
     - Implements `IAnalyticsService`
     - Tracks events in memory
     - Provides `GetEvents()` for assertions
   - File: `src/VoiceStudio.App.Tests/Services/MockNavigationService.cs`
     - Implements `INavigationService`
     - Tracks navigation calls
     - Provides `GetNavigationHistory()` for assertions

2. **Create ViewModel Test Base:**
   - File: `src/VoiceStudio.App.Tests/ViewModels/ViewModelTestBase.cs`
   - Setup method creates mock services
   - Helper methods for common test patterns
   - Example:
     ```csharp
     protected MockBackendClient MockBackend { get; private set; }
     protected MockAnalyticsService MockAnalytics { get; private set; }
     protected MockNavigationService MockNavigation { get; private set; }
     
     [TestInitialize]
     public void Setup()
     {
         MockBackend = new MockBackendClient();
         MockAnalytics = new MockAnalyticsService();
         MockNavigation = new MockNavigationService();
     }
     ```

3. **Create Tests for Major ViewModels:**
   - Start with these high-priority ViewModels:
     - `ProfilesViewModelTests.cs` - Test CRUD operations
     - `TimelineViewModelTests.cs` - Test editing operations
     - `VoiceSynthesisViewModelTests.cs` - Test synthesis flow
     - `EffectsMixerViewModelTests.cs` - Test effect application
     - `QualityDashboardViewModelTests.cs` - Test quality metrics
   
   - For each ViewModel, test:
     - Command execution
     - State changes
     - Error handling
     - Cancellation support

4. **Expand Existing Tests:**
   - Enhance `GlobalSearchViewModelTests.cs` with more scenarios
   - Enhance `MultiSelectServiceTests.cs` with edge cases

**Files to Create:**
- `src/VoiceStudio.App.Tests/Services/MockAnalyticsService.cs`
- `src/VoiceStudio.App.Tests/Services/MockNavigationService.cs`
- `src/VoiceStudio.App.Tests/ViewModels/ViewModelTestBase.cs`
- `src/VoiceStudio.App.Tests/ViewModels/ProfilesViewModelTests.cs`
- `src/VoiceStudio.App.Tests/ViewModels/TimelineViewModelTests.cs`
- `src/VoiceStudio.App.Tests/ViewModels/VoiceSynthesisViewModelTests.cs`
- `src/VoiceStudio.App.Tests/ViewModels/EffectsMixerViewModelTests.cs`
- `src/VoiceStudio.App.Tests/ViewModels/QualityDashboardViewModelTests.cs`

**Acceptance Criteria:**
- [ ] Mock services created
- [ ] ViewModel test base created
- [ ] Tests for 5+ major ViewModels created
- [ ] All tests passing
- [ ] Test coverage >60% for tested ViewModels

---

### TASK 3.4: Diagnostics Pane Enhancements (MEDIUM PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 6-8 hours  
**Foundation Ready:** ✅ FeatureFlagsService, ✅ AnalyticsService, ✅ ErrorLoggingService

**What to Do:**

1. **Enhance DiagnosticsView:**
   - File: `src/VoiceStudio.App/Views/Panels/DiagnosticsView.xaml` (modify)
   - Add `TabView` with 5 tabs:
     - **Errors Tab:** Recent errors from ErrorLoggingService
     - **Analytics Tab:** Recent events from AnalyticsService
     - **Performance Tab:** Performance budgets and violations
     - **Feature Flags Tab:** List of flags with toggles
     - **Environment Tab:** App version, .NET version, config

2. **Enhance DiagnosticsViewModel:**
   - File: `src/VoiceStudio.App/ViewModels/DiagnosticsViewModel.cs` (modify)
   - Add properties for each tab's data
   - Add commands to refresh data
   - Add command to toggle feature flags

3. **Implement Each Tab:**
   - Errors Tab: Load from `ErrorLoggingService.GetRecentErrors()`
   - Analytics Tab: Load from `AnalyticsService.GetRecentEvents()`
   - Performance Tab: Load from `PerformanceProfiler` (if available)
   - Feature Flags Tab: Load from `FeatureFlagsService.GetAllFlags()`
   - Environment Tab: Load from system info

**Files to Modify:**
- `src/VoiceStudio.App/Views/Panels/DiagnosticsView.xaml`
- `src/VoiceStudio.App/ViewModels/DiagnosticsViewModel.cs`

**Acceptance Criteria:**
- [ ] TabView added with 5 tabs
- [ ] Errors tab displays recent errors
- [ ] Analytics tab displays recent events
- [ ] Feature flags tab allows toggling
- [ ] Environment tab displays system info
- [ ] All tabs functional

---

## 🚀 START HERE - RECOMMENDED ORDER

**Start with TASK 3.3 (Async Safety)** - It's the foundation for everything else:
1. Audit ViewModels (create a checklist)
2. Update 5-10 high-priority ViewModels first
3. Create async patterns guide
4. Continue with remaining ViewModels

**Then TASK 3.6 (UI Smoke Tests)** - Quick wins:
1. Create SmokeTestBase
2. Create launch tests (easiest)
3. Create navigation tests
4. Create common action tests

**Then TASK 3.7 (ViewModel Tests)** - Build on smoke tests:
1. Create mock services
2. Create test base
3. Test 5 major ViewModels
4. Expand to more ViewModels

**Finally TASK 3.4 (Diagnostics)** - Polish:
1. Add TabView to DiagnosticsView
2. Implement each tab one at a time
3. Test each tab

---

## ⚠️ IMPORTANT NOTES

1. **Do NOT recreate completed services** - They already exist and are registered
2. **Focus on one task at a time** - Complete TASK 3.3 before moving to 3.6
3. **Test as you go** - Run tests after each change
4. **Ask for help if stuck** - Don't freeze, ask the Overseer for clarification
5. **Use existing patterns** - Look at existing tests and ViewModels for examples

---

## 📊 PROGRESS TRACKING

After completing each task, update:
- `docs/governance/overseer/REMAINING_TASKS_SUMMARY_2025-01-28.md`
- Mark task as complete
- Document what was created/modified

---

**Last Updated:** 2025-01-28  
**Status:** 🚧 **READY - FOCUSED ON 4 REMAINING TASKS**
