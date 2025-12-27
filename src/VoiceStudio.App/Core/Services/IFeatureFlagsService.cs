using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Service for managing feature flags to enable/disable features at runtime.
    /// </summary>
    public interface IFeatureFlagsService
    {
        /// <summary>
        /// Checks if a feature flag is enabled.
        /// </summary>
        /// <param name="flag">The feature flag name.</param>
        /// <returns>True if the flag is enabled, false otherwise.</returns>
        bool IsEnabled(string flag);

        /// <summary>
        /// Sets a feature flag to enabled or disabled.
        /// </summary>
        /// <param name="flag">The feature flag name.</param>
        /// <param name="enabled">True to enable, false to disable.</param>
        void SetFlag(string flag, bool enabled);

        /// <summary>
        /// Gets all feature flags and their current state.
        /// </summary>
        /// <returns>Dictionary of flag names to enabled state.</returns>
        IReadOnlyDictionary<string, bool> GetAllFlags();

        /// <summary>
        /// Gets the description of a feature flag.
        /// </summary>
        /// <param name="flag">The feature flag name.</param>
        /// <returns>The description, or null if not found.</returns>
        string? GetDescription(string flag);

        /// <summary>
        /// Event raised when a feature flag changes.
        /// </summary>
        event EventHandler<string> FlagChanged;
    }
}
