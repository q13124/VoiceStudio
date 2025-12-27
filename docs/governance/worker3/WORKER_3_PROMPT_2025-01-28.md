# Worker 3 Prompt - Testing/QA/Documentation/Navigation
## Complete Task Instructions

**Date:** 2025-01-28  
**Worker:** Worker 3 (Testing/QA/Documentation Specialist)  
**Status:** 🚧 **READY FOR IMPLEMENTATION**

---

## 🎯 YOUR ROLE

You are **Worker 3**, responsible for:
- Testing infrastructure and test implementation
- Quality assurance and verification
- Documentation and guides
- Navigation and state management
- Diagnostics and observability

---

## ✅ COMPLETED WORK (DO NOT REDO)

1. ✅ **C# Test Framework** - MSTest framework set up, test project created
2. ✅ **Example Tests** - MultiSelectServiceTests, GlobalSearchViewModelTests, ToastNotificationServiceTests, ContextMenuServiceTests created
3. ✅ **ErrorLoggingService Enhancement** - Correlation IDs and breadcrumbs added
4. ✅ **AnalyticsService** - Created with flow tracking
5. ✅ **Debouncer Utility** - Created for expensive command debouncing
6. ✅ **Performance Budgets** - Added to PerformanceProfiler

---

## 📋 YOUR TASKS (8 TASKS - 50-60 HOURS)

### TASK 3.1: NavigationService Implementation

**Priority:** HIGH  
**Estimated Time:** 6-8 hours  
**Status:** ⏳ **PENDING**

**Objective:** Create NavigationService to coordinate panel navigation, deep-links, and backstack behavior.

**Detailed Steps:**

1. **Create NavigationService Interface:**
   - File: `src/VoiceStudio.Core/Services/INavigationService.cs`
   - Methods:
     - `Task NavigateToPanelAsync(string panelId, Dictionary<string, object>? parameters = null, CancellationToken cancellationToken = default)`
     - `Task NavigateBackAsync(CancellationToken cancellationToken = default)`
     - `bool CanNavigateBack()`
     - `string? GetCurrentPanelId()`
     - `IReadOnlyList<NavigationEntry> GetBackStack()`
     - `void ClearBackStack()`
   - Events:
     - `event EventHandler<NavigationEventArgs> NavigationChanged`
     - `event EventHandler BackStackChanged`

2. **Create Navigation Models:**
   - File: `src/VoiceStudio.Core/Models/NavigationModels.cs`
   - Classes:
     - `NavigationEntry` - Panel ID, parameters, timestamp
     - `NavigationEventArgs` - Old panel, new panel, parameters

3. **Implement NavigationService:**
   - File: `src/VoiceStudio.App/Services/NavigationService.cs`
   - Integrate with `PanelStateService`
   - Manage backstack (max 50 entries)
   - Support deep-links:
     - Format: `panelId?param1=value1&param2=value2`
     - Parse query string parameters
     - Pass parameters to panel
   - Persist navigation state to user settings
   - Restore navigation state on app startup

4. **Add Deep-Link Support:**
   - Parse deep-link format: `voicestudio://profiles?profileId=123`
   - Support protocol handler (optional, for future)
   - Support command-line arguments (optional)
   - Navigate to panel with parameters

5. **Integrate with MainWindow:**
   - File: `src/VoiceStudio.App/MainWindow.xaml.cs` (modify)
   - Use NavigationService for panel navigation
   - Handle back button (if available in UI)
   - Update UI based on navigation state
   - Support keyboard shortcuts (Alt+Left for back)

6. **Add Navigation Breadcrumbs:**
   - File: `src/VoiceStudio.App/Controls/NavigationBreadcrumbs.xaml` + `.xaml.cs`
   - Display navigation path
   - Support clicking breadcrumbs to navigate
   - Visual indicator of current location
   - Example: "Profiles > Profile Details > Edit"

7. **Test Navigation:**
   - Test panel navigation
   - Test back navigation
   - Test deep-links
   - Test navigation persistence
   - Test breadcrumbs

