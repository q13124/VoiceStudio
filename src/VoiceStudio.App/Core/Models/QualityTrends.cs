using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Represents quality trends and statistics for a voice profile.
    /// Used for quality history visualization and analysis.
    /// </summary>
    public class QualityTrends
    {
        /// <summary>
        /// Voice profile ID these trends belong to.
        /// </summary>
        public string ProfileId { get; set; } = string.Empty;

        /// <summary>
        /// Time range for these trends (e.g., "30d", "1y", "all").
        /// </summary>
        public string TimeRange { get; set; } = "30d";

        /// <summary>
        /// Trend data for each metric over time.
        /// Key: metric name (e.g., "mos_score", "similarity")
        /// Value: List of timestamp-value pairs
        /// </summary>
        public Dictionary<string, List<QualityTrendPoint>> Trends { get; set; } = new();

        /// <summary>
        /// Statistics for each metric (average, min, max, trend).
        /// Key: metric name
        /// Value: statistics dictionary
        /// </summary>
        public Dictionary<string, QualityMetricStatistics> Statistics { get; set; } = new();

        /// <summary>
        /// Best quality history entry (highest quality score).
        /// </summary>
        public QualityHistoryEntry? BestEntry { get; set; }

        /// <summary>
        /// Worst quality history entry (lowest quality score).
        /// </summary>
        public QualityHistoryEntry? WorstEntry { get; set; }

        // Compatibility properties expected by older viewmodels
        public string? OverallTrend { get; set; }

        public Dictionary<string, List<double>>? MetricsOverTime
        {
            get
            {
                if (Trends == null) return null;
                var dict = new Dictionary<string, List<double>>();
                foreach (var kv in Trends)
                {
                    dict[kv.Key] = kv.Value.Select(p => p.Value).ToList();
                }
                return dict;
            }
        }
    }

    /// <summary>
    /// Represents a single point in a quality trend.
    /// </summary>
    public class QualityTrendPoint
    {
        /// <summary>
        /// Timestamp for this data point (ISO format).
        /// </summary>
        public string Timestamp { get; set; } = string.Empty;

        /// <summary>
        /// Value of the metric at this timestamp.
        /// </summary>
        public double Value { get; set; }
    }

    /// <summary>
    /// Statistics for a quality metric.
    /// </summary>
    public class QualityMetricStatistics
    {
        /// <summary>
        /// Average value of the metric.
        /// </summary>
        public double Average { get; set; }

        /// <summary>
        /// Minimum value of the metric.
        /// </summary>
        public double Min { get; set; }

        /// <summary>
        /// Maximum value of the metric.
        /// </summary>
        public double Max { get; set; }

        /// <summary>
        /// Trend value (slope of linear regression, positive = improving, negative = declining).
        /// </summary>
        public double Trend { get; set; }
    }
}

