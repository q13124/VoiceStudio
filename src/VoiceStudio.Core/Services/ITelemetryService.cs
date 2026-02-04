using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Services
{
  /// <summary>
  /// Application telemetry and metrics service.
  /// Supports SLO monitoring (TASK-0007) and general application diagnostics.
  /// </summary>
  /// <remarks>
  /// Implementation: TelemetryService in VoiceStudio.App/Services/.
  /// Integrates with SLO Dashboard, Diagnostics panel, and error tracking.
  /// </remarks>
  public interface ITelemetryService
  {
    /// <summary>
    /// Track a named event with optional properties.
    /// </summary>
    /// <param name="eventName">Event identifier (e.g., "synthesis_completed")</param>
    /// <param name="properties">Event metadata (duration, engine, etc.)</param>
    void TrackEvent(string eventName, IDictionary<string, object>? properties = null);

    /// <summary>
    /// Record a metric value with optional dimensions.
    /// Used for SLO tracking (latency, quality scores, error rates).
    /// </summary>
    /// <param name="metricName">Metric identifier (e.g., "synthesis_latency_ms")</param>
    /// <param name="value">Metric value</param>
    /// <param name="dimensions">Dimensions for metric aggregation (engine, quality_mode)</param>
    void TrackMetric(string metricName, double value, IDictionary<string, string>? dimensions = null);

    /// <summary>
    /// Track an exception for error monitoring.
    /// </summary>
    void TrackException(Exception exception, IDictionary<string, string>? properties = null);

    /// <summary>
    /// Start tracking a timed operation.
    /// Returns IDisposable that tracks duration on disposal.
    /// </summary>
    /// <param name="operationName">Operation identifier</param>
    /// <returns>Tracker that records duration when disposed</returns>
    IDisposable TrackOperation(string operationName);

    /// <summary>
    /// Flush pending telemetry data (for shutdown scenarios).
    /// </summary>
    void Flush();

    /// <summary>
    /// Apply diagnostics settings (telemetry level, error reporting, etc.).
    /// </summary>
    /// <param name="settings">DiagnosticsSettings object</param>
    void ApplyDiagnosticsSettings(object settings);
  }
}