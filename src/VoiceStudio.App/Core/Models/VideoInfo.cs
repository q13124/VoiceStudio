using System;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Model for video information.
  /// </summary>
  public class VideoInfo
  {
    public double Duration { get; set; }
    public int Width { get; set; }
    public int Height { get; set; }
    public double Fps { get; set; }
    public string? Format { get; set; }
  }
}