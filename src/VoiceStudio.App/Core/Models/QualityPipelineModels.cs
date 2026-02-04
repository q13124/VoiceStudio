using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Enhancement step in a quality pipeline.
  /// Implements IDEA 58: Engine-Specific Quality Enhancement Pipelines.
  /// </summary>
  public class PipelineStep
  {
    /// <summary>
    /// Step name (e.g., "denoise", "normalize", "enhance_spectral").
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Whether this step is enabled.
    /// </summary>
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Step-specific parameters.
    /// </summary>
    public Dictionary<string, object> Parameters { get; set; } = new();
  }

  /// <summary>
  /// Quality enhancement pipeline for a specific engine.
  /// Implements IDEA 58: Engine-Specific Quality Enhancement Pipelines.
  /// </summary>
  public class QualityPipeline
  {
    /// <summary>
    /// Engine identifier (e.g., "xtts_v2", "chatterbox", "tortoise").
    /// </summary>
    public string EngineId { get; set; } = string.Empty;

    /// <summary>
    /// Pipeline name/preset (e.g., "fast", "standard", "balanced", "high_quality").
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Pipeline description.
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Enhancement steps in the pipeline.
    /// </summary>
    public List<PipelineStep> Steps { get; set; } = new();
  }

  /// <summary>
  /// Pipeline configuration matching backend PipelineConfiguration (IDEA 58).
  /// </summary>
  public class PipelineConfiguration
  {
    /// <summary>
    /// Engine identifier.
    /// </summary>
    public string EngineId { get; set; } = string.Empty;

    /// <summary>
    /// Preset name.
    /// </summary>
    public string? PresetName { get; set; }

    /// <summary>
    /// Pipeline steps (list of step names).
    /// </summary>
    public List<string> Steps { get; set; } = new();

    /// <summary>
    /// Pipeline settings dictionary.
    /// </summary>
    public Dictionary<string, object> Settings { get; set; } = new();

    /// <summary>
    /// Pipeline description.
    /// </summary>
    public string? Description { get; set; }
  }

  /// <summary>
  /// Request to preview a quality pipeline on audio.
  /// </summary>
  public class PreviewPipelineRequest
  {
    /// <summary>
    /// Audio ID to preview.
    /// </summary>
    public string AudioId { get; set; } = string.Empty;

    /// <summary>
    /// Engine identifier.
    /// </summary>
    public string EngineId { get; set; } = string.Empty;

    /// <summary>
    /// Preset name to use (optional, uses default if not specified).
    /// </summary>
    public string? PresetName { get; set; }

    /// <summary>
    /// Optional custom pipeline configuration.
    /// </summary>
    public PipelineConfiguration? PipelineConfig { get; set; }
  }

  /// <summary>
  /// Response from pipeline preview (IDEA 58).
  /// </summary>
  public class PreviewPipelineResponse
  {
    /// <summary>
    /// Enhanced audio ID.
    /// </summary>
    public string EnhancedAudioId { get; set; } = string.Empty;

    /// <summary>
    /// Quality metrics before enhancement.
    /// </summary>
    public Dictionary<string, object> BeforeMetrics { get; set; } = new();

    /// <summary>
    /// Quality metrics after enhancement.
    /// </summary>
    public Dictionary<string, object> AfterMetrics { get; set; } = new();

    /// <summary>
    /// Optional comparison data.
    /// </summary>
    public PipelineComparisonResponse? Comparison { get; set; }
  }

  /// <summary>
  /// Response from pipeline comparison (IDEA 58).
  /// </summary>
  public class PipelineComparisonResponse
  {
    /// <summary>
    /// Quality metrics before enhancement.
    /// </summary>
    public Dictionary<string, object> BeforeMetrics { get; set; } = new();

    /// <summary>
    /// Quality metrics after enhancement.
    /// </summary>
    public Dictionary<string, object> AfterMetrics { get; set; } = new();

    /// <summary>
    /// Quality improvements (delta values and percentages).
    /// </summary>
    public Dictionary<string, object> Improvements { get; set; } = new();
  }
}