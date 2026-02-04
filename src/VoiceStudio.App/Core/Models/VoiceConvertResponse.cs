using System;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Response model for voice conversion.
  /// </summary>
  public class VoiceConvertResponse
  {
    public string AudioId { get; set; } = string.Empty;
    public string AudioUrl { get; set; } = string.Empty;
    public double Duration { get; set; }
    public string Format { get; set; } = "wav";
  }
}