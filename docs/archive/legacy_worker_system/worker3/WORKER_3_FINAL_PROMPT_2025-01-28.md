# Worker 3 Final Prompt - Testing/QA/Documentation/Navigation

**Date:** 2025-01-28  
**Worker:** Worker 3 (Testing/QA/Documentation/Navigation Specialist)  
**Status:** 🚧 **READY - 4 TASKS REMAINING**

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
2. ✅ **Example Tests** - MultiSelectServiceTests, GlobalSearchViewModelTests, etc.
3. ✅ **ErrorLoggingService Enhancement** - Correlation IDs and breadcrumbs
4. ✅ **AnalyticsService** - Created with flow tracking
5. ✅ **FeatureFlagsService** - Created and registered
6. ✅ **ErrorPresentationService** - Created and registered
7. ✅ **EnhancedAsyncRelayCommand** - Created with in-flight guards
8. ✅ **CommandGuard** - Created for duplicate execution prevention
9. ✅ **NavigationService** - INavigationService, NavigationService, NavigationModels complete
10. ✅ **PanelLifecycleHelper** - Created with reflection-based lifecycle
11. ✅ **PerformanceProfiler** - Enhanced with budgets
12. ✅ **Debouncer** - Created for expensive operations
13. ✅ **Async Patterns Documentation** - `docs/developer/ASYNC_PATTERNS.md` complete
14. ✅ **ProfilesViewModel** - Async safety complete (12/12 commands updated)
15. ✅ **TimelineViewModel** - Async safety complete (verified)
16. ✅ **VoiceSynthesisViewModel** - Async safety complete (verified)
17. ✅ **QualityDashboardViewModel** - Async safety complete (verified)
18. ✅ **RecordingViewModel** - Async safety complete (verified)

**DO NOT recreate these. They are complete.**

---

## 📋 YOUR REMAINING TASKS (4 TASKS)

### TASK 3.3: Complete Async Safety Migration (HIGH PRIORITY)

**Status:** 🚧 **IN PROGRESS - 5/72 ViewModels Complete**  
**Time:** 6-8 hours remaining  
**Progress:** ProfilesViewModel, TimelineViewModel, VoiceSynthesisViewModel, QualityDashboardViewModel, RecordingViewModel complete

**What to Do:**

1. **Continue ViewModel Migration:**

   - Remaining ViewModels: ~67 files
   - Focus on medium-priority ViewModels next:
     - QualityControlViewModel
     - EffectsMixerViewModel
     - TextSpeechEditorViewModel
     - MultiVoiceGeneratorViewModel
     - TodoPanelViewModel
   - Follow the same pattern as completed ViewModels

2. **Migration Pattern (Reference):**

   ```csharp
   // 1. Replace AsyncRelayCommand with EnhancedAsyncRelayCommand
   LoadCommand = new EnhancedAsyncRelayCommand(async (ct) =>
   {
       using var profiler = PerformanceProfiler.StartCommand("Load");
       await LoadAsync(ct);
   });

   // 2. Update async method to accept CancellationToken
   private async Task LoadAsync(CancellationToken cancellationToken)
   {
       IsLoading = true;
       ErrorMessage = null;

       try
       {
           var data = await _backendClient.GetDataAsync(cancellationToken);
           Data = data;
       }
       catch (OperationCanceledException)
       {
           return; // User cancelled
       }
       catch (Exception ex)
       {
           ErrorMessage = ResourceHelper.GetString("Error.LoadFailed");
           _errorService?.ShowError(ex, "Failed to load data");
           _logService?.LogError(ex, "LoadData");
       }
       finally
       {
           IsLoading = false;
       }
   }
   ```

3. **Verify Each ViewModel:**
   - All commands use EnhancedAsyncRelayCommand
   - All async methods accept CancellationToken
   - All methods handle OperationCanceledException
   - All methods use ErrorPresentationService and ErrorLoggingService
   - No fire-and-forget operations remain

**Files to Modify:**

- Remaining ViewModels (~67 files in `src/VoiceStudio.App/ViewModels/` and `src/VoiceStudio.App/Views/Panels/`)

**Acceptance Criteria:**

- [ ] All ViewModels use EnhancedAsyncRelayCommand
- [ ] All async methods accept CancellationToken
- [ ] All methods have proper error handling
- [ ] No fire-and-forget operations
- [ ] All ViewModels verified

