# VoiceStudio Services Documentation

Complete guide to all services available in VoiceStudio Quantum+ and how to use them.

**Last Updated:** 2025-01-28  
**Version:** 1.0

---

## 📋 Table of Contents

1. [Service Provider](#service-provider)
2. [UI Services](#ui-services)
3. [State Management Services](#state-management-services)
4. [Error Handling Services](#error-handling-services)
5. [Audio Services](#audio-services)
6. [Backend Services](#backend-services)
7. [Quality Services](#quality-services)
8. [Panel Services](#panel-services)
9. [Other Services](#other-services)
10. [Service Usage Patterns](#service-usage-patterns)

---

## Service Provider

All services are accessed through the `ServiceProvider` class located at `src/VoiceStudio.App/Services/ServiceProvider.cs`.

### Initialization

Services are automatically initialized when first accessed. You can also manually initialize:

```csharp
ServiceProvider.Initialize();
```

### Accessing Services

```csharp
// Get a required service (throws if not initialized)
var service = ServiceProvider.GetMultiSelectService();

// Get an optional service (returns null if not available)
var service = ServiceProvider.TryGetMultiSelectService();
```

---

## UI Services

### MultiSelectService

**Location:** `src/VoiceStudio.App/Services/MultiSelectService.cs`  
**Purpose:** Manages multi-select state across panels. Implements IDEA 12: Multi-Select with Visual Selection Indicators.

**Key Features:**
- Per-panel selection state management
- Range selection support (Shift+Click)
- Selection change events
- Visual selection indicators

**Usage Example:**

```csharp
// Get the service
var multiSelectService = ServiceProvider.GetMultiSelectService();

// Get state for a panel
var state = multiSelectService.GetState("ProfilesPanel");

// Add item to selection
state.Add("profile-123");

// Toggle selection
state.Toggle("profile-456");

// Set range selection
state.SetRange("profile-1", "profile-5", allProfileIds);

// Clear selection
multiSelectService.ClearSelection("ProfilesPanel");

// Subscribe to selection changes
multiSelectService.SelectionChanged += (sender, e) =>
{
    Console.WriteLine($"Selection changed in {e.PanelId}: {e.State.Count} items");
};
```

**Integration Points:**
- ProfilesView (voice profiles)
- EnsembleSynthesisView (jobs)
- DiagnosticsView (logs, error logs)
- Any list/grid that supports multi-selection

---

### ContextMenuService

**Location:** `src/VoiceStudio.App/Services/ContextMenuService.cs`  
**Purpose:** Manages contextual right-click menus. Implements IDEA 10: Contextual Right-Click Menus for All Interactive Elements.

**Key Features:**
- Context-aware menu generation
- Keyboard shortcut display
- Multiple context types (timeline, profile, audio, effect, track, clip, marker)
- Custom menu item support

**Usage Example:**

```csharp
// Get the service
var contextMenuService = ServiceProvider.GetContextMenuService();

// Create a context menu for a profile
var menu = contextMenuService.CreateContextMenu("profile", profileData);

// Attach to UI element
profileElement.ContextFlyout = menu;

// Create custom menu
var customMenu = new MenuFlyout();
customMenu.Items.Add(contextMenuService.CreateMenuItem("Custom Action", "Ctrl+K", () => {
    // Handle action
}));
```

**Supported Context Types:**
- `timeline` - Timeline operations
- `profile` - Voice profile operations
- `audio` - Audio file operations
- `effect` - Audio effect operations
- `track` - Track operations
- `clip` - Clip operations
- `marker` - Marker operations

**Integration Points:**
- All interactive UI elements
- TimelineView
- ProfilesView
- EffectsMixerView
- MarkerManagerView
- And 3+ more panels

---

### DragDropVisualFeedbackService

**Location:** `src/VoiceStudio.App/Services/DragDropVisualFeedbackService.cs`  
**Purpose:** Provides enhanced visual feedback during drag-and-drop operations. Implements IDEA 4: Enhanced Drag-and-Drop Visual Feedback.

**Key Features:**
- Visual drag preview
- Drop target indicators
- Position-based feedback (Before, After, On)
- Smooth animations

**Usage Example:**

```csharp
// Get the service
var dragDropService = ServiceProvider.GetDragDropVisualFeedbackService();

// Create drag preview
var preview = dragDropService.CreateDragPreview(sourceElement, "Item Label");

// Show drop target indicator
dragDropService.ShowDropTargetIndicator(targetElement, DropPosition.Before);

// Hide indicator
dragDropService.HideDropTargetIndicator();

// Cleanup
dragDropService.Cleanup();
```

**DropPosition Enum:**
- `Before` - Insert before target
- `After` - Insert after target
- `On` - Drop on target

**Integration Points:**
- MarkerManagerView (marker reordering)
- TranscribeView (transcription reordering)
- EnsembleSynthesisView (job reordering)
- ScriptEditorView (script segment reordering)
- TagManagerView (tag reordering)
- And 5+ more panels

---

### ToastNotificationService

**Location:** `src/VoiceStudio.App/Services/ToastNotificationService.cs`  
**Purpose:** Displays toast notifications for user feedback. Implements IDEA 11: Toast Notification System for User Feedback.

**Key Features:**
- Multiple notification types (Success, Error, Info, Warning, Progress)
- Auto-dismiss timers
- Action buttons
- Progress tracking
- Maximum visible toasts limit

**Usage Example:**

```csharp
// Register service (done in App.xaml.cs)
var toastContainer = new StackPanel();
var toastService = new ToastNotificationService(toastContainer);
ServiceProvider.RegisterToastNotificationService(toastService);

// Show notifications
var toastService = ServiceProvider.GetToastNotificationService();

// Success notification (auto-dismisses after 3s)
toastService.ShowSuccess("Profile created successfully!");

// Error notification (doesn't auto-dismiss)
toastService.ShowError("Failed to save profile", "Error", () => {
    // View details action
});

// Info notification (auto-dismisses after 5s)
toastService.ShowInfo("Processing complete");

// Warning notification (auto-dismisses after 5s)
toastService.ShowWarning("Low disk space");

// Progress notification
var progressToast = toastService.ShowProgress("Uploading file...");
progressToast.UpdateProgress(0.5); // 50% complete
progressToast.Dismiss();
```

**Notification Types:**
- `Success` - Auto-dismisses after 3 seconds
- `Error` - Does not auto-dismiss
- `Info` - Auto-dismisses after 5 seconds
- `Warning` - Auto-dismisses after 5 seconds
- `Progress` - Manual dismissal required

**Integration Points:**
- All ViewModels (via BaseViewModel)
- Operation completion notifications
- Error notifications
- Progress tracking

---

## State Management Services

### UndoRedoService

**Location:** `src/VoiceStudio.App/Services/UndoRedoService.cs`  
**Purpose:** Manages undo/redo operations across the application.

**Key Features:**
- Undo/redo stack management
- Action history preview
- Maximum stack size limit (100)
- Observable properties for UI binding

**Usage Example:**

```csharp
// Get the service
var undoRedoService = ServiceProvider.GetUndoRedoService();

// Register an action
var action = new CreateProfileAction(profileId, profileData);
undoRedoService.RegisterAction(action);

// Perform undo
if (undoRedoService.CanUndo)
{
    undoRedoService.Undo();
}

// Perform redo
if (undoRedoService.CanRedo)
{
    undoRedoService.Redo();
}

// Get action history
var history = undoRedoService.GetUndoHistory(10);

// Bind to UI
public bool CanUndo => undoRedoService.CanUndo;
public string? NextUndoAction => undoRedoService.NextUndoActionName;
```

**Creating Custom Actions:**

```csharp
public class CreateProfileAction : IUndoableAction
{
    public string ActionName => "Create Profile";
    private readonly string _profileId;
    private readonly ProfileData _data;

    public CreateProfileAction(string profileId, ProfileData data)
    {
        _profileId = profileId;
        _data = data;
    }

    public void Undo()
    {
        // Remove the profile
        Profiles.Remove(_profileId);
    }

    public void Redo()
    {
        // Recreate the profile
        Profiles.Add(_profileId, _data);
    }
}
```

**Integration Points:**
- LexiconViewModel (lexicon operations)
- EmotionControlViewModel (emotion preset operations)
- All ViewModels that perform mutable operations

**Available Action Types:**
- ProfileActions (Create, Delete, BatchDelete)
- LexiconActions (Create, Delete, CreateEntry, DeleteEntry)
- EmotionActions (Create, Delete)
- TimelineActions (AddTrack, AddClip, DeleteClips)
- And 20+ more action types

---

### RecentProjectsService

**Location:** `src/VoiceStudio.App/Services/RecentProjectsService.cs`  
**Purpose:** Manages recent projects history. Implements IDEA 16: Recent Projects Quick Access.

**Key Features:**
- Recent projects list (max 10)
- Pinned projects (max 3)
- Automatic persistence
- Last accessed tracking

**Usage Example:**

```csharp
// Get the service
var recentProjectsService = ServiceProvider.GetRecentProjectsService();

// Add a project
await recentProjectsService.AddRecentProjectAsync(projectPath, projectName);

// Pin a project
await recentProjectsService.PinProjectAsync(projectPath);

// Unpin a project
await recentProjectsService.UnpinProjectAsync(projectPath);

// Get all projects (pinned first)
var allProjects = recentProjectsService.AllProjects;

// Get only recent projects
var recentProjects = recentProjectsService.RecentProjects;

// Get only pinned projects
var pinnedProjects = recentProjectsService.PinnedProjects;

// Remove a project
await recentProjectsService.RemoveProjectAsync(projectPath);
```

**Integration Points:**
- MainWindow (recent projects menu)
- Project opening workflow
- Project management

---

### StatePersistenceService

**Location:** `src/VoiceStudio.App/Services/StatePersistenceService.cs`  
**Purpose:** Persists application state for recovery.

**Key Features:**
- Save state before critical operations
- Restore state on failure
- Automatic cleanup of old states

**Usage Example:**

```csharp
// Get the service
var stateService = ServiceProvider.GetStatePersistenceService();

// Save state before operation
var statePath = await stateService.SaveStateAsync("operation-id", stateData);

// Restore state on failure
var restoredState = await stateService.RestoreStateAsync<StateType>(statePath);

// Cleanup old states
await stateService.CleanupOldStatesAsync(TimeSpan.FromDays(7));
```

**Integration Points:**
- BaseViewModel (ExecuteWithStatePersistenceAsync)
- Critical operations that need rollback

---

### StateCacheService

**Location:** `src/VoiceStudio.App/Services/StateCacheService.cs`  
**Purpose:** Caches application state for performance.

**Key Features:**
- In-memory state caching
- Cache expiration
- Cache invalidation

**Usage Example:**

```csharp
// Get the service
var cacheService = ServiceProvider.GetStateCacheService();

// Cache state
cacheService.SetCache("key", data, TimeSpan.FromMinutes(5));

// Get cached state
var cached = cacheService.GetCache<DataType>("key");

// Invalidate cache
cacheService.InvalidateCache("key");
```

---

## Error Handling Services

### ErrorLoggingService

**Location:** `src/VoiceStudio.App/Services/ErrorLoggingService.cs`  
**Interface:** `src/VoiceStudio.App/Services/IErrorLoggingService.cs`  
**Purpose:** Logs errors, warnings, and info messages.

**Key Features:**
- Error logging with stack traces
- Warning logging
- Info logging
- Context information

**Usage Example:**

```csharp
// Get the service
var loggingService = ServiceProvider.GetErrorLoggingService();

// Log error
loggingService.LogError(exception, "Context information");

// Log warning
loggingService.LogWarning("Warning message", "Context");

// Log info
loggingService.LogInfo("Info message", "Context");
```

**Integration Points:**
- BaseViewModel (automatic error logging)
- All ViewModels
- Service implementations

---

### ErrorDialogService

**Location:** `src/VoiceStudio.App/Services/ErrorDialogService.cs`  
**Interface:** `src/VoiceStudio.App/Services/IErrorDialogService.cs`  
**Purpose:** Displays user-friendly error dialogs.

**Key Features:**
- User-friendly error messages
- Recovery suggestions
- Retry buttons for transient errors
- Error details view

**Usage Example:**

```csharp
// Get the service
var errorDialogService = ServiceProvider.GetErrorDialogService();

// Show error
await errorDialogService.ShowErrorAsync(exception, context: "Operation context");

// Show error with retry
await errorDialogService.ShowErrorAsync(
    exception,
    title: "Operation Failed",
    context: "Context",
    retryAction: async () => {
        // Retry operation
    }
);
```

**Integration Points:**
- BaseViewModel (automatic error dialogs)
- All ViewModels
- Error handling workflows

---

## Audio Services

### AudioPlayerService

**Location:** `src/VoiceStudio.App/Services/AudioPlayerService.cs`  
**Interface:** `src/VoiceStudio.Core/Services/IAudioPlayerService.cs`  
**Purpose:** Plays audio files and streams using NAudio.

**Key Features:**
- File playback
- Stream playback
- Playback controls (Play, Pause, Stop, Resume)
- Volume control
- Position tracking
- Events (PositionChanged, PlaybackCompleted, IsPlayingChanged)

**Usage Example:**

```csharp
// Get the service
var audioService = ServiceProvider.GetAudioPlayerService();

// Play file
await audioService.PlayFileAsync(filePath);

// Play stream
await audioService.PlayStreamAsync(stream);

// Control playback
audioService.Pause();
audioService.Resume();
audioService.Stop();

// Volume control
audioService.Volume = 0.5; // 50%

// Position tracking
var position = audioService.Position;
var duration = audioService.Duration;

// Subscribe to events
audioService.PositionChanged += (sender, e) => {
    Console.WriteLine($"Position: {e.Position}");
};
audioService.PlaybackCompleted += (sender, e) => {
    Console.WriteLine("Playback completed");
};
```

**Integration Points:**
- VoiceSynthesisViewModel
- ProfilesViewModel
- TimelineViewModel
- Any ViewModel that plays audio

---

### AudioPlaybackService

**Location:** `src/VoiceStudio.App/Services/AudioPlaybackService.cs`  
**Interface:** `src/VoiceStudio.Core/Services/IAudioPlaybackService.cs`  
**Purpose:** Alternative audio playback service with cleaner interface.

**Key Features:**
- File playback with CancellationToken
- URL playback
- Properties-based interface

**Usage Example:**

```csharp
// Get the service
var playbackService = ServiceProvider.GetAudioPlaybackService();

// Play file
await playbackService.PlayFileAsync(filePath, cancellationToken);

// Play URL
await playbackService.PlayUrlAsync(url, cancellationToken);
```

---

## Backend Services

### BackendClient

**Location:** `src/VoiceStudio.Core/Services/IBackendClient.cs`  
**Implementation:** `src/VoiceStudio.App/Services/BackendClient.cs`  
**Purpose:** Communicates with the backend API.

**Key Features:**
- REST API calls
- WebSocket support
- MCP operation support
- Health checks
- Voice synthesis
- Profile management
- Project management

**Usage Example:**

```csharp
// Get the service
var backendClient = ServiceProvider.GetBackendClient();

// Health check
var isHealthy = await backendClient.CheckHealthAsync();

// Synthesize voice
var response = await backendClient.SynthesizeVoiceAsync(request);

// Get profiles
var profiles = await backendClient.GetProfilesAsync();

// Get profile
var profile = await backendClient.GetProfileAsync(profileId);

// Create profile
var newProfile = await backendClient.CreateProfileAsync(
    name: "My Voice",
    language: "en",
    emotion: "neutral",
    tags: new List<string> { "custom", "female" }
);
```

**Integration Points:**
- All ViewModels that interact with backend
- Service implementations
- Data synchronization

---

## Quality Services

### RealTimeQualityService

**Location:** `src/VoiceStudio.App/Services/RealTimeQualityService.cs`  
**Purpose:** Provides real-time quality metrics for voice profiles.

**Key Features:**
- Real-time quality score updates
- Quality metrics tracking
- Event notifications

**Usage Example:**

```csharp
// Get the service
var qualityService = ServiceProvider.GetRealTimeQualityService();

// Subscribe to quality updates
qualityService.QualityUpdated += (sender, e) => {
    Console.WriteLine($"Profile {e.ProfileId}: Quality = {e.QualityScore}");
};

// Get current quality
var quality = await qualityService.GetQualityAsync(profileId);
```

**Integration Points:**
- ProfilesViewModel
- QualityBadgeControl
- Quality monitoring

---

## Panel Services

### PanelStateService

**Location:** `src/VoiceStudio.App/Services/PanelStateService.cs`  
**Purpose:** Manages panel state (visibility, size, position).

**Key Features:**
- Panel visibility state
- Panel size and position
- State persistence

**Usage Example:**

```csharp
// Get the service
var panelStateService = ServiceProvider.GetPanelStateService();

// Save panel state
await panelStateService.SavePanelStateAsync(panelId, state);

// Restore panel state
var state = await panelStateService.GetPanelStateAsync(panelId);
```

---

### HelpOverlayService

**Location:** `src/VoiceStudio.App/Services/HelpOverlayService.cs`  
**Interface:** `src/VoiceStudio.App/Services/IHelpOverlayService.cs`  
**Purpose:** Manages help overlays for panels.

**Key Features:**
- Help overlay display
- Contextual help
- Help content management

**Usage Example:**

```csharp
// Get the service
var helpService = ServiceProvider.GetHelpOverlayService();

// Show help overlay
helpService.ShowHelpOverlay(panelId, helpContent);

// Hide help overlay
helpService.HideHelpOverlay(panelId);
```

**Integration Points:**
- All panels with HelpButton
- Onboarding workflow
- User assistance

---

## Other Services

### OperationQueueService

**Location:** `src/VoiceStudio.App/Services/OperationQueueService.cs`  
**Purpose:** Queues operations when backend is unavailable.

**Key Features:**
- Operation queuing
- Automatic processing when backend is available
- Queue persistence

**Usage Example:**

```csharp
// Get the service
var queueService = ServiceProvider.GetOperationQueueService();

// Queue operation
await queueService.QueueOperationAsync(operation);

// Process queue
await queueService.ProcessQueueAsync();
```

---

### GracefulDegradationService

**Location:** `src/VoiceStudio.App/Services/GracefulDegradationService.cs`  
**Purpose:** Manages graceful degradation when backend is unavailable.

**Key Features:**
- Degraded mode management
- Feature disabling
- User notifications

**Usage Example:**

```csharp
// Get the service
var degradationService = ServiceProvider.GetGracefulDegradationService();

// Enter degraded mode
degradationService.EnterDegradedMode("Backend unavailable", "VoiceSynthesis", "Training");

// Exit degraded mode
degradationService.ExitDegradedMode();

// Check if feature is available
var isAvailable = degradationService.IsFeatureAvailable("VoiceSynthesis");
```

---

### SettingsService

**Location:** `src/VoiceStudio.App/Services/SettingsService.cs`  
**Interface:** `src/VoiceStudio.App/Services/ISettingsService.cs`  
**Purpose:** Manages application settings.

**Key Features:**
- Settings storage
- Settings retrieval
- Settings synchronization

**Usage Example:**

```csharp
// Get the service
var settingsService = ServiceProvider.GetSettingsService();

// Get setting
var value = await settingsService.GetSettingAsync<string>("key");

// Set setting
await settingsService.SetSettingAsync("key", value);

// Get all settings
var allSettings = await settingsService.GetAllSettingsAsync();
```

---

### UpdateService

**Location:** `src/VoiceStudio.App/Services/UpdateService.cs`  
**Interface:** `src/VoiceStudio.App/Services/IUpdateService.cs`  
**Purpose:** Manages application updates.

**Key Features:**
- Update checking
- Update downloading
- Update installation

**Usage Example:**

```csharp
// Get the service
var updateService = ServiceProvider.GetUpdateService();

// Check for updates
await updateService.CheckForUpdatesAsync();

// Download update
await updateService.DownloadUpdateAsync(version);

// Install update
await updateService.InstallUpdateAsync(updatePath);
```

---

### CommandPaletteService

**Location:** `src/VoiceStudio.App/Services/CommandPaletteService.cs`  
**Purpose:** Manages command palette functionality.

**Key Features:**
- Command registration
- Command execution
- Command search

**Usage Example:**

```csharp
// Get the service
var commandPaletteService = ServiceProvider.GetCommandPaletteService();

// Register command
commandPaletteService.RegisterCommand("command-id", "Command Name", () => {
    // Execute command
});

// Execute command
commandPaletteService.ExecuteCommand("command-id");
```

---

### KeyboardShortcutService

**Location:** `src/VoiceStudio.App/Services/KeyboardShortcutService.cs`  
**Purpose:** Manages keyboard shortcuts.

**Key Features:**
- Shortcut registration
- Shortcut execution
- Shortcut conflicts detection

**Usage Example:**

```csharp
// Get the service
var shortcutService = ServiceProvider.GetKeyboardShortcutService();

// Register shortcut
shortcutService.RegisterShortcut("Ctrl+S", () => {
    // Execute action
});

// Execute shortcut
shortcutService.ExecuteShortcut("Ctrl+S");
```

---

### OnboardingService

**Location:** `src/VoiceStudio.App/Services/OnboardingService.cs`  
**Purpose:** Manages user onboarding flow.

**Key Features:**
- Onboarding step management
- Progress tracking
- Completion tracking

**Usage Example:**

```csharp
// Get the service
var onboardingService = ServiceProvider.GetOnboardingService();

// Start onboarding
await onboardingService.StartOnboardingAsync();

// Complete step
await onboardingService.CompleteStepAsync(stepId);

// Check if onboarding is complete
var isComplete = await onboardingService.IsOnboardingCompleteAsync();
```

---

### PluginManager

**Location:** `src/VoiceStudio.App/Services/PluginManager.cs`  
**Purpose:** Manages loading and registration of VoiceStudio plugins.

**Key Features:**
- Plugin discovery and loading
- Plugin registration
- Panel registration from plugins
- Plugin lifecycle management

**Usage Example:**

```csharp
// Get the service
var pluginManager = ServiceProvider.GetPluginManager();

// Load all plugins
await pluginManager.LoadPluginsAsync();

// Get all loaded plugins
var plugins = pluginManager.Plugins;

// Get plugin by name
var plugin = pluginManager.GetPlugin("MyPlugin");

// Unload plugins
pluginManager.UnloadPlugins();
```

**Integration Points:**
- Application startup
- Panel registration
- Plugin system

---

### PanelRegistry

**Location:** `src/VoiceStudio.Core/Panels/PanelRegistry.cs`  
**Purpose:** Central registry for all available panels in the application.

**Key Features:**
- Panel registration
- Panel discovery
- Panel metadata management

**Usage Example:**

```csharp
// Get the service
var panelRegistry = ServiceProvider.GetPanelRegistry();

// Get all registered panels
var panels = panelRegistry.GetAllPanels();

// Get panel by ID
var panel = panelRegistry.GetPanel("ProfilesPanel");

// Register a panel
panelRegistry.RegisterPanel(panelDescriptor);
```

**Integration Points:**
- MainWindow (panel navigation)
- CommandPaletteService
- Plugin system

---

### WindowHostService

**Location:** `src/VoiceStudio.App/Services/WindowHostService.cs`  
**Purpose:** Manages floating windows that host panels.

**Key Features:**
- Floating window creation
- Window lifecycle management
- Panel content hosting

**Usage Example:**

```csharp
// Create service instance (not in ServiceProvider)
var windowHostService = new WindowHostService();

// Create floating window for a panel
var window = windowHostService.CreateFloatingWindow(
    panelId: "ProfilesPanel",
    title: "Voice Profiles",
    content: panelContent,
    width: 800,
    height: 600
);

// Check if panel is floating
var isFloating = windowHostService.IsFloating("ProfilesPanel");

// Close floating window
windowHostService.CloseFloatingWindow("ProfilesPanel");

// Get all floating windows
var floatingWindows = windowHostService.GetFloatingWindows();
```

**Integration Points:**
- Panel docking system
- Multi-window workflows

---

### ThemeManager

**Location:** `src/VoiceStudio.App/Services/ThemeManager.cs`  
**Purpose:** Manages application themes and layout density.

**Key Features:**
- Theme switching
- Layout density management
- Theme persistence

**Usage Example:**

```csharp
// Create service instance (not in ServiceProvider)
var themeManager = new ThemeManager();

// Apply theme
themeManager.ApplyTheme("SciFi");

// Apply layout density
themeManager.ApplyLayoutDensity("Compact");

// Get current theme
var currentTheme = themeManager.CurrentTheme;
var density = themeManager.Density;
```

**Integration Points:**
- SettingsView
- Application initialization
- User preferences

---

### ReferenceAudioQualityAnalyzer

**Location:** `src/VoiceStudio.App/Services/ReferenceAudioQualityAnalyzer.cs`  
**Purpose:** Analyzes reference audio quality before voice cloning. Implements IDEA 41: Reference Audio Quality Analyzer and Recommendations.

**Key Features:**
- Comprehensive quality analysis
- Quality issue detection
- Enhancement suggestions
- Suitability assessment

**Usage Example:**

```csharp
// Create service instance (requires BackendClient)
var backendClient = ServiceProvider.GetBackendClient();
var analyzer = new ReferenceAudioQualityAnalyzer(backendClient);

// Analyze reference audio
var result = await analyzer.AnalyzeAsync(audioStream, cancellationToken);

// Check quality score
var qualityScore = result.QualityScore; // 0-100

// Check if suitable for cloning
var isSuitable = result.IsSuitableForCloning;

// Get issues
var issues = result.Issues;

// Get suggestions
var suggestions = result.Suggestions;

// Get derived scores
var clarity = result.ClarityScore;
var noise = result.NoiseLevel;
var consistency = result.ConsistencyScore;
```

**Integration Points:**
- ProfilesView (reference audio upload)
- Voice profile creation workflow
- Quality optimization

---

### PanelSettingsStore

**Location:** `src/VoiceStudio.App/Services/PanelSettingsStore.cs`  
**Purpose:** Centralized store for panel-specific settings.

**Key Features:**
- Panel settings persistence
- Settings retrieval
- Settings application

**Usage Example:**

```csharp
// Create service instance (not in ServiceProvider)
var settingsStore = new PanelSettingsStore();

// Save panel settings
var settings = new MyPanelSettings { /* ... */ };
settingsStore.SaveSettings("ProfilesPanel", settings);

// Get panel settings
var loadedSettings = settingsStore.GetSettings<MyPanelSettings>("ProfilesPanel");

// Apply settings to panel
if (panel is IPanelConfigurable configurable)
{
    var panelSettings = settingsStore.GetPanelSettings(configurable, "ProfilesPanel");
    if (panelSettings != null)
    {
        settingsStore.ApplyPanelSettings(configurable, "ProfilesPanel", panelSettings);
    }
}
```

**Integration Points:**
- PanelStateService
- Panel initialization
- Settings persistence

---

### CommandRegistry

**Location:** `src/VoiceStudio.App/Services/CommandRegistry.cs`  
**Interface:** `src/VoiceStudio.Core/Services/ICommandRegistry.cs`  
**Purpose:** Registry for application commands.

**Key Features:**
- Command registration
- Command execution
- Command discovery

**Usage Example:**

```csharp
// Create service instance (not in ServiceProvider)
var commandRegistry = new CommandRegistry();

// Register command
commandRegistry.RegisterCommand(
    commandId: "save-project",
    title: "Save Project",
    description: "Saves the current project",
    category: "File",
    action: () => { /* Save project */ },
    shortcut: "Ctrl+S"
);

// Execute command
commandRegistry.ExecuteCommand("save-project");

// Get all commands
var allCommands = commandRegistry.GetAllCommands();
```

**Integration Points:**
- CommandPaletteService
- Keyboard shortcuts
- Menu system

---

## Service Usage Patterns

### Pattern 1: Service Injection in ViewModel

```csharp
public class MyViewModel : BaseViewModel
{
    private readonly MultiSelectService _multiSelectService;
    private readonly UndoRedoService _undoRedoService;

    public MyViewModel()
    {
        _multiSelectService = ServiceProvider.GetMultiSelectService();
        _undoRedoService = ServiceProvider.GetUndoRedoService();
    }
}
```

### Pattern 2: Optional Service Usage

```csharp
var service = ServiceProvider.TryGetMultiSelectService();
if (service != null)
{
    // Use service
}
```

### Pattern 3: Service Events

```csharp
var service = ServiceProvider.GetMultiSelectService();
service.SelectionChanged += (sender, e) => {
    // Handle selection change
};
```

### Pattern 4: Service in Code-Behind

```csharp
public partial class MyView : UserControl
{
    private readonly ContextMenuService _contextMenuService;

    public MyView()
    {
        InitializeComponent();
        _contextMenuService = ServiceProvider.GetContextMenuService();
    }

    private void Element_RightTapped(object sender, RightTappedRoutedEventArgs e)
    {
        var menu = _contextMenuService.CreateContextMenu("profile", profileData);
        menu.ShowAt(sender as UIElement, e.GetPosition(sender as UIElement));
    }
}
```

---

## Best Practices

1. **Always use ServiceProvider:** Don't create service instances directly
2. **Handle null services:** Use `TryGet*` methods for optional services
3. **Dispose services:** Services that implement `IDisposable` should be disposed
4. **Subscribe to events:** Use service events for reactive updates
5. **Error handling:** Always handle errors when using services
6. **Service initialization:** Services are auto-initialized, but you can manually initialize if needed

---

## Service Dependencies

Some services depend on others:

- `ErrorDialogService` depends on `ErrorLoggingService`
- `PanelStateService` depends on `SettingsService`
- `RealTimeQualityService` depends on `BackendClient`
- `StatePersistenceService` is standalone
- `OperationQueueService` is standalone

---

## Troubleshooting

### Service Not Initialized

**Error:** `InvalidOperationException: Service not initialized`

**Solution:** Ensure `ServiceProvider.Initialize()` is called, or access the service through a getter which auto-initializes.

### Service Returns Null

**Error:** Service getter returns null

**Solution:** Use `TryGet*` methods for optional services, or check service initialization.

### Service Events Not Firing

**Error:** Service events not being raised

**Solution:** Ensure you're subscribing to events before the service raises them, and that the service is properly initialized.

---

**Last Updated:** 2025-01-28  
**Version:** 1.0

