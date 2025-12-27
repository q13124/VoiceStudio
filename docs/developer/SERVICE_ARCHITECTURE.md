# Service Architecture
## VoiceStudio Quantum+ - Complete Service Documentation

**Date:** 2025-01-28  
**Status:** Complete  
**Purpose:** Document all services, their dependencies, lifecycle, and usage patterns

---

## Overview

VoiceStudio Quantum+ uses a service-oriented architecture with dependency injection through a static `ServiceProvider` class. All services are initialized during application startup and are available throughout the application lifecycle.

**Total Services:** 23 services  
**Service Provider:** `src/VoiceStudio.App/Services/ServiceProvider.cs`  
**Initialization:** `App.xaml.cs` → `ServiceProvider.Initialize()`

---

## Service Provider Architecture

### ServiceProvider Class

**Location:** `src/VoiceStudio.App/Services/ServiceProvider.cs`

**Pattern:** Static service locator (can be upgraded to Microsoft.Extensions.DependencyInjection)

**Initialization:**
- Called once during application startup
- Services are created in dependency order
- Lazy initialization on first access (if not already initialized)

**Disposal:**
- `Dispose()` method cleans up disposable services
- Called during application shutdown

---

## Service Categories

### 1. Core Services (Backend & Communication)

#### BackendClient
**Interface:** `IBackendClient`  
**Implementation:** `BackendClient`  
**Location:** `src/VoiceStudio.App/Services/BackendClient.cs`

**Purpose:** HTTP/WebSocket communication with FastAPI backend

**Dependencies:**
- `BackendClientConfig` (configuration)

**Features:**
- HTTP request/response handling
- WebSocket connection management
- Circuit breaker pattern
- Retry logic with exponential backoff
- Connection status monitoring
- Request/response serialization

**Usage:**
```csharp
var backendClient = ServiceProvider.GetBackendClient();
var response = await backendClient.GetAsync<ProfileResponse>("/api/profiles");
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Disposed during `ServiceProvider.Dispose()`
- Singleton instance

---

### 2. Audio Services

#### AudioPlayerService
**Interface:** `IAudioPlayerService`  
**Implementation:** `AudioPlayerService`  
**Location:** `src/VoiceStudio.App/Services/AudioPlayerService.cs`

**Purpose:** Audio playback and management

**Dependencies:** None

**Features:**
- Audio file playback
- Playback control (play, pause, stop)
- Volume control
- Playback position tracking

**Usage:**
```csharp
var audioService = ServiceProvider.GetAudioPlayerService();
await audioService.PlayAsync(audioFilePath);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Disposed during `ServiceProvider.Dispose()`
- Singleton instance

---

### 3. Error Handling Services

#### ErrorLoggingService
**Interface:** `IErrorLoggingService`  
**Implementation:** `ErrorLoggingService`  
**Location:** `src/VoiceStudio.App/Services/ErrorLoggingService.cs`

**Purpose:** Centralized error logging

**Dependencies:** None

**Features:**
- Error logging to file
- Error categorization
- Stack trace capture
- Error aggregation

**Usage:**
```csharp
var errorLogger = ServiceProvider.GetErrorLoggingService();
await errorLogger.LogErrorAsync(exception, context);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Disposed during `ServiceProvider.Dispose()`
- Singleton instance

#### ErrorDialogService
**Interface:** `IErrorDialogService`  
**Implementation:** `ErrorDialogService`  
**Location:** `src/VoiceStudio.App/Services/ErrorDialogService.cs`

**Purpose:** User-facing error dialogs

**Dependencies:**
- `IErrorLoggingService` (for logging errors)

**Features:**
- Error dialog display
- User-friendly error messages
- Error recovery suggestions
- Error reporting

**Usage:**
```csharp
var errorDialog = ServiceProvider.GetErrorDialogService();
await errorDialog.ShowErrorAsync("Operation failed", exception);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Disposed during `ServiceProvider.Dispose()`
- Singleton instance

---

### 4. State Management Services

#### StatePersistenceService
**Implementation:** `StatePersistenceService`  
**Location:** `src/VoiceStudio.App/Services/StatePersistenceService.cs`

**Purpose:** Save and restore application state

**Dependencies:** None

**Features:**
- State snapshot creation
- State restoration
- Automatic state saving
- State versioning

