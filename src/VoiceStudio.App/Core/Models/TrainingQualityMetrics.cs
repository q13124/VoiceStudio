using System;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Quality metrics for a training epoch (IDEA 54).
    /// </summary>
    public class TrainingQualityMetrics
    {
        /// <summary>
        /// Epoch number.
        /// </summary>
        public int Epoch { get; set; }

        /// <summary>
        /// Training loss for this epoch.
        /// </summary>
        public double? TrainingLoss { get; set; }

        /// <summary>
        /// Validation loss for this epoch.
        /// </summary>
        public double? ValidationLoss { get; set; }

        /// <summary>
        /// Overall quality score (0.0-1.0).
        /// </summary>
        public double? QualityScore { get; set; }

        /// <summary>
        /// Mean Opinion Score estimate.
        /// </summary>
        public double? MosScore { get; set; }

        /// <summary>
        /// Voice similarity score (0.0-1.0).
        /// </summary>
        public double? Similarity { get; set; }

        /// <summary>
        /// Naturalness score (0.0-1.0).
        /// </summary>
        public double? Naturalness { get; set; }

        /// <summary>
        /// Timestamp when metrics were recorded.
        /// </summary>
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Quality alert for training monitoring (IDEA 54).
    /// </summary>
    public class TrainingQualityAlert
    {
        /// <summary>
        /// Alert type (degradation, plateau, overfitting).
        /// </summary>
        public string Type { get; set; } = string.Empty;

        /// <summary>
        /// Alert severity (info, warning, error).
        /// </summary>
        public string Severity { get; set; } = "info";

        /// <summary>
        /// Alert message.
        /// </summary>
        public string Message { get; set; } = string.Empty;

        /// <summary>
        /// Epoch when alert was detected.
        /// </summary>
        public int Epoch { get; set; }

        /// <summary>
        /// Confidence in the alert (0.0-1.0).
        /// </summary>
        public double Confidence { get; set; } = 0.5;

        /// <summary>
        /// Timestamp when alert was created.
        /// </summary>
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Early stopping recommendation (IDEA 54).
    /// </summary>
    public class EarlyStoppingRecommendation
    {
        /// <summary>
        /// Whether early stopping is recommended.
        /// </summary>
        public bool ShouldStop { get; set; }

        /// <summary>
        /// Reason for recommendation.
        /// </summary>
        public string Reason { get; set; } = string.Empty;

        /// <summary>
        /// Confidence in recommendation (0.0-1.0).
        /// </summary>
        public double Confidence { get; set; }

        /// <summary>
        /// Current epoch.
        /// </summary>
        public int CurrentEpoch { get; set; }

        /// <summary>
        /// Best epoch found so far.
        /// </summary>
        public int? BestEpoch { get; set; }

        /// <summary>
        /// Quality metrics at best epoch.
        /// </summary>
        public TrainingQualityMetrics? BestMetrics { get; set; }
    }
}

