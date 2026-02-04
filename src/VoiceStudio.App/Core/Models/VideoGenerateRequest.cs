using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Request model for video generation.
  /// </summary>
  public class VideoGenerateRequest
  {
    public string Engine { get; set; } = string.Empty;
    public string? Prompt { get; set; }
    public string? ImageId { get; set; }
    public string? AudioId { get; set; }
    public int? Width { get; set; }
    public int? Height { get; set; }
    public double? Fps { get; set; }
    public double? Duration { get; set; }
    public int? Steps { get; set; }
    public double? CfgScale { get; set; }
    public int? Seed { get; set; }
    public bool EnablePreprocessing { get; set; }
    public string? DenoisingMethod { get; set; }
    public string? EnhancementMethod { get; set; }
    public int EnhancementStrength { get; set; } = 50;
    public Dictionary<string, object>? AdditionalParams { get; set; }
  }
}