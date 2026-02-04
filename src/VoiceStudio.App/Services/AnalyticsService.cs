using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for tracking structured analytics events for key user flows.
  /// </summary>
  public interface IAnalyticsService
  {
    /// <summary>
    /// Tracks an analytics event.
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
    /// Event raised when a new analytics event is tracked.
    /// </summary>
    event EventHandler<AnalyticsEvent>? EventTracked;
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
  /// </summary>
  public class AnalyticsService : IAnalyticsService
  {
    private readonly List<AnalyticsEvent> _events = new();
    private readonly Dictionary<string, FlowContext> _activeFlows = new();
    private readonly object _lock = new();
    private const int MaxEvents = 1000;
    private readonly IErrorLoggingService? _errorLoggingService;

    public event EventHandler<AnalyticsEvent>? EventTracked;

    public AnalyticsService()
    {
      _errorLoggingService = ServiceProvider.GetErrorLoggingService();
    }

    public void TrackEvent(string eventName, Dictionary<string, object>? properties = null)
    {
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

    private class FlowContext
    {
      public string FlowId { get; set; } = string.Empty;
      public string FlowName { get; set; } = string.Empty;
      public DateTime StartTime { get; set; }
      public Dictionary<string, object> Properties { get; set; } = new();
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