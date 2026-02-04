using System;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Request model for video editing operations.
  /// </summary>
  public class VideoEditRequest
  {
    public string Operation { get; set; } = string.Empty; // trim, split, effect, transition, export, resize, add_audio, upscale
    public string? InputPath { get; set; }
    public string? OutputPath { get; set; }
    public double? StartTime { get; set; }
    public double? EndTime { get; set; }
    public double? SplitTime { get; set; }
    public string? Effect { get; set; }
    public string? Transition { get; set; }
    public double? Duration { get; set; }
    public string? Format { get; set; }
    public int? Quality { get; set; }
    public int? Width { get; set; }
    public int? Height { get; set; }
    public string? AudioPath { get; set; }
    public double? Scale { get; set; }
  }
}