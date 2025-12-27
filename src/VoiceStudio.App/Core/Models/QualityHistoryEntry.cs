using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Represents a quality history entry for a voice profile.
    /// Tracks quality metrics over time to enable quality trend analysis.
    /// </summary>
    public class QualityHistoryEntry
    {
        /// <summary>
        /// Unique identifier for this history entry.
        /// </summary>
        public string Id { get; set; } = string.Empty;

        /// <summary>
        /// Voice profile ID this entry belongs to.
        /// </summary>
        public string ProfileId { get; set; } = string.Empty;

        /// <summary>
        /// Timestamp when this quality measurement was taken.
        /// </summary>
        public DateTime Timestamp { get; set; }

        /// <summary>
        /// Engine used for this synthesis.
        /// </summary>
        public string Engine { get; set; } = string.Empty;

        /// <summary>
        /// Quality metrics for this entry.
        /// </summary>
        public QualityMetrics? Metrics { get; set; }

        /// <summary>
        /// Overall quality score (computed from metrics).
        /// </summary>
        public double QualityScore { get; set; }

        /// <summary>
        /// Text that was synthesized (optional, for reference).
        /// </summary>
        public string? SynthesisText { get; set; }

        /// <summary>
        /// Audio file URL or path (optional, for reference).
        /// </summary>
        public string? AudioUrl { get; set; }

        /// <summary>
        /// Whether quality enhancement was enabled.
        /// </summary>
        public bool EnhancedQuality { get; set; }

        /// <summary>
        /// Additional metadata for this entry.
        /// </summary>
        public Dictionary<string, object>? Metadata { get; set; }
    }
}

