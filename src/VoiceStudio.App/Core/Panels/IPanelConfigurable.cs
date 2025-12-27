namespace VoiceStudio.Core.Panels
{
    /// <summary>
    /// Interface for panels that have configurable settings.
    /// </summary>
    public interface IPanelConfigurable
    {
        /// <summary>
        /// Gets the settings view model or configuration object for this panel.
        /// </summary>
        object? GetSettings();

        /// <summary>
        /// Applies settings to the panel.
        /// </summary>
        void ApplySettings(object settings);

        /// <summary>
        /// Gets whether this panel has any settings to configure.
        /// </summary>
        bool HasSettings { get; }
    }
}