**Usage:**
```csharp
var stateService = ServiceProvider.GetStatePersistenceService();
var statePath = await stateService.SaveStateAsync("operation_id", stateObject);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

#### StateCacheService
**Implementation:** `StateCacheService`  
**Location:** `src/VoiceStudio.App/Services/StateCacheService.cs`

**Purpose:** In-memory state caching

**Dependencies:** None

**Features:**
- Key-value caching
- Cache expiration
- Cache invalidation
- Memory-efficient storage

**Usage:**
```csharp
var cacheService = ServiceProvider.GetStateCacheService();
cacheService.Set("key", value, TimeSpan.FromMinutes(5));
var value = cacheService.Get<Type>("key");
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

#### PanelStateService
**Implementation:** `PanelStateService`  
**Location:** `src/VoiceStudio.App/Services/PanelStateService.cs`

**Purpose:** Panel state persistence and restoration

**Dependencies:**
- `ISettingsService` (for storing panel state)

**Features:**
- Panel size/position persistence
- Panel visibility state
- Workspace profile management
- Panel layout restoration

**Usage:**
```csharp
var panelStateService = ServiceProvider.GetPanelStateService();
await panelStateService.SavePanelStateAsync(panelId, state);
var state = await panelStateService.LoadPanelStateAsync(panelId);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

---

### 5. Operation Management Services

#### OperationQueueService
**Implementation:** `OperationQueueService`  
**Location:** `src/VoiceStudio.App/Services/OperationQueueService.cs`

**Purpose:** Queue operations for offline/retry scenarios

**Dependencies:** None

**Features:**
- Operation queuing
- Queue processing
- Retry logic
- Operation prioritization

**Usage:**
```csharp
var queueService = ServiceProvider.GetOperationQueueService();
await queueService.QueueOperationAsync(operation);
await queueService.ProcessQueueAsync();
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Monitored by background task for connection restoration
- Singleton instance

#### GracefulDegradationService
**Implementation:** `GracefulDegradationService`  
**Location:** `src/VoiceStudio.App/Services/GracefulDegradationService.cs`

**Purpose:** Handle degraded mode when backend is unavailable

**Dependencies:** None

**Features:**
- Degraded mode detection
- Feature disabling
- User notification
- Automatic recovery

**Usage:**
```csharp
var degradationService = ServiceProvider.GetGracefulDegradationService();
degradationService.EnterDegradedMode("Backend unavailable", "VoiceSynthesis");
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Monitored by background task for connection status
- Singleton instance

---

### 6. UI Services (IDEA 2, 4, 5, 9, 10, 11, 12, 15, 16)

#### ToastNotificationService
**Implementation:** `ToastNotificationService`  
**Location:** `src/VoiceStudio.App/Services/ToastNotificationService.cs`

**Purpose:** Toast notification display (IDEA 11)

**Dependencies:**
- `ToastContainer` (UI element, registered separately)

**Features:**
- Success/error/warning/info notifications
- Auto-dismiss with configurable timeout
- Manual dismiss
- Maximum 4 visible notifications
- Progress notifications

**Usage:**
```csharp
var toastService = ServiceProvider.GetToastNotificationService();
toastService.ShowSuccess("Operation completed");
toastService.ShowError("Operation failed", dismissible: true);
```

**Lifecycle:**
- Registered via `RegisterToastNotificationService()` in `MainWindow.xaml.cs`
- Singleton instance

#### MultiSelectService
**Implementation:** `MultiSelectService`  
**Location:** `src/VoiceStudio.App/Services/MultiSelectService.cs`

**Purpose:** Multi-select functionality (IDEA 12)

**Dependencies:** None

**Features:**
- Item selection management
- Selection count tracking
- Batch operations
- Selection persistence

**Usage:**
```csharp
var multiSelect = ServiceProvider.GetMultiSelectService();
multiSelect.SelectItem(itemId);
multiSelect.SelectRange(startId, endId);
var selected = multiSelect.GetSelectedItems();
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

#### ContextMenuService
**Implementation:** `ContextMenuService`  
**Location:** `src/VoiceStudio.App/Services/ContextMenuService.cs`

**Purpose:** Contextual right-click menus (IDEA 10)

**Dependencies:** None

**Features:**
- Context menu creation
- Action registration
- Keyboard shortcut display
- Context-sensitive actions

