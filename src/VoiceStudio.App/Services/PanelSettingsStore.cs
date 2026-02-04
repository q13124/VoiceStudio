using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using VoiceStudio.Core.Panels;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Centralized store for panel-specific settings.
  /// </summary>
  public class PanelSettingsStore
  {
    private readonly Dictionary<string, object> _settings = new();
    private readonly string _settingsPath;

    public PanelSettingsStore()
    {
      var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
      var settingsDir = Path.Combine(appDataPath, "VoiceStudio", "PanelSettings");
      Directory.CreateDirectory(settingsDir);
      _settingsPath = Path.Combine(settingsDir, "settings.json");
      LoadSettings();
    }

    /// <summary>
    /// Gets settings for a panel.
    /// </summary>
    public T? GetSettings<T>(string panelId) where T : class
    {
      if (_settings.TryGetValue(panelId, out var settingsObj))
      {
        if (settingsObj is JsonElement jsonElement)
        {
          return JsonSerializer.Deserialize<T>(jsonElement.GetRawText());
        }
        return settingsObj as T;
      }
      return null;
    }

    /// <summary>
    /// Saves settings for a panel.
    /// </summary>
    public void SaveSettings<T>(string panelId, T settings) where T : class
    {
      _settings[panelId] = settings;
      SaveSettings();
    }

    /// <summary>
    /// Gets settings for a panel that implements IPanelConfigurable.
    /// </summary>
    public object? GetPanelSettings(IPanelConfigurable panel, string panelId)
    {
      if (panel.HasSettings)
      {
        var stored = GetSettings<object>(panelId);
        if (stored != null)
        {
          return stored;
        }
        return panel.GetSettings();
      }
      return null;
    }

    /// <summary>
    /// Applies settings to a panel.
    /// </summary>
    public void ApplyPanelSettings(IPanelConfigurable panel, string panelId, object settings)
    {
      if (panel.HasSettings)
      {
        panel.ApplySettings(settings);
        SaveSettings(panelId, settings);
      }
    }

    private void LoadSettings()
    {
      if (File.Exists(_settingsPath))
      {
        try
        {
          var json = File.ReadAllText(_settingsPath);
          var dict = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json);
          if (dict != null)
          {
            foreach (var kvp in dict)
            {
              _settings[kvp.Key] = kvp.Value;
            }
          }
        }
        catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "PanelSettingsStore.LoadSettings");
      }
      }
    }

    private void SaveSettings()
    {
      try
      {
        var json = JsonSerializer.Serialize(_settings, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(_settingsPath, json);
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "PanelSettingsStore.SaveSettings");
      }
    }
  }
}