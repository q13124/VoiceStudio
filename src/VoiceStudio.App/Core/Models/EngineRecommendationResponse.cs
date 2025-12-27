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
    }
}

