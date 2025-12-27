using System;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace VoiceStudio.Core.Plugins
{
    /// <summary>
    /// Interface for VoiceStudio plugins.
    /// All plugins must implement this interface.
    /// </summary>
    public interface IPlugin
    {
        /// <summary>
        /// Plugin name (must match manifest.json name).
        /// </summary>
        string Name { get; }
        
        /// <summary>
        /// Plugin version (must match manifest.json version).
        /// </summary>
        string Version { get; }
        
        /// <summary>
        /// Plugin author (from manifest.json).
        /// </summary>
        string Author { get; }
        
        /// <summary>
        /// Plugin description (from manifest.json).
        /// </summary>
        string Description { get; }
        
        /// <summary>
        /// Register UI panels with the panel registry.
        /// Called during plugin initialization.
        /// </summary>
        /// <param name="registry">Panel registry to register panels with</param>
        void RegisterPanels(IPanelRegistry registry);
        
        /// <summary>
        /// Initialize plugin with backend client.
        /// Called after panel registration.
        /// </summary>
        /// <param name="backend">Backend client for API calls</param>
        void Initialize(IBackendClient backend);
        
        /// <summary>
        /// Cleanup plugin resources.
        /// Called on application shutdown.
        /// </summary>
        void Cleanup();
        
        /// <summary>
        /// Check if plugin is initialized.
        /// </summary>
        bool IsInitialized { get; }
    }
}

