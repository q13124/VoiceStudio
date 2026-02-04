using System;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Response model for video upscaling.
  /// </summary>
  public class VideoUpscaleResponse
  {
    public string VideoId { get; set; } = string.Empty;
    public string VideoUrl { get; set; } = string.Empty;
    public int Width { get; set; }
    public int Height { get; set; }
    public int Scale { get; set; }
    public string Format { get; set; } = "mp4";
  }
}