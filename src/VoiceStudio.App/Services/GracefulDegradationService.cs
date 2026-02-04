using System;
using System.Collections.Generic;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for managing graceful degradation when errors occur.
  /// </summary>
  public class GracefulDegradationService
  {
    private readonly HashSet<string> _disabledFeatures = new();
    private bool _isDegradedMode;
    private string? _degradationReason;

    public event EventHandler<bool>? DegradedModeChanged;
    public event EventHandler<string>? FeatureDisabled;
    public event EventHandler<string>? FeatureEnabled;

    /// <summary>
    /// Gets whether the application is in degraded mode.
    /// </summary>
    public bool IsDegradedMode => _isDegradedMode;

    /// <summary>
    /// Gets the reason for degradation.
    /// </summary>
    public string? DegradationReason => _degradationReason;

    /// <summary>
    /// Gets the list of disabled features.
    /// </summary>
    public IReadOnlySet<string> DisabledFeatures => _disabledFeatures;

    /// <summary>
    /// Enters degraded mode with a reason.
    /// </summary>
    public void EnterDegradedMode(string reason, params string[] featuresToDisable)
    {
      _isDegradedMode = true;
      _degradationReason = reason;

      foreach (var feature in featuresToDisable)
      {
        _disabledFeatures.Add(feature);
        FeatureDisabled?.Invoke(this, feature);
      }

      DegradedModeChanged?.Invoke(this, true);
    }

    /// <summary>
    /// Exits degraded mode and re-enables all features.
    /// </summary>
    public void ExitDegradedMode()
    {
      var wasDegraded = _isDegradedMode;
      _isDegradedMode = false;
      _degradationReason = null;

      var featuresToReEnable = new List<string>(_disabledFeatures);
      _disabledFeatures.Clear();

      foreach (var feature in featuresToReEnable)
      {
        FeatureEnabled?.Invoke(this, feature);
      }

      if (wasDegraded)
      {
        DegradedModeChanged?.Invoke(this, false);
      }
    }

    /// <summary>
    /// Disables a specific feature.
    /// </summary>
    public void DisableFeature(string feature)
    {
      if (_disabledFeatures.Add(feature))
      {
        FeatureDisabled?.Invoke(this, feature);
      }
    }

    /// <summary>
    /// Enables a specific feature.
    /// </summary>
    public void EnableFeature(string feature)
    {
      if (_disabledFeatures.Remove(feature))
      {
        FeatureEnabled?.Invoke(this, feature);
      }
    }

    /// <summary>
    /// Checks if a feature is enabled.
    /// </summary>
    public bool IsFeatureEnabled(string feature)
    {
      return !_disabledFeatures.Contains(feature);
    }
  }
}