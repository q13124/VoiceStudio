using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Quality consistency report for a project (IDEA 59).
  /// </summary>
  public class QualityConsistencyReport
  {
    /// <summary>
    /// Project identifier.
    /// </summary>
    public string ProjectId { get; set; } = string.Empty;

    /// <summary>
    /// Whether quality data is available.
    /// </summary>
    public bool HasData { get; set; }

    /// <summary>
    /// Time period analyzed in days.
    /// </summary>
    public int TimePeriodDays { get; set; }

    /// <summary>
    /// Total number of quality samples.
    /// </summary>
    public int? TotalSamples { get; set; }

    /// <summary>
    /// Consistency score (0.0-1.0).
    /// </summary>
    public double? ConsistencyScore { get; set; }

    /// <summary>
    /// Whether project meets consistency standards.
    /// </summary>
    public bool? IsConsistent { get; set; }

    /// <summary>
    /// Quality statistics (mean, min, max, std for each metric).
    /// </summary>
    public Dictionary<string, object>? Statistics { get; set; }

    /// <summary>
    /// List of quality standard violations.
    /// </summary>
    public List<QualityViolation>? Violations { get; set; }

    /// <summary>
    /// Quality trends (improving, declining, stable).
    /// </summary>
    public Dictionary<string, string>? Trends { get; set; }

    /// <summary>
    /// Recommendations for maintaining quality.
    /// </summary>
    public List<QualityRecommendation>? Recommendations { get; set; }

    /// <summary>
    /// Optional message.
    /// </summary>
    public string? Message { get; set; }
  }

  /// <summary>
  /// Quality standard violation (IDEA 59).
  /// </summary>
  public class QualityViolation
  {
    /// <summary>
    /// Sample index where violation occurred.
    /// </summary>
    public int SampleIndex { get; set; }

    /// <summary>
    /// List of violated metrics.
    /// </summary>
    public List<ViolatedMetric> ViolatedMetrics { get; set; } = new();
  }

  /// <summary>
  /// Violated metric details (IDEA 59).
  /// </summary>
  public class ViolatedMetric
  {
    /// <summary>
    /// Metric name.
    /// </summary>
    public string Metric { get; set; } = string.Empty;

    /// <summary>
    /// Actual value.
    /// </summary>
    public double Value { get; set; }

    /// <summary>
    /// Required threshold.
    /// </summary>
    public double Threshold { get; set; }
  }

  /// <summary>
  /// Quality recommendation (IDEA 59).
  /// Reuses the shared QualityRecommendation model defined in QualityRecommendation.cs.
  /// </summary>
  /// <summary>
  /// Quality trends response (IDEA 59).
  /// </summary>
  public class QualityTrendsResponse
  {
    /// <summary>
    /// Project identifier.
    /// </summary>
    public string ProjectId { get; set; } = string.Empty;

    /// <summary>
    /// Whether quality data is available.
    /// </summary>
    public bool HasData { get; set; }

    /// <summary>
    /// Time period analyzed in days.
    /// </summary>
    public int TimePeriodDays { get; set; }

    /// <summary>
    /// Daily averages of quality metrics.
    /// </summary>
    public Dictionary<string, Dictionary<string, Dictionary<string, double>>>? DailyAverages { get; set; }

    /// <summary>
    /// Overall trend (improving, declining, stable).
    /// </summary>
    public string? OverallTrend { get; set; }

    /// <summary>
    /// Optional message.
    /// </summary>
    public string? Message { get; set; }
  }

  /// <summary>
  /// All projects consistency response (IDEA 59).
  /// </summary>
  public class AllProjectsConsistencyResponse
  {
    /// <summary>
    /// Total number of projects.
    /// </summary>
    public int TotalProjects { get; set; }

    /// <summary>
    /// Number of projects with quality data.
    /// </summary>
    public int ProjectsWithData { get; set; }

    /// <summary>
    /// Number of consistent projects.
    /// </summary>
    public int ConsistentProjects { get; set; }

    /// <summary>
    /// Overall consistency score (0.0-1.0).
    /// </summary>
    public double OverallConsistency { get; set; }

    /// <summary>
    /// Total number of quality samples.
    /// </summary>
    public int TotalSamples { get; set; }

    /// <summary>
    /// Total number of violations.
    /// </summary>
    public int TotalViolations { get; set; }

    /// <summary>
    /// Consistency reports for each project.
    /// </summary>
    public Dictionary<string, QualityConsistencyReport> Projects { get; set; } = new();
  }

  /// <summary>
  /// Request to set quality standard (IDEA 59).
  /// </summary>
  public class QualityStandardRequest
  {
    /// <summary>
    /// Project identifier.
    /// </summary>
    public string ProjectId { get; set; } = string.Empty;

    /// <summary>
    /// Standard name (professional, high, standard, minimum).
    /// </summary>
    public string StandardName { get; set; } = "professional";
  }
}