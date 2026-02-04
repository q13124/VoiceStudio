using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Status of a batch processing job.
  /// </summary>
  public enum JobStatus
  {
    Pending = 0,
    Running = 1,
    Completed = 2,
    Failed = 3,
    Cancelled = 4
  }

  /// <summary>
  /// A batch processing job.
  /// </summary>
  public class BatchJob
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string ProjectId { get; set; } = string.Empty;
    public string VoiceProfileId { get; set; } = string.Empty;
    public string EngineId { get; set; } = string.Empty;
    public string Text { get; set; } = string.Empty;
    public string Language { get; set; } = "en";
    public string? OutputPath { get; set; }
    public JobStatus Status { get; set; } = JobStatus.Pending;
    public double Progress { get; set; }  // 0.0 to 1.0
    public string? ErrorMessage { get; set; }
    public string? ResultAudioId { get; set; }
    public DateTime Created { get; set; }
    public DateTime? Started { get; set; }
    public DateTime? Completed { get; set; }

    // Quality-Based Batch Processing (IDEA 57)
    public Dictionary<string, object>? QualityMetrics { get; set; } // Quality metrics dict
    public double? QualityScore { get; set; } // Overall quality score (0.0-1.0)
    public double? QualityThreshold { get; set; } // Minimum quality threshold
    public string? QualityStatus { get; set; } // "pass", "fail", "warning"
  }

  /// <summary>
  /// Request to create a batch job.
  /// </summary>
  public class BatchJobRequest
  {
    public string Name { get; set; } = string.Empty;
    public string ProjectId { get; set; } = string.Empty;
    public string VoiceProfileId { get; set; } = string.Empty;
    public string EngineId { get; set; } = string.Empty;
    public string Text { get; set; } = string.Empty;
    public string Language { get; set; } = "en";
    public string? OutputPath { get; set; }

    // Quality-Based Batch Processing (IDEA 57)
    public double? QualityThreshold { get; set; } // Minimum quality threshold (0.0-1.0)
    public bool EnhanceQuality { get; set; }  // Enable quality enhancement
  }

  /// <summary>
  /// Status of the batch processing queue.
  /// </summary>
  public class BatchQueueStatus
  {
    public int QueueLength { get; set; }
    public int Pending { get; set; }
    public int Running { get; set; }
    public int Completed { get; set; }
    public int Failed { get; set; }
    public int Total { get; set; }
  }
}