**Files to Create:**
- `src/VoiceStudio.Core/Services/INavigationService.cs`
- `src/VoiceStudio.Core/Models/NavigationModels.cs`
- `src/VoiceStudio.App/Services/NavigationService.cs`
- `src/VoiceStudio.App/Controls/NavigationBreadcrumbs.xaml` + `.xaml.cs`

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
- [ ] Navigation persistence works

---

### TASK 3.2: Panel Lifecycle Documentation

**Priority:** MEDIUM  
**Estimated Time:** 4-6 hours  
**Status:** ⏳ **PENDING**

**Objective:** Document panel lifecycle (init/activate/deactivate) and persist/restore rules in Panel Cookbook.

**Detailed Steps:**

1. **Extend IPanelView Interface:**
   - File: `src/VoiceStudio.Core/Panels/IPanelView.cs` (modify)
   - Add lifecycle methods:
     - `Task OnInitializeAsync(CancellationToken cancellationToken = default)`
     - `Task OnActivateAsync(CancellationToken cancellationToken = default)`
     - `Task OnDeactivateAsync(CancellationToken cancellationToken = default)`
     - `Task<Dictionary<string, object>> OnPersistAsync(CancellationToken cancellationToken = default)`
     - `Task OnRestoreAsync(Dictionary<string, object> state, CancellationToken cancellationToken = default)`

2. **Create Panel Lifecycle Helper:**
   - File: `src/VoiceStudio.App/Utilities/PanelLifecycleHelper.cs`
   - Helper methods:
     - `Task InvokeLifecycleMethodAsync(object panel, string methodName, CancellationToken cancellationToken)`
     - `bool ImplementsLifecycle(object panel)`
   - Common patterns:
     - Load data in Initialize
     - Refresh data in Activate
     - Save state in Deactivate
     - Persist selection in Persist
     - Restore selection in Restore

3. **Create Panel Cookbook:**
   - File: `docs/developer/PANEL_COOKBOOK.md`
   - Sections:
     - **Panel Lifecycle:**
       - Initialize: Load data, set up services
       - Activate: Refresh data, focus controls
       - Deactivate: Save state, cleanup
       - Persist: Save user preferences, selection
       - Restore: Restore user preferences, selection
     - **Command Patterns:**
       - Async commands with cancellation
       - In-flight guards
       - Progress indicators
       - Error handling
     - **Validation Patterns:**
       - Input validation
       - Business rule validation
       - Error presentation
     - **Async Operation Patterns:**
       - Loading states
       - Progress reporting
       - Cancellation support
     - **State Management Patterns:**
       - ViewModel state
       - Panel state
       - Persistence rules
     - **Error Handling Patterns:**
       - Toast notifications
       - Inline errors
       - Error dialogs

4. **Document Persist/Restore Rules:**
   - What state to persist:
     - User selections
     - Filter/search terms
     - Sort order
     - View preferences
   - What NOT to persist:
     - Temporary UI state
     - Loading indicators
     - Error states
   - When to persist:
     - On panel deactivate
     - On app suspend
     - Periodically (for long-running panels)
   - How to restore:
     - On panel activate
     - On app resume
     - Validate restored state

5. **Create Panel Template:**
   - Directory: `docs/developer/templates/PanelTemplate/`
   - Files:
     - `PanelView.xaml` - XAML template
     - `PanelView.xaml.cs` - Code-behind template
     - `PanelViewModel.cs` - ViewModel template
     - `PanelRegistration.cs` - Registration example
     - `README.md` - Template usage instructions

6. **Update Existing Panels:**
   - Add lifecycle methods to key panels:
     - ProfilesView
     - TimelineView
     - EffectsMixerView
     - QualityDashboardView
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
**Status:** ⏳ **PENDING**

**Objective:** Standardize async patterns in ViewModels with cancellation tokens, in-flight guards, and user-visible progress.

**Detailed Steps:**

1. **Enhance AsyncRelayCommand:**
   - File: `src/VoiceStudio.App/Utilities/AsyncRelayCommand.cs` (enhance existing or create)
   - Add properties:
     - `bool IsExecuting` - In-flight guard
     - `IProgress<double>? Progress` - Progress reporting
     - `CancellationTokenSource? CancellationTokenSource` - Cancellation support
   - Add methods:
     - `void Cancel()` - Cancel execution
     - `void ReportProgress(double progress)` - Report progress (0-100)
   - Prevent duplicate execution when `IsExecuting` is true
   - Auto-disable command during execution

