using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Comprehensive quality analysis result for reference audio before voice cloning.
    /// Implements IDEA 41: Reference Audio Quality Analyzer and Recommendations.
    /// </summary>
    public class ReferenceAudioQualityResult
    {
        /// <summary>
        /// Overall quality score (0-100). Higher is better.
        /// Indicates suitability for voice cloning.
        /// </summary>
        public double QualityScore { get; set; }

        /// <summary>
        /// Detailed quality metrics (MOS, SNR, etc.)
        /// </summary>
        public QualityMetrics? Metrics { get; set; }

        /// <summary>
        /// Detected quality issues.
        /// </summary>
        public List<QualityIssue> Issues { get; set; } = new List<QualityIssue>();

        /// <summary>
        /// Enhancement suggestions to improve quality.
        /// </summary>
        public List<EnhancementSuggestion> Suggestions { get; set; } = new List<EnhancementSuggestion>();

        /// <summary>
        /// Clarity score (0-100). Higher indicates clearer audio.
        /// </summary>
        public double ClarityScore { get; set; }

        /// <summary>
        /// Noise level score (0-100). Lower indicates less noise.
        /// </summary>
        public double NoiseLevel { get; set; }

        /// <summary>
        /// Consistency score (0-100). Higher indicates more consistent audio quality.
        /// </summary>
        public double ConsistencyScore { get; set; }

        /// <summary>
        /// Whether the audio is suitable for voice cloning without enhancement.
        /// </summary>
        public bool IsSuitableForCloning { get; set; }

        /// <summary>
        /// Analysis timestamp.
        /// </summary>
        public DateTime AnalyzedAt { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// A detected quality issue in the reference audio.
    /// </summary>
    public class QualityIssue
    {
        /// <summary>
        /// Issue type (e.g., "BackgroundNoise", "Clipping", "Distortion", "LowVolume").
        /// </summary>
        public string Type { get; set; } = string.Empty;

        /// <summary>
        /// Human-readable description of the issue.
        /// </summary>
        public string Description { get; set; } = string.Empty;

        /// <summary>
        /// Severity level (Low, Medium, High, Critical).
        /// </summary>
        public string Severity { get; set; } = "Medium";

        /// <summary>
        /// Impact on voice cloning quality (0-100). Higher indicates more impact.
        /// </summary>
        public double Impact { get; set; }

        /// <summary>
        /// Additional details about the issue.
        /// </summary>
        public Dictionary<string, object>? Details { get; set; }
    }

    /// <summary>
    /// Enhancement suggestion to improve reference audio quality.
    /// </summary>
    public class EnhancementSuggestion
    {
        /// <summary>
        /// Suggestion type (e.g., "Denoise", "Normalize", "Enhance", "RemoveSilence").
        /// </summary>
        public string Type { get; set; } = string.Empty;

        /// <summary>
        /// Human-readable description of the suggestion.
        /// </summary>
        public string Description { get; set; } = string.Empty;

        /// <summary>
        /// Priority level (Low, Medium, High).
        /// </summary>
        public string Priority { get; set; } = "Medium";

        /// <summary>
        /// Expected quality improvement (0-100). Higher indicates more improvement.
        /// </summary>
        public double ExpectedImprovement { get; set; }

        /// <summary>
        /// Whether this enhancement is recommended before training.
        /// </summary>
        public bool Recommended { get; set; }

        /// <summary>
        /// Additional parameters or settings for the enhancement.
        /// </summary>
        public Dictionary<string, object>? Parameters { get; set; }
    }
}

