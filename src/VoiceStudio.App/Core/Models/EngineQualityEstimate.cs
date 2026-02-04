namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Quality estimate for an engine.
  /// </summary>
  public class EngineQualityEstimate
  {
    /// <summary>
    /// Estimated MOS score (1.0-5.0).
    /// </summary>
    public double? MosScore { get; set; }

    /// <summary>
    /// Estimated similarity (0.0-1.0).
    /// </summary>
    public double? Similarity { get; set; }

    /// <summary>
    /// Estimated naturalness (0.0-1.0).
    /// </summary>
    public double? Naturalness { get; set; }

    /// <summary>
    /// Speed estimate (e.g., "fast", "medium", "slow").
    /// </summary>
    public string? SpeedEstimate { get; set; }
  }
}