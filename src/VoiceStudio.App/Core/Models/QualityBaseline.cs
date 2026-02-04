using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Quality baseline for a voice profile (IDEA 56).
  /// </summary>
  public class QualityBaseline
  {
    /// <summary>
    /// Voice profile ID.
    /// </summary>
    public string ProfileId { get; set; } = string.Empty;

    /// <summary>
    /// Dictionary of metric name to average value.
    /// </summary>
    public Dictionary<string, double> BaselineMetrics { get; set; } = new();

    /// <summary>
    /// Average quality score.
    /// </summary>
    public double BaselineQualityScore { get; set; }

    /// <summary>
    /// Number of samples used for baseline calculation.
    /// </summary>
    public int SampleCount { get; set; }

    /// <summary>
    /// Time period used for baseline calculation in days.
    /// </summary>
    public int TimePeriodDays { get; set; }

    /// <summary>
    /// ISO timestamp when baseline was calculated.
    /// </summary>
    public string CalculatedAt { get; set; } = string.Empty;
  }
}