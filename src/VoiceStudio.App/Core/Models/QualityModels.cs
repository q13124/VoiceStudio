using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
    /// <summary>
    /// Quality preset information.
    /// </summary>
    public class QualityPresetInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public Dictionary<string, double> TargetMetrics { get; set; } = new();
        public Dictionary<string, object> Parameters { get; set; } = new();
    }

    /// <summary>
    /// Request for quality analysis.
    /// </summary>
    public class QualityAnalysisRequest
    {
        public double? MosScore { get; set; }
        public double? Similarity { get; set; }
        public double? Naturalness { get; set; }
        public double? SnrDb { get; set; }
        public string TargetTier { get; set; } = "standard";
    }

    /// <summary>
    /// Response from quality analysis.
    /// </summary>
    public class QualityAnalysisResponse
    {
        public bool MeetsTarget { get; set; }
        public double QualityScore { get; set; }
        public List<Dictionary<string, object>> Deficiencies { get; set; } = new();
        public List<Dictionary<string, object>> Recommendations { get; set; } = new();
    }

    /// <summary>
    /// Request for quality optimization.
    /// </summary>
    public class QualityOptimizationRequest
    {
        public Dictionary<string, object> Metrics { get; set; } = new();
        public Dictionary<string, object> CurrentParams { get; set; } = new();
        public string TargetTier { get; set; } = "standard";
    }

    /// <summary>
    /// Response from quality optimization.
    /// </summary>
    public class QualityOptimizationResponse
    {
        public Dictionary<string, object> OptimizedParams { get; set; } = new();
        public Dictionary<string, object> Analysis { get; set; } = new();

        // Compatibility aliases
        public Dictionary<string, object> OptimizedParameters
        {
            get => OptimizedParams;
            set => OptimizedParams = value;
        }

        // Estimated expected improvement (some responses include this)
        public double? ExpectedImprovement { get; set; }
    }

    /// <summary>
    /// Sample for quality comparison.
    /// </summary>
    public class QualityComparisonSample
    {
        public string Name { get; set; } = string.Empty;
        public string AudioPath { get; set; } = string.Empty;
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    /// <summary>
    /// Request for quality comparison.
    /// </summary>
    public class QualityComparisonRequest
    {
        public List<QualityComparisonSample> Samples { get; set; } = new();
    }

    /// <summary>
    /// Response from quality comparison.
    /// </summary>
    public class QualityComparisonResponse
    {
        public int TotalSamples { get; set; }
        public Dictionary<int, Dictionary<string, object>> Rankings { get; set; } = new();
        public Dictionary<string, Dictionary<string, double>> Statistics { get; set; } = new();
        public Dictionary<string, Dictionary<string, object>> BestSamples { get; set; } = new();
        public List<Dictionary<string, object>> ComparisonTable { get; set; } = new();
    }

    /// <summary>
    /// Request for engine recommendation.
    /// Implements IDEA 47: Quality-Based Engine Recommendation System.
    /// </summary>
    public class EngineRecommendationRequest
    {
        public string TaskType { get; set; } = "tts";
        public double? MinMosScore { get; set; }
        public double? MinSimilarity { get; set; }
        public double? MinNaturalness { get; set; }
        public bool PreferSpeed { get; set; } = false;
        public string? QualityTier { get; set; }
    }

    /// <summary>
    /// Request for A/B testing two synthesis configurations.
    /// Implements IDEA 46: A/B Testing Interface for Quality Comparison.
    /// </summary>
    public class ABTestRequest
    {
        public string ProfileId { get; set; } = string.Empty;
        public string Text { get; set; } = string.Empty;
        public string Language { get; set; } = "en";

        // Configuration A
        public string EngineA { get; set; } = string.Empty;
        public string? EmotionA { get; set; }
        public bool EnhanceQualityA { get; set; } = true;

        // Configuration B
        public string EngineB { get; set; } = string.Empty;
        public string? EmotionB { get; set; }
        public bool EnhanceQualityB { get; set; } = true;
    }

    /// <summary>
    /// Result for one side of A/B test.
    /// </summary>
    public class ABTestResult
    {
        public string SampleLabel { get; set; } = string.Empty;
        public string AudioId { get; set; } = string.Empty;
        public string AudioUrl { get; set; } = string.Empty;
        public double Duration { get; set; }
        public string Engine { get; set; } = string.Empty;
        public string? Emotion { get; set; }
        public double? QualityScore { get; set; }
        public QualityMetrics? QualityMetrics { get; set; }
    }

    /// <summary>
    /// Response from A/B test.
    /// </summary>
    public class ABTestResponse
    {
        public ABTestResult SampleA { get; set; } = new();
        public ABTestResult SampleB { get; set; } = new();
        public Dictionary<string, object> Comparison { get; set; } = new();
        public string TestId { get; set; } = string.Empty;
    }

    /// <summary>
    /// Request for quality benchmarking.
    /// Implements IDEA 52: Quality Benchmarking and Comparison Tool.
    /// </summary>
    public class BenchmarkRequest
    {
        public string? ProfileId { get; set; }
        public string? ReferenceAudioId { get; set; }
        public string TestText { get; set; } = string.Empty;
        public string Language { get; set; } = "en";
        public List<string>? Engines { get; set; }
        public bool EnhanceQuality { get; set; } = true;
    }

    /// <summary>
    /// Result for a single engine benchmark.
    /// </summary>
    public class BenchmarkResult
    {
        public string Engine { get; set; } = string.Empty;
        public bool Success { get; set; }
        public string? Error { get; set; }
        public Dictionary<string, object> QualityMetrics { get; set; } = new();
        public Dictionary<string, object> Performance { get; set; } = new();
    }

    /// <summary>
    /// Response from quality benchmarking.
    /// </summary>
    public class BenchmarkResponse
    {
        public List<BenchmarkResult> Results { get; set; } = new();
        public int TotalEngines { get; set; }
        public int SuccessfulEngines { get; set; }
        public string? BenchmarkId { get; set; }
    }

    /// <summary>
    /// Quality metrics dashboard data.
    /// Implements IDEA 49: Quality Metrics Visualization Dashboard.
    /// </summary>
    public class QualityDashboard
    {
        /// <summary>
        /// Overview statistics.
        /// </summary>
        public QualityDashboardOverview? Overview { get; set; }

        /// <summary>
        /// Quality trends over time.
        /// </summary>
        public Dictionary<string, List<QualityTrendDataPoint>>? Trends { get; set; }

        /// <summary>
        /// Quality metric distributions.
        /// </summary>
        public Dictionary<string, QualityDistribution>? Distribution { get; set; }

        /// <summary>
        /// Quality alerts and warnings.
        /// </summary>
        public List<DashboardQualityAlert>? Alerts { get; set; }

        /// <summary>
        /// Quality insights and recommendations.
        /// </summary>
        public List<string>? Insights { get; set; }
    }

    /// <summary>
    /// Overview statistics for quality dashboard.
    /// </summary>
    public class QualityDashboardOverview
    {
        public int TotalSyntheses { get; set; }
        public double AverageMosScore { get; set; }
        public double AverageSimilarity { get; set; }
        public double AverageNaturalness { get; set; }
        public Dictionary<string, int>? QualityTierDistribution { get; set; }
    }

    /// <summary>
    /// Data point for quality trend.
    /// </summary>
    public class QualityTrendDataPoint
    {
        public DateTime Date { get; set; }
        public double Value { get; set; }
    }

    /// <summary>
    /// Quality metric distribution.
    /// </summary>
    public class QualityDistribution
    {
        public double Min { get; set; }
        public double Max { get; set; }
        public double Mean { get; set; }
        public double Median { get; set; }
        public double StdDev { get; set; }
        public Dictionary<string, int>? Histogram { get; set; }
    }

    /// <summary>
    /// Quality alert or warning used in the quality dashboard.
    /// </summary>
    public class DashboardQualityAlert
    {
        public string Severity { get; set; } = string.Empty; // "info", "warning", "error"
        public string Message { get; set; } = string.Empty;
        public DateTime Timestamp { get; set; }
        public string? ProfileId { get; set; }
        public Dictionary<string, object>? Details { get; set; }
    }

    // Quality Degradation Detection (IDEA 56)

    /// <summary>
    /// Quality trend analysis result (IDEA 56) used in the dashboard.
    /// </summary>
    public class DashboardQualityTrend
    {
        public string Trend { get; set; } = string.Empty; // "improving", "degrading", "stable", "unknown"
        public double ChangePercentage { get; set; }
        public bool IsImproving { get; set; }
        public bool IsDegrading { get; set; }
        public Dictionary<string, double>? MetricChanges { get; set; }
    }
}

