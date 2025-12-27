using System;
using Windows.ApplicationModel.Resources;

namespace VoiceStudio.App.Utilities
{
    /// <summary>
    /// Helper utility for loading localized strings from Resources.resw files.
    /// </summary>
    public static class ResourceHelper
    {
        private static ResourceLoader? _resourceLoader;

        private static ResourceLoader ResourceLoader
        {
            get
            {
                if (_resourceLoader == null)
                {
                    _resourceLoader = new ResourceLoader();
                }
                return _resourceLoader;
            }
        }

        /// <summary>
        /// Gets a localized string by key.
        /// </summary>
        /// <param name="key">The resource key (e.g., "Button.Save").</param>
        /// <param name="defaultValue">Optional default value if key not found.</param>
        /// <returns>The localized string, or the default value if not found.</returns>
        public static string GetString(string key, string? defaultValue = null)
        {
            if (string.IsNullOrWhiteSpace(key))
                return defaultValue ?? string.Empty;

            try
            {
                var value = ResourceLoader.GetString(key);
                return string.IsNullOrWhiteSpace(value) ? (defaultValue ?? key) : value;
            }
            catch
            {
                return defaultValue ?? key;
            }
        }

        /// <summary>
        /// Gets a localized string with formatting.
        /// </summary>
        /// <param name="key">The resource key.</param>
        /// <param name="args">Format arguments.</param>
        /// <returns>The formatted localized string.</returns>
        public static string FormatString(string key, params object[] args)
        {
            var format = GetString(key);
            try
            {
                return args.Length > 0 ? string.Format(format, args) : format;
            }
            catch
            {
                return format;
            }
        }

        /// <summary>
        /// Reloads the resource loader (useful after locale change).
        /// </summary>
        public static void Reload()
        {
            _resourceLoader = new ResourceLoader();
        }
    }
}