2. **Create Command Guard Helper:**
   - File: `src/VoiceStudio.App/Utilities/CommandGuard.cs`
   - Static class with methods:
     - `bool IsCommandExecuting(ICommand command)`
     - `void PreventDuplicateExecution(ICommand command)`
     - `IDisposable CreateExecutionScope(ICommand command)` - Using pattern
   - Track in-flight operations per command
   - Thread-safe implementation

3. **Create Error Presentation Service:**
   - File: `src/VoiceStudio.App/Services/ErrorPresentationService.cs`
   - Interface: `IErrorPresentationService`
   - Methods:
     - `void ShowError(Exception exception, string context, ErrorPresentationType type = ErrorPresentationType.Toast)`
     - `void ShowError(string message, string context, ErrorPresentationType type = ErrorPresentationType.Toast)`
   - Enum: `ErrorPresentationType` (Toast, Inline, Dialog)
   - Decision logic:
     - Toast: Transient errors, non-critical
     - Inline: Form validation errors
     - Dialog: Critical errors requiring user action

4. **Audit All ViewModels:**
   - Review all async operations (70+ ViewModels)
   - Checklist for each:
     - [ ] Uses CancellationToken
     - [ ] Has in-flight guard
     - [ ] Shows progress indicator
     - [ ] Handles errors properly
     - [ ] Uses ErrorPresentationService
   - Create audit report

5. **Update All Commands:**
   - Replace fire-and-forget with proper async
   - Add cancellation support
   - Add progress indicators
   - Add error handling
   - Use ErrorPresentationService
   - Files to update (70+ ViewModels)

6. **Create Async Patterns Guide:**
   - File: `docs/developer/ASYNC_PATTERNS.md`
   - Sections:
     - **Best Practices:**
       - Always use CancellationToken
       - Always check cancellation
       - Always show progress
       - Always handle errors
     - **Common Patterns:**
       - Async command with progress
       - Async command with cancellation
       - Long-running operation pattern
     - **Anti-Patterns to Avoid:**
       - Fire-and-forget
       - Ignoring cancellation
       - No progress indication
       - Swallowing exceptions

**Files to Create:**
- `src/VoiceStudio.App/Utilities/CommandGuard.cs`
- `src/VoiceStudio.App/Services/IErrorPresentationService.cs`
- `src/VoiceStudio.App/Services/ErrorPresentationService.cs`
- `docs/developer/ASYNC_PATTERNS.md`

**Files to Modify:**
- `src/VoiceStudio.App/Utilities/AsyncRelayCommand.cs` (enhance)
- All ViewModels with async operations (70+ files)

**Acceptance Criteria:**
- [ ] AsyncRelayCommand enhanced
- [ ] CommandGuard created
- [ ] ErrorPresentationService created
- [ ] All ViewModels audited
- [ ] All commands updated
- [ ] Async patterns guide complete
- [ ] No fire-and-forget operations remain

---

### TASK 3.4: Diagnostics Pane Enhancements

**Priority:** MEDIUM  
**Estimated Time:** 6-8 hours  
**Dependencies:** AnalyticsService (✅ exists), FeatureFlagsService (create)

**Objective:** Enhance DiagnosticsView with tabs for errors, analytics, performance, feature flags, and environment info.

**Detailed Steps:**

1. **Create FeatureFlagsService:**
   - File: `src/VoiceStudio.App/Services/IFeatureFlagsService.cs`
   - Methods:
     - `bool IsEnabled(string flag)`
     - `void SetFlag(string flag, bool enabled)`
     - `IReadOnlyDictionary<string, bool> GetAllFlags()`
     - `event EventHandler<string> FlagChanged`
   - File: `src/VoiceStudio.App/Services/FeatureFlagsService.cs`
   - Persist flags to user settings
   - Default flags:
     - `HeavyPanelsEnabled` (default: true)
     - `AnalyticsEnabled` (default: true)
     - `PerformanceProfilingEnabled` (default: false)
     - `StressTestMode` (default: false)

