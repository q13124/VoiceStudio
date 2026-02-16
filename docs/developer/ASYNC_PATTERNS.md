# Async Patterns Guide - VoiceStudio Quantum+

**Date:** 2025-01-28  
**Status:** Complete  
**Purpose:** Comprehensive guide for async/await patterns in ViewModels

---

## 🎯 OVERVIEW

This guide documents best practices for async operations in ViewModels, ensuring:
- ✅ Thread safety
- ✅ Proper cancellation support
- ✅ User-friendly error handling
- ✅ Progress indication
- ✅ Prevention of duplicate operations

---

## 📋 CORE PRINCIPLES

### 1. Always Use CancellationToken

**✅ CORRECT:**
```csharp
private async Task LoadDataAsync(CancellationToken cancellationToken)
{
    await _backendClient.GetDataAsync(cancellationToken);
}
```

**❌ WRONG:**
```csharp
private async Task LoadDataAsync()
{
    await _backendClient.GetDataAsync(); // No cancellation support
}
```

### 2. Always Handle Errors

**✅ CORRECT:**
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

**❌ WRONG:**
```csharp
await operationAsync(ct); // No error handling
```

### 3. Always Show Progress for Long Operations

**✅ CORRECT:**
```csharp
private async Task ProcessDataAsync(CancellationToken cancellationToken)
{
    using var profiler = PerformanceProfiler.StartCommand("ProcessData");
    
    IsLoading = true;
    try
    {
        // Report progress
        command.ReportProgress(25);
        await Step1Async(cancellationToken);
        
        command.ReportProgress(50);
        await Step2Async(cancellationToken);
        
        command.ReportProgress(75);
        await Step3Async(cancellationToken);
        
        command.ReportProgress(100);
    }
    finally
    {
        IsLoading = false;
    }
}
```

**❌ WRONG:**
```csharp
private async Task ProcessDataAsync(CancellationToken cancellationToken)
{
    await Step1Async(cancellationToken);
    await Step2Async(cancellationToken);
    await Step3Async(cancellationToken);
    // No progress indication
}
```

### 4. Prevent Duplicate Execution

**✅ CORRECT:**
```csharp
LoadCommand = new EnhancedAsyncRelayCommand(async (ct) =>
{
    using var profiler = PerformanceProfiler.StartCommand("Load");
    await LoadDataAsync(ct);
});
```

**❌ WRONG:**
```csharp
LoadCommand = new AsyncRelayCommand(LoadDataAsync);
// No in-flight guard - can execute multiple times
```

---

## 🔧 ENHANCED ASYNC RELAY COMMAND

### Basic Usage

**Before (AsyncRelayCommand):**
```csharp
LoadCommand = new AsyncRelayCommand(LoadDataAsync);
```

**After (EnhancedAsyncRelayCommand):**
```csharp
LoadCommand = new EnhancedAsyncRelayCommand(async (ct) =>
{
    using var profiler = PerformanceProfiler.StartCommand("Load");
    await LoadDataAsync(ct);
});
```

### With CancellationToken Support

```csharp
private async Task LoadDataAsync(CancellationToken cancellationToken)
{
    IsLoading = true;
    try
    {
        var data = await _backendClient.GetDataAsync(cancellationToken);
        Data = data;
    }
    catch (OperationCanceledException)
    {
        // User cancelled - this is expected
        return;
    }
    catch (Exception ex)
    {
        var errorService = ServiceProvider.TryGetErrorPresentationService();
        errorService?.ShowError(ex, "Failed to load data");
    }
    finally
    {
        IsLoading = false;
    }
}
```

### With Progress Reporting

```csharp
LoadCommand = new EnhancedAsyncRelayCommand(async (ct) =>
{
    using var profiler = PerformanceProfiler.StartCommand("Load");
    
    LoadCommand.ReportProgress(0);
    await LoadStep1Async(ct);
    
    LoadCommand.ReportProgress(33);
    await LoadStep2Async(ct);
    
    LoadCommand.ReportProgress(66);
    await LoadStep3Async(ct);
    
    LoadCommand.ReportProgress(100);
});
```

### With Parameter Support

```csharp
DeleteCommand = new EnhancedAsyncRelayCommand<string>(async (id, ct) =>
{
    using var profiler = PerformanceProfiler.StartCommand("Delete");
    await DeleteItemAsync(id, ct);
});
```

---

## 🛡️ ERROR HANDLING PATTERNS

