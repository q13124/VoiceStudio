# Service Locator Migration Guide (TD-004)

This document describes the approach for migrating from static `ServiceProvider.Get*()` calls to constructor injection.

## Current State

| Metric | Value |
|--------|-------|
| Total `ServiceProvider.Get*()` calls | ~413 |
| Files with static service access | ~139 |
| Target | Constructor injection via DI |

## Why Migrate?

1. **Testability**: Constructor injection makes dependencies explicit and mockable
2. **Maintainability**: Dependencies are visible in the constructor signature
3. **SOLID Principles**: Follows Dependency Inversion Principle
4. **Performance**: Reduces runtime service lookups

## Migration Strategy

### Phase A: Infrastructure (DONE)

1. ✅ `IViewModelFactory` created for ViewModel instantiation
2. ✅ `ViewModelLocator` created for XAML design-time support
3. ✅ All services registered in `AppServices.cs`

### Phase B: New Code Standard

All **new** code should use constructor injection:

```csharp
// ✅ GOOD - Constructor injection
public class MyViewModel : BaseViewModel
{
    private readonly IBackendClient _backendClient;
    
    public MyViewModel(IBackendClient backendClient)
    {
        _backendClient = backendClient;
    }
}

// ❌ BAD - Static service locator
public class MyViewModel : BaseViewModel
{
    private readonly IBackendClient _backendClient;
    
    public MyViewModel()
    {
        _backendClient = ServiceProvider.GetBackendClient(); // Avoid!
    }
}
```

### Phase C: Incremental Migration

Migrate files in batches of 10-15 per sprint:

#### Priority 1: ViewModels with High Test Value
- `VoiceSynthesisViewModel` (4 calls)
- `ProfilesViewModel` (2 calls)
- `SettingsViewModel`
- `QualityDashboardViewModel`

#### Priority 2: Critical Path Views
- `MainWindow.xaml.cs` (24 calls)
- `TimelineView.xaml.cs` (15 calls)
- `LibraryView.xaml.cs` (11 calls)

#### Priority 3: Panel Views (bulk)
- All `*View.xaml.cs` files with `ServiceProvider.Get*()` calls

### Phase D: Deprecation

After migration:
1. Mark `ServiceProvider` class as `[Obsolete]`
2. Configure warning-as-error for obsolete usage
3. Remove `ServiceProvider` shim in future major version

## Migration Pattern

### For Views

```csharp
// BEFORE
public partial class MyView : UserControl
{
    public MyView()
    {
        InitializeComponent();
        ViewModel = new MyViewModel(ServiceProvider.GetBackendClient());
    }
}

// AFTER (ViewModel-first)
public partial class MyView : UserControl
{
    public MyView(MyViewModel viewModel)
    {
        InitializeComponent();
        ViewModel = viewModel;
        DataContext = ViewModel;
    }
}
```

### For ViewModels

```csharp
// BEFORE
public class MyViewModel : BaseViewModel
{
    public MyViewModel()
    {
        _backendClient = ServiceProvider.GetBackendClient();
        _audioPlayer = ServiceProvider.GetAudioPlayerService();
    }
}

// AFTER
public class MyViewModel : BaseViewModel
{
    public MyViewModel(
        IBackendClient backendClient,
        IAudioPlayerService audioPlayer)
    {
        _backendClient = backendClient;
        _audioPlayer = audioPlayer;
    }
}
```

## Registration Pattern

ViewModels should be registered in `AppServices.cs`:

```csharp
// In AppServices.Initialize()
services.AddTransient<VoiceSynthesisViewModel>();
services.AddTransient<ProfilesViewModel>();
services.AddTransient<SettingsViewModel>();
// ... etc
```

## Testing Pattern

With constructor injection, unit tests become simpler:

```csharp
[TestMethod]
public async Task LoadVoices_CallsBackend()
{
    // Arrange
    var mockBackend = new Mock<IBackendClient>();
    mockBackend.Setup(x => x.GetVoicesAsync())
        .ReturnsAsync(new List<Voice> { new() { Name = "Test" } });
    
    var viewModel = new VoiceSynthesisViewModel(mockBackend.Object);
    
    // Act
    await viewModel.LoadVoicesCommand.ExecuteAsync(null);
    
    // Assert
    Assert.AreEqual(1, viewModel.Voices.Count);
}
```

## Tracking Progress

Run this PowerShell command to track progress:

```powershell
# Count remaining ServiceProvider calls
Get-ChildItem -Path src/VoiceStudio.App -Filter "*.cs" -Recurse | 
    Select-String "ServiceProvider\.Get" | 
    Measure-Object | 
    Select-Object Count
```

Current count: ~413 (as of 2026-02-01)

## References

- [ADR-023: UI Assembly Split](../architecture/decisions/ADR-023-ui-assembly-split.md)
- [TECH_DEBT_REGISTER](../governance/TECH_DEBT_REGISTER.md) - TD-004
- [ViewModelFactory](../../src/VoiceStudio.App/Services/ViewModelFactory.cs)
