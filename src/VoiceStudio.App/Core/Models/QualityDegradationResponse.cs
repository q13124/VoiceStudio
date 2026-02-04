using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Response for quality degradation detection (IDEA 56).
  /// </summary>
  public class QualityDegradationResponse
  {
    /// <summary>
    /// Voice profile ID.
    /// </summary>
    public string ProfileId { get; set; } = string.Empty;

    /// <summary>
    /// Whether degradation was detected.
    /// </summary>
    public bool HasDegradation { get; set; }

    /// <summary>
    /// List of degradation alerts.
    /// </summary>
    public List<QualityDegradationAlert> Alerts { get; set; } = new();

    /// <summary>
    /// Time window analyzed in days.
    /// </summary>
    public int TimeWindowDays { get; set; }
  }
}