namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Engine recommendation result.
    /// </summary>
    public class EngineRecommendation
    {
        /// <summary>
        /// Engine identifier.
        /// </summary>
        public string EngineId { get; set; } = string.Empty;

        /// <summary>
        /// Display name of the engine.
        /// </summary>
        public string EngineName { get; set; } = string.Empty;

        /// <summary>
        /// Recommendation score (0.0-1.0, higher is better).
        /// </summary>
        public double RecommendationScore { get; set; }

        /// <summary>
        /// Estimated quality metrics.
        /// </summary>
        public EngineQualityEstimate QualityEstimate { get; set; } = new();

        /// <summary>
        /// Whether engine meets all minimum requirements.
        /// </summary>
        public bool MeetsRequirements { get; set; }

        /// <summary>
        /// Explanation for why this engine was recommended.
        /// </summary>
        public string Reasoning { get; set; } = string.Empty;

        // Compatibility aliases
        public string RecommendedEngine
        {
            get => EngineId;
            set => EngineId = value;
        }

        public string Reason
        {
            get => Reasoning;
            set => Reasoning = value;
        }
    }
}