---

### TASK 3.6: UI Smoke Tests (HIGH PRIORITY)

**Status:** ⏳ **PENDING**  
**Time:** 8-10 hours  
**Foundation Ready:** ✅ C# Test Framework exists

**What to Do:**

1. **Create Smoke Test Base:**

   - File: `src/VoiceStudio.App.Tests/UI/SmokeTestBase.cs`
   - Inherit from existing `TestBase`
   - Helper methods:
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
     - Verify 3-row grid structure
     - Verify panel hosts visible

3. **Create Panel Navigation Tests:**

   - File: `src/VoiceStudio.App.Tests/UI/PanelNavigationSmokeTests.cs`
   - Test: `[UITestMethod] NavigateToProfilesPanel()`
   - Test: `[UITestMethod] NavigateToTimelinePanel()`
   - Test: `[UITestMethod] PanelSwitchingWorks()`

4. **Create Common Action Tests:**

   - File: `src/VoiceStudio.App.Tests/UI/CommonActionsSmokeTests.cs`
   - Test: `[UITestMethod] CreateProfile()`
   - Test: `[UITestMethod] SynthesizeVoice()`
   - Test: `[UITestMethod] ApplyEffect()`

5. **Create Critical Path Test:**
   - File: `src/VoiceStudio.App.Tests/UI/CriticalPathSmokeTests.cs`
   - Test: `[UITestMethod] FullWorkflow()`
     - Create profile → Synthesize → Apply effect → Export

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
- [ ] All tests run in < 2 minutes

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
   - Setup: Create mock services, register in test DI
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

   - File: `src/VoiceStudio.App/Views/Panels/DiagnosticsView.xaml`
   - Add `TabView` with 5 tabs:
     - **Errors Tab:** Recent errors from ErrorLoggingService
     - **Analytics Tab:** Recent events from AnalyticsService
     - **Performance Tab:** Performance budgets and violations
     - **Feature Flags Tab:** List of flags with toggles
     - **Environment Tab:** App version, .NET version, config

2. **Enhance DiagnosticsViewModel:**

   - File: `src/VoiceStudio.App/ViewModels/DiagnosticsViewModel.cs`
   - Add properties for each tab's data:
     - `ObservableCollection<ErrorLogEntry> RecentErrors`
     - `ObservableCollection<AnalyticsEvent> RecentAnalyticsEvents`
     - `ObservableCollection<PerformanceMetric> PerformanceMetrics`
     - `ObservableCollection<FeatureFlag> FeatureFlags`
     - `EnvironmentInfo EnvironmentInfo`
   - Add commands:
     - `ICommand RefreshAnalyticsCommand`
     - `ICommand RefreshPerformanceCommand`
     - `ICommand ToggleFeatureFlagCommand`
     - `ICommand ExportLogsCommand`

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

## 🚀 START HERE

**Immediate Next Steps:**

1. **TASK 3.3: Complete Async Safety** (Continue migration)

   - Update remaining ViewModels systematically
   - Follow established pattern
   - Verify each ViewModel

2. **TASK 3.6: UI Smoke Tests** (High priority - QA)

   - Create test base
   - Create launch tests (easiest)
   - Create navigation tests

3. **TASK 3.7: ViewModel Tests** (High priority - QA)
   - Create mock services
   - Create test base
   - Test 5 major ViewModels

---

## 📊 CURRENT STATUS

**Worker 3 Progress:** 7/8 tasks complete (87.5%)  
**Remaining:** 1-4 tasks (depending on async safety progress)

**Completed:**

- 5 high-priority ViewModels (Profiles, Timeline, VoiceSynthesis, QualityDashboard, Recording)
- All foundation services ready

**Next:** Complete remaining ViewModels, add tests

---

## ⚠️ IMPORTANT NOTES

1. **Do NOT recreate completed services** - They exist and are registered
2. **Follow established patterns** - Use completed ViewModels as reference
3. **Test as you go** - Run tests after each change
4. **Use existing test framework** - MSTest is set up

---

**Last Updated:** 2025-01-28  
**Status:** 🚧 **4 TASKS REMAINING - CONTINUE ASYNC SAFETY MIGRATION**