**Usage:**
```csharp
var contextMenu = ServiceProvider.GetContextMenuService();
var menu = contextMenu.CreateMenu(context);
contextMenu.ShowMenu(menu, position);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

#### DragDropVisualFeedbackService
**Implementation:** `DragDropVisualFeedbackService`  
**Location:** `src/VoiceStudio.App/Services/DragDropVisualFeedbackService.cs`

**Purpose:** Enhanced drag-and-drop visual feedback (IDEA 4)

**Dependencies:** None

**Features:**
- Drag preview creation
- Drop target highlighting
- Visual feedback during drag
- Drop operation feedback

**Usage:**
```csharp
var dragDrop = ServiceProvider.GetDragDropVisualFeedbackService();
dragDrop.ShowDragPreview(item);
dragDrop.HighlightDropTarget(target);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

#### UndoRedoService
**Implementation:** `UndoRedoService`  
**Location:** `src/VoiceStudio.App/Services/UndoRedoService.cs`

**Purpose:** Undo/redo functionality (IDEA 15)

**Dependencies:** None

**Features:**
- Action history tracking
- Undo/redo operations
- Maximum 100 actions
- Action grouping

**Usage:**
```csharp
var undoRedo = ServiceProvider.GetUndoRedoService();
undoRedo.RecordAction(action);
undoRedo.Undo();
undoRedo.Redo();
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

#### RecentProjectsService
**Implementation:** `RecentProjectsService`  
**Location:** `src/VoiceStudio.App/Services/RecentProjectsService.cs`

**Purpose:** Recent projects quick access (IDEA 16)

**Dependencies:** None

**Features:**
- Recent project tracking (last 10)
- Project pinning (max 3)
- Quick access menu
- Project metadata

**Usage:**
```csharp
var recentProjects = ServiceProvider.GetRecentProjectsService();
recentProjects.AddProject(projectPath);
recentProjects.PinProject(projectPath);
var recent = recentProjects.GetRecentProjects();
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

---

### 7. Settings & Configuration Services

#### SettingsService
**Interface:** `ISettingsService`  
**Implementation:** `SettingsService`  
**Location:** `src/VoiceStudio.App/Services/SettingsService.cs`

**Purpose:** Application settings management

**Dependencies:**
- `IBackendClient` (for backend API calls)

**Features:**
- Settings CRUD operations
- Settings categories
- Settings caching (5-minute cache)
- Local storage fallback
- Thread-safe operations

**Usage:**
```csharp
var settingsService = ServiceProvider.GetSettingsService();
var settings = await settingsService.GetSettingsAsync<GeneralSettings>("general");
await settingsService.UpdateSettingsAsync("general", settings);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

---

### 8. Update & Maintenance Services

#### UpdateService
**Interface:** `IUpdateService`  
**Implementation:** `UpdateService`  
**Location:** `src/VoiceStudio.App/Services/UpdateService.cs`

**Purpose:** Application update checking and installation

**Dependencies:** None

**Features:**
- Update availability checking
- Update download
- Update installation
- Version comparison
- Streaming downloads

**Usage:**
```csharp
var updateService = ServiceProvider.GetUpdateService();
var updateInfo = await updateService.CheckForUpdatesAsync();
if (updateInfo.HasUpdate)
{
    await updateService.DownloadUpdateAsync(updateInfo);
}
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Disposed during `ServiceProvider.Dispose()`
- Singleton instance

---

### 9. Help & Onboarding Services

#### HelpOverlayService
**Interface:** `IHelpOverlayService`  
**Implementation:** `HelpOverlayService`  
**Location:** `src/VoiceStudio.App/Services/HelpOverlayService.cs`

**Purpose:** Contextual help overlay system

**Dependencies:** None

**Features:**
- Help overlay display
- Context-sensitive help
- Help content management
- Help overlay positioning

