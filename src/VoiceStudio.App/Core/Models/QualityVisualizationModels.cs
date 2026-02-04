using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Request for quality heatmap visualization (IDEA 60).
  /// </summary>
  public class QualityHeatmapRequest
  {
    /// <summary>
    /// List of quality records with metrics.
    /// </summary>
    public List<Dictionary<string, object>> QualityData { get; set; } = new();

    /// <summary>
    /// Dimension for X axis (engine, profile, time_period).
    /// </summary>
    public string XDimension { get; set; } = "engine";

    /// <summary>
    /// Dimension for Y axis (engine, profile, time_period).
    /// </summary>
    public string YDimension { get; set; } = "profile";

    /// <summary>
    /// Metric to visualize (mos_score, similarity, naturalness, snr, artifacts).
    /// </summary>
    public string Metric { get; set; } = "mos_score";
  }

  /// <summary>
  /// Response for quality heatmap visualization (IDEA 60).
  /// </summary>
  public class QualityHeatmapResponse
  {
    /// <summary>
    /// Dimension for X axis.
    /// </summary>
    public string XDimension { get; set; } = string.Empty;

    /// <summary>
    /// Dimension for Y axis.
    /// </summary>
    public string YDimension { get; set; } = string.Empty;

    /// <summary>
    /// Metric visualized.
    /// </summary>
    public string Metric { get; set; } = string.Empty;

    /// <summary>
    /// List of X axis values.
    /// </summary>
    public List<string> XValues { get; set; } = new();

    /// <summary>
    /// List of Y axis values.
    /// </summary>
    public List<string> YValues { get; set; } = new();

    /// <summary>
    /// Heatmap matrix (x_value -> y_value -> metric value/statistics).
    /// </summary>
    public Dictionary<string, Dictionary<string, object>> Matrix { get; set; } = new();

    /// <summary>
    /// Minimum value in the matrix.
    /// </summary>
    public double MinValue { get; set; }

    /// <summary>
    /// Maximum value in the matrix.
    /// </summary>
    public double MaxValue { get; set; }
  }

  /// <summary>
  /// Response for quality metric correlations (IDEA 60).
  /// </summary>
  public class QualityCorrelationResponse
  {
    /// <summary>
    /// List of metric names.
    /// </summary>
    public List<string> Metrics { get; set; } = new();

    /// <summary>
    /// Correlation matrix (metric -> metric -> correlation coefficient).
    /// </summary>
    public Dictionary<string, Dictionary<string, double>> Correlations { get; set; } = new();
  }

  /// <summary>
  /// Quality anomaly detection result (IDEA 60).
  /// </summary>
  public class QualityAnomaly
  {
    /// <summary>
    /// Index or identifier of the anomalous sample.
    /// </summary>
    public int Index { get; set; }

    /// <summary>
    /// Full record data for this sample.
    /// </summary>
    public Dictionary<string, object>? Record { get; set; }

    /// <summary>
    /// Metric name that was analyzed.
    /// </summary>
    public string Metric { get; set; } = string.Empty;

    /// <summary>
    /// Anomalous value.
    /// </summary>
    public double Value { get; set; }

    /// <summary>
    /// Mean value of the metric.
    /// </summary>
    public double Mean { get; set; }

    /// <summary>
    /// Standard deviation of the metric.
    /// </summary>
    public double Std { get; set; }

    /// <summary>
    /// Z-score of the anomaly (higher = more anomalous).
    /// </summary>
    public double ZScore { get; set; }

    /// <summary>
    /// Deviation from mean (value - mean).
    /// </summary>
    public double Deviation { get; set; }
  }

  /// <summary>
  /// Response for quality anomaly detection (IDEA 60).
  /// </summary>
  public class QualityAnomalyResponse
  {
    /// <summary>
    /// Metric analyzed.
    /// </summary>
    public string Metric { get; set; } = string.Empty;

    /// <summary>
    /// Threshold standard deviations used.
    /// </summary>
    public double ThresholdStd { get; set; }

    /// <summary>
    /// List of detected anomalies.
    /// </summary>
    public List<QualityAnomaly> Anomalies { get; set; } = new();

    /// <summary>
    /// Total number of samples analyzed.
    /// </summary>
    public int TotalSamples { get; set; }

    /// <summary>
    /// Number of anomalies detected.
    /// </summary>
    public int AnomalyCount { get; set; }
  }

  /// <summary>
  /// Request for quality prediction (IDEA 60).
  /// </summary>
  public class QualityPredictionRequest
  {
    /// <summary>
    /// Input factors for prediction (engine, profile, text_length, etc.).
    /// </summary>
    public Dictionary<string, object> InputFactors { get; set; } = new();

    /// <summary>
    /// Optional quality data for training/calibration.
    /// </summary>
    public List<Dictionary<string, object>>? QualityData { get; set; }
  }

  /// <summary>
  /// Response for quality prediction (IDEA 60).
  /// </summary>
  public class QualityPredictionResponse
  {
    /// <summary>
    /// Input factors used for prediction.
    /// </summary>
    public Dictionary<string, object> InputFactors { get; set; } = new();

    /// <summary>
    /// Predicted metric values.
    /// </summary>
    public Dictionary<string, double?> PredictedMetrics { get; set; } = new();

    /// <summary>
    /// Confidence score (0.0-1.0).
    /// </summary>
    public double Confidence { get; set; }

    /// <summary>
    /// Number of samples used for prediction.
    /// </summary>
    public int SampleCount { get; set; }
  }

  /// <summary>
  /// Quality insight (IDEA 60).
  /// </summary>
  public class QualityInsight
  {
    /// <summary>
    /// Insight type (positive, warning, info).
    /// </summary>
    public string Type { get; set; } = string.Empty;

    /// <summary>
    /// Insight title.
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Insight message.
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Priority level (high, medium, low).
    /// </summary>
    public string Priority { get; set; } = string.Empty;

    /// <summary>
    /// Recommended action (optional).
    /// </summary>
    public string? Action { get; set; }
  }

  /// <summary>
  /// Response for quality insights (IDEA 60).
  /// </summary>
  public class QualityInsightsResponse
  {
    /// <summary>
    /// List of quality insights.
    /// </summary>
    public List<QualityInsight> Insights { get; set; } = new();

    /// <summary>
    /// Time period analyzed in days.
    /// </summary>
    public int TimePeriodDays { get; set; }

    /// <summary>
    /// Total number of quality samples analyzed.
    /// </summary>
    public int TotalSamples { get; set; }
  }
}