### Pattern 1: Toast Notification (Default)

```csharp
try
{
    await operationAsync(ct);
}
catch (Exception ex)
{
    var errorService = ServiceProvider.TryGetErrorPresentationService();
    errorService?.ShowError(ex, "Operation failed");
}
```

### Pattern 2: Dialog for Critical Errors

```csharp
try
{
    await criticalOperationAsync(ct);
}
catch (Exception ex)
{
    var errorService = ServiceProvider.TryGetErrorPresentationService();
    errorService?.ShowError(ex, "Critical operation failed", ErrorPresentationType.Dialog);
}
```

### Pattern 3: Inline Error Message

```csharp
try
{
    await operationAsync(ct);
    ErrorMessage = null;
}
catch (Exception ex)
{
    ErrorMessage = ErrorHandler.GetUserFriendlyMessage(ex);
    var logService = ServiceProvider.TryGetErrorLoggingService();
    logService?.LogError(ex, "Operation context");
}
```

### Pattern 4: Silent Logging (Non-Critical)

```csharp
try
{
    await backgroundOperationAsync(ct);
}
catch (Exception ex)
{
    // Log but don't show to user (background operation)
    var logService = ServiceProvider.TryGetErrorLoggingService();
    logService?.LogError(ex, "Background operation failed");
}
```

---

## ⚡ PERFORMANCE PROFILING

### Using PerformanceProfiler

```csharp
LoadCommand = new EnhancedAsyncRelayCommand(async (ct) =>
{
    using var profiler = PerformanceProfiler.StartCommand("Load");
    await LoadDataAsync(ct);
});
```

### With Budget Checking

```csharp
LoadCommand = new EnhancedAsyncRelayCommand(async (ct) =>
{
    using var profiler = PerformanceProfiler.StartCommand("Load", budget: TimeSpan.FromSeconds(2));
    await LoadDataAsync(ct);
    
    if (profiler.Elapsed > profiler.Budget)
    {
        var logService = ServiceProvider.TryGetErrorLoggingService();
        logService?.LogWarning($"Load exceeded budget: {profiler.Elapsed}", "Performance");
    }
});
```

---

## 🚫 ANTI-PATTERNS TO AVOID

### ❌ Fire-and-Forget

```csharp
// WRONG - No error handling, no cancellation
_ = LoadDataAsync();
```

**✅ CORRECT:**
```csharp
// Use command with proper error handling
await LoadCommand.ExecuteAsync(null);
```

### ❌ Ignoring Cancellation

```csharp
// WRONG - Doesn't check cancellation token
private async Task ProcessAsync(CancellationToken ct)
{
    for (int i = 0; i < 1000; i++)
    {
        await ProcessItemAsync(i); // Never checks ct
    }
}
```

**✅ CORRECT:**
```csharp
private async Task ProcessAsync(CancellationToken ct)
{
    for (int i = 0; i < 1000; i++)
    {
        ct.ThrowIfCancellationRequested();
        await ProcessItemAsync(i);
    }
}
```

### ❌ No Progress Indication

```csharp
// WRONG - User has no idea what's happening
private async Task LongOperationAsync(CancellationToken ct)
{
    await Step1Async(ct);
    await Step2Async(ct);
    await Step3Async(ct);
}
```

**✅ CORRECT:**
```csharp
private async Task LongOperationAsync(CancellationToken ct)
{
    IsLoading = true;
    try
    {
        command.ReportProgress(33);
        await Step1Async(ct);
        
        command.ReportProgress(66);
        await Step2Async(ct);
        
        command.ReportProgress(100);
        await Step3Async(ct);
    }
    finally
    {
        IsLoading = false;
    }
}
```

### ❌ No Error Handling

```csharp
// WRONG - Exceptions will crash the app
LoadCommand = new AsyncRelayCommand(LoadDataAsync);
```

**✅ CORRECT:**
```csharp
LoadCommand = new EnhancedAsyncRelayCommand(async (ct) =>
{
    try
    {
        await LoadDataAsync(ct);
    }
    catch (Exception ex)
    {
        var errorService = ServiceProvider.TryGetErrorPresentationService();
        errorService?.ShowError(ex, "Failed to load data");
    }
});
```

---

## 📝 COMPLETE EXAMPLE

### ViewModel with EnhancedAsyncRelayCommand

