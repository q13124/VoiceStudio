using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Real-time quality metrics during synthesis.
  /// Implements IDEA 42: Real-Time Quality Feedback During Synthesis.
  /// </summary>
  public class RealTimeQualityMetrics
  {
    /// <summary>
    /// Timestamp when metrics were recorded.
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Synthesis progress (0.0-1.0).
    /// </summary>
    public double Progress { get; set; }

    /// <summary>
    /// Current MOS score estimate (1.0-5.0).
    /// </summary>
    public double? MosScore { get; set; }

    /// <summary>
    /// Current similarity score (0.0-1.0).
    /// </summary>
    public double? Similarity { get; set; }

    /// <summary>
    /// Current naturalness score (0.0-1.0).
    /// </summary>
    public double? Naturalness { get; set; }

    /// <summary>
    /// Current SNR in dB.
    /// </summary>
    public double? SnrDb { get; set; }

    /// <summary>
    /// Overall quality score (0.0-1.0).
    /// </summary>
    public double QualityScore { get; set; }

    /// <summary>
    /// Whether quality is above threshold.
    /// </summary>
    public bool IsQualityGood { get; set; }

    /// <summary>
    /// Quality trend (improving, stable, degrading).
    /// </summary>
    public QualityTrend Trend { get; set; } = QualityTrend.Stable;

    /// <summary>
    /// Active quality alerts.
    /// </summary>
    public List<QualityAlert> Alerts { get; set; } = new List<QualityAlert>();
  }

  /// <summary>
  /// Quality trend direction.
  /// </summary>
  public enum QualityTrend
  {
    Improving = 0,
    Stable = 1,
    Degrading = 2
  }

  /// <summary>
  /// Quality alert for issues detected during synthesis.
  /// </summary>
  public class QualityAlert
  {
    /// <summary>
    /// Alert type (e.g., "QualityDrop", "LowMOS", "HighNoise").
    /// </summary>
    public string Type { get; set; } = string.Empty;

    /// <summary>
    /// Alert message.
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Alert severity (Info, Warning, Critical).
    /// </summary>
    public AlertSeverity Severity { get; set; } = AlertSeverity.Warning;

    /// <summary>
    /// Timestamp when alert was triggered.
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Suggested action to resolve the alert.
    /// </summary>
    public string? SuggestedAction { get; set; }
  }

  /// <summary>
  /// Alert severity level.
  /// </summary>
  public enum AlertSeverity
  {
    Info = 0,
    Warning = 1,
    Critical = 2
  }

  /// <summary>
  /// Complete real-time quality feedback data for a synthesis job.
  /// </summary>
  public class RealTimeQualityFeedback
  {
    /// <summary>
    /// Synthesis job ID.
    /// </summary>
    public string SynthesisId { get; set; } = string.Empty;

    /// <summary>
    /// Profile ID used for synthesis.
    /// </summary>
    public string ProfileId { get; set; } = string.Empty;

    /// <summary>
    /// Engine used for synthesis.
    /// </summary>
    public string Engine { get; set; } = string.Empty;

    /// <summary>
    /// Timestamp when synthesis started.
    /// </summary>
    public DateTime StartTime { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Timestamp when synthesis completed (null if in progress).
    /// </summary>
    public DateTime? EndTime { get; set; }

    /// <summary>
    /// Real-time quality metrics history.
    /// </summary>
    public List<RealTimeQualityMetrics> MetricsHistory { get; set; } = new List<RealTimeQualityMetrics>();

    /// <summary>
    /// Current quality metrics.
    /// </summary>
    public RealTimeQualityMetrics? CurrentMetrics { get; set; }

    /// <summary>
    /// Final quality metrics after synthesis completes.
    /// </summary>
    public QualityMetrics? FinalMetrics { get; set; }

    /// <summary>
    /// Quality comparison with previous syntheses.
    /// </summary>
    public QualityComparison? Comparison { get; set; }

    /// <summary>
    /// Quality recommendations.
    /// </summary>
    public List<QualityRecommendation> Recommendations { get; set; } = new List<QualityRecommendation>();

    /// <summary>
    /// Whether synthesis is in progress.
    /// </summary>
    public bool IsInProgress => EndTime == null;
  }

  /// <summary>
  /// Quality comparison with previous syntheses.
  /// </summary>
  public class QualityComparison
  {
    /// <summary>
    /// Average quality score from previous syntheses.
    /// </summary>
    public double? AverageQualityScore { get; set; }

    /// <summary>
    /// Best quality score from previous syntheses.
    /// </summary>
    public double? BestQualityScore { get; set; }

    /// <summary>
    /// Quality difference from average (current - average).
    /// </summary>
    public double? QualityDifference { get; set; }

    /// <summary>
    /// Whether current quality is better than average.
    /// </summary>
    public bool IsBetterThanAverage { get; set; }

    /// <summary>
    /// Comparison message.
    /// </summary>
    public string Message { get; set; } = string.Empty;
  }
}