// VoiceStudio - Panel Architecture: Job Service
// Provides unified job tracking across panels with event-driven status updates

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.Core.Services;

/// <summary>
/// Represents the current state of a tracked job.
/// Named TrackedJobStatus to avoid collision with VoiceStudio.Core.Models.JobStatus.
/// </summary>
public enum TrackedJobStatus
{
    /// <summary>Job is queued but not yet started.</summary>
    Queued,
    
    /// <summary>Job is currently running.</summary>
    Running,
    
    /// <summary>Job completed successfully.</summary>
    Completed,
    
    /// <summary>Job failed with an error.</summary>
    Failed,
    
    /// <summary>Job was cancelled by user or system.</summary>
    Cancelled,
    
    /// <summary>Job is paused (if supported).</summary>
    Paused
}

/// <summary>
/// Represents a job being tracked by the job service.
/// </summary>
public record JobInfo
{
    /// <summary>Unique identifier for the job.</summary>
    public required string JobId { get; init; }
    
    /// <summary>Type of job (e.g., "synthesis", "transcription", "training").</summary>
    public required string JobType { get; init; }
    
    /// <summary>Human-readable name for the job.</summary>
    public required string Name { get; init; }
    
    /// <summary>Current status of the job.</summary>
    public TrackedJobStatus Status { get; init; } = TrackedJobStatus.Queued;
    
    /// <summary>Progress from 0.0 to 1.0.</summary>
    public double Progress { get; init; }
    
    /// <summary>Current status message.</summary>
    public string? StatusMessage { get; init; }
    
    /// <summary>Estimated time remaining in seconds (-1 if unknown).</summary>
    public double EstimatedRemainingSeconds { get; init; } = -1;
    
    /// <summary>When the job was created/queued.</summary>
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.Now;
    
    /// <summary>When the job started running (null if not yet started).</summary>
    public DateTimeOffset? StartedAt { get; init; }
    
    /// <summary>When the job completed/failed/cancelled (null if still running).</summary>
    public DateTimeOffset? CompletedAt { get; init; }
    
    /// <summary>Duration if completed.</summary>
    public TimeSpan? Duration => CompletedAt.HasValue && StartedAt.HasValue
        ? CompletedAt.Value - StartedAt.Value
        : null;
    
    /// <summary>Error message if failed.</summary>
    public string? ErrorMessage { get; init; }
    
    /// <summary>Result object if completed successfully.</summary>
    public object? Result { get; init; }
    
    /// <summary>Panel that initiated this job.</summary>
    public string? SourcePanelId { get; init; }
    
    /// <summary>Whether the job can be cancelled.</summary>
    public bool IsCancellable { get; init; } = true;
    
    /// <summary>Additional metadata for the job.</summary>
    public IReadOnlyDictionary<string, object>? Metadata { get; init; }
}

/// <summary>
/// Options for creating a new job.
/// </summary>
public record JobCreateOptions
{
    /// <summary>Type of job (e.g., "synthesis", "transcription").</summary>
    public required string JobType { get; init; }
    
    /// <summary>Human-readable name for the job.</summary>
    public required string Name { get; init; }
    
    /// <summary>Panel that initiated this job.</summary>
    public string? SourcePanelId { get; init; }
    
    /// <summary>Whether the job can be cancelled.</summary>
    public bool IsCancellable { get; init; } = true;
    
    /// <summary>Additional metadata.</summary>
    public IReadOnlyDictionary<string, object>? Metadata { get; init; }
}

/// <summary>
/// Event arguments for job status changes.
/// </summary>
public class JobStatusChangedEventArgs : EventArgs
{
    public required JobInfo Job { get; init; }
    public TrackedJobStatus PreviousStatus { get; init; }
    public bool IsTerminal => Job.Status is TrackedJobStatus.Completed or TrackedJobStatus.Failed or TrackedJobStatus.Cancelled;
}

/// <summary>
/// Event arguments for job progress updates.
/// </summary>
public class JobProgressChangedEventArgs : EventArgs
{
    public required string JobId { get; init; }
    public double Progress { get; init; }
    public string? StatusMessage { get; init; }
    public double EstimatedRemainingSeconds { get; init; }
}

