using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Response model for listing available video engines.
  /// </summary>
  public class VideoEnginesListResponse
  {
    public List<string>? Engines { get; set; }
  }
}