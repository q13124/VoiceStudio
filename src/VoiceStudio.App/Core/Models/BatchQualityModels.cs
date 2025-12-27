using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Quality report for a batch job (IDEA 57).
    /// </summary>
    public class BatchQualityReport
    {
        public string JobId { get; set; } = string.Empty;
        public string JobName { get; set; } = string.Empty;
        public double? QualityScore { get; set; }
        public string? QualityStatus { get; set; }
        public double? QualityThreshold { get; set; }
        public Dictionary<string, object> Metrics { get; set; } = new();
        public Dictionary<string, object> Summary { get; set; } = new();
        public Dictionary<string, object>? Comparison { get; set; }
    }

    /// <summary>
    /// Quality statistics for a batch of jobs (IDEA 57).
    /// </summary>
    public class BatchQualityStatistics
    {
        public int TotalJobs { get; set; }
        public int CompletedJobs { get; set; }
        public int JobsWithQuality { get; set; }
        public double? AverageQuality { get; set; }
        public double? MinQuality { get; set; }
        public double? MaxQuality { get; set; }
        public Dictionary<string, int> QualityDistribution { get; set; } = new();
        public Dictionary<string, int> StatusDistribution { get; set; } = new();
    }

    /// <summary>
    /// Request to retry a batch job with quality settings (IDEA 57).
    /// </summary>
    public class BatchRetryWithQualityRequest
    {
        public double? QualityThreshold { get; set; }
        public bool EnhanceQuality { get; set; }
        public string? QualityMode { get; set; }
    }
}
