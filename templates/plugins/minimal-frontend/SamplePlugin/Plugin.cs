using System;
using System.Collections.Generic;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Plugins;
using VoiceStudio.Core.Services;

namespace {{CLASS_NAME}}Plugin;

/// <summary>
/// {{DISPLAY_NAME}} Frontend Plugin
/// 
/// A minimal template demonstrating:
/// - Plugin interface implementation (IPlugin)
/// - Panel registration
/// - Backend client usage
/// </summary>
public class Plugin : IPlugin
{
    private IBackendClient _backend;
    private bool _isInitialized;

    /// <summary>Unique plugin identifier (matches manifest.json name)</summary>
    public string Name => "{{PLUGIN_NAME}}";

    /// <summary>Plugin version (matches manifest.json version)</summary>
    public string Version => "{{VERSION}}";

    /// <summary>Plugin author</summary>
    public string Author => "{{AUTHOR}}";

    /// <summary>Plugin description</summary>
    public string Description => "{{DESCRIPTION}}";

    /// <summary>Whether the plugin has been initialized</summary>
    public bool IsInitialized => _isInitialized;

    /// <summary>
    /// Register UI panels with the application.
    /// 
    /// Called during plugin discovery to register any UI panels
    /// this plugin provides. Panels are displayed in specified regions.
    /// </summary>
    public void RegisterPanels(IPanelRegistry registry)
    {
        // Register the settings panel
        registry.Register(new PanelDescriptor
        {
            PanelId = "{{PLUGIN_NAME}}_settings",
            DisplayName = "{{DISPLAY_NAME}} Settings",
            ViewType = typeof(SettingsPanel),
            Region = PanelRegion.Right,
            Priority = 0,
            IsVisible = true
        });
    }

    /// <summary>
    /// Initialize the plugin after panel registration.
    /// 
    /// Called after RegisterPanels when the plugin is ready to initialize.
    /// Use this to connect to the backend, load configuration, etc.
    /// </summary>
    public void Initialize(IBackendClient backend)
    {
        _backend = backend;
        _isInitialized = true;
    }

    /// <summary>
    /// Clean up plugin resources on application shutdown.
    /// 
    /// Called when VoiceStudio is closing. Release any resources,
    /// stop timers, close connections, etc.
    /// </summary>
    public void Cleanup()
    {
        _backend = null;
        _isInitialized = false;
    }
}
