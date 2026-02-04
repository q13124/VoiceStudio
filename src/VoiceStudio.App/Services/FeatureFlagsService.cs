using System;
using System.Collections.Generic;
using System.Linq;
using Windows.Storage;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Logging;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Implementation of feature flags service using Windows.Storage for persistence.
  /// </summary>
  public class FeatureFlagsService : IFeatureFlagsService
  {
    private const string SettingsKey = "FeatureFlags";
    private readonly Dictionary<string, bool> _flags;
    private readonly Dictionary<string, string> _descriptions;

    public event EventHandler<string>? FlagChanged;

    public FeatureFlagsService()
    {
      _flags = new Dictionary<string, bool>();
      _descriptions = new Dictionary<string, string>();

      // Initialize default flags with descriptions
      InitializeDefaultFlags();

      // Load persisted flags
      LoadFlags();
    }

    private void InitializeDefaultFlags()
    {
      // Core feature flags
      AddFlag("HeavyPanelsEnabled", true, "Enable heavy panels (Quality Dashboard, Spatial Stage, etc.)");
      AddFlag("AnalyticsEnabled", true, "Enable analytics event tracking");
      AddFlag("PerformanceProfilingEnabled", false, "Enable performance profiling and budget monitoring");
      AddFlag("StressTestMode", false, "Enable stress test mode for performance testing");

      // UI feature flags
      AddFlag("RealTimeQualityMetrics", true, "Enable real-time quality metrics display");
      AddFlag("AdvancedEffectsEnabled", true, "Enable advanced audio effects processing");
      AddFlag("MultiEngineEnsemble", true, "Enable multi-engine ensemble synthesis");

      // Backend feature flags
      AddFlag("BackendCachingEnabled", true, "Enable backend response caching");
      AddFlag("WebSocketEnabled", true, "Enable WebSocket real-time communication");

      // Experimental features
      AddFlag("ExperimentalVoiceMorphing", false, "Enable experimental voice morphing features");
      AddFlag("ExperimentalStyleTransfer", false, "Enable experimental style transfer features");
    }

    private void AddFlag(string flag, bool defaultValue, string description)
    {
      _flags[flag] = defaultValue;
      _descriptions[flag] = description;
    }

    public bool IsEnabled(string flag)
    {
      return _flags.TryGetValue(flag, out var value) && value;
    }

    public void SetFlag(string flag, bool enabled)
    {
      if (!_flags.ContainsKey(flag))
      {
        throw new ArgumentException($"Unknown feature flag: {flag}", nameof(flag));
      }

      if (_flags[flag] != enabled)
      {
        _flags[flag] = enabled;
        SaveFlags();
        FlagChanged?.Invoke(this, flag);
      }
    }

    public IReadOnlyDictionary<string, bool> GetAllFlags()
    {
      return _flags;
    }

    public string? GetDescription(string flag)
    {
      return _descriptions.TryGetValue(flag, out var description) ? description : null;
    }

    private void LoadFlags()
    {
      try
      {
        var localSettings = ApplicationData.Current.LocalSettings;
        if (localSettings.Values.TryGetValue(SettingsKey, out var value) && value is ApplicationDataCompositeValue composite)
        {
          foreach (var flag in _flags.Keys.ToList())
          {
            if (composite.TryGetValue(flag, out var flagValue) && flagValue is bool enabled)
            {
              _flags[flag] = enabled;
            }
          }
        }
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "FeatureFlagsService.LoadFlags");
      }
    }

    private void SaveFlags()
    {
      try
      {
        var localSettings = ApplicationData.Current.LocalSettings;
        var composite = new ApplicationDataCompositeValue();

        foreach (var kvp in _flags)
        {
          composite[kvp.Key] = kvp.Value;
        }

        localSettings.Values[SettingsKey] = composite;
      }
      catch (Exception ex)
      {
        ErrorLogger.LogWarning($"Best effort operation failed: {ex.Message}", "FeatureFlagsService.SaveFlags");
      }
    }
  }
}