using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services
{
  /// <summary>
  /// Analyzes reference audio quality before voice cloning.
  /// Implements IDEA 41: Reference Audio Quality Analyzer and Recommendations.
  /// </summary>
  public class ReferenceAudioQualityAnalyzer
  {
    private readonly IBackendClient _backendClient;

    public ReferenceAudioQualityAnalyzer(IBackendClient backendClient)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
    }

    /// <summary>
    /// Analyzes reference audio quality and provides recommendations.
    /// </summary>
    /// <param name="audioStream">Stream containing reference audio file</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Complete quality analysis result</returns>
    public async Task<ReferenceAudioQualityResult> AnalyzeAsync(
        Stream audioStream,
        CancellationToken cancellationToken = default)
    {
      if (audioStream == null)
        throw new ArgumentNullException(nameof(audioStream));

      // Reset stream position if possible
      if (audioStream.CanSeek)
        audioStream.Position = 0;

      // Request all quality metrics from backend
      var analysisResponse = await _backendClient.AnalyzeVoiceAsync(
          audioStream,
          metrics: "all", // Request all metrics
          cancellationToken
      );

      // Extract quality metrics
      var metrics = analysisResponse.Metrics;
      var qualityScore = analysisResponse.QualityScore;

      // Calculate comprehensive quality score (0-100)
      var comprehensiveScore = CalculateQualityScore(metrics, qualityScore);

      // Detect quality issues
      var issues = DetectIssues(metrics);

      // Calculate derived scores (clarity, noise, consistency)
      var clarityScore = CalculateClarityScore(metrics);
      var noiseLevel = CalculateNoiseLevel(metrics);
      var consistencyScore = CalculateConsistencyScore(metrics);

      // Generate enhancement suggestions based on issues
      var suggestions = GenerateEnhancementSuggestions(issues, metrics);

      // Determine suitability for cloning
      var isSuitable = comprehensiveScore >= 70.0 && issues.All(i => i.Severity != "Critical");

      return new ReferenceAudioQualityResult
      {
        QualityScore = comprehensiveScore,
        Metrics = ConvertToQualityMetrics(metrics),
        Issues = issues,
        Suggestions = suggestions,
        ClarityScore = clarityScore,
        NoiseLevel = noiseLevel,
        ConsistencyScore = consistencyScore,
        IsSuitableForCloning = isSuitable,
        AnalyzedAt = DateTime.UtcNow
      };
    }

    /// <summary>
    /// Calculates overall quality score (0-100) from metrics.
    /// </summary>
    private double CalculateQualityScore(Dictionary<string, double> metrics, double backendQualityScore)
    {
      // Start with backend quality score (0-1) as base
      double score = backendQualityScore * 100.0;

      // Factor in MOS score if available (1-5 scale)
      if (metrics.TryGetValue("mos", out var mos) && mos > 0)
      {
        var mosNormalized = mos / 5.0 * 100.0;
        score = (score * 0.4) + (mosNormalized * 0.6); // Weight MOS more
      }

      // Factor in SNR if available (higher is better, typically 0-60dB)
      if (metrics.TryGetValue("snr", out var snr))
      {
        var snrNormalized = Math.Min(100.0, Math.Max(0.0, snr / 60.0 * 100.0));
        score = (score * 0.7) + (snrNormalized * 0.3);
      }

      // Factor in naturalness if available (0-1 scale)
      if (metrics.TryGetValue("naturalness", out var naturalness))
      {
        var naturalnessNormalized = naturalness * 100.0;
        score = (score * 0.8) + (naturalnessNormalized * 0.2);
      }

      // Penalize for artifacts
      if (metrics.TryGetValue("artifact_score", out var artifactScore))
      {
        var artifactPenalty = artifactScore * 30.0; // Up to 30 point penalty
        score = Math.Max(0.0, score - artifactPenalty);
      }

      return Math.Min(100.0, Math.Max(0.0, score));
    }

    /// <summary>
    /// Detects quality issues in the audio.
    /// </summary>
    private List<QualityIssue> DetectIssues(Dictionary<string, double> metrics)
    {
      var issues = new List<QualityIssue>();

      // Check for low SNR (background noise)
      if (metrics.TryGetValue("snr", out var snr) && snr < 20.0)
      {
        issues.Add(new QualityIssue
        {
          Type = "BackgroundNoise",
          Description = $"High background noise detected (SNR: {snr:F1} dB). Low signal-to-noise ratio affects voice cloning quality.",
          Severity = snr < 10.0 ? "Critical" : snr < 15.0 ? "High" : "Medium",
          Impact = Math.Min(100.0, (20.0 - snr) * 5.0),
          Details = new Dictionary<string, object> { { "snr_db", snr } }
        });
      }

      // Check for clipping/distortion
      if (metrics.TryGetValue("artifact_score", out var artifactScore) && artifactScore > 0.1)
      {
        var hasClicks = metrics.ContainsKey("has_clicks") && metrics["has_clicks"] > 0.5;
        var hasDistortion = metrics.ContainsKey("has_distortion") && metrics["has_distortion"] > 0.5;

        if (hasClicks || hasDistortion)
        {
          issues.Add(new QualityIssue
          {
            Type = hasDistortion ? "Clipping" : "Clicks",
            Description = hasDistortion
                  ? "Audio clipping/distortion detected. Peak levels are too high, causing distortion."
                  : "Audio clicks/pops detected. Sudden amplitude changes affect quality.",
            Severity = artifactScore > 0.5 ? "Critical" : artifactScore > 0.3 ? "High" : "Medium",
            Impact = artifactScore * 100.0,
            Details = new Dictionary<string, object>
                            {
                                { "artifact_score", artifactScore },
                                { "has_clicks", hasClicks },
                                { "has_distortion", hasDistortion }
                            }
          });
        }
      }

      // Check for low MOS score
      if (metrics.TryGetValue("mos", out var mos) && mos < 3.0)
      {
        issues.Add(new QualityIssue
        {
          Type = "LowQuality",
          Description = $"Low overall quality score (MOS: {mos:F1}/5.0). Audio quality may not be suitable for voice cloning.",
          Severity = mos < 2.0 ? "Critical" : mos < 2.5 ? "High" : "Medium",
          Impact = (3.0 - mos) * 25.0,
          Details = new Dictionary<string, object> { { "mos", mos } }
        });
      }

      // Check for low naturalness
      if (metrics.TryGetValue("naturalness", out var naturalness) && naturalness < 0.6)
      {
        issues.Add(new QualityIssue
        {
          Type = "LowNaturalness",
          Description = $"Low naturalness score ({naturalness:F2}). Audio may sound unnatural, affecting cloning quality.",
          Severity = naturalness < 0.4 ? "High" : "Medium",
          Impact = (0.6 - naturalness) * 50.0,
          Details = new Dictionary<string, object> { { "naturalness", naturalness } }
        });
      }

      return issues;
    }

    /// <summary>
    /// Calculates clarity score (0-100) based on metrics.
    /// </summary>
    private double CalculateClarityScore(Dictionary<string, double> metrics)
    {
      double clarity = 70.0; // Base score

      // Higher SNR = clearer
      if (metrics.TryGetValue("snr", out var snr))
      {
        var snrFactor = Math.Min(1.0, snr / 40.0);
        clarity = (clarity * 0.5) + (snrFactor * 100.0 * 0.5);
      }

      // Lower artifacts = clearer
      if (metrics.TryGetValue("artifact_score", out var artifactScore))
      {
        clarity *= 1.0 - artifactScore;
      }

      // Higher MOS = clearer
      if (metrics.TryGetValue("mos", out var mos))
      {
        var mosFactor = mos / 5.0;
        clarity = (clarity * 0.6) + (mosFactor * 100.0 * 0.4);
      }

      return Math.Min(100.0, Math.Max(0.0, clarity));
    }

    /// <summary>
    /// Calculates noise level (0-100, where lower is better).
    /// </summary>
    private double CalculateNoiseLevel(Dictionary<string, double> metrics)
    {
      if (metrics.TryGetValue("snr", out var snr))
      {
        // Convert SNR to noise level (inverse relationship)
        // SNR of 40dB = 0 noise, SNR of 0dB = 100 noise
        return (double)Math.Max(0.0, Math.Min(100.0, (40.0 - snr) / 40.0 * 100.0));
      }

      // Default noise level if SNR not available
      return 50.0;
    }

    /// <summary>
    /// Calculates consistency score (0-100) based on stability metrics.
    /// </summary>
    private double CalculateConsistencyScore(Dictionary<string, double> metrics)
    {
      double consistency = 75.0; // Base score

      // Lower artifact score = more consistent
      if (metrics.TryGetValue("artifact_score", out var artifactScore))
      {
        consistency *= 1.0 - (artifactScore * 0.5);
      }

      // Higher naturalness = more consistent
      if (metrics.TryGetValue("naturalness", out var naturalness))
      {
        consistency = (consistency * 0.6) + (naturalness * 100.0 * 0.4);
      }

      return Math.Min(100.0, Math.Max(0.0, consistency));
    }

    /// <summary>
    /// Generates enhancement suggestions based on detected issues.
    /// </summary>
    private List<EnhancementSuggestion> GenerateEnhancementSuggestions(
        List<QualityIssue> issues,
        Dictionary<string, double> metrics)
    {
      var suggestions = new List<EnhancementSuggestion>();

      // Denoise suggestion for high noise
      var noiseIssue = issues.FirstOrDefault(i => i.Type == "BackgroundNoise");
      if (noiseIssue != null)
      {
        suggestions.Add(new EnhancementSuggestion
        {
          Type = "Denoise",
          Description = "Apply noise reduction to remove background noise. This will improve SNR and overall quality.",
          Priority = noiseIssue.Severity == "Critical" ? "High" : "Medium",
          ExpectedImprovement = Math.Min(30.0, noiseIssue.Impact * 0.3),
          Recommended = true,
          Parameters = new Dictionary<string, object>
                    {
                        { "aggressiveness", noiseIssue.Severity == "Critical" ? "high" : "medium" }
                    }
        });
      }

      // Normalize suggestion for clipping/low volume
      var clippingIssue = issues.FirstOrDefault(i => i.Type == "Clipping");
      if (clippingIssue != null)
      {
        suggestions.Add(new EnhancementSuggestion
        {
          Type = "Normalize",
          Description = "Normalize audio levels to prevent clipping while maximizing volume. This will remove distortion.",
          Priority = "High",
          ExpectedImprovement = clippingIssue.Impact * 0.4,
          Recommended = true,
          Parameters = new Dictionary<string, object>
                    {
                        { "target_lufs", -23.0 },
                        { "prevent_clipping", true }
                    }
        });
      }

      // Enhance suggestion for general quality improvement
      if (metrics.TryGetValue("mos", out var mos) && mos < 4.0)
      {
        suggestions.Add(new EnhancementSuggestion
        {
          Type = "Enhance",
          Description = "Apply general audio enhancement to improve clarity, dynamics, and overall quality.",
          Priority = mos < 3.0 ? "High" : "Medium",
          ExpectedImprovement = (4.0 - mos) * 5.0,
          Recommended = mos < 3.5,
          Parameters = new Dictionary<string, object>
                    {
                        { "denoise", true },
                        { "normalize", true },
                        { "enhance_clarity", true }
                    }
        });
      }

      // Remove silence suggestion (always recommended for voice cloning)
      suggestions.Add(new EnhancementSuggestion
      {
        Type = "RemoveSilence",
        Description = "Remove leading/trailing silence and long pauses. This improves training efficiency.",
        Priority = "Low",
        ExpectedImprovement = 5.0,
        Recommended = true,
        Parameters = new Dictionary<string, object>
                {
                    { "threshold_db", -40.0 },
                    { "min_silence_duration_ms", 100 }
                }
      });

      return suggestions.OrderByDescending(s => s.Recommended)
          .ThenByDescending(s => s.ExpectedImprovement)
          .ToList();
    }

    /// <summary>
    /// Converts backend metrics dictionary to QualityMetrics object.
    /// </summary>
    private QualityMetrics? ConvertToQualityMetrics(Dictionary<string, double> metrics)
    {
      if (metrics == null || metrics.Count == 0)
        return null;

      return new QualityMetrics
      {
        MosScore = metrics.TryGetValue("mos", out var mos) ? mos : null,
        Similarity = metrics.TryGetValue("similarity", out var similarity) ? similarity : null,
        Naturalness = metrics.TryGetValue("naturalness", out var naturalness) ? naturalness : null,
        SnrDb = metrics.TryGetValue("snr", out var snr) ? snr : null,
        ArtifactScore = metrics.TryGetValue("artifact_score", out var artifact) ? artifact : null,
        HasClicks = metrics.TryGetValue("has_clicks", out var hasClicks) && hasClicks > 0.5,
        HasDistortion = metrics.TryGetValue("has_distortion", out var hasDistortion) && hasDistortion > 0.5
      };
    }
  }
}