2. **Enhance DiagnosticsView:**
   - File: `src/VoiceStudio.App/Views/Panels/DiagnosticsView.xaml` (modify)
   - Add TabView with tabs:
     - **Errors Tab:**
       - Recent errors list
       - Filter by level (Error, Warning, Info)
       - Search functionality
       - Export logs button
     - **Analytics Tab:**
       - Recent analytics events
       - Filter by event type
       - Timeline visualization
       - Correlation ID linking
     - **Performance Tab:**
       - Performance budgets display
       - Budget violations list
       - Panel load times
       - Command execution times
       - Chart visualization
     - **Feature Flags Tab:**
       - List all feature flags
       - Toggle switches for each flag
       - Flag descriptions
       - Save changes button
     - **Environment Tab:**
       - App version
       - .NET version
       - Windows version
       - Backend URL
       - Log level
       - Performance profiling enabled
       - Environment variables

3. **Enhance DiagnosticsViewModel:**
   - File: `src/VoiceStudio.App/ViewModels/DiagnosticsViewModel.cs` (modify)
   - Add properties:
     - `ObservableCollection<AnalyticsEvent> RecentAnalyticsEvents`
     - `ObservableCollection<PerformanceMetric> PerformanceMetrics`
     - `ObservableCollection<FeatureFlag> FeatureFlags`
     - `EnvironmentInfo EnvironmentInfo`
   - Add commands:
     - `ICommand RefreshAnalyticsCommand`
     - `ICommand RefreshPerformanceCommand`
     - `ICommand ToggleFeatureFlagCommand`
     - `ICommand ExportLogsCommand`

4. **Add Analytics Events Display:**
   - Load recent events from AnalyticsService
   - Display in list with:
     - Timestamp
     - Event type
     - Correlation ID
     - Properties
   - Filter by event type
   - Search by correlation ID
   - Click correlation ID to show related events

5. **Add Performance Metrics Display:**
   - Load performance data from PerformanceProfiler
   - Display budgets and violations
   - Show panel load times
   - Show command execution times
   - Visualize with charts (if charting library available)

6. **Add Feature Flags Display:**
   - Load flags from FeatureFlagsService
   - Display as toggle switches
   - Show flag descriptions
   - Save changes on toggle
   - Persist to user settings

7. **Add Environment Info Display:**
   - Load from VersionService
   - Display system information
   - Display configuration
   - Display environment variables (filtered for security)

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
- [ ] All tabs functional

---

### TASK 3.5: Analytics Events Integration

**Priority:** MEDIUM  
**Estimated Time:** 6-8 hours  
**Dependencies:** AnalyticsService (✅ exists), ErrorLoggingService (✅ exists)

**Objective:** Integrate analytics events into key user flows (import, editing, synthesis, export) with correlation IDs.

**Detailed Steps:**

1. **Create Analytics Event Constants:**
   - File: `src/VoiceStudio.Core/Models/AnalyticsEvents.cs`
   - Constants for all event names:
     ```csharp
     public static class AnalyticsEvents
     {
         public const string ImportStart = "Flow.Start.Import";
         public const string ImportComplete = "Flow.End.Import";
         public const string ImportFailed = "Flow.Failed.Import";
         // ... etc
     }
     ```
   - Event property definitions
   - Documentation

2. **Integrate into ProfilesViewModel:**
   - File: `src/VoiceStudio.App/ViewModels/ProfilesViewModel.cs` (modify)
   - Track profile creation flow:
     - Start correlation on "Create Profile" command
     - Add breadcrumb: "Starting profile creation"
     - Track completion/failure
     - End correlation
   - Track profile deletion flow
   - Track profile update flow

3. **Integrate into TimelineViewModel:**
   - File: `src/VoiceStudio.App/ViewModels/TimelineViewModel.cs` (modify)
   - Track editing flow:
     - Start correlation on edit operation
     - Add breadcrumbs at key points
     - Track completion/failure
     - End correlation

4. **Integrate into Voice Synthesis:**
   - File: `src/VoiceStudio.App/ViewModels/VoiceSynthesisViewModel.cs` (modify)
   - Track synthesis flow:
     - Start correlation on synthesis command
     - Add breadcrumbs: "Starting synthesis", "Engine selected", "Synthesis complete"
     - Track duration, success, quality metrics
     - End correlation

