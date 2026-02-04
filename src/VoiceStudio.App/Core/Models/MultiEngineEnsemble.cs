using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Request for multi-engine ensemble synthesis (IDEA 55).
  /// </summary>
  public class MultiEngineEnsembleRequest
  {
    public string Text { get; set; } = string.Empty;
    public string ProfileId { get; set; } = string.Empty;
    public List<string> Engines { get; set; } = new(); // ["xtts_v2", "chatterbox", "tortoise"]
    public string Language { get; set; } = "en";
    public string? Emotion { get; set; }
    public string SelectionMode { get; set; } = "voting"; // "voting", "hybrid", "fusion"
    public string? FusionStrategy { get; set; } // "quality_weighted", "equal", "best_segment"
    public double SegmentSize { get; set; } = 0.5; // seconds
    public double QualityThreshold { get; set; } = 0.85; // Minimum quality for selection
  }

  /// <summary>
  /// Response from multi-engine ensemble synthesis.
  /// </summary>
  public class MultiEngineEnsembleResponse
  {
    public string JobId { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty; // queued, processing, completed, failed
    public List<string> Engines { get; set; } = new();
    public string Message { get; set; } = string.Empty;
  }

  /// <summary>
  /// Status of a multi-engine ensemble job.
  /// </summary>
  public class MultiEngineEnsembleStatus
  {
    public string JobId { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public double Progress { get; set; } // 0.0 to 1.0
    public List<string> Engines { get; set; } = new();
    public Dictionary<string, string> EngineOutputs { get; set; } = new(); // engine -> audio_id
    public Dictionary<string, Dictionary<string, object>> EngineQualities { get; set; } = new(); // engine -> quality metrics
    public string? EnsembleAudioId { get; set; }
    public Dictionary<string, object>? EnsembleQuality { get; set; }
    public string? Error { get; set; }
    public string Created { get; set; } = string.Empty;
    public string Updated { get; set; } = string.Empty;
  }

  /// <summary>
  /// Quality metrics for a single engine output in ensemble.
  /// </summary>
  public class EngineQualityResult
  {
    public string Engine { get; set; } = string.Empty;
    public string AudioId { get; set; } = string.Empty;
    public double? QualityScore { get; set; }
    public double? MosScore { get; set; }
    public double? Similarity { get; set; }
    public double? Naturalness { get; set; }
    public string? Error { get; set; }
  }
}