# {{DISPLAY_NAME}} Frontend Plugin Template

A minimal VoiceStudio frontend plugin template for C# WinUI 3 development.

## Quick Start

### 1. Rename the Project

This template uses `SamplePlugin` as the example name. Rename it:

1. Rename the folder `SamplePlugin/` to `{{CLASS_NAME}}Plugin/`
2. Rename the folder `SamplePlugin.Tests/` to `{{CLASS_NAME}}Plugin.Tests/`
3. Edit both `.csproj` files and update `<AssemblyName>` and `<RootNamespace>`
4. In all `.cs` files, replace `namespace {{CLASS_NAME}}Plugin;` 

### 2. Update manifest.json

Replace template tokens:

- `{{PLUGIN_NAME}}` → lowercase_identifier (e.g., `my_plugin`)
- `{{DISPLAY_NAME}}` → Human Readable Name (e.g., `My Plugin`)
- `{{VERSION}}` → Version number (e.g., `1.0.0`)
- `{{AUTHOR}}` → Your name
- `{{DESCRIPTION}}` → Plugin description

### 3. Customize the Plugin Class

Edit `Plugin.cs`:

- Update the `Name`, `Version`, `Author`, `Description` properties
- Add your own panels by registering them in `RegisterPanels()`
- Add backend initialization logic in `Initialize()`

### 4. Create Your Panels

Copy `SettingsPanel.xaml` and related files to create additional panels:

```
SamplePlugin/
  Plugin.cs
  SettingsPanel.xaml
  SettingsPanel.xaml.cs
  SettingsPanelViewModel.cs
  MyCustomPanel.xaml          # New panel
  MyCustomPanel.xaml.cs
  MyCustomPanelViewModel.cs
```

Then register it in `Plugin.cs`:

```csharp
public void RegisterPanels(IPanelRegistry registry)
{
    // Register existing panel
    registry.Register(new PanelDescriptor { ... });
    
    // Register new panel
    registry.Register(new PanelDescriptor
    {
        PanelId = "{{PLUGIN_NAME}}_custom",
        DisplayName = "My Custom Panel",
        ViewType = typeof(MyCustomPanel),
        Region = PanelRegion.Center
    });
}
```

## Project Structure

```
{{CLASS_NAME}}Plugin/
  {{CLASS_NAME}}Plugin.csproj    # Plugin project file
  Plugin.cs                      # Main plugin class (implements IPlugin)
  SettingsPanel.xaml             # UI panel XAML
  SettingsPanel.xaml.cs          # Panel code-behind
  SettingsPanelViewModel.cs      # ViewModel for data binding

{{CLASS_NAME}}Plugin.Tests/
  {{CLASS_NAME}}Plugin.Tests.csproj
  PluginTests.cs                 # Unit tests
```

## Building and Testing

### Build

```bash
dotnet build {{CLASS_NAME}}Plugin/{{CLASS_NAME}}Plugin.csproj
```

### Test

```bash
dotnet test {{CLASS_NAME}}Plugin.Tests/{{CLASS_NAME}}Plugin.Tests.csproj
```

## MVVM Pattern

This template uses MVVM (Model-View-ViewModel) for clean separation:

- **View** (`SettingsPanel.xaml`) — UI layout only
- **Code-Behind** (`SettingsPanel.xaml.cs`) — Lifecycle hooks
- **ViewModel** (`SettingsPanelViewModel.cs`) — Logic and data binding

### Example: Two-Way Binding

In XAML:
```xaml
<TextBox Text="{Binding Message, UpdateSourceTrigger=PropertyChanged}" />
```

In ViewModel:
```csharp
private string _message;
public string Message
{
    get => _message;
    set => SetProperty(ref _message, value);  // Notifies UI
}
```

## Panel Lifecycle

Panels can implement `ILifecyclePanelView` to hook into lifecycle events:

```csharp
public class MyPanel : UserControl, ILifecyclePanelView
{
    // Called when panel becomes visible
    public async Task OnActivatedAsync(CancellationToken ct) { }
    
    // Called when panel becomes hidden
    public async Task OnDeactivatedAsync(CancellationToken ct) { }
    
    // Called to refresh on demand
    public async Task RefreshAsync(CancellationToken ct) { }
}
```

## Calling Backend API

Use `IBackendClient` to call your backend plugin:

```csharp
public async Task LoadDataAsync()
{
    var data = await _backend.GetAsync<MyData>(
        "/api/plugin/{{PLUGIN_NAME}}/data"
    );
    
    UpdateUI(data);
}
```

## Resources

- [Getting Started Guide](../../../docs/plugins/getting-started.md)
- [Frontend API Reference](../../../docs/plugins/api-reference-frontend.md)
- [Best Practices Guide](../../../docs/plugins/best-practices.md)

## License

MIT (update in manifest.json if different)