**Usage:**
```csharp
var helpService = ServiceProvider.GetHelpOverlayService();
helpService.ShowHelpOverlay(panelId, helpContent);
helpService.HideHelpOverlay();
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

#### OnboardingService
**Implementation:** `OnboardingService`  
**Location:** `src/VoiceStudio.App/Services/OnboardingService.cs`

**Purpose:** User onboarding and tutorials

**Dependencies:** None

**Features:**
- Onboarding flow management
- Tutorial progression
- Feature highlights
- User progress tracking

**Usage:**
```csharp
var onboarding = new OnboardingService();
await onboarding.StartOnboardingAsync();
```

**Lifecycle:**
- Created on-demand (not in ServiceProvider)
- Instance per onboarding session

---

### 10. Quality & Analysis Services

#### RealTimeQualityService
**Implementation:** `RealTimeQualityService`  
**Location:** `src/VoiceStudio.App/Services/RealTimeQualityService.cs`

**Purpose:** Real-time quality analysis

**Dependencies:**
- `IBackendClient` (for quality API calls)

**Features:**
- Real-time quality metrics
- Quality monitoring
- Quality alerts
- Quality trends

**Usage:**
```csharp
var qualityService = ServiceProvider.GetRealTimeQualityService();
var metrics = await qualityService.GetQualityMetricsAsync(audioId);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

#### ReferenceAudioQualityAnalyzer
**Implementation:** `ReferenceAudioQualityAnalyzer`  
**Location:** `src/VoiceStudio.App/Services/ReferenceAudioQualityAnalyzer.cs`

**Purpose:** Reference audio quality analysis

**Dependencies:** None

**Features:**
- Reference audio analysis
- Quality recommendations
- Optimal segment selection
- Quality enhancement suggestions

**Usage:**
```csharp
var analyzer = new ReferenceAudioQualityAnalyzer();
var analysis = await analyzer.AnalyzeAsync(audioPath);
```

**Lifecycle:**
- Created on-demand (not in ServiceProvider)
- Instance per analysis

---

### 11. Plugin & Panel Services

#### PluginManager
**Implementation:** `PluginManager`  
**Location:** `src/VoiceStudio.App/Services/PluginManager.cs`

**Purpose:** Plugin system management

**Dependencies:**
- `PanelRegistry` (for panel registration)
- `IBackendClient` (for plugin API calls)

**Features:**
- Plugin loading
- Plugin discovery
- Plugin lifecycle management
- Plugin API integration

**Usage:**
```csharp
var pluginManager = ServiceProvider.GetPluginManager();
await pluginManager.LoadPluginsAsync();
var plugins = pluginManager.GetLoadedPlugins();
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Disposed during `ServiceProvider.Dispose()` (unloads plugins)
- Singleton instance

#### PanelRegistry
**Implementation:** `PanelRegistry`  
**Location:** `VoiceStudio.Core.Panels.PanelRegistry`

**Purpose:** Panel registration and discovery

**Dependencies:** None

**Features:**
- Panel registration
- Panel discovery
- Panel region management
- Panel metadata

**Usage:**
```csharp
var panelRegistry = ServiceProvider.GetPanelRegistry();
panelRegistry.RegisterPanel(panel);
var panels = panelRegistry.GetPanelsForRegion(PanelRegion.Left);
```

**Lifecycle:**
- Created during `ServiceProvider.Initialize()`
- Singleton instance

---

### 12. Utility Services

#### KeyboardShortcutService
**Implementation:** `KeyboardShortcutService`  
**Location:** `src/VoiceStudio.App/Services/KeyboardShortcutService.cs`

**Purpose:** Keyboard shortcut management

**Dependencies:** None

**Features:**
- Shortcut registration
- Shortcut execution
- Shortcut conflict detection
- Shortcut customization

**Usage:**
```csharp
var shortcutService = new KeyboardShortcutService();
shortcutService.RegisterShortcut("Ctrl+S", () => Save());
```

**Lifecycle:**
- Created in `MainWindow.xaml.cs` (not in ServiceProvider)
- Instance per window

#### CommandPaletteService
**Implementation:** `CommandPaletteService`  
**Location:** `src/VoiceStudio.App/Services/CommandPaletteService.cs`

**Purpose:** Command palette functionality

**Dependencies:** None

**Features:**
- Command registration
- Command search
- Command execution
- Command categorization

**Usage:**
```csharp
var commandPalette = new CommandPaletteService();
commandPalette.RegisterCommand("save", "Save Project", () => Save());
```

**Lifecycle:**
- Created on-demand (not in ServiceProvider)
- Instance per command palette

#### CommandRegistry
**Implementation:** `CommandRegistry`  
**Location:** `src/VoiceStudio.App/Services/CommandRegistry.cs`

**Purpose:** Command registration and lookup

**Dependencies:** None

**Features:**
- Command storage
- Command lookup
- Command metadata

**Usage:**
```csharp
var registry = new CommandRegistry();
registry.Register("command_id", command);
var command = registry.Get("command_id");
```

**Lifecycle:**
- Created on-demand (not in ServiceProvider)
- Instance per registry

#### ThemeManager
**Implementation:** `ThemeManager`  
**Location:** `src/VoiceStudio.App/Services/ThemeManager.cs`

**Purpose:** Theme management

**Dependencies:** None

**Features:**
- Theme switching
- Theme persistence
- Theme customization

**Usage:**
```csharp
var themeManager = new ThemeManager();
themeManager.SetTheme(Theme.Dark);
```

**Lifecycle:**
- Created on-demand (not in ServiceProvider)
- Instance per theme manager

#### WindowHostService
**Implementation:** `WindowHostService`  
**Location:** `src/VoiceStudio.App/Services/WindowHostService.cs`

**Purpose:** Window management

**Dependencies:** None

**Features:**
- Window creation
- Window positioning
- Window state management

**Usage:**
```csharp
var windowHost = new WindowHostService();
var window = windowHost.CreateWindow(content);
```

**Lifecycle:**
- Created on-demand (not in ServiceProvider)
- Instance per window host

#### PanelSettingsStore
**Implementation:** `PanelSettingsStore`  
**Location:** `src/VoiceStudio.App/Services/PanelSettingsStore.cs`

**Purpose:** Per-panel settings storage

**Dependencies:** None

**Features:**
- Panel-specific settings
- Settings persistence
- Settings retrieval

**Usage:**
```csharp
var settingsStore = new PanelSettingsStore();
settingsStore.SaveSettings(panelId, settings);
var settings = settingsStore.LoadSettings(panelId);
```

**Lifecycle:**
- Created on-demand (not in ServiceProvider)
- Instance per settings store

---

## Service Dependency Graph

```
BackendClient
    ├── SettingsService
    ├── RealTimeQualityService
    └── PluginManager
        └── PanelRegistry