5. **Integrate into Export:**
   - File: `src/VoiceStudio.App/ViewModels/ExportViewModel.cs` (if exists, modify)
   - Track export flow:
     - Start correlation on export command
     - Add breadcrumbs
     - Track completion/failure
     - End correlation

6. **Add Breadcrumbs to Critical Flows:**
   - Recording flow: Add breadcrumbs at start, pause, resume, stop
   - Editing flow: Add breadcrumbs at edit start, save, undo, redo
   - Export flow: Add breadcrumbs at export start, format selection, completion

7. **Test Analytics Integration:**
   - Test all key flows
   - Verify events tracked
   - Verify correlation IDs
   - Verify breadcrumbs
   - Verify events appear in Diagnostics pane

**Files to Create:**
- `src/VoiceStudio.Core/Models/AnalyticsEvents.cs`

**Files to Modify:**
- `src/VoiceStudio.App/ViewModels/ProfilesViewModel.cs`
- `src/VoiceStudio.App/ViewModels/TimelineViewModel.cs`
- `src/VoiceStudio.App/ViewModels/VoiceSynthesisViewModel.cs`
- Other ViewModels with key flows (20+ files)

**Acceptance Criteria:**
- [ ] Analytics event constants created
- [ ] Analytics integrated into all key flows
- [ ] Correlation IDs linked
- [ ] Breadcrumbs added
- [ ] All flows tested
- [ ] Events visible in Diagnostics pane

---

### TASK 3.6: UI Smoke Tests

**Priority:** HIGH  
**Estimated Time:** 8-10 hours  
**Dependencies:** C# test framework (✅ exists)

**Objective:** Create golden-path UI smoke tests covering launch, panel navigation, and common actions.

**Detailed Steps:**

1. **Create Smoke Test Base:**
   - File: `src/VoiceStudio.App.Tests/UI/SmokeTestBase.cs`
   - Setup:
     - Initialize app
     - Wait for MainWindow
     - Set up test data
   - Teardown:
     - Clean up test data
     - Close app
   - Helper methods:
     - `Task WaitForPanelAsync(string panelId)`
     - `Task ClickButtonAsync(string buttonName)`
     - `Task EnterTextAsync(string controlName, string text)`

2. **Create Launch Test:**
   - File: `src/VoiceStudio.App.Tests/UI/LaunchSmokeTests.cs`
   - Test: `[UITestMethod] ApplicationLaunches()`
     - Verify app launches
     - Verify MainWindow displays
     - Verify no crashes
     - Verify startup time < 3 seconds
   
   - Test: `[UITestMethod] MainWindowDisplaysCorrectly()`
     - Verify 3-row grid structure
     - Verify 4 PanelHosts visible
     - Verify Nav Rail visible
     - Verify Status Bar visible

3. **Create Panel Navigation Tests:**
   - File: `src/VoiceStudio.App.Tests/UI/PanelNavigationSmokeTests.cs`
   - Test: `[UITestMethod] NavigateToProfilesPanel()`
     - Click Profiles button in Nav Rail
     - Verify ProfilesView displays
     - Verify panel loads < 500ms
   
   - Test: `[UITestMethod] NavigateToTimelinePanel()`
   - Test: `[UITestMethod] NavigateToEffectsPanel()`
   - Test: `[UITestMethod] NavigateToQualityPanel()`
   - Test: `[UITestMethod] PanelSwitchingWorks()`

4. **Create Common Action Tests:**
   - File: `src/VoiceStudio.App.Tests/UI/CommonActionsSmokeTests.cs`
   - Test: `[UITestMethod] CreateProfile()`
     - Navigate to Profiles panel
     - Click "Create Profile" button
     - Enter profile name
     - Click "Save"
     - Verify profile created
     - Verify success toast displayed
   
   - Test: `[UITestMethod] SynthesizeVoice()`
   - Test: `[UITestMethod] ApplyEffect()`
   - Test: `[UITestMethod] ExportAudio()`

