# VoiceStudio Quantum+ Design Patterns

Comprehensive guide to design patterns used in VoiceStudio Quantum+.

**Last Updated:** 2025-01-28  
**Version:** 1.0

---

## Table of Contents

1. [MVVM Pattern](#mvvm-pattern)
2. [Service-Oriented Architecture](#service-oriented-architecture)
3. [Repository Pattern](#repository-pattern)
4. [Observer Pattern](#observer-pattern)
5. [Strategy Pattern](#strategy-pattern)
6. [Factory Pattern](#factory-pattern)
7. [Dependency Injection](#dependency-injection)
8. [Command Pattern](#command-pattern)
9. [Template Method Pattern](#template-method-pattern)
10. [Design Decisions](#design-decisions)

---

## MVVM Pattern

### Overview

MVVM (Model-View-ViewModel) is the primary architectural pattern used in the VoiceStudio frontend. It provides clear separation of concerns and enables data binding.

### Pattern Structure

```
┌─────────────┐
│    View     │  (XAML - UI Definition)
│  (XAML)     │
└──────┬──────┘
       │ Data Binding
       │ (x:Bind, Binding)
       ▼
┌─────────────┐
│  ViewModel  │  (C# - Business Logic)
│   (C#)      │
└──────┬──────┘
       │ Uses
       ▼
┌─────────────┐
│    Model    │  (C# - Data Structures)
│   (C#)      │
└─────────────┘
```

### Implementation

**View (XAML):**
```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.ProfilesView">
    <Grid>
        <ListView ItemsSource="{x:Bind ViewModel.Profiles, Mode=OneWay}">
            <ListView.ItemTemplate>
                <DataTemplate>
                    <TextBlock Text="{x:Bind Name}" />
                </DataTemplate>
            </ListView.ItemTemplate>
        </ListView>
        <Button Command="{x:Bind ViewModel.LoadProfilesCommand}" 
                Content="Load Profiles" />
    </Grid>
</UserControl>
```

**ViewModel (C#):**
```csharp
public class ProfilesViewModel : BaseViewModel
{
    private readonly IBackendClient _backendClient;
    
    public ObservableCollection<VoiceProfile> Profiles { get; } = new();
    
    public IAsyncRelayCommand LoadProfilesCommand { get; }
    
    public ProfilesViewModel(IBackendClient backendClient)
    {
        _backendClient = backendClient;
        LoadProfilesCommand = new AsyncRelayCommand(LoadProfilesAsync);
    }
    
    private async Task LoadProfilesAsync()
    {
        var profiles = await _backendClient.GetProfilesAsync();
        Profiles.Clear();
        foreach (var profile in profiles)
        {
            Profiles.Add(profile);
        }
    }
}
```

**Model (C#):**
```csharp
public class VoiceProfile
{
    public string Id { get; set; }
    public string Name { get; set; }
    public string Language { get; set; }
    public double QualityScore { get; set; }
    // ... other properties
}
```

### Key Principles

1. **View is Passive:** View only displays data and forwards user actions to ViewModel
2. **ViewModel is Stateful:** ViewModel holds presentation logic and state
3. **Model is Data:** Model represents data structures and business entities
4. **Data Binding:** Two-way binding for user input, one-way for display
5. **Commands:** Use `ICommand` for user actions (buttons, menu items)

### Benefits

- **Testability:** ViewModels can be unit tested without UI
- **Separation of Concerns:** Clear boundaries between UI and logic
- **Maintainability:** Changes to UI don't affect business logic
- **Reusability:** ViewModels can be reused with different views

### Usage Guidelines

1. **Always use BaseViewModel:** Inherit from `BaseViewModel` for error handling
2. **Use ObservableCollection:** For collections that need to notify UI of changes
3. **Use Commands:** For all user actions (buttons, menu items, shortcuts)
4. **Async Operations:** Use `AsyncRelayCommand` for async operations
5. **Property Change Notifications:** Use `SetProperty` from `ObservableObject`

### Example: Complete MVVM Implementation

**ProfilesView.xaml:**
```xml
<UserControl x:Class="VoiceStudio.App.Views.Panels.ProfilesView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>
        
        <StackPanel Orientation="Horizontal" Margin="12">
            <Button Command="{x:Bind ViewModel.CreateProfileCommand}" 
                    Content="New Profile" Margin="0,0,8,0"/>
            <Button Command="{x:Bind ViewModel.DeleteSelectedCommand}" 
                    Content="Delete" 
                    IsEnabled="{x:Bind ViewModel.HasSelection, Mode=OneWay}"/>
        </StackPanel>
        
        <ListView Grid.Row="1" 
                  ItemsSource="{x:Bind ViewModel.Profiles, Mode=OneWay}"
                  SelectedItem="{x:Bind ViewModel.SelectedProfile, Mode=TwoWay}">
            <ListView.ItemTemplate>
                <DataTemplate>
                    <StackPanel Orientation="Horizontal" Margin="8">
                        <TextBlock Text="{x:Bind Name}" FontSize="14" Margin="0,0,8,0"/>
                        <TextBlock Text="{x:Bind QualityScore, StringFormat='Quality: {0:P0}'}" 
                                   Foreground="Gray"/>
                    </StackPanel>
                </DataTemplate>
            </ListView.ItemTemplate>
        </ListView>
    </Grid>
</UserControl>
```

**ProfilesViewModel.cs:**
```csharp
public class ProfilesViewModel : BaseViewModel
{
    private readonly IBackendClient _backendClient;
    private VoiceProfile? _selectedProfile;
    
    public ObservableCollection<VoiceProfile> Profiles { get; } = new();
    
    public VoiceProfile? SelectedProfile
    {
        get => _selectedProfile;
        set => SetProperty(ref _selectedProfile, value);
    }
    
    public bool HasSelection => SelectedProfile != null;
    
    public IAsyncRelayCommand CreateProfileCommand { get; }
    public IAsyncRelayCommand DeleteSelectedCommand { get; }
    
    public ProfilesViewModel(IBackendClient backendClient)
    {
        _backendClient = backendClient;
        CreateProfileCommand = new AsyncRelayCommand(CreateProfileAsync);
        DeleteSelectedCommand = new AsyncRelayCommand(DeleteSelectedAsync, () => HasSelection);
    }
    
    private async Task CreateProfileAsync()
    {
        // Implementation
    }
    
    private async Task DeleteSelectedAsync()
    {
        if (SelectedProfile == null) return;
        await _backendClient.DeleteProfileAsync(SelectedProfile.Id);
        Profiles.Remove(SelectedProfile);
    }
}
```

---

## Service-Oriented Architecture

### Overview

VoiceStudio uses a service-oriented architecture where functionality is encapsulated in services that can be injected and reused across the application.

### Service Provider Pattern

**ServiceProvider.cs:**
```csharp
public static class ServiceProvider
{
    private static IBackendClient? _backendClient;
    private static MultiSelectService? _multiSelectService;
    // ... other services
    
    public static void Initialize()
    {
        _backendClient = new BackendClient(config);
        _multiSelectService = new MultiSelectService();
        // ... initialize other services
    }
    
    public static IBackendClient GetBackendClient()
    {
        return _backendClient ?? throw new InvalidOperationException();
    }
    
    public static MultiSelectService GetMultiSelectService()
    {
        return _multiSelectService ?? throw new InvalidOperationException();
    }
}
```

### Service Usage

**In ViewModel:**
```csharp
public class MyViewModel : BaseViewModel
{
    private readonly IBackendClient _backendClient;
    private readonly MultiSelectService _multiSelectService;
    
    public MyViewModel()
    {
        _backendClient = ServiceProvider.GetBackendClient();
        _multiSelectService = ServiceProvider.GetMultiSelectService();
    }
}
```

### Service Categories

1. **UI Services:**
   - `MultiSelectService` - Multi-selection management
   - `ContextMenuService` - Context menu generation
   - `DragDropVisualFeedbackService` - Drag-and-drop feedback
   - `ToastNotificationService` - Toast notifications

2. **State Management Services:**
   - `UndoRedoService` - Undo/redo operations
   - `RecentProjectsService` - Recent projects management
   - `StatePersistenceService` - State persistence
   - `StateCacheService` - State caching

3. **Error Handling Services:**
   - `ErrorLoggingService` - Error logging
   - `ErrorDialogService` - Error dialogs

4. **Audio Services:**
   - `IAudioPlayerService` - Audio playback
   - `IAudioPlaybackService` - Alternative audio playback

5. **Backend Services:**
   - `IBackendClient` - Backend API communication

### Service Interface Pattern

**Interface Definition:**
```csharp
public interface IBackendClient
{
    Task<List<VoiceProfile>> GetProfilesAsync(CancellationToken cancellationToken = default);
    Task<VoiceProfile> GetProfileAsync(string profileId, CancellationToken cancellationToken = default);
    // ... other methods
}
```

**Implementation:**
```csharp
public class BackendClient : IBackendClient
{
    private readonly HttpClient _httpClient;
    
    public BackendClient(BackendClientConfig config)
    {
        _httpClient = new HttpClient { BaseAddress = new Uri(config.BaseUrl) };
    }
    
    public async Task<List<VoiceProfile>> GetProfilesAsync(CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.GetAsync("/api/profiles", cancellationToken);
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadAsStringAsync(cancellationToken);
        return JsonSerializer.Deserialize<List<VoiceProfile>>(json) ?? new();
    }
}
```

### Benefits

- **Testability:** Services can be mocked for testing
- **Reusability:** Services can be used across multiple ViewModels
- **Maintainability:** Changes to service implementation don't affect consumers
- **Dependency Injection:** Services are injected, not created directly

---

## Repository Pattern

### Overview

The Repository pattern abstracts data access and provides a consistent interface for data operations.

### Implementation

**Backend as Repository:**
```csharp
// IBackendClient acts as a repository interface
public interface IBackendClient
{
    // Profile repository methods
    Task<List<VoiceProfile>> GetProfilesAsync();
    Task<VoiceProfile> GetProfileAsync(string profileId);
    Task<VoiceProfile> CreateProfileAsync(string name, string language);
    Task<VoiceProfile> UpdateProfileAsync(string profileId, VoiceProfile profile);
    Task<bool> DeleteProfileAsync(string profileId);
    
    // Project repository methods
    Task<List<Project>> GetProjectsAsync();
    Task<Project> GetProjectAsync(string projectId);
    // ... other repository methods
}
```

### Benefits

- **Abstraction:** ViewModels don't need to know about HTTP/API details
- **Testability:** Can mock IBackendClient for testing
- **Consistency:** All data access goes through the same interface
- **Flexibility:** Can swap backend implementation without changing ViewModels

---

## Observer Pattern

### Overview

The Observer pattern is used extensively for event-driven updates, particularly with WebSocket real-time updates.

### WebSocket Observer

**Backend (Publisher):**
```python
# backend/api/ws/realtime.py
async def broadcast_quality_update(profile_id: str, quality_score: float):
    message = {
        "type": "quality_update",
        "profile_id": profile_id,
        "quality_score": quality_score
    }
    await manager.broadcast(json.dumps(message))
```

**Frontend (Observer):**
```csharp
// Subscribe to WebSocket updates
_backendClient.QualityUpdated += OnQualityUpdated;

private void OnQualityUpdated(object? sender, QualityUpdateEventArgs e)
{
    // Update UI
    var profile = Profiles.FirstOrDefault(p => p.Id == e.ProfileId);
    if (profile != null)
    {
        profile.QualityScore = e.QualityScore;
    }
}
```

### Property Change Observer

**ViewModel:**
```csharp
public class ProfilesViewModel : BaseViewModel
{
    private string _searchText = string.Empty;
    
    public string SearchText
    {
        get => _searchText;
        set
        {
            if (SetProperty(ref _searchText, value))
            {
                // Observer pattern: Property change triggers filter
                FilterProfiles();
            }
        }
    }
    
    private void FilterProfiles()
    {
        // Filter logic
    }
}
```

### Event Observer

**Service Events:**
```csharp
// Subscribe to service events
_multiSelectService.SelectionChanged += OnSelectionChanged;

private void OnSelectionChanged(object? sender, SelectionChangedEventArgs e)
{
    if (e.PanelId == "ProfilesPanel")
    {
        OnPropertyChanged(nameof(SelectedCount));
    }
}
```

---

## Strategy Pattern

### Overview

The Strategy pattern is used for engine selection and quality-based routing.

### Engine Selection Strategy

**Strategy Interface:**
```python
# app/core/engines/engine_protocol.py
class EngineProtocol(ABC):
    @abstractmethod
    def synthesize(self, text: str, **kwargs) -> bytes:
        pass
```

**Concrete Strategies:**
```python
# app/core/engines/xtts_engine.py
class XTTSEngine(EngineProtocol):
    def synthesize(self, text: str, **kwargs) -> bytes:
        # XTTS implementation
        pass

# app/core/engines/chatterbox_engine.py
class ChatterboxEngine(EngineProtocol):
    def synthesize(self, text: str, **kwargs) -> bytes:
        # Chatterbox implementation
        pass
```

**Strategy Selection:**
```python
# backend/api/routes/voice.py
@router.post("/api/voice/synthesize")
async def synthesize(request: VoiceSynthesizeRequest):
    # Strategy selection based on quality requirements
    if request.quality_requirement == "high":
        engine = get_engine("xtts_v2")
    elif request.quality_requirement == "fast":
        engine = get_engine("chatterbox")
    else:
        engine = get_engine("tortoise")
    
    # Execute strategy
    audio = await engine.synthesize(request.text, **request.parameters)
    return VoiceSynthesizeResponse(audio=audio)
```

### Quality-Based Routing Strategy

```python
# backend/api/utils/quality_recommendations.py
def recommend_engine(quality_requirements: QualityRequirements) -> str:
    if quality_requirements.priority == "quality":
        return "xtts_v2"
    elif quality_requirements.priority == "speed":
        return "chatterbox"
    elif quality_requirements.priority == "naturalness":
        return "tortoise"
    else:
        return "xtts_v2"  # Default
```

---

## Factory Pattern

### Overview

The Factory pattern is used for creating engine instances and UI components.

### Engine Factory

**Factory Implementation:**
```python
# app/core/engines/engine_factory.py
class EngineFactory:
    @staticmethod
    def create_engine(engine_id: str) -> EngineProtocol:
        if engine_id == "xtts_v2":
            return XTTSEngine()
        elif engine_id == "chatterbox":
            return ChatterboxEngine()
        elif engine_id == "tortoise":
            return TortoiseEngine()
        else:
            raise ValueError(f"Unknown engine: {engine_id}")
```

### Context Menu Factory

**Factory Implementation:**
```csharp
// Services/ContextMenuService.cs
public class ContextMenuService
{
    public MenuFlyout CreateContextMenu(string contextType, object? contextData = null)
    {
        return contextType.ToLower() switch
        {
            "timeline" => CreateTimelineMenu(contextData),
            "profile" => CreateProfileMenu(contextData),
            "audio" => CreateAudioMenu(contextData),
            _ => CreateDefaultMenu(contextData)
        };
    }
}
```

---

## Dependency Injection

### Overview

VoiceStudio uses a simple dependency injection pattern through the ServiceProvider.

### Service Registration

```csharp
public static class ServiceProvider
{
    private static IBackendClient? _backendClient;
    private static IAudioPlayerService? _audioPlayerService;
    
    public static void Initialize()
    {
        _backendClient = new BackendClient(config);
        _audioPlayerService = new AudioPlayerService();
    }
}
```

### Service Injection

```csharp
public class ProfilesViewModel : BaseViewModel
{
    private readonly IBackendClient _backendClient;
    
    public ProfilesViewModel()
    {
        // Dependency injection via ServiceProvider
        _backendClient = ServiceProvider.GetBackendClient();
    }
}
```

### Constructor Injection Pattern

```csharp
public class MyViewModel : BaseViewModel
{
    private readonly IBackendClient _backendClient;
    private readonly IAudioPlayerService _audioService;
    
    // Constructor injection (preferred)
    public MyViewModel(IBackendClient backendClient, IAudioPlayerService audioService)
    {
        _backendClient = backendClient;
        _audioService = audioService;
    }
}
```

---

## Command Pattern

### Overview

The Command pattern is used extensively for user actions and undo/redo operations.

### ICommand Implementation

**RelayCommand:**
```csharp
public class ProfilesViewModel : BaseViewModel
{
    public IAsyncRelayCommand LoadProfilesCommand { get; }
    public IRelayCommand ClearSelectionCommand { get; }
    
    public ProfilesViewModel()
    {
        LoadProfilesCommand = new AsyncRelayCommand(LoadProfilesAsync);
        ClearSelectionCommand = new RelayCommand(ClearSelection, () => HasSelection);
    }
    
    private async Task LoadProfilesAsync()
    {
        // Command execution
    }
    
    private void ClearSelection()
    {
        // Command execution
    }
}
```

### Undoable Commands

**IUndoableAction:**
```csharp
public interface IUndoableAction
{
    string ActionName { get; }
    void Undo();
    void Redo();
}

public class CreateProfileAction : IUndoableAction
{
    public string ActionName => "Create Profile";
    private readonly string _profileId;
    private readonly VoiceProfile _profile;
    
    public void Undo()
    {
        // Undo operation
    }
    
    public void Redo()
    {
        // Redo operation
    }
}
```

---

## Template Method Pattern

### Overview

The Template Method pattern is used in BaseViewModel for common error handling workflows.

### Template Method Implementation

**BaseViewModel:**
```csharp
public abstract class BaseViewModel : ObservableObject
{
    protected async Task<T?> ExecuteWithErrorHandlingAsync<T>(
        Func<Task<T>> operation,
        string context = "",
        int maxRetries = 0)
    {
        // Template method: Define algorithm structure
        int attempts = 0;
        while (attempts <= maxRetries)
        {
            try
            {
                return await operation(); // Call hook method
            }
            catch (Exception ex)
            {
                if (attempts < maxRetries && IsRetryableException(ex))
                {
                    await Task.Delay(1000 * (int)Math.Pow(2, attempts));
                    attempts++;
                    continue;
                }
                await HandleErrorAsync(ex, context);
                return default(T);
            }
        }
        return default(T);
    }
    
    protected abstract bool IsRetryableException(Exception ex); // Hook method
}
```

---

## Design Decisions

### Why MVVM?

**Decision:** Use MVVM pattern for frontend architecture.

**Rationale:**
- WinUI 3 and XAML are designed for MVVM
- Enables data binding and testability
- Clear separation of concerns
- Industry standard for WPF/WinUI applications

### Why Service-Oriented Architecture?

**Decision:** Use service-oriented architecture with ServiceProvider.

**Rationale:**
- Centralized service management
- Easy to mock for testing
- Reusable across ViewModels
- Simple dependency injection

### Why FastAPI for Backend?

**Decision:** Use FastAPI for backend API.

**Rationale:**
- High performance async framework
- Automatic OpenAPI documentation
- Type safety with Pydantic
- Easy to extend with routes

### Why Engine Protocol?

**Decision:** Use EngineProtocol interface for all engines.

**Rationale:**
- Consistent interface across engines
- Easy to add new engines
- Strategy pattern for engine selection
- Testability and mockability

### Why WebSocket for Real-Time Updates?

**Decision:** Use WebSocket for real-time updates.

**Rationale:**
- Low latency for real-time data
- Efficient for frequent updates
- Bidirectional communication
- Better than polling

### Why Local-First Architecture?

**Decision:** All processing happens locally.

**Rationale:**
- Privacy: No data sent to cloud
- Performance: No network latency
- Reliability: Works offline
- Control: User owns their data

---

## Pattern Usage Summary

| Pattern | Usage | Location |
|---------|-------|----------|
| MVVM | Frontend architecture | All ViewModels and Views |
| Service-Oriented | Service management | ServiceProvider, Services |
| Repository | Data access | IBackendClient |
| Observer | Event-driven updates | WebSocket, PropertyChanged |
| Strategy | Engine selection | Engine selection logic |
| Factory | Object creation | EngineFactory, ContextMenuService |
| Dependency Injection | Service injection | ServiceProvider |
| Command | User actions | ICommand, IUndoableAction |
| Template Method | Common workflows | BaseViewModel |

---

## Best Practices

1. **Always use MVVM:** Keep Views passive, ViewModels stateful
2. **Use Services:** Don't create dependencies directly, use ServiceProvider
3. **Use Commands:** All user actions should use ICommand
4. **Handle Errors:** Use BaseViewModel error handling methods
5. **Async Operations:** Use AsyncRelayCommand for async operations
6. **Property Notifications:** Use SetProperty for property changes
7. **Testability:** Design for testability with interfaces and dependency injection

---

**Last Updated:** 2025-01-28  
**Version:** 1.0

