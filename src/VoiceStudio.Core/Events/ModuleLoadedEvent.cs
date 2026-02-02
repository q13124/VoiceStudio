namespace VoiceStudio.Core.Events
{
    /// <summary>
    /// Event raised when a UI module completes initialization.
    /// Useful for modules that need to know when other modules are ready.
    /// </summary>
    public sealed class ModuleLoadedEvent
    {
        /// <summary>
        /// The module identifier that was loaded.
        /// </summary>
        public string ModuleId { get; init; } = string.Empty;

        /// <summary>
        /// The module display name.
        /// </summary>
        public string DisplayName { get; init; } = string.Empty;

        /// <summary>
        /// The module version.
        /// </summary>
        public string Version { get; init; } = string.Empty;
    }
}
