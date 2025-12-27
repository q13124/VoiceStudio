using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Request model for quality recommendations (IDEA 53).
    /// </summary>
    public class QualityRecommendationRequest
    {
        /// <summary>
        /// Text to analyze for recommendations.
        /// </summary>
        public string Text { get; set; } = string.Empty;

        /// <summary>
        /// Language code (default: "en").
        /// </summary>
        public string Language { get; set; } = "en";

        /// <summary>
        /// Available engines to choose from.
        /// </summary>
        public List<string>? AvailableEngines { get; set; }

        /// <summary>
        /// Target quality score (0.0-1.0), null for auto.
        /// </summary>
        public double? TargetQuality { get; set; }
    }
}

