# ViewModel DI Refactor Spec (TD-004)

> **Version**: 1.0  
> **Last Updated**: 2026-01-30  
> **Owner**: Role 3 (UI Engineer), Role 4 (Core Platform)  
> **Status**: ACTIVE  
> **Traceability**: [TECH_DEBT_REGISTER](../governance/TECH_DEBT_REGISTER.md) TD-004; [GAP_ANALYSIS_REMEDIATION_PLAN](../reports/audit/GAP_ANALYSIS_REMEDIATION_PLAN_2026-01-30.md) GAP-003

This document specifies the migration from `AppServices.Get<T>()` anti-pattern and parameterless `BaseViewModel()` constructors to proper dependency injection for ViewModels.

---

## 1. Problem Statement

**Current pattern (anti-pattern):**

```csharp
// In View code-behind (e.g. ProfilesView.xaml.cs)
public ProfilesView()
{
    InitializeComponent();
    ViewModel = new ProfilesViewModel(
        AppServices.GetBackendClient(),
        AppServices.GetProfilesUseCase(),
        AppServices.GetErrorLoggingService()
    );
}

// Or parameterless BaseViewModel constructor
public class SomeViewModel : BaseViewModel
{
    public SomeViewModel() : base() // Calls AppServices internally
    {
        // ...
    }
}
```

**Issues:**
- Couples Views to service resolution (AppServices singleton).
- Violates MVVM (View should not know about service location).
- Harder to test (can't inject mocks).
- Treated as warnings in Debug; errors in Release (TD-002 dependency).

---

## 2. Target Pattern (DI-based)

**Desired pattern:**

```csharp
// In View code-behind
public ProfilesView(ProfilesViewModel viewModel)
{
    InitializeComponent();
    ViewModel = viewModel; // Injected via DI
}

// ViewModel with explicit dependencies
public class ProfilesViewModel : BaseViewModel
{
    public ProfilesViewModel(
        IBackendClient backendClient,
        IProfilesUseCase profilesUseCase,
        IErrorLoggingService errorLogging)
        : base(errorLogging) // Or inject via property/field
    {
        // ...
    }
}
```

---

## 3. Migration Strategy

### Phase 1: Configure DI Container

- **Where**: `App.xaml.cs` or `Program.cs`
- **Action**: Configure `IServiceCollection` or `IHost` to register ViewModels and services.
- **Example**:

```csharp
services.AddSingleton<IBackendClient, BackendClient>();
services.AddSingleton<IAudioPlayerService, AudioPlayerService>();
// ... all services

services.AddTransient<ProfilesViewModel>();
services.AddTransient<TimelineViewModel>();
// ... all ViewModels
```

### Phase 2: Update View Constructors

- **Where**: All View code-behind files (e.g. `ProfilesView.xaml.cs`)
- **Action**: Add ViewModel parameter to constructor; remove `AppServices.Get*()` calls.
- **Count**: ~98 ViewModels per CODEBASE_INVENTORY; subset used in Views.

### Phase 3: Update ViewModel Constructors

- **Where**: All ViewModel files
- **Action**: Add explicit service parameters; remove parameterless constructors or `AppServices` calls.
- **Affected**: 5 ViewModels don't inherit BaseViewModel (GAP-005); fix inheritance first.

### Phase 4: Phase Out AppServices

- **Where**: `ServiceProvider.cs`, `AppServices.cs` (if exists)
- **Action**: After all call sites migrated, remove or mark obsolete.

---

## 4. Affected ViewModels (Priority)

From GAP-005 (don't inherit BaseViewModel):
1. ProfilesViewModel
2. VoiceSynthesisViewModel
3. TimelineViewModel
4. GlobalSearchViewModel
5. CommandPaletteViewModel

**Action**: Change inheritance from `ObservableObject` to `BaseViewModel`; add constructor with service parameters.

---

## 5. Rollout Plan

- **Incremental**: Migrate one View/ViewModel pair at a time; verify build and runtime.
- **Test**: Unit tests for each ViewModel with mocked services.
- **Verification**: After migration, run Gate C UI smoke to confirm zero binding failures.

---

## 6. Exit Criteria

- [ ] DI container configured in App.xaml.cs or Program.cs
- [ ] All Views use DI-resolved ViewModels (no `AppServices.Get*()` in Views)
- [ ] All ViewModels have explicit service constructors
- [ ] All ViewModels inherit BaseViewModel
- [ ] Gate C UI smoke PASS (0 binding failures)
- [ ] TD-004 closed in TECH_DEBT_REGISTER

---

## 7. References

- [TECH_DEBT_REGISTER](../governance/TECH_DEBT_REGISTER.md) TD-004
- [GAP_ANALYSIS_REMEDIATION_PLAN](../reports/audit/GAP_ANALYSIS_REMEDIATION_PLAN_2026-01-30.md) GAP-003, GAP-005
- [OPTIONAL_TASK_INVENTORY](../governance/OPTIONAL_TASK_INVENTORY.md) §2.2
