# Frontend Plugin API Reference

This document provides complete documentation of the VoiceStudio frontend (C#) plugin API for creating UI plugins and full-stack plugins.

---

## Core Plugin Interface

### IPlugin

The main interface that all C# frontend plugins must implement.

**Location**: `src/VoiceStudio.App/Core/Plugins/IPlugin.cs`

#### Properties

##### Name

```csharp
string Name { get; }
```

Gets the unique plugin identifier (must match `name` in manifest.json).

**Example**:
```csharp
public string Name => "my_plugin";
```

##### Version

```csharp
string Version { get; }
```

Gets the plugin version matching manifest.json.

**Example**:
```csharp
public string Version => "1.0.0";
```

##### Author

```csharp
string Author { get; }
```

Gets the plugin author name from manifest.json.

##### Description

```csharp
string Description { get; }
```

Gets the plugin description from manifest.json.

##### IsInitialized

```csharp
bool IsInitialized { get; }
```

Returns whether the plugin has been initialized.

#### Methods

##### RegisterPanels

```csharp
void RegisterPanels(IPanelRegistry registry);
```

Called to register UI panels provided by the plugin.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `registry` | `IPanelRegistry` | Registry to register panels with |

**Called**: Early in plugin lifecycle, before `Initialize`

**Example**:

```csharp
public void RegisterPanels(IPanelRegistry registry)
{
    // Register a settings panel
    registry.Register(new PanelDescriptor
    {
        PanelId = "my_plugin_settings",
        DisplayName = "My Plugin Settings",
        ViewType = typeof(SettingsPanel),
        Region = PanelRegion.Right
    });
    
    // Register a main panel
    registry.Register(new PanelDescriptor
    {
        PanelId = "my_plugin_main",
        DisplayName = "My Plugin",
        ViewType = typeof(MainPanel),
        Region = PanelRegion.Center
    });
}
```

##### Initialize

```csharp
void Initialize(IBackendClient backend);
```

Called after panel registration to initialize the plugin.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `backend` | `IBackendClient` | Client for calling backend API |

**Called**: After `RegisterPanels`, when plugin is ready to initialize

**Example**:

```csharp
public void Initialize(IBackendClient backend)
{
    _backend = backend;
    
    // Initialize UI components
    // Connect to backend services
    // Load configuration
    
    _isInitialized = true;
}
```

##### Cleanup

```csharp
void Cleanup();
```

Called when VoiceStudio is shutting down.

**Example**:

```csharp
public void Cleanup()
{
    // Save state
    // Disconnect from backend
    // Release resources
    // Stop timers
    
    _isInitialized = false;
}
```

---

## Panel Interfaces

### IPanelView

Base interface for all panel views.

**Location**: `src/VoiceStudio.Core/Panels/IPanelView.cs`

#### Properties

##### PanelId

```csharp
string PanelId { get; }
```

Gets the unique panel identifier (e.g., "my_plugin_settings").

##### DisplayName

```csharp
string DisplayName { get; }
```

Gets the human-readable panel name shown in UI.

##### Region

```csharp
PanelRegion Region { get; }
```

Gets where in the UI the panel should be displayed.

---

### IPanelLifecycle

Interface for panels that need lifecycle callbacks.

**Location**: `src/VoiceStudio.Core/Panels/IPanelView.cs`

#### Methods

##### OnActivatedAsync

```csharp
Task OnActivatedAsync(CancellationToken cancellationToken = default);
```

Called when the panel becomes active/visible.

**Use for**:
- Starting timers or polling
- Subscribing to events
- Refreshing data
- Enabling UI interactions

**Example**:

```csharp
public async Task OnActivatedAsync(CancellationToken cancellationToken = default)
{
    // Load fresh data
    await RefreshAsync(cancellationToken);
    
    // Start update timer
    _updateTimer?.Dispose();
    _updateTimer = new Timer(_ => UpdateUI(), null, 0, 1000);
}
```

##### OnDeactivatedAsync

```csharp
Task OnDeactivatedAsync(CancellationToken cancellationToken = default);
```

Called when the panel becomes inactive/hidden.

**Use for**:
- Stopping timers
- Unsubscribing from events
- Saving state
- Cleaning up resources

**Example**:

```csharp
public async Task OnDeactivatedAsync(CancellationToken cancellationToken = default)
{
    // Stop update timer
    _updateTimer?.Dispose();
    _updateTimer = null;
    
    // Save current state
    await SaveStateAsync();
}
```

##### RefreshAsync

```csharp
Task RefreshAsync(CancellationToken cancellationToken = default);
```

Called to refresh the panel's data and UI.

**Example**:

```csharp
public async Task RefreshAsync(CancellationToken cancellationToken = default)
{
    try
    {
        var data = await _backend.GetAsync("/api/plugin/my_plugin/data");
        UpdateUIWithData(data);
    }
    catch (Exception ex)
    {
        LogError(ex);
    }
}
```

---

### ILifecyclePanelView

Combined interface implementing both `IPanelView` and `IPanelLifecycle`.

Use this for panels that need full lifecycle support:

```csharp
public class MyPanel : UserControl, ILifecyclePanelView
{
    public string PanelId => "my_plugin_panel";
    public string DisplayName => "My Plugin";
    public PanelRegion Region => PanelRegion.Center;
    
    public async Task OnActivatedAsync(CancellationToken ct) { ... }
    public async Task OnDeactivatedAsync(CancellationToken ct) { ... }
    public async Task RefreshAsync(CancellationToken ct) { ... }
}
```

---

## Panel Registry

### IPanelRegistry

Interface for registering and managing UI panels.

**Location**: `src/VoiceStudio.Core/Services/IPanelRegistry.cs`

#### Methods

##### Register (via Descriptor)

```csharp
void Register(PanelDescriptor descriptor);
```

Register a panel using a descriptor.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `descriptor` | `PanelDescriptor` | Panel descriptor |

**Example**:

```csharp
registry.Register(new PanelDescriptor
{
    PanelId = "my_plugin",
    DisplayName = "My Plugin",
    ViewType = typeof(MyPanel),
    Region = PanelRegion.Center
});
```

##### RegisterPanel

```csharp
void RegisterPanel(IPanelView panel);
```

Register a panel view directly.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `panel` | `IPanelView` | Panel implementing IPanelView |

##### CreatePanel

```csharp
object CreatePanel(string panelId);
```

Create an instance of a registered panel.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `panelId` | `string` | The panel ID to create |

**Returns**: New panel instance (usually UserControl)

**Throws**: `KeyNotFoundException` if panel not registered

##### IsRegistered

```csharp
bool IsRegistered(string panelId);
```

Check if a panel is registered.

##### TryGetDescriptor

```csharp
bool TryGetDescriptor(string panelId, out PanelDescriptor descriptor);
```

Try to get a panel's descriptor.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `panelId` | `string` | The panel ID |
| `descriptor` | `PanelDescriptor` | Output descriptor if found |

**Returns**: True if descriptor found

##### GetPanelsForRegion

```csharp
IEnumerable<IPanelView> GetPanelsForRegion(PanelRegion region);
```

Get all panels for a specific region.

##### GetDefaultPanel

```csharp
IPanelView GetDefaultPanel(PanelRegion region);
```

Get the default panel for a region (usually the first registered).

---

## Panel Region

Enum specifying where panels appear in the UI.

**Location**: `src/VoiceStudio.Core/Panels/`

```csharp
public enum PanelRegion
{
    Left,       // Left sidebar
    Center,     // Main center area
    Right,      // Right sidebar
    Bottom,     // Bottom docking area
    Floating    // Floating window
}
```

---

## Panel Descriptor

Data class describing a panel.

**Location**: `src/VoiceStudio.Core/Panels/`

```csharp
public class PanelDescriptor
{
    public string PanelId { get; set; }              // Unique ID
    public string DisplayName { get; set; }          // Display name
    public Type ViewType { get; set; }               // Panel type (UserControl)
    public PanelRegion Region { get; set; }          // Where to display
    public int Priority { get; set; } = 0;           // Display priority
    public bool IsVisible { get; set; } = true;      // Initially visible
    public object ViewModelFactory { get; set; }     // Optional VM factory
}
```

---

## Backend Client Interface

### IBackendClient

Interface for calling the backend API from frontend panels.

**Location**: `src/VoiceStudio.App/Core/Services/IBackendClient.cs`

#### Methods

##### GetAsync

```csharp
Task<T?> GetAsync<T>(
    string endpoint,
    CancellationToken cancellationToken = default
) where T : class;
```

Make a GET request to the backend.

**Type Parameters**:

| Name | Description |
|------|-------------|
| `T` | Response type to deserialize to |

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `endpoint` | `string` | API endpoint path |

**Returns**: `Task<T?>` with response data (nullable reference result)

**Example**:

```csharp
var health = await _backend.GetAsync<HealthStatus>(
    "/api/plugin/my_plugin/health",
    CancellationToken.None
);
```

##### PostAsync

```csharp
Task<TResponse> PostAsync<TRequest, TResponse>(
    string endpoint,
    TRequest request,
    CancellationToken cancellationToken = default
);
```

Make a POST request to the backend.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `endpoint` | `string` | API endpoint path |
| `request` | `TRequest` | Request body (serialized to JSON) |

**Returns**: `Task<TResponse>` with response data

**Example**:

```csharp
var result = await _backend.PostAsync<ProcessRequest, ProcessResult>(
    "/api/plugin/my_plugin/process",
    new ProcessRequest { Text = "hello world" },
    CancellationToken.None
);
```

##### PutAsync

```csharp
Task<TResponse> PutAsync<TRequest, TResponse>(
    string endpoint,
    TRequest request,
    CancellationToken cancellationToken = default
);
```

Make a PUT request to the backend.

##### SendRequestAsync (Advanced)

```csharp
Task<TResponse> SendRequestAsync<TRequest, TResponse>(
    string endpoint,
    TRequest request,
    CancellationToken cancellationToken = default
);
```

General-purpose request helper for custom endpoint patterns.

##### Other Backend Methods

`IBackendClient` also exposes domain-specific methods such as profile, project,
audio, export, and workflow operations. For real-time backend updates, use
`IWebSocketService` exposed by `IBackendClient.WebSocketService`.

---

## MVVM Patterns for Plugins

### ViewModel Pattern

Use `INotifyPropertyChanged` for two-way binding:

```csharp
public class MyPanelViewModel : INotifyPropertyChanged
{
    private string _message;
    
    public string Message
    {
        get => _message;
        set
        {
            if (_message != value)
            {
                _message = value;
                OnPropertyChanged(nameof(Message));
            }
        }
    }
    
    public event PropertyChangedEventHandler PropertyChanged;
    
    protected void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

### Panel with ViewModel

```csharp
public partial class MyPanel : UserControl
{
    private MyPanelViewModel _viewModel;
    
    public MyPanel()
    {
        InitializeComponent();
        _viewModel = new MyPanelViewModel();
        DataContext = _viewModel;
    }
}
```

### XAML Binding

```xaml
<TextBlock Text="{Binding Message}" />
<TextBox Text="{Binding Message, UpdateSourceTrigger=PropertyChanged}" />
```

---

## WebSocket Sync Models

For full-stack plugins that coordinate with the backend.

**Location**: `src/VoiceStudio.Core/Plugins/PluginSyncModels.cs`

### PluginState Enum

```csharp
public enum PluginState
{
    Discovered,   // Found but not loaded
    Loading,      // Loading in progress
    Active,       // Ready to use
    Disabled,     // User disabled
    Error,        // Load/runtime error
    Unloading     // Unloading in progress
}
```

### PluginStatus Class

```csharp
public class PluginStatus
{
    public string PluginId { get; set; }
    public PluginState State { get; set; }
    public string Version { get; set; }
    public List<string> Permissions { get; set; }
    public string ErrorMessage { get; set; }
}
```

### PluginCommand Enum

```csharp
public enum PluginCommand
{
    Enable,      // Enable/load plugin
    Disable,     // Disable/unload plugin
    Reload,      // Hot reload
    HealthCheck, // Check plugin health
    Install,     // Install plugin
    Uninstall    // Uninstall plugin
}
```

---

## Plugin Loading Process

### How Plugins Load

1. **Discovery** — `PluginManager` scans `Plugins/` directory for subdirectories
2. **Validation** — Loads and validates `manifest.json` against schema
3. **Assembly Loading** — Loads C# DLL from path in entry_points.frontend
4. **Interface Finding** — Searches assembly for class implementing `IPlugin`
5. **Instantiation** — Creates instance of plugin class
6. **Panel Registration** — Calls `RegisterPanels(registry)`
7. **Initialization** — Calls `Initialize(backend)`
8. **Activation** — Plugin is now active and ready

### Plugin Discovery (Code Reference)

**File**: `src/VoiceStudio.App/Services/PluginManager.cs`

The PluginManager class:
1. Scans `Plugins/` directory
2. For each subdirectory:
   - Loads manifest.json
   - Validates against schema
   - Checks for `entry_points.frontend` DLL
   - Loads assembly via `Assembly.LoadFrom()`
   - Finds class implementing `IPlugin`
   - Calls `RegisterPanels()` and `Initialize()`

---

## Complete Frontend Plugin Example

Here's a complete C# frontend plugin:

```csharp
using System;
using System.Threading.Tasks;
using VoiceStudio.Core.Plugins;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

public class MyPlugin : IPlugin
{
    private IBackendClient _backend;
    private bool _isInitialized;
    
    // IPlugin properties
    public string Name => "my_plugin";
    public string Version => "1.0.0";
    public string Author => "Author Name";
    public string Description => "My plugin description";
    public bool IsInitialized => _isInitialized;
    
    // IPlugin methods
    public void RegisterPanels(IPanelRegistry registry)
    {
        // Register the main panel
        registry.Register(new PanelDescriptor
        {
            PanelId = "my_plugin_main",
            DisplayName = "My Plugin",
            ViewType = typeof(MyPanel),
            Region = PanelRegion.Center,
            Priority = 0,
            IsVisible = true
        });
    }
    
    public void Initialize(IBackendClient backend)
    {
        _backend = backend;
        _isInitialized = true;
    }
    
    public void Cleanup()
    {
        _backend = null;
        _isInitialized = false;
    }
}

public partial class MyPanel : UserControl, ILifecyclePanelView
{
    private MyViewModel _viewModel;
    private IBackendClient _backend;
    
    public string PanelId => "my_plugin_main";
    public string DisplayName => "My Plugin";
    public PanelRegion Region => PanelRegion.Center;
    
    public MyPanel()
    {
        InitializeComponent();
        _viewModel = new MyViewModel();
        DataContext = _viewModel;
    }
    
    public async Task OnActivatedAsync(CancellationToken ct)
    {
        // Refresh data when activated
        await _viewModel.RefreshAsync(_backend, ct);
    }
    
    public async Task OnDeactivatedAsync(CancellationToken ct)
    {
        // Save state when deactivated
        await _viewModel.SaveStateAsync();
    }
    
    public async Task RefreshAsync(CancellationToken ct)
    {
        // Refresh on demand
        await _viewModel.RefreshAsync(_backend, ct);
    }
}

public class MyViewModel : INotifyPropertyChanged
{
    private string _status;
    
    public string Status
    {
        get => _status;
        set
        {
            if (_status != value)
            {
                _status = value;
                OnPropertyChanged(nameof(Status));
            }
        }
    }
    
    public async Task RefreshAsync(IBackendClient backend, CancellationToken ct)
    {
        try
        {
            var health = await backend.GetAsync<HealthStatus>(
                "/api/plugin/my_plugin/health"
            );
            Status = health.Healthy ? "Healthy" : "Unhealthy";
        }
        catch (Exception ex)
        {
            Status = $"Error: {ex.Message}";
        }
    }
    
    public async Task SaveStateAsync()
    {
        // Save state...
    }
    
    public event PropertyChangedEventHandler PropertyChanged;
    
    protected void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, 
            new PropertyChangedEventArgs(propertyName));
    }
}
```

XAML for MyPanel:

```xaml
<UserControl
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Grid Background="White" Padding="16">
        <StackPanel>
            <TextBlock 
                Text="Status:" 
                FontSize="14" 
                FontWeight="Bold"/>
            <TextBlock 
                Text="{Binding Status}" 
                FontSize="12"
                Margin="0,8,0,0"/>
        </StackPanel>
    </Grid>
</UserControl>
```

---

## Best Practices

1. **Implement ILifecyclePanelView** — For proper resource management
2. **Use async/await** — Don't block the UI thread
3. **Handle exceptions** — Catch and log errors gracefully
4. **Update UI on main thread** — Use `Dispatcher.Invoke` if needed
5. **Use MVVM pattern** — Separate logic from UI
6. **Validate backend responses** — Don't trust backend data
7. **Implement cancellation** — Support CancellationToken
8. **Clean up resources** — Dispose timers, listeners, etc.

---

## Reference Links

- [Getting Started Guide](getting-started.md)
- [Backend API Reference](api-reference-backend.md)
- [Best Practices Guide](best-practices.md)
