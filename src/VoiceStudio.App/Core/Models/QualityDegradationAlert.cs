namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Quality degradation alert for a voice profile (IDEA 56).
    /// </summary>
    public class QualityDegradationAlert
    {
        /// <summary>
        /// Alert severity (warning, critical).
        /// </summary>
        public string Severity { get; set; } = string.Empty;

        /// <summary>
        /// Percentage drop from baseline.
        /// </summary>
        public double DegradationPercentage { get; set; }

        /// <summary>
        /// Name of the degraded metric.
        /// </summary>
        public string MetricName { get; set; } = string.Empty;

        /// <summary>
        /// Current metric value.
        /// </summary>
        public double CurrentValue { get; set; }

        /// <summary>
        /// Baseline metric value.
        /// </summary>
        public double BaselineValue { get; set; }

        /// <summary>
        /// Time window analyzed in days.
        /// </summary>
        public int TimeWindowDays { get; set; }

        /// <summary>
        /// Recommended action to resolve degradation.
        /// </summary>
        public string Recommendation { get; set; } = string.Empty;

        /// <summary>
        /// Confidence score (0.0-1.0).
        /// </summary>
        public double Confidence { get; set; }

        // Compatibility alias
        public double DegradationPercent
        {
            get => DegradationPercentage;
            set => DegradationPercentage = value;
        }
    }
}

