using System;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Quality settings recommendation based on text analysis (IDEA 53).
    /// </summary>
    public class QualityRecommendation
    {
        /// <summary>
        /// Recommended engine (xtts, chatterbox, tortoise).
        /// </summary>
        public string RecommendedEngine { get; set; } = string.Empty;

        /// <summary>
        /// Recommended quality mode (fast, standard, high, ultra).
        /// </summary>
        public string RecommendedQualityMode { get; set; } = string.Empty;

        /// <summary>
        /// Whether quality enhancement should be enabled.
        /// </summary>
        public bool RecommendedEnhanceQuality { get; set; }

        /// <summary>
        /// Predicted quality score (0.0-1.0).
        /// </summary>
        public double PredictedQualityScore { get; set; }

        /// <summary>
        /// Human-readable reasoning for the recommendations.
        /// </summary>
        public string Reasoning { get; set; } = string.Empty;

        /// <summary>
        /// Confidence in the recommendations (0.0-1.0).
        /// </summary>
        public double Confidence { get; set; }

        /// <summary>
        /// Text analysis results used to generate recommendations.
        /// </summary>
        public TextAnalysisResult? TextAnalysis { get; set; }

        // Compatibility properties (older code expects these names)
        public string Type { get; set; } = string.Empty;
        public string Message
        {
            get => Reasoning;
            set => Reasoning = value;
        }
        public string Priority { get; set; } = string.Empty;
        public double ExpectedImprovement { get; set; }
    }
}

