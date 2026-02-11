using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Gateways
{
  /// <summary>
  /// Gateway for job queue management and status operations.
  /// </summary>
  public interface IJobGateway
  {
    /// <summary>
    /// Gets all jobs with optional filtering.
    /// </summary>
    /// <param name="status">Optional status filter.</param>
    /// <param name="limit">Maximum number of jobs to return.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the jobs or error.</returns>
    Task<GatewayResult<IReadOnlyList<JobInfo>>> GetAllAsync(
        JobStatus? status = null,
        int? limit = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets a job by ID.
    /// </summary>
    /// <param name="jobId">The job identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the job or error.</returns>
    Task<GatewayResult<JobDetail>> GetByIdAsync(
        string jobId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Cancels a job.
    /// </summary>
    /// <param name="jobId">The job identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result indicating success or error.</returns>
    Task<GatewayResult<bool>> CancelAsync(
        string jobId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Retries a failed job.
    /// </summary>
    /// <param name="jobId">The job identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the new job or error.</returns>
    Task<GatewayResult<JobDetail>> RetryAsync(
        string jobId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the queue status.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the queue status or error.</returns>
    Task<GatewayResult<JobQueueStatus>> GetQueueStatusAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Clears completed jobs from history.
    /// </summary>
    /// <param name="olderThan">Optional age filter.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Result containing the number of cleared jobs or error.</returns>
    Task<GatewayResult<int>> ClearHistoryAsync(
        TimeSpan? olderThan = null,
        CancellationToken cancellationToken = default);
  }

  #region Enums and Models

  /// <summary>
  /// Job execution status.
  /// </summary>
  public enum JobStatus
  {
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
    Paused
  }

  /// <summary>
  /// Summary information about a job.
  /// </summary>
  public sealed class JobInfo
  {
    public string Id { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string? Description { get; set; }
    public JobStatus Status { get; set; }
    public double Progress { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
  }

  /// <summary>
  /// Detailed job information.
  /// </summary>
  public sealed class JobDetail
  {
    public string Id { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string? Description { get; set; }
    public JobStatus Status { get; set; }
    public double Progress { get; set; }
    public string? ProgressMessage { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public string? ErrorMessage { get; set; }
    public Dictionary<string, object>? Input { get; set; }
    public Dictionary<string, object>? Output { get; set; }
  }

  /// <summary>
  /// Job queue status information.
  /// </summary>
  public sealed class JobQueueStatus
  {
    public int PendingCount { get; set; }
    public int RunningCount { get; set; }
    public int CompletedCount { get; set; }
    public int FailedCount { get; set; }
    public JobInfo? CurrentJob { get; set; }
    public IReadOnlyList<JobInfo>? NextJobs { get; set; }
  }

  #endregion
}
