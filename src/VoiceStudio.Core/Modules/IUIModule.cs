using System.Collections.Generic;
using System.Linq;
using Microsoft.Extensions.DependencyInjection;
using VoiceStudio.Core.Commands;

namespace VoiceStudio.Core.Modules
{
    /// <summary>
    /// Interface for VoiceStudio UI modules.
    /// Unlike IPlugin (external), IUIModule is for internal feature modules
    /// that split the UI into multiple assemblies for better maintainability
    /// and to avoid WinUI XAML compiler limits.
    /// </summary>
    public interface IUIModule
    {
        /// <summary>
        /// Module identifier (e.g., "Voice", "Media", "Analysis", "Workflow").
        /// Must be unique across all modules.
        /// </summary>
        string ModuleId { get; }

        /// <summary>
        /// Human-readable module name for display purposes.
        /// </summary>
        string DisplayName { get; }

        /// <summary>
        /// Module version (should match assembly version).
        /// </summary>
        string Version { get; }

        /// <summary>
        /// Priority for module initialization order.
        /// Lower values initialize first. Default is 100.
        /// </summary>
        int Priority => 100;

        /// <summary>
        /// Register services, ViewModels, and other dependencies with the DI container.
        /// Called during app startup before any modules are initialized.
        /// </summary>
        /// <param name="services">The service collection to register with.</param>
        void RegisterServices(IServiceCollection services);

        /// <summary>
        /// Called after all modules have registered their services and the DI container is built.
        /// Use for initialization that depends on other modules or services.
        /// Panel registration should happen here via IPanelRegistry.
        /// </summary>
        /// <param name="provider">The built service provider.</param>
        void OnInitialized(IServiceProvider provider);

        /// <summary>
        /// Called on application shutdown for cleanup.
        /// Modules are shut down in reverse initialization order.
        /// </summary>
        void OnShutdown();

        /// <summary>
        /// Returns resource dictionary URIs to be merged into the application resources.
        /// URIs should be in ms-appx format (e.g., "ms-appx:///ModuleName/Themes/Styles.xaml").
        /// Called after OnInitialized.
        /// </summary>
        /// <returns>Collection of resource dictionary URIs, or empty if none.</returns>
        IEnumerable<string> GetResourceDictionaryUris() => Enumerable.Empty<string>();

        /// <summary>
        /// Returns commands to be registered with the command palette and keyboard shortcut system.
        /// Called after OnInitialized.
        /// </summary>
        /// <returns>Collection of command descriptors, or empty if none.</returns>
        IEnumerable<CommandDescriptor> GetCommands() => Enumerable.Empty<CommandDescriptor>();
    }
}