ErrorLoggingService
    └── ErrorDialogService

ISettingsService
    └── PanelStateService

ToastContainer (UI)
    └── ToastNotificationService (registered separately)
```

---

## Service Lifecycle

### Initialization Order

1. **BackendClient** - Core communication service
2. **AudioPlayerService** - Audio services
3. **ErrorLoggingService** - Error handling foundation
4. **ErrorDialogService** - Depends on ErrorLoggingService
5. **OperationQueueService** - Operation management
6. **StatePersistenceService** - State management
7. **StateCacheService** - Caching
8. **GracefulDegradationService** - Degradation handling
9. **UpdateService** - Update mechanism
10. **SettingsService** - Depends on BackendClient
11. **HelpOverlayService** - Help system
12. **RealTimeQualityService** - Depends on BackendClient
13. **PanelStateService** - Depends on SettingsService
14. **MultiSelectService** - UI services
15. **DragDropVisualFeedbackService** - UI services
16. **ContextMenuService** - UI services
17. **UndoRedoService** - UI services
18. **RecentProjectsService** - UI services
19. **PanelRegistry** - Panel system
20. **PluginManager** - Depends on PanelRegistry and BackendClient
21. **ToastNotificationService** - Registered separately in MainWindow

### Disposal Order

1. **BackendClient** - Dispose HTTP client
2. **AudioPlayerService** - Dispose audio resources
3. **ErrorLoggingService** - Flush logs
4. **UpdateService** - Dispose update resources
5. **PluginManager** - Unload all plugins

---

## Service Usage Patterns

### Pattern 1: Direct Service Access

```csharp
var backendClient = ServiceProvider.GetBackendClient();
var response = await backendClient.GetAsync<ProfileResponse>("/api/profiles");
```

### Pattern 2: Service Injection in ViewModels

```csharp
public class MyViewModel : BaseViewModel
{
    private readonly IBackendClient _backendClient;
    
    public MyViewModel()
    {
        _backendClient = ServiceProvider.GetBackendClient();
    }
}
```

### Pattern 3: Service Injection in Code-Behind

```csharp
public sealed partial class MyView : UserControl
{
    private readonly MultiSelectService _multiSelectService;
    