```csharp
public partial class ExampleViewModel : ObservableObject
{
    private readonly IBackendClient _backendClient;
    private readonly IErrorPresentationService? _errorService;
    private readonly IErrorLoggingService? _logService;

    [ObservableProperty]
    private bool isLoading;

    [ObservableProperty]
    private string? errorMessage;

    public ExampleViewModel(IBackendClient backendClient)
    {
        _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
        
        // Get services
        _errorService = ServiceProvider.TryGetErrorPresentationService();
        _logService = ServiceProvider.TryGetErrorLoggingService();
        
        // Initialize commands with EnhancedAsyncRelayCommand
        LoadCommand = new EnhancedAsyncRelayCommand(async (ct) =>
        {
            using var profiler = PerformanceProfiler.StartCommand("Load");
            await LoadDataAsync(ct);
        });
        
        SaveCommand = new EnhancedAsyncRelayCommand(async (ct) =>
        {
            using var profiler = PerformanceProfiler.StartCommand("Save");
            await SaveDataAsync(ct);
        });
        
        DeleteCommand = new EnhancedAsyncRelayCommand<string>(async (id, ct) =>
        {
            using var profiler = PerformanceProfiler.StartCommand("Delete");
            await DeleteItemAsync(id, ct);
        });
    }

    public EnhancedAsyncRelayCommand LoadCommand { get; }
    public EnhancedAsyncRelayCommand SaveCommand { get; }
    public EnhancedAsyncRelayCommand<string> DeleteCommand { get; }

    private async Task LoadDataAsync(CancellationToken cancellationToken)
    {
        IsLoading = true;
        ErrorMessage = null;
        
        try
        {
            LoadCommand.ReportProgress(0);
            var data = await _backendClient.GetDataAsync(cancellationToken);
            
            LoadCommand.ReportProgress(50);
            ProcessData(data);
            
            LoadCommand.ReportProgress(100);
        }
        catch (OperationCanceledException)
        {
            // User cancelled - expected
            return;
        }
        catch (Exception ex)
        {
            ErrorMessage = ErrorHandler.GetUserFriendlyMessage(ex);
            _errorService?.ShowError(ex, "Failed to load data");
            _logService?.LogError(ex, "LoadData");
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task SaveDataAsync(CancellationToken cancellationToken)
    {
        IsLoading = true;
        ErrorMessage = null;
        
        try
        {
            await _backendClient.SaveDataAsync(Data, cancellationToken);
            _toastNotificationService?.ShowSuccess("Data saved successfully");
        }
        catch (OperationCanceledException)
        {
            return;
        }
        catch (Exception ex)
        {
            ErrorMessage = ErrorHandler.GetUserFriendlyMessage(ex);
            _errorService?.ShowError(ex, "Failed to save data");
            _logService?.LogError(ex, "SaveData");
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task DeleteItemAsync(string id, CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(id))
            return;

        IsLoading = true;
        ErrorMessage = null;
        
        try
        {
            await _backendClient.DeleteItemAsync(id, cancellationToken);
            _toastNotificationService?.ShowSuccess("Item deleted successfully");
        }
        catch (OperationCanceledException)
        {
            return;
        }
        catch (Exception ex)
        {
            ErrorMessage = ErrorHandler.GetUserFriendlyMessage(ex);
            _errorService?.ShowError(ex, "Failed to delete item");
            _logService?.LogError(ex, "DeleteItem");
        }
        finally
        {
            IsLoading = false;
        }
    }
}
```

---

## 🔗 CANCELLATION TOKEN PROPAGATION (GAP-I15)

### Policy

All async methods MUST follow these cancellation token rules:

1. **ALWAYS propagate** the incoming `CancellationToken` to all async calls
2. **NEVER use `CancellationToken.None`** except for fire-and-forget cleanup operations
3. **Use linked tokens** when combining user cancellation with timeout
4. **Fire-and-forget MUST use disposal token** from `_disposalCts`

### Anti-Patterns (DO NOT USE)

```csharp
// ❌ BAD: Ignoring incoming token
public async Task LoadDataAsync(CancellationToken ct)
{
    await _backend.GetDataAsync(CancellationToken.None);  // WRONG - should use ct
}

// ❌ BAD: Fire-and-forget without cancellation awareness
_ = LoadLogsAsync(CancellationToken.None);  // WRONG - use disposal token

// ❌ BAD: Method doesn't accept token
public async Task LoadAsync()  // WRONG - no CancellationToken parameter
{
    await _backend.GetAsync();
}

// ❌ BAD: Command handler ignores the token
CreateProfileCommand = new EnhancedAsyncRelayCommand<string>(async (name, ct) =>
{
    await CreateProfileAsync(name, CancellationToken.None);  // WRONG - should use ct
});
```

