# Task 3 Integration Guidance
## Store Integration Steps for Worker 2

**Date:** 2025-01-28  
**Overseer:** New Overseer  
**Purpose:** Guide Worker 2 on completing Task 3 Store integration

---

## ✅ Stores Created (5 Stores)

1. **EngineStore** ✅ - `src/VoiceStudio.App/Services/Stores/EngineStore.cs`
2. **AudioStore** ✅ - `src/VoiceStudio.App/Services/Stores/AudioStore.cs`
3. **ProjectStore** ✅ - `src/VoiceStudio.App/Services/Stores/ProjectStore.cs`
4. **SystemStore** ✅ - `src/VoiceStudio.App/Services/Stores/SystemStore.cs`
5. **JobStore** ✅ - `src/VoiceStudio.App/Services/Stores/JobStore.cs`

**Status:** All stores created and ready for integration

---

## 🎯 Integration Steps

### Step 1: Register Stores in ServiceProvider

**File:** `src/VoiceStudio.App/Services/ServiceProvider.cs`

**Add Store Fields:**
```csharp
private static EngineStore? _engineStore;
private static AudioStore? _audioStore;
private static ProjectStore? _projectStore;
private static SystemStore? _systemStore;
private static JobStore? _jobStore;
```

**Initialize Stores in Initialize() Method:**
```csharp
// After StateCacheService initialization
try
{
    _engineStore = new EngineStore(_backendClient, _stateCacheService);
    _audioStore = new AudioStore(_backendClient, _stateCacheService);
    _projectStore = new ProjectStore(_backendClient, _stateCacheService);
    _systemStore = new SystemStore(_backendClient, _stateCacheService);
    _jobStore = new JobStore(_backendClient, _stateCacheService);
    _errorLoggingService?.LogInfo("Stores initialized", "ServiceProvider");
}
catch (Exception ex)
{
    _errorLoggingService?.LogError(ex, "Failed to initialize Stores");
}
```

**Add Getter Methods:**
```csharp
public static EngineStore GetEngineStore()
{
    if (_engineStore == null)
        throw new InvalidOperationException("EngineStore not initialized");
    return _engineStore;
}

public static AudioStore GetAudioStore()
{
    if (_audioStore == null)
        throw new InvalidOperationException("AudioStore not initialized");
    return _audioStore;
}

public static ProjectStore GetProjectStore()
{
    if (_projectStore == null)
        throw new InvalidOperationException("ProjectStore not initialized");
    return _projectStore;
}

public static SystemStore GetSystemStore()
{
    if (_systemStore == null)
        throw new InvalidOperationException("SystemStore not initialized");
    return _systemStore;
}

public static JobStore GetJobStore()
{
    if (_jobStore == null)
        throw new InvalidOperationException("JobStore not initialized");
    return _jobStore;
}
```

---

### Step 2: Integrate Stores into ViewModels

**Example: JobProgressViewModel Integration**

**Current Pattern:**
```csharp
public class JobProgressViewModel : BaseViewModel, IPanelView
{
    private readonly IBackendClient _backendClient;
    private ObservableCollection<JobItem> jobs = new();
    
    public async Task LoadJobsAsync()
    {
        // Direct API call
        var jobsArray = await _backendClient.SendRequestAsync<object, Job[]>(...);
    }
}
```

**New Pattern with Store:**
```csharp
public class JobProgressViewModel : BaseViewModel, IPanelView
{
    private readonly IBackendClient _backendClient;
    private readonly JobStore _jobStore;
    
    public JobProgressViewModel(IBackendClient backendClient)
    {
        _backendClient = backendClient;
        _jobStore = ServiceProvider.GetJobStore();
        
        // Bind to store properties
        _jobStore.PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == nameof(JobStore.Jobs))
            {
                Jobs = _jobStore.Jobs;
                OnPropertyChanged(nameof(Jobs));
            }
            if (e.PropertyName == nameof(JobStore.IsLoading))
            {
                IsLoading = _jobStore.IsLoading;
            }
        };
    }
    
    public ObservableCollection<JobItem> Jobs => _jobStore.Jobs;
    public bool IsLoading => _jobStore.IsLoading;
    
    public async Task LoadJobsAsync()
    {
        // Use store instead of direct API call
        await _jobStore.LoadJobsAsync();
    }
}
```

**ViewModels to Update:**
- JobProgressViewModel → Use JobStore
- TimelineViewModel → Use ProjectStore, AudioStore
- VoiceSynthesisViewModel → Use EngineStore (if needed)
- AnalyzerViewModel → Use AudioStore
- Other ViewModels as appropriate

---

### Step 3: Test Store Integration

**Test Checklist:**
- [ ] Stores initialize correctly in ServiceProvider
- [ ] ViewModels can access stores
- [ ] Store properties update correctly
- [ ] State caching works
- [ ] Error handling works
- [ ] Loading states work
- [ ] UI updates when store properties change

---

### Step 4: Document Patterns

**Create Documentation:**
- Document React/TypeScript patterns extracted
- Document Store pattern implementation
- Document ViewModel integration patterns
- Add examples and usage guidelines

---

## 📋 Task 3 Completion Criteria

### Task 3 is Complete When:
1. ✅ Stores registered in ServiceProvider
2. ✅ Stores integrated into at least 3-5 ViewModels
3. ✅ Stores tested and working
4. ✅ Patterns documented
5. ✅ No placeholders or forbidden terms
6. ✅ All functionality working

---

## 🚀 Recommended Order

1. **Register Stores** - Add to ServiceProvider (30 min)
2. **Integrate JobStore** - Update JobProgressViewModel (1 hour)
3. **Integrate ProjectStore** - Update TimelineViewModel (1 hour)
4. **Integrate AudioStore** - Update AnalyzerViewModel (1 hour)
5. **Test Integration** - Test all integrations (1 hour)
6. **Document Patterns** - Create documentation (1 hour)

**Estimated Time:** 5-6 hours

---

## 📝 Notes

1. **Stores Created:** All 5 stores are created and ready
2. **Integration Needed:** Stores need to be registered and integrated
3. **Testing Required:** Integration must be tested
4. **Documentation:** Patterns must be documented

---

**Status:** Stores ready for integration  
**Next Action:** Register stores in ServiceProvider, then integrate into ViewModels  
**Priority:** Complete Task 3 integration

