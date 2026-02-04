using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Request model for storing a quality history entry.
  /// Matches the backend API QualityHistoryRequest structure.
  /// </summary>
  public class QualityHistoryRequest
  {
    /// <summary>
    /// Voice profile ID this entry belongs to.
    /// </summary>
    public string ProfileId { get; set; } = string.Empty;

    /// <summary>
    /// Engine used for this synthesis.
    /// </summary>
    public string Engine { get; set; } = string.Empty;

    /// <summary>
    /// Quality metrics as dictionary (for backend API).
    /// </summary>
    public Dictionary<string, object> Metrics { get; set; } = new();

    /// <summary>
    /// Overall quality score (computed from metrics).
    /// </summary>
    public double QualityScore { get; set; }

    /// <summary>
    /// Text that was synthesized (optional, for reference).
    /// </summary>
    public string? SynthesisText { get; set; }

    /// <summary>
    /// Audio file URL or path (optional, for reference).
    /// </summary>
    public string? AudioUrl { get; set; }

    /// <summary>
    /// Whether quality enhancement was enabled.
    /// </summary>
    public bool EnhancedQuality { get; set; }

    /// <summary>
    /// Additional metadata for this entry.
    /// </summary>
    public Dictionary<string, object>? Metadata { get; set; }
  }
}