### Correct Patterns

```csharp
// ✅ GOOD: Propagate token throughout the call chain
public async Task LoadDataAsync(CancellationToken ct)
{
    await _backend.GetDataAsync(ct);  // Propagate the token
}

// ✅ GOOD: Linked token for timeout + user cancellation
var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
linkedCts.CancelAfter(TimeSpan.FromSeconds(30));
try
{
    await _backend.GetDataAsync(linkedCts.Token);
}
finally
{
    linkedCts.Dispose();
}

// ✅ GOOD: Fire-and-forget with disposal token
private CancellationTokenSource _disposalCts = new();

partial void OnSelectedItemChanged(Item? value)
{
    // Use disposal token for fire-and-forget operations
    _ = LoadDetailsAsync(_disposalCts.Token);
}

public void Dispose()
{
    _disposalCts.Cancel();
    _disposalCts.Dispose();
}

// ✅ GOOD: Command handler propagates the token
CreateProfileCommand = new EnhancedAsyncRelayCommand<string>(async (name, ct) =>
{
    await CreateProfileAsync(name, ct);  // Propagate the token from the command
});
```

### Polling Loops

Polling loops MUST check and propagate cancellation:

```csharp
// ✅ GOOD: Polling with proper cancellation
private async Task PollStatusAsync(CancellationToken cancellationToken)
{
    while (!cancellationToken.IsCancellationRequested)
    {
        await LoadStatusAsync(cancellationToken);  // Propagate token
        await Task.Delay(5000, cancellationToken);  // Delay respects cancellation
    }
}
```

### Linked Token Pattern for Timeouts

When you need both user cancellation AND a timeout:

```csharp
public async Task<T> GetWithTimeoutAsync<T>(CancellationToken userToken)
{
    using var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(userToken);
    linkedCts.CancelAfter(TimeSpan.FromSeconds(30));
    
    try
    {
        return await _client.GetAsync<T>(linkedCts.Token);
    }
    catch (OperationCanceledException) when (!userToken.IsCancellationRequested)
    {
        throw new TimeoutException("Operation timed out after 30 seconds");
    }
}
```

### Selection Change Pattern

When loading data on selection change, use a dedicated cancellation token source:

```csharp
private CancellationTokenSource? _selectionChangeCts;

partial void OnSelectedItemChanged(Item? value)
{
    // Cancel previous selection change operations
    _selectionChangeCts?.Cancel();
    _selectionChangeCts?.Dispose();
    _selectionChangeCts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
    
    if (value != null)
    {
        var ct = _selectionChangeCts.Token;
        _ = LoadDetailsAsync(ct).ContinueWith(t =>
        {
            if (t.IsFaulted && t.Exception?.InnerException is not OperationCanceledException)
                _logService?.LogError(t.Exception.InnerException, "LoadDetails");
        }, TaskScheduler.Default);
    }
}
```

---

## 🔍 VERIFICATION CHECKLIST

Before marking a ViewModel as complete, verify:

- [ ] All async commands use `EnhancedAsyncRelayCommand` (not `AsyncRelayCommand`)
- [ ] All async methods accept `CancellationToken` parameter
- [ ] All async operations wrapped in try-catch
- [ ] Errors shown to user via `ErrorPresentationService`
- [ ] Errors logged via `ErrorLoggingService`
- [ ] Progress reported for long operations (>1 second)
- [ ] `PerformanceProfiler` used for command execution
- [ ] `IsLoading` property set appropriately
- [ ] `ErrorMessage` property set on errors
- [ ] No fire-and-forget operations (`_ = MethodAsync()`)
- [ ] Cancellation tokens checked in loops

---

## 📚 RELATED DOCUMENTS

- `docs/developer/ERROR_HANDLING_PATTERNS.md` - Error handling patterns
- `docs/developer/SERVICES.md` - Service architecture
- `src/VoiceStudio.App/Utilities/EnhancedAsyncRelayCommand.cs` - Implementation
- `src/VoiceStudio.App/Utilities/CommandGuard.cs` - Duplicate execution prevention

---

**Last Updated:** 2025-01-28  
**Status:** Complete