    public MyView()
    {
        InitializeComponent();
        _multiSelectService = ServiceProvider.GetMultiSelectService();
    }
}
```

### Pattern 4: Service Registration (ToastNotificationService)

```csharp
// In MainWindow.xaml.cs
var toastService = new ToastNotificationService(ToastContainer);
ServiceProvider.RegisterToastNotificationService(toastService);
```

---

## Service Best Practices

### 1. Service Initialization

- ✅ Always check if service is initialized before use
- ✅ Use lazy initialization for expensive services
- ✅ Initialize services in dependency order

### 2. Service Access

- ✅ Use `ServiceProvider.GetXxxService()` methods
- ✅ Handle `InvalidOperationException` if service not initialized
- ✅ Cache service references in ViewModels/Views

### 3. Service Disposal

- ✅ Implement `IDisposable` for services with resources
- ✅ Dispose services in `ServiceProvider.Dispose()`
- ✅ Clean up resources properly

### 4. Service Dependencies

- ✅ Document service dependencies clearly
- ✅ Initialize dependencies before dependent services
- ✅ Avoid circular dependencies

### 5. Service Threading

- ✅ Make services thread-safe if accessed from multiple threads
- ✅ Use `ConfigureAwait(false)` in async methods
- ✅ Use locks or concurrent collections for shared state

---

## Service Registration

### Current Implementation

Services are registered in `ServiceProvider.Initialize()`:

```csharp
public static void Initialize()
{
    // Create services in dependency order
    _backendClient = new BackendClient(config);
    _settingsService = new SettingsService(_backendClient);
    // ... other services
}
```

### Future Migration

The current static service locator can be migrated to `Microsoft.Extensions.DependencyInjection`:

```csharp
// Future implementation
var services = new ServiceCollection();
services.AddSingleton<IBackendClient, BackendClient>();
services.AddSingleton<ISettingsService, SettingsService>();
// ... register all services
var serviceProvider = services.BuildServiceProvider();
```

---

## Service Testing

### Unit Testing Services

```csharp
[Test]
public void TestServiceInitialization()
{
    ServiceProvider.Initialize();
    var service = ServiceProvider.GetBackendClient();
    Assert.IsNotNull(service);
}
```

### Integration Testing Services

```csharp
[Test]
public async Task TestServiceIntegration()
{
    ServiceProvider.Initialize();
    var backendClient = ServiceProvider.GetBackendClient();
    var settingsService = ServiceProvider.GetSettingsService();
    
    // Test service interaction
    var settings = await settingsService.GetSettingsAsync<GeneralSettings>("general");
    Assert.IsNotNull(settings);
}
```

---

## Service Statistics

### Service Count by Category

- **Core Services:** 1 (BackendClient)
- **Audio Services:** 1 (AudioPlayerService)
- **Error Handling:** 2 (ErrorLoggingService, ErrorDialogService)
- **State Management:** 3 (StatePersistenceService, StateCacheService, PanelStateService)
- **Operation Management:** 2 (OperationQueueService, GracefulDegradationService)
- **UI Services:** 6 (ToastNotificationService, MultiSelectService, ContextMenuService, DragDropVisualFeedbackService, UndoRedoService, RecentProjectsService)
- **Settings & Configuration:** 1 (SettingsService)
- **Update & Maintenance:** 1 (UpdateService)
- **Help & Onboarding:** 2 (HelpOverlayService, OnboardingService)
- **Quality & Analysis:** 2 (RealTimeQualityService, ReferenceAudioQualityAnalyzer)
- **Plugin & Panel:** 2 (PluginManager, PanelRegistry)
- **Utility Services:** 5 (KeyboardShortcutService, CommandPaletteService, CommandRegistry, ThemeManager, WindowHostService, PanelSettingsStore)

**Total:** 23 services

### Service Registration Status

- **Registered in ServiceProvider:** 20 services
- **Registered Separately:** 1 service (ToastNotificationService)
- **Created On-Demand:** 2 services (OnboardingService, ReferenceAudioQualityAnalyzer)

---

## Related Documentation

- **Architecture:** `docs/developer/ARCHITECTURE.md`
- **Code Structure:** `docs/developer/CODE_STRUCTURE.md`
- **UI Services Architecture:** `docs/developer/ARCHITECTURE.md#ui-services-architecture`

---

**Last Updated:** 2025-01-28  
**Maintained By:** Worker 3  
**Status:** Complete

