// ============================================================================
// AnalyticsService.cs - Opt-in analytics tracking service
//
// AI GUIDELINES:
// - This service respects user privacy with opt-in consent
// - Analytics are LOCAL ONLY by default (no remote transmission)
// - User consent is persisted and can be changed at any time
// - All tracking methods respect consent status
// ============================================================================

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Analytics consent status.
  /// </summary>
  public enum AnalyticsConsentStatus
  {
    /// <summary>User has not yet made a choice.</summary>
    NotAsked,
    /// <summary>User has opted in to analytics.</summary>
    OptedIn,
    /// <summary>User has opted out of analytics.</summary>
    OptedOut
  }

  /// <summary>
  /// Service for tracking structured analytics events for key user flows.
  /// Respects user privacy with opt-in consent model.
  /// </summary>
  public interface IAnalyticsService
  {
    /// <summary>
    /// Gets or sets whether analytics collection is enabled.
    /// </summary>
    bool IsEnabled { get; }

    /// <summary>
    /// Gets the current consent status.
    /// </summary>
    AnalyticsConsentStatus ConsentStatus { get; }

    /// <summary>
    /// Sets the user's consent preference.
    /// </summary>
    /// <param name="optIn">True to opt in, false to opt out.</param>
    void SetConsent(bool optIn);

    /// <summary>
    /// Resets consent to NotAsked state (for testing/reset purposes).
    /// </summary>
    void ResetConsent();

    /// <summary>
    /// Tracks an analytics event (only if opted in).
    /// </summary>
    void TrackEvent(string eventName, Dictionary<string, object>? properties = null);

    /// <summary>
    /// Tracks the start of a flow (import, editing, synthesis, export).
    /// </summary>
    string StartFlow(string flowName, Dictionary<string, object>? properties = null);

    /// <summary>
    /// Tracks the completion of a flow.
    /// </summary>
    void EndFlow(string flowId, bool success = true, Dictionary<string, object>? properties = null);

    /// <summary>
    /// Gets recent events for analysis.
    /// </summary>
    IReadOnlyList<AnalyticsEvent> GetRecentEvents(int count = 100);

    /// <summary>
    /// Clears all stored analytics data.
    /// </summary>
    void ClearData();

    /// <summary>
    /// Exports analytics data to a file (for user transparency).
    /// </summary>
    Task<string> ExportDataAsync(string? outputPath = null);

    /// <summary>
    /// Event raised when a new analytics event is tracked.
    /// </summary>
    event EventHandler<AnalyticsEvent>? EventTracked;

    /// <summary>
    /// Event raised when consent status changes.
    /// </summary>
    event EventHandler<AnalyticsConsentStatus>? ConsentChanged;
  }

  /// <summary>
  /// Represents a single analytics event.
  /// </summary>
  public class AnalyticsEvent
  {
    public DateTime Timestamp { get; set; }
    public string EventName { get; set; } = string.Empty;
    public string? FlowId { get; set; }
    public Dictionary<string, object>? Properties { get; set; }
  }

  /// <summary>
  /// Implementation of IAnalyticsService for tracking user flows and events.
  /// Includes opt-in consent management for privacy.
  /// </summary>
  public class AnalyticsService : IAnalyticsService
  {
    private readonly List<AnalyticsEvent> _events = new();
    private readonly Dictionary<string, FlowContext> _activeFlows = new();
    private readonly object _lock = new();
    private const int MaxEvents = 1000;
    private readonly IErrorLoggingService? _errorLoggingService;
    private readonly IFeatureFlagsService? _featureFlagsService;
    private readonly string _consentFilePath;
    private readonly string _analyticsDataPath;
    private AnalyticsConsentStatus _consentStatus = AnalyticsConsentStatus.NotAsked;

    public event EventHandler<AnalyticsEvent>? EventTracked;
    public event EventHandler<AnalyticsConsentStatus>? ConsentChanged;

    /// <summary>
    /// Gets whether analytics collection is currently enabled.
    /// Requires both user consent (OptedIn) AND the AnalyticsEnabled feature flag.
    /// </summary>
    public bool IsEnabled
    {
      get
      {
        // Must have explicit opt-in consent
        if (_consentStatus != AnalyticsConsentStatus.OptedIn)
          return false;

        // Must also have feature flag enabled (if service is available)
        if (_featureFlagsService != null)
          return _featureFlagsService.IsEnabled("AnalyticsEnabled");

        return true;
      }
    }

    /// <summary>
    /// Gets the current consent status.
    /// </summary>
    public AnalyticsConsentStatus ConsentStatus => _consentStatus;

    public AnalyticsService()
    {
      _errorLoggingService = ServiceProvider.GetErrorLoggingService();
      _featureFlagsService = AppServices.TryGetFeatureFlagsService();

      // Setup local storage paths
      var appDataPath = Path.Combine(
          Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
          "VoiceStudio", "Analytics");
      Directory.CreateDirectory(appDataPath);

      _consentFilePath = Path.Combine(appDataPath, "consent.json");
      _analyticsDataPath = Path.Combine(appDataPath, "events.json");

      // Load consent status on startup
      LoadConsentStatus();
    }

    /// <summary>
    /// Sets the user's consent preference.
    /// </summary>
    public void SetConsent(bool optIn)
    {
      var newStatus = optIn ? AnalyticsConsentStatus.OptedIn : AnalyticsConsentStatus.OptedOut;

      if (_consentStatus != newStatus)
      {
        _consentStatus = newStatus;
        SaveConsentStatus();
        ConsentChanged?.Invoke(this, _consentStatus);

        // If user opted out, optionally clear existing data
        if (!optIn)
        {
          // Data is kept locally but not processed; user can clear manually
          _errorLoggingService?.LogInfo("Analytics consent changed to OptedOut", "Analytics");
        }
        else
        {
          _errorLoggingService?.LogInfo("Analytics consent changed to OptedIn", "Analytics");
        }
      }
    }

    /// <summary>
    /// Resets consent to NotAsked state.
    /// </summary>
    public void ResetConsent()
    {
      _consentStatus = AnalyticsConsentStatus.NotAsked;
      SaveConsentStatus();
      ConsentChanged?.Invoke(this, _consentStatus);
    }

    /// <summary>
    /// Clears all stored analytics data.
    /// </summary>
    public void ClearData()
    {
      lock (_lock)
      {
        _events.Clear();
        _activeFlows.Clear();
      }

      // Delete persisted data file
      try
      {
        if (File.Exists(_analyticsDataPath))
        {
          File.Delete(_analyticsDataPath);
        }
        _errorLoggingService?.LogInfo("Analytics data cleared", "Analytics");
      }
      catch (Exception ex)
      {
        _errorLoggingService?.LogWarning($"Failed to delete analytics data: {ex.Message}", "Analytics");
      }
    }

    /// <summary>
    /// Exports analytics data to a file for user transparency.
    /// </summary>
    public async Task<string> ExportDataAsync(string? outputPath = null)
    {
      var exportPath = outputPath ?? Path.Combine(
          Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
          $"VoiceStudio_Analytics_Export_{DateTime.Now:yyyyMMdd_HHmmss}.json");

      var exportData = new
      {
        ExportedAt = DateTime.UtcNow,
        ConsentStatus = _consentStatus.ToString(),
        TotalEvents = _events.Count,
        Events = GetRecentEvents(MaxEvents)
      };

      var json = JsonSerializer.Serialize(exportData, new JsonSerializerOptions { WriteIndented = true });
      await File.WriteAllTextAsync(exportPath, json);

      return exportPath;
    }

    public void TrackEvent(string eventName, Dictionary<string, object>? properties = null)
    {
      // Respect consent - do not track if not opted in
      if (!IsEnabled)
      {
        return;
      }

      var evt = new AnalyticsEvent
      {
        Timestamp = DateTime.UtcNow,
        EventName = eventName,
        Properties = properties
      };

      lock (_lock)
      {
        _events.Add(evt);

        if (_events.Count > MaxEvents)
        {
          _events.RemoveAt(0);
        }
      }

      EventTracked?.Invoke(this, evt);

      _errorLoggingService?.LogInfo($"Analytics: {eventName}", "Analytics", properties);
    }

    public string StartFlow(string flowName, Dictionary<string, object>? properties = null)
    {
      var flowId = Guid.NewGuid().ToString("N");

      // Even if analytics disabled, return a flow ID for API consistency
      if (!IsEnabled)
      {
        return flowId;
      }

      var context = new FlowContext
      {
        FlowId = flowId,
        FlowName = flowName,
        StartTime = DateTime.UtcNow,
        Properties = properties ?? new Dictionary<string, object>()
      };

      lock (_lock)
      {
        _activeFlows[flowId] = context;
      }

      TrackEvent($"Flow.Start.{flowName}", new Dictionary<string, object>
      {
        ["flowId"] = flowId
      }.Merge(properties));

      return flowId;
    }

    public void EndFlow(string flowId, bool success = true, Dictionary<string, object>? properties = null)
    {
      if (!IsEnabled)
      {
        return;
      }

      FlowContext? context;
      lock (_lock)
      {
        if (!_activeFlows.TryGetValue(flowId, out context))
          return;

        _activeFlows.Remove(flowId);
      }

      var duration = (DateTime.UtcNow - context.StartTime).TotalMilliseconds;

      TrackEvent($"Flow.End.{context.FlowName}", new Dictionary<string, object>
      {
        ["flowId"] = flowId,
        ["success"] = success,
        ["durationMs"] = duration
      }.Merge(properties));

      if (!success)
      {
        TrackEvent($"Flow.Failed.{context.FlowName}", new Dictionary<string, object>
        {
          ["flowId"] = flowId,
          ["durationMs"] = duration
        }.Merge(properties));
      }
    }

    public IReadOnlyList<AnalyticsEvent> GetRecentEvents(int count = 100)
    {
      lock (_lock)
      {
        var events = new List<AnalyticsEvent>(_events);
        events.Reverse();
        return events.Take(count).ToList().AsReadOnly();
      }
    }

    private void LoadConsentStatus()
    {
      try
      {
        if (File.Exists(_consentFilePath))
        {
          var json = File.ReadAllText(_consentFilePath);
          var data = JsonSerializer.Deserialize<ConsentData>(json);
          if (data != null && Enum.TryParse<AnalyticsConsentStatus>(data.Status, out var status))
          {
            _consentStatus = status;
          }
        }
      }
      catch (Exception ex)
      {
        _errorLoggingService?.LogWarning($"Failed to load consent status: {ex.Message}", "Analytics");
      }
    }

    private void SaveConsentStatus()
    {
      try
      {
        var data = new ConsentData
        {
          Status = _consentStatus.ToString(),
          UpdatedAt = DateTime.UtcNow
        };
        var json = JsonSerializer.Serialize(data, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(_consentFilePath, json);
      }
      catch (Exception ex)
      {
        _errorLoggingService?.LogWarning($"Failed to save consent status: {ex.Message}", "Analytics");
      }
    }

    private class FlowContext
    {
      public string FlowId { get; set; } = string.Empty;
      public string FlowName { get; set; } = string.Empty;
      public DateTime StartTime { get; set; }
      public Dictionary<string, object> Properties { get; set; } = new();
    }

    private class ConsentData
    {
      public string Status { get; set; } = nameof(AnalyticsConsentStatus.NotAsked);
      public DateTime UpdatedAt { get; set; }
    }
  }

  internal static class DictionaryExtensions
  {
    public static Dictionary<string, object> Merge(this Dictionary<string, object> dict, Dictionary<string, object>? other)
    {
      if (other == null)
        return dict;

      var result = new Dictionary<string, object>(dict);
      foreach (var kvp in other)
      {
        result[kvp.Key] = kvp.Value;
      }
      return result;
    }
  }
}