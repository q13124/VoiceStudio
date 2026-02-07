// Copyright (c) VoiceStudio. All rights reserved.
// Licensed under the MIT license.

using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace VoiceStudio.App.Helpers;

/// <summary>
/// Provides a file-based key-value settings storage for unpackaged WinUI 3 applications.
/// This is a fallback for <see cref="Windows.Storage.ApplicationData.Current.LocalSettings"/>
/// which is not available in unpackaged desktop apps.
/// </summary>
public static class UnpackagedSettingsHelper
{
    private static readonly string _settingsFilePath;
    private static readonly object _lock = new();
    private static Dictionary<string, object?>? _cachedSettings;

    static UnpackagedSettingsHelper()
    {
        var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        var voiceStudioDir = Path.Combine(appDataPath, "VoiceStudio");
        Directory.CreateDirectory(voiceStudioDir);
        _settingsFilePath = Path.Combine(voiceStudioDir, "appsettings.json");
    }

    /// <summary>
    /// Gets a setting value by key.
    /// </summary>
    /// <typeparam name="T">The type of the setting value.</typeparam>
    /// <param name="key">The setting key.</param>
    /// <param name="defaultValue">Default value if the key doesn't exist.</param>
    /// <returns>The setting value or default.</returns>
    public static T? GetValue<T>(string key, T? defaultValue = default)
    {
        lock (_lock)
        {
            var settings = LoadSettings();
            if (settings.TryGetValue(key, out var value))
            {
                try
                {
                    if (value is JsonElement element)
                    {
                        return JsonSerializer.Deserialize<T>(element.GetRawText());
                    }
                    if (value is T typedValue)
                    {
                        return typedValue;
                    }
                    // Try conversion for simple types
                    return (T?)Convert.ChangeType(value, typeof(T));
                }
                catch
                {
                    return defaultValue;
                }
            }
            return defaultValue;
        }
    }

    /// <summary>
    /// Sets a setting value by key.
    /// </summary>
    /// <typeparam name="T">The type of the setting value.</typeparam>
    /// <param name="key">The setting key.</param>
    /// <param name="value">The value to set.</param>
    public static void SetValue<T>(string key, T value)
    {
        lock (_lock)
        {
            var settings = LoadSettings();
            settings[key] = value;
            SaveSettings(settings);
        }
    }

    /// <summary>
    /// Checks if a setting key exists.
    /// </summary>
    /// <param name="key">The setting key.</param>
    /// <returns>True if the key exists.</returns>
    public static bool ContainsKey(string key)
    {
        lock (_lock)
        {
            var settings = LoadSettings();
            return settings.ContainsKey(key);
        }
    }

    /// <summary>
    /// Removes a setting by key.
    /// </summary>
    /// <param name="key">The setting key.</param>
    /// <returns>True if the key was removed.</returns>
    public static bool Remove(string key)
    {
        lock (_lock)
        {
            var settings = LoadSettings();
            var removed = settings.Remove(key);
            if (removed)
            {
                SaveSettings(settings);
            }
            return removed;
        }
    }

    private static Dictionary<string, object?> LoadSettings()
    {
        if (_cachedSettings != null)
        {
            return _cachedSettings;
        }

        try
        {
            if (File.Exists(_settingsFilePath))
            {
                var json = File.ReadAllText(_settingsFilePath);
                _cachedSettings = JsonSerializer.Deserialize<Dictionary<string, object?>>(json)
                    ?? new Dictionary<string, object?>();
            }
            else
            {
                _cachedSettings = new Dictionary<string, object?>();
            }
        }
        catch
        {
            _cachedSettings = new Dictionary<string, object?>();
        }

        return _cachedSettings;
    }

    private static void SaveSettings(Dictionary<string, object?> settings)
    {
        try
        {
            var json = JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(_settingsFilePath, json);
            _cachedSettings = settings;
        }
        catch
        {
            // Silently fail - settings are non-critical
        }
    }
}
