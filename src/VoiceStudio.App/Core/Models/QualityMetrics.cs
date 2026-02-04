using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Detailed quality metrics for voice cloning evaluation.
  /// </summary>
  public class QualityMetrics
  {
    /// <summary>
    /// Mean Opinion Score (1.0-5.0). Higher is better.
    /// </summary>
    public double? MosScore { get; set; }

    /// <summary>
    /// Voice similarity to reference (0.0-1.0). Higher is better.
    /// </summary>
    public double? Similarity { get; set; }

    /// <summary>
    /// Naturalness score (0.0-1.0). Higher is better.
    /// </summary>
    public double? Naturalness { get; set; }

    /// <summary>
    /// Signal-to-noise ratio in dB. Higher is better.
    /// </summary>
    public double? SnrDb { get; set; }

    /// <summary>
    /// Artifact score (0.0-1.0). Lower is better.
    /// </summary>
    public double? ArtifactScore { get; set; }

    /// <summary>
    /// Whether audio clicks/pops were detected.
    /// </summary>
    public bool? HasClicks { get; set; }

    /// <summary>
    /// Whether distortion/clipping was detected.
    /// </summary>
    public bool? HasDistortion { get; set; }

    /// <summary>
    /// Voice profile matching results (dictionary of matching scores).
    /// </summary>
    public Dictionary<string, object>? VoiceProfileMatch { get; set; }
  }
}