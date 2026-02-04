using System;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Request model for text analysis (IDEA 53).
  /// </summary>
  public class TextAnalysisRequest
  {
    /// <summary>
    /// Text to analyze.
    /// </summary>
    public string Text { get; set; } = string.Empty;

    /// <summary>
    /// Language code (default: "en").
    /// </summary>
    public string Language { get; set; } = "en";
  }
}