5. **Create Critical Path Tests:**
   - File: `src/VoiceStudio.App.Tests/UI/CriticalPathSmokeTests.cs`
   - Test: `[UITestMethod] FullWorkflow()`
     - Create profile
     - Synthesize voice
     - Apply effect
     - Export audio
     - Verify all steps complete
   
   - Test: `[UITestMethod] ErrorHandling()`
     - Trigger error condition
     - Verify error displayed correctly
     - Verify recovery works

6. **Add Test Data Setup:**
   - Use seed data for tests
   - Clean up after tests
   - Isolated test data per test
   - Mock backend if needed

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
- [ ] Test data setup working

---

### TASK 3.7: ViewModel Contract Tests

**Priority:** HIGH  
**Estimated Time:** 8-10 hours  
**Dependencies:** C# test framework (✅ exists), MockBackendClient (✅ exists)

**Objective:** Expand ViewModel contract tests with mocks for all services and comprehensive business logic testing.

**Detailed Steps:**

1. **Create Mock Services:**
   - File: `src/VoiceStudio.App.Tests/Services/MockAnalyticsService.cs`
     - Implements `IAnalyticsService`
     - Tracks events in memory
     - Provides test assertions
   
   - File: `src/VoiceStudio.App.Tests/Services/MockStateService.cs`
     - Implements state management interfaces
     - In-memory state storage
   
   - File: `src/VoiceStudio.App.Tests/Services/MockNavigationService.cs`
     - Implements `INavigationService`
     - Tracks navigation calls
     - Provides test assertions

2. **Create ViewModel Test Base:**
   - File: `src/VoiceStudio.App.Tests/ViewModels/ViewModelTestBase.cs`
   - Setup:
     - Create mock services
     - Register in test DI container
     - Initialize ViewModel
   - Helper methods:
     - `T GetMockService<T>()`
     - `void VerifyServiceCall<T>(Expression<Action<T>> call)`
   - Common test utilities

3. **Expand Existing ViewModel Tests:**
   - File: `src/VoiceStudio.App.Tests/ViewModels/GlobalSearchViewModelTests.cs` (enhance)
     - Add more test cases
     - Test error scenarios
     - Test edge cases
     - Test cancellation
   
   - File: `src/VoiceStudio.App.Tests/ViewModels/MultiSelectServiceTests.cs` (enhance)
     - Add integration tests
     - Test complex scenarios

4. **Create New ViewModel Tests:**
   - Test all major ViewModels (30+ ViewModels):
     - ProfilesViewModelTests
     - TimelineViewModelTests
     - EffectsMixerViewModelTests
     - QualityDashboardViewModelTests
     - VoiceSynthesisViewModelTests
     - etc.
   - Test business logic
   - Test command execution
   - Test state management
   - Test error handling

5. **Create Contract Test Suite:**
   - File: `src/VoiceStudio.App.Tests/Contracts/IBackendClientContractTests.cs`
     - Test IBackendClient contract
     - Verify all methods work
     - Test error handling
   
   - File: `src/VoiceStudio.App.Tests/Contracts/IAnalyticsServiceContractTests.cs`
   - File: `src/VoiceStudio.App.Tests/Contracts/IStateServiceContractTests.cs`
   - Verify interface compliance

**Files to Create:**
- `src/VoiceStudio.App.Tests/Services/MockAnalyticsService.cs`
- `src/VoiceStudio.App.Tests/Services/MockStateService.cs`
- `src/VoiceStudio.App.Tests/Services/MockNavigationService.cs`
- `src/VoiceStudio.App.Tests/ViewModels/ViewModelTestBase.cs`
- `src/VoiceStudio.App.Tests/Contracts/IBackendClientContractTests.cs`
- `src/VoiceStudio.App.Tests/Contracts/IAnalyticsServiceContractTests.cs`
- `src/VoiceStudio.App.Tests/Contracts/IStateServiceContractTests.cs`
- 30+ new ViewModel test files

**Files to Enhance:**
- Existing ViewModel test files (10+ files)

**Acceptance Criteria:**
- [ ] Mock services created
- [ ] ViewModel test base created
- [ ] All major ViewModels tested
- [ ] Contract tests complete
- [ ] Test coverage >80%
- [ ] All tests passing

---

### TASK 3.8: Snapshot Tests

**Priority:** MEDIUM  
**Estimated Time:** 6-8 hours  
**Dependencies:** C# test framework (✅ exists)

**Objective:** Add snapshot tests for analytics/visualization outputs and critical XAML layouts.

**Detailed Steps:**

1. **Create Snapshot Test Framework:**
   - File: `src/VoiceStudio.App.Tests/Snapshot/SnapshotTestBase.cs`
   - Methods:
     - `void AssertSnapshotMatches(string snapshotName, object actual)`
     - `void UpdateSnapshot(string snapshotName, object actual)`
     - `string LoadSnapshot(string snapshotName)`
   - Snapshot storage: `tests/snapshots/`
   - Snapshot format: JSON
   - Diff generation for failures

2. **Create Analytics Snapshot Tests:**
   - File: `src/VoiceStudio.App.Tests/Snapshot/AnalyticsSnapshotTests.cs`
   - Test: `AnalyticsEventStructureMatches()`
     - Generate analytics event
     - Compare structure to snapshot
     - Verify consistency
   
   - Test: `AnalyticsFlowStructureMatches()`
     - Generate flow events
     - Compare to snapshot

3. **Create Visualization Snapshot Tests:**
   - File: `src/VoiceStudio.App.Tests/Snapshot/VisualizationSnapshotTests.cs`
   - Test: `QualityMetricsStructureMatches()`
     - Generate quality metrics
     - Compare to snapshot
   
   - Test: `ChartDataStructureMatches()`
   - Test: `WaveformDataStructureMatches()`

4. **Create XAML Layout Snapshot Tests:**
   - File: `src/VoiceStudio.App.Tests/Snapshot/XamlLayoutSnapshotTests.cs`
   - Test: `MainWindowLayoutMatches()`
     - Load MainWindow XAML
     - Extract structure (elements, properties)
     - Compare to snapshot
   
   - Test: `ProfilesViewLayoutMatches()`
   - Test: `TimelineViewLayoutMatches()`
   - Test: `EffectsMixerViewLayoutMatches()`

5. **Add Snapshot Update Command:**
   - CLI command: `dotnet test -- UpdateSnapshots`
   - Document update process
   - CI/CD integration (fail on snapshot changes)

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
- [ ] CI/CD integration complete

---

## 📊 TASK SUMMARY

**Total Tasks:** 8  
**Estimated Time:** 50-60 hours  
**Priority Breakdown:**
- HIGH: 3 tasks (NavigationService, Async safety, UI smoke tests, ViewModel tests)
- MEDIUM: 4 tasks (Panel lifecycle, Diagnostics, Analytics integration, Snapshots)

**Dependencies:**
- TASK 3.4 (Diagnostics) → FeatureFlagsService (create)
- TASK 3.5 (Analytics integration) → AnalyticsService (✅ exists)
- All other tasks are independent

---

## ✅ COMPLETION CRITERIA

### Code Complete
- [ ] All 8 tasks implemented
- [ ] NavigationService functional
- [ ] All ViewModels use async safety patterns
- [ ] Diagnostics pane enhanced
- [ ] Analytics integrated into all flows
- [ ] UI smoke tests passing
- [ ] ViewModel tests >80% coverage
- [ ] Snapshot tests working

### Documentation Complete
- [ ] Panel Cookbook complete
- [ ] Async patterns guide complete
- [ ] All patterns documented

### Testing Complete
- [ ] UI smoke tests complete
- [ ] ViewModel contract tests complete
- [ ] Snapshot tests complete
- [ ] All tests passing

---

## 🚀 START HERE

**Immediate Next Steps:**

1. **TASK 3.1: NavigationService** (Start here - foundation for navigation)
   - Create interface and implementation
   - Integrate with MainWindow
   - Test navigation

2. **TASK 3.3: Async Safety Patterns** (High priority - UX safety)
   - Enhance AsyncRelayCommand
   - Create ErrorPresentationService
   - Audit and update ViewModels

3. **TASK 3.6: UI Smoke Tests** (High priority - QA)
   - Create test base
   - Create launch tests
   - Create navigation tests

---

**Last Updated:** 2025-01-28  
**Status:** 🚧 **READY FOR IMPLEMENTATION**