/// <summary>
/// Service for unified job tracking across panels.
/// Provides a single view of all background operations with event-driven status updates.
/// </summary>
public interface IJobService
{
    /// <summary>
    /// Creates and queues a new job.
    /// </summary>
    /// <param name="options">Options for the new job.</param>
    /// <returns>The job ID.</returns>
    string CreateJob(JobCreateOptions options);
    
    /// <summary>
    /// Gets information about a specific job.
    /// </summary>
    /// <param name="jobId">The job ID.</param>
    /// <returns>Job info or null if not found.</returns>
    JobInfo? GetJob(string jobId);
    
    /// <summary>
    /// Gets all currently tracked jobs.
    /// </summary>
    /// <returns>List of all jobs.</returns>
    IReadOnlyList<JobInfo> GetAllJobs();
    
    /// <summary>
    /// Gets all jobs matching a filter.
    /// </summary>
    /// <param name="predicate">Filter predicate.</param>
    /// <returns>Matching jobs.</returns>
    IReadOnlyList<JobInfo> GetJobs(Func<JobInfo, bool> predicate);
    
    /// <summary>
    /// Gets all jobs of a specific type.
    /// </summary>
    /// <param name="jobType">The job type to filter by.</param>
    /// <returns>Jobs of the specified type.</returns>
    IReadOnlyList<JobInfo> GetJobsByType(string jobType);
    
    /// <summary>
    /// Gets all active (non-terminal) jobs.
    /// </summary>
    /// <returns>Active jobs.</returns>
    IReadOnlyList<JobInfo> GetActiveJobs();
    
    /// <summary>
    /// Gets jobs initiated by a specific panel.
    /// </summary>
    /// <param name="panelId">The panel ID.</param>
    /// <returns>Jobs from the specified panel.</returns>
    IReadOnlyList<JobInfo> GetJobsByPanel(string panelId);
    
    /// <summary>
    /// Marks a job as started (transition from Queued to Running).
    /// </summary>
    /// <param name="jobId">The job ID.</param>
    void StartJob(string jobId);
    
    /// <summary>
    /// Updates the progress of a running job.
    /// </summary>
    /// <param name="jobId">The job ID.</param>
    /// <param name="progress">Progress from 0.0 to 1.0.</param>
    /// <param name="statusMessage">Optional status message.</param>
    /// <param name="estimatedRemainingSeconds">Estimated time remaining (-1 if unknown).</param>
    void UpdateProgress(string jobId, double progress, string? statusMessage = null, double estimatedRemainingSeconds = -1);
    
    /// <summary>
    /// Marks a job as successfully completed.
    /// </summary>
    /// <param name="jobId">The job ID.</param>
    /// <param name="result">Optional result object.</param>
    void CompleteJob(string jobId, object? result = null);
    
    /// <summary>
    /// Marks a job as failed.
    /// </summary>
    /// <param name="jobId">The job ID.</param>
    /// <param name="errorMessage">Error message describing the failure.</param>
    void FailJob(string jobId, string errorMessage);
    
    /// <summary>
    /// Cancels a job if it is cancellable.
    /// </summary>
    /// <param name="jobId">The job ID.</param>
    /// <returns>True if the job was cancelled, false if not cancellable or already terminal.</returns>
    bool CancelJob(string jobId);
    
    /// <summary>
    /// Removes a terminal job from tracking.
    /// </summary>
    /// <param name="jobId">The job ID.</param>
    void RemoveJob(string jobId);
    
    /// <summary>
    /// Removes all terminal jobs from tracking.
    /// </summary>
    void ClearCompletedJobs();
    
    /// <summary>
    /// Event raised when a job's status changes.
    /// </summary>
    event EventHandler<JobStatusChangedEventArgs>? JobStatusChanged;
    
    /// <summary>
    /// Event raised when a job's progress updates.
    /// </summary>
    event EventHandler<JobProgressChangedEventArgs>? JobProgressChanged;
}
