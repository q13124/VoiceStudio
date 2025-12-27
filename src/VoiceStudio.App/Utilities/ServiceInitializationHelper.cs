using System;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Utilities
{
    /// <summary>
    /// Helper class for initializing services from ServiceProvider.
    /// Reduces code duplication across ViewModels that don't inherit from BaseViewModel.
    /// </summary>
    public static class ServiceInitializationHelper
    {
        /// <summary>
        /// Safely gets a service from ServiceProvider, returning null if not available.
        /// </summary>
        /// <typeparam name="T">The service type</typeparam>
        /// <param name="getter">Function to get the service (may return null)</param>
        /// <returns>The service instance, or null if not available</returns>
        public static T? TryGetService<T>(Func<T?> getter) where T : class
        {
            try
            {
                return getter();
            }
            catch
            {
                // Service may not be initialized yet - that's okay
                return null;
            }
        }
    }
}
