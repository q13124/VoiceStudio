# VoiceStudio Plugins

This directory contains user-installed plugins that extend VoiceStudio functionality.

## Plugin Structure

Each plugin should have the following structure:

```
plugins/
  {plugin_name}/
    manifest.json       # Plugin manifest (required)
    plugin.py          # Python plugin implementation (required)
    {PluginName}Plugin.cs  # C# plugin implementation (optional)
    ui/                 # UI components (optional)
      {PanelName}View.xaml
      {PanelName}ViewModel.cs
```

## Plugin Manifest

See `plugins/{plugin_name}/manifest.json` for the manifest schema.

## Creating a Plugin

1. Create a new directory in `plugins/` with your plugin name
2. Create `manifest.json` with plugin metadata
3. Create `plugin.py` implementing the `BasePlugin` class
4. Optionally create C# UI components
5. Test your plugin
6. Document your plugin

## Plugin Loading

Plugins are automatically discovered and loaded at startup:
- Backend plugins: Loaded from `plugins/` directory
- Frontend plugins: Loaded from `src/VoiceStudio.App/Plugins/` directory

## Plugin API

### Python Plugin API

```python
from app.core.plugins_api.base import BasePlugin

class MyPlugin(BasePlugin):
    def register(self, app):
        """Register plugin routes with FastAPI app"""
        @app.post("/api/plugin/myplugin/action")
        async def my_action():
            return {"result": "success"}
```

### C# Plugin API

```csharp
using VoiceStudio.Core.Plugins;

public class MyPlugin : IPlugin
{
    public string Name => "MyPlugin";
    public string Version => "1.0.0";
    
    public void RegisterPanels(IPanelRegistry registry)
    {
        // Register UI panels
    }
    
    public void Initialize(IBackendClient backend)
    {
        // Initialize plugin
    }
}
```

## Example Plugins

See `plugins/example/` for a complete example plugin.

