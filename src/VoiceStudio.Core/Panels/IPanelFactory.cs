using System;

namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Factory for creating panel content (View + ViewModel) for a given panel ID.
    /// Use with PanelRegistry so MainWindow and hosts can create panels via DI.
    /// </summary>
    public interface IPanelFactory
    {
        /// <summary>
        /// Create the content (View with ViewModel set as DataContext) for the given panel ID.
        /// Returns null if the panel is not registered or creation fails.
        /// </summary>
        object? CreatePanelContent(string panelId);

        /// <summary>
        /// Create the content for the given panel descriptor.
        /// Returns null if creation fails.
        /// </summary>
        object? CreatePanelContent(PanelDescriptor descriptor);
    }
}
