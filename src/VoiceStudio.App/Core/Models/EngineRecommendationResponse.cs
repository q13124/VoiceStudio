using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Response from engine recommendation (IDEA 47).
  /// Separated into its own file to avoid duplicate definitions.
  /// </summary>
  public class EngineRecommendationResponse
  {
    public List<EngineRecommendation> Recommendations { get; set; } = new();
    public int TotalEngines { get; set; }
    public int MatchingEngines { get; set; }

    // Convenience aliases for the top recommendation (used by some XAML bindings).
    public string? RecommendedEngine =>
        Recommendations.Count > 0 ? Recommendations[0].RecommendedEngine : null;

    public string? Reason =>
        Recommendations.Count > 0 ? Recommendations[0].Reason : null;
  }
}