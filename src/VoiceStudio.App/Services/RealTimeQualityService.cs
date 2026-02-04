using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Service for tracking real-time quality metrics during voice synthesis.
  /// Implements IDEA 42: Real-Time Quality Feedback During Synthesis.
  /// </summary>
  public class RealTimeQualityService : IDisposable
  {
    private readonly IBackendClient _backendClient;
    private readonly Dictionary<string, RealTimeQualityFeedback> _activeSyntheses = new();
    private readonly List<RealTimeQualityFeedback> _synthesisHistory = new();
    private readonly int _maxHistorySize = 100;
    private bool _disposed;

    public RealTimeQualityService(IBackendClient backendClient)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
    }

    /// <summary>
    /// Starts tracking quality metrics for a synthesis job.
    /// </summary>
    public RealTimeQualityFeedback StartTracking(
        string synthesisId,
        string profileId,
        string engine)
    {
      if (string.IsNullOrWhiteSpace(synthesisId))
        throw new ArgumentException("Synthesis ID cannot be null or empty.", nameof(synthesisId));

      var feedback = new RealTimeQualityFeedback
      {
        SynthesisId = synthesisId,
        ProfileId = profileId,
        Engine = engine,
        StartTime = DateTime.UtcNow
      };

      _activeSyntheses[synthesisId] = feedback;
      return feedback;
    }

    /// <summary>
    /// Updates quality metrics for an active synthesis.
    /// </summary>
    public void UpdateMetrics(
        string synthesisId,
        double progress,
        QualityMetrics? metrics,
        double? qualityScore = null)
    {
      if (!_activeSyntheses.TryGetValue(synthesisId, out var feedback))
        return;

      var qualityMetrics = new RealTimeQualityMetrics
      {
        Timestamp = DateTime.UtcNow,
        Progress = Math.Max(0.0, Math.Min(1.0, progress)),
        MosScore = metrics?.MosScore,
        Similarity = metrics?.Similarity,
        Naturalness = metrics?.Naturalness,
        SnrDb = metrics?.SnrDb,
        QualityScore = qualityScore ?? CalculateQualityScore(metrics),
        IsQualityGood = (qualityScore ?? CalculateQualityScore(metrics)) >= 0.7
      };

      // Calculate trend based on previous metrics
      if (feedback.MetricsHistory.Count > 0)
      {
        var previousMetrics = feedback.MetricsHistory.Last();
        qualityMetrics.Trend = CalculateTrend(
            previousMetrics.QualityScore,
            qualityMetrics.QualityScore
        );
      }

      // Detect quality alerts
      qualityMetrics.Alerts = DetectQualityAlerts(qualityMetrics, feedback);

      // Add to history
      feedback.MetricsHistory.Add(qualityMetrics);
      feedback.CurrentMetrics = qualityMetrics;

      // Trigger quality updated event
      QualityMetricsUpdated?.Invoke(this, new QualityMetricsUpdatedEventArgs
      {
        SynthesisId = synthesisId,
        Metrics = qualityMetrics
      });
    }

    /// <summary>
    /// Completes tracking for a synthesis job and generates final analysis.
    /// </summary>
    public RealTimeQualityFeedback CompleteTracking(
        string synthesisId,
        QualityMetrics? finalMetrics,
        double? finalQualityScore = null)
    {
      if (!_activeSyntheses.TryGetValue(synthesisId, out var feedback))
        return null!;

      feedback.EndTime = DateTime.UtcNow;
      feedback.FinalMetrics = finalMetrics;
      feedback.CurrentMetrics = null; // Clear current since synthesis is done

      // Add final quality metrics if provided
      if (finalMetrics != null || finalQualityScore.HasValue)
      {
        var finalQualityMetrics = new RealTimeQualityMetrics
        {
          Timestamp = DateTime.UtcNow,
          Progress = 1.0,
          MosScore = finalMetrics?.MosScore,
          Similarity = finalMetrics?.Similarity,
          Naturalness = finalMetrics?.Naturalness,
          SnrDb = finalMetrics?.SnrDb,
          QualityScore = finalQualityScore ?? CalculateQualityScore(finalMetrics),
          IsQualityGood = (finalQualityScore ?? CalculateQualityScore(finalMetrics)) >= 0.7
        };

        if (feedback.MetricsHistory.Count > 0)
        {
          var previousMetrics = feedback.MetricsHistory.Last();
          finalQualityMetrics.Trend = CalculateTrend(
              previousMetrics.QualityScore,
              finalQualityMetrics.QualityScore
          );
        }

        feedback.MetricsHistory.Add(finalQualityMetrics);
      }

      // Generate quality comparison with previous syntheses
      feedback.Comparison = GenerateQualityComparison(feedback);

      // Generate quality recommendations
      feedback.Recommendations = GenerateRecommendations(feedback);

      // Move to history
      _synthesisHistory.Add(feedback);
      _activeSyntheses.Remove(synthesisId);

      // Trim history if too large
      if (_synthesisHistory.Count > _maxHistorySize)
      {
        _synthesisHistory.RemoveAt(0);
      }

      // Trigger completion event
      SynthesisCompleted?.Invoke(this, new SynthesisCompletedEventArgs
      {
        SynthesisId = synthesisId,
        Feedback = feedback
      });

      return feedback;
    }

    /// <summary>
    /// Gets current quality feedback for an active synthesis.
    /// </summary>
    public RealTimeQualityFeedback? GetCurrentFeedback(string synthesisId)
    {
      return _activeSyntheses.TryGetValue(synthesisId, out var feedback) ? feedback : null;
    }

    /// <summary>
    /// Gets quality history for a specific profile.
    /// </summary>
    public List<RealTimeQualityFeedback> GetProfileHistory(string profileId)
    {
      return _synthesisHistory
          .Where(f => f.ProfileId == profileId)
          .OrderByDescending(f => f.StartTime)
          .ToList();
    }

    /// <summary>
    /// Gets recent synthesis history (all profiles).
    /// </summary>
    public List<RealTimeQualityFeedback> GetRecentHistory(int count = 10)
    {
      return _synthesisHistory
          .OrderByDescending(f => f.StartTime)
          .Take(count)
          .ToList();
    }

    /// <summary>
    /// Event raised when quality metrics are updated during synthesis.
    /// </summary>
    public event EventHandler<QualityMetricsUpdatedEventArgs>? QualityMetricsUpdated;

    /// <summary>
    /// Event raised when synthesis completes with quality analysis.
    /// </summary>
    public event EventHandler<SynthesisCompletedEventArgs>? SynthesisCompleted;

    /// <summary>
    /// Calculates overall quality score from metrics (0.0-1.0).
    /// </summary>
    private double CalculateQualityScore(QualityMetrics? metrics)
    {
      if (metrics == null)
        return 0.5; // Default neutral score

      double score = 0.5; // Base score

      // Factor in MOS score (1-5 scale → 0-1)
      if (metrics.MosScore.HasValue)
      {
        var mosNormalized = (metrics.MosScore.Value - 1.0) / 4.0; // 1-5 → 0-1
        score = (score * 0.4) + (mosNormalized * 0.6);
      }

      // Factor in similarity (0-1 scale)
      if (metrics.Similarity.HasValue)
      {
        score = (score * 0.7) + (metrics.Similarity.Value * 0.3);
      }

      // Factor in naturalness (0-1 scale)
      if (metrics.Naturalness.HasValue)
      {
        score = (score * 0.8) + (metrics.Naturalness.Value * 0.2);
      }

      // Factor in SNR (normalize to 0-1, typical range 0-60dB)
      if (metrics.SnrDb.HasValue)
      {
        var snrNormalized = Math.Min(1.0, Math.Max(0.0, metrics.SnrDb.Value / 60.0));
        score = (score * 0.85) + (snrNormalized * 0.15);
      }

      // Penalize for artifacts
      if (metrics.ArtifactScore.HasValue)
      {
        var artifactPenalty = metrics.ArtifactScore.Value * 0.3;
        score = Math.Max(0.0, score - artifactPenalty);
      }

      return Math.Min(1.0, Math.Max(0.0, score));
    }

    /// <summary>
    /// Calculates quality trend from two scores.
    /// </summary>
    private QualityTrend CalculateTrend(double previousScore, double currentScore)
    {
      var difference = currentScore - previousScore;
      const double threshold = 0.05; // 5% change threshold

      if (difference > threshold)
        return QualityTrend.Improving;
      else if (difference < -threshold)
        return QualityTrend.Degrading;
      else
        return QualityTrend.Stable;
    }

    /// <summary>
    /// Detects quality alerts based on current metrics.
    /// </summary>
    private List<QualityAlert> DetectQualityAlerts(
        RealTimeQualityMetrics metrics,
        RealTimeQualityFeedback feedback)
    {
      var alerts = new List<QualityAlert>();

      // Check for quality drop
      if (feedback.MetricsHistory.Count > 1)
      {
        var previousMetrics = feedback.MetricsHistory[feedback.MetricsHistory.Count - 2];
        var qualityDrop = previousMetrics.QualityScore - metrics.QualityScore;
        if (qualityDrop > 0.15) // 15% drop
        {
          alerts.Add(new QualityAlert
          {
            Type = "QualityDrop",
            Message = $"Quality dropped by {qualityDrop:P0}",
            Severity = qualityDrop > 0.25 ? AlertSeverity.Critical : AlertSeverity.Warning,
            SuggestedAction = "Consider adjusting synthesis parameters or trying a different engine."
          });
        }
      }

      // Check for low MOS score
      if (metrics.MosScore.HasValue && metrics.MosScore.Value < 3.0)
      {
        alerts.Add(new QualityAlert
        {
          Type = "LowMOS",
          Message = $"Low MOS score: {metrics.MosScore.Value:F1}/5.0",
          Severity = metrics.MosScore.Value < 2.0 ? AlertSeverity.Critical : AlertSeverity.Warning,
          SuggestedAction = "Enable quality enhancement or use a higher quality preset."
        });
      }

      // Check for low quality score
      if (metrics.QualityScore < 0.6)
      {
        alerts.Add(new QualityAlert
        {
          Type = "LowQuality",
          Message = $"Quality score below threshold: {metrics.QualityScore:P0}",
          Severity = metrics.QualityScore < 0.5 ? AlertSeverity.Critical : AlertSeverity.Warning,
          SuggestedAction = "Review synthesis settings and reference audio quality."
        });
      }

      return alerts;
    }

    /// <summary>
    /// Generates quality comparison with previous syntheses.
    /// </summary>
    private QualityComparison GenerateQualityComparison(RealTimeQualityFeedback feedback)
    {
      var profileHistory = GetProfileHistory(feedback.ProfileId)
          .Where(f => f.SynthesisId != feedback.SynthesisId && f.FinalMetrics != null)
          .ToList();

      if (profileHistory.Count == 0)
        return null!;

      var finalScore = feedback.FinalMetrics != null
          ? CalculateQualityScore(feedback.FinalMetrics)
          : feedback.MetricsHistory.LastOrDefault()?.QualityScore ?? 0.5;

      var historicalScores = profileHistory
          .Select(f => f.FinalMetrics != null
              ? CalculateQualityScore(f.FinalMetrics)
              : f.MetricsHistory.LastOrDefault()?.QualityScore ?? 0.5)
          .ToList();

      var averageScore = historicalScores.Average();
      var bestScore = historicalScores.Max();
      var qualityDifference = finalScore - averageScore;

      return new QualityComparison
      {
        AverageQualityScore = averageScore,
        BestQualityScore = bestScore,
        QualityDifference = qualityDifference,
        IsBetterThanAverage = qualityDifference > 0,
        Message = qualityDifference > 0.05
              ? $"Quality is {qualityDifference:P0} better than average"
              : qualityDifference < -0.05
                  ? $"Quality is {Math.Abs(qualityDifference):P0} worse than average"
                  : "Quality is similar to previous syntheses"
      };
    }

    /// <summary>
    /// Generates quality recommendations based on synthesis feedback.
    /// </summary>
    private List<QualityRecommendation> GenerateRecommendations(RealTimeQualityFeedback feedback)
    {
      var recommendations = new List<QualityRecommendation>();

      var finalScore = feedback.FinalMetrics != null
          ? CalculateQualityScore(feedback.FinalMetrics)
          : feedback.MetricsHistory.LastOrDefault()?.QualityScore ?? 0.5;

      // Low quality recommendation
      if (finalScore < 0.7)
      {
        recommendations.Add(new QualityRecommendation
        {
          Type = "IncreaseQuality",
          Message = "Enable quality enhancement or use a higher quality preset to improve results.",
          Priority = finalScore < 0.5 ? "High" : "Medium",
          ExpectedImprovement = (0.85 - finalScore) * 0.5 // Estimate 50% of gap
        });
      }

      // Engine-specific recommendations
      if (finalScore < 0.75)
      {
        var alternativeEngines = new[] { "xtts", "chatterbox", "tortoise" }
            .Where(e => e != feedback.Engine)
            .ToList();

        if (alternativeEngines.Any())
        {
          recommendations.Add(new QualityRecommendation
          {
            Type = "TryDifferentEngine",
            Message = $"Try a different engine ({string.Join(", ", alternativeEngines)}) for potentially better results.",
            Priority = "Medium",
            ExpectedImprovement = 0.1
          });
        }
      }

      // Quality enhancement recommendation
      if (feedback.FinalMetrics != null && !feedback.FinalMetrics.HasDistortion == true && finalScore < 0.8)
      {
        recommendations.Add(new QualityRecommendation
        {
          Type = "EnableEnhancement",
          Message = "Enable quality enhancement for improved clarity and naturalness.",
          Priority = "Low",
          ExpectedImprovement = 0.05
        });
      }

      return recommendations.OrderByDescending(r => r.Priority == "High" ? 3 : r.Priority == "Medium" ? 2 : 1)
          .ThenByDescending(r => r.ExpectedImprovement)
          .ToList();
    }

    public void Dispose()
    {
      if (!_disposed)
      {
        _activeSyntheses.Clear();
        _synthesisHistory.Clear();
        _disposed = true;
      }
    }
  }

  /// <summary>
  /// Event args for quality metrics updates.
  /// </summary>
  public class QualityMetricsUpdatedEventArgs : EventArgs
  {
    public string SynthesisId { get; set; } = string.Empty;
    public RealTimeQualityMetrics Metrics { get; set; } = null!;
  }

  /// <summary>
  /// Event args for synthesis completion.
  /// </summary>
  public class SynthesisCompletedEventArgs : EventArgs
  {
    public string SynthesisId { get; set; } = string.Empty;
    public RealTimeQualityFeedback Feedback { get; set; } = null!;
  }
}