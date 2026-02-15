// VoiceStudio - Panel Architecture: Job Service Implementation
// Provides unified job tracking with EventAggregator integration

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Extensions.Logging;
using VoiceStudio.Core.Events;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services;

/// <summary>
/// Implementation of IJobService providing unified job tracking across panels.
/// Integrates with EventAggregator for cross-panel notifications.
/// </summary>
public class JobService : IJobService
{
    private readonly IEventAggregator? _eventAggregator;
    private readonly ILogger<JobService>? _logger;
    private readonly ConcurrentDictionary<string, JobInfo> _jobs = new();
    
    private const string JobServicePanelId = "job-service";

    public JobService(
        IEventAggregator? eventAggregator = null,
        ILogger<JobService>? logger = null)
    {
        _eventAggregator = eventAggregator;
        _logger = logger;
    }

    public string CreateJob(JobCreateOptions options)
    {
        var jobId = Guid.NewGuid().ToString("N")[..12];
        
        var job = new JobInfo
        {
            JobId = jobId,
            JobType = options.JobType,
            Name = options.Name,
            Status = TrackedJobStatus.Queued,
            Progress = 0,
            SourcePanelId = options.SourcePanelId,
            IsCancellable = options.IsCancellable,
            Metadata = options.Metadata,
            CreatedAt = DateTimeOffset.Now
        };
        
        _jobs[jobId] = job;
        
        _logger?.LogInformation("Job created: {JobId} ({JobType}: {Name})", jobId, options.JobType, options.Name);
        
        OnJobStatusChanged(job, TrackedJobStatus.Queued);
        
        return jobId;
    }

    public JobInfo? GetJob(string jobId)
    {
        return _jobs.TryGetValue(jobId, out var job) ? job : null;
    }

    public IReadOnlyList<JobInfo> GetAllJobs()
    {
        return _jobs.Values.ToList();
    }

    public IReadOnlyList<JobInfo> GetJobs(Func<JobInfo, bool> predicate)
    {
        return _jobs.Values.Where(predicate).ToList();
    }

    public IReadOnlyList<JobInfo> GetJobsByType(string jobType)
    {
        return _jobs.Values
            .Where(j => j.JobType.Equals(jobType, StringComparison.OrdinalIgnoreCase))
            .ToList();
    }

    public IReadOnlyList<JobInfo> GetActiveJobs()
    {
        return _jobs.Values
            .Where(j => j.Status is TrackedJobStatus.Queued or TrackedJobStatus.Running or TrackedJobStatus.Paused)
            .ToList();
    }

    public IReadOnlyList<JobInfo> GetJobsByPanel(string panelId)
    {
        return _jobs.Values
            .Where(j => j.SourcePanelId == panelId)
            .ToList();
    }

    public void StartJob(string jobId)
    {
        if (!_jobs.TryGetValue(jobId, out var job))
        {
            _logger?.LogWarning("Attempted to start non-existent job: {JobId}", jobId);
            return;
        }

        if (job.Status != TrackedJobStatus.Queued)
        {
            _logger?.LogWarning("Attempted to start job {JobId} with status {Status}", jobId, job.Status);
            return;
        }

        var previousStatus = job.Status;
        var updatedJob = job with
        {
            Status = TrackedJobStatus.Running,
            StartedAt = DateTimeOffset.Now
        };
        
        _jobs[jobId] = updatedJob;
        
        _logger?.LogInformation("Job started: {JobId}", jobId);
        
        OnJobStatusChanged(updatedJob, previousStatus);
        PublishJobStartedEvent(updatedJob);
    }

    public void UpdateProgress(string jobId, double progress, string? statusMessage = null, double estimatedRemainingSeconds = -1)
    {
        if (!_jobs.TryGetValue(jobId, out var job))
        {
            _logger?.LogWarning("Attempted to update progress for non-existent job: {JobId}", jobId);
            return;
        }

        if (job.Status != TrackedJobStatus.Running)
        {
            return; // Silently ignore progress updates for non-running jobs
        }

        var clampedProgress = Math.Clamp(progress, 0.0, 1.0);
        
        var updatedJob = job with
        {
            Progress = clampedProgress,
            StatusMessage = statusMessage ?? job.StatusMessage,
            EstimatedRemainingSeconds = estimatedRemainingSeconds
        };
        
        _jobs[jobId] = updatedJob;
        
        OnJobProgressChanged(jobId, clampedProgress, statusMessage, estimatedRemainingSeconds);
        PublishJobProgressEvent(updatedJob);
    }

    public void CompleteJob(string jobId, object? result = null)
    {
        if (!_jobs.TryGetValue(jobId, out var job))
        {
            _logger?.LogWarning("Attempted to complete non-existent job: {JobId}", jobId);
            return;
        }

        if (job.Status is TrackedJobStatus.Completed or TrackedJobStatus.Failed or TrackedJobStatus.Cancelled)
        {
            _logger?.LogWarning("Attempted to complete terminal job {JobId} with status {Status}", jobId, job.Status);
            return;
        }

        var previousStatus = job.Status;
        var updatedJob = job with
        {
            Status = TrackedJobStatus.Completed,
            Progress = 1.0,
            CompletedAt = DateTimeOffset.Now,
            Result = result
        };
        
        _jobs[jobId] = updatedJob;
        
        _logger?.LogInformation("Job completed: {JobId} (Duration: {Duration})", jobId, updatedJob.Duration);
        
        OnJobStatusChanged(updatedJob, previousStatus);
        PublishJobCompletedEvent(updatedJob, success: true);
    }

    public void FailJob(string jobId, string errorMessage)
    {
        if (!_jobs.TryGetValue(jobId, out var job))
        {
            _logger?.LogWarning("Attempted to fail non-existent job: {JobId}", jobId);
            return;
        }

        if (job.Status is TrackedJobStatus.Completed or TrackedJobStatus.Failed or TrackedJobStatus.Cancelled)
        {
            _logger?.LogWarning("Attempted to fail terminal job {JobId} with status {Status}", jobId, job.Status);
            return;
        }

        var previousStatus = job.Status;
        var updatedJob = job with
        {
            Status = TrackedJobStatus.Failed,
            CompletedAt = DateTimeOffset.Now,
            ErrorMessage = errorMessage
        };
        
        _jobs[jobId] = updatedJob;
        
        _logger?.LogError("Job failed: {JobId} - {ErrorMessage}", jobId, errorMessage);
        
        OnJobStatusChanged(updatedJob, previousStatus);
        PublishJobCompletedEvent(updatedJob, success: false);
    }

    public bool CancelJob(string jobId)
    {
        if (!_jobs.TryGetValue(jobId, out var job))
        {
            _logger?.LogWarning("Attempted to cancel non-existent job: {JobId}", jobId);
            return false;
        }

        if (!job.IsCancellable)
        {
            _logger?.LogWarning("Attempted to cancel non-cancellable job: {JobId}", jobId);
            return false;
        }

        if (job.Status is TrackedJobStatus.Completed or TrackedJobStatus.Failed or TrackedJobStatus.Cancelled)
        {
            _logger?.LogWarning("Attempted to cancel terminal job {JobId} with status {Status}", jobId, job.Status);
            return false;
        }

        var previousStatus = job.Status;
        var updatedJob = job with
        {
            Status = TrackedJobStatus.Cancelled,
            CompletedAt = DateTimeOffset.Now
        };
        
        _jobs[jobId] = updatedJob;
        
        _logger?.LogInformation("Job cancelled: {JobId}", jobId);
        
        OnJobStatusChanged(updatedJob, previousStatus);
        PublishJobCompletedEvent(updatedJob, success: false, wasCancelled: true);
        
        return true;
    }

    public void RemoveJob(string jobId)
    {
        if (_jobs.TryRemove(jobId, out var job))
        {
            _logger?.LogDebug("Job removed from tracking: {JobId}", jobId);
        }
    }

    public void ClearCompletedJobs()
    {
        var toRemove = _jobs.Values
            .Where(j => j.Status is TrackedJobStatus.Completed or TrackedJobStatus.Failed or TrackedJobStatus.Cancelled)
            .Select(j => j.JobId)
            .ToList();
        
        foreach (var jobId in toRemove)
        {
            _jobs.TryRemove(jobId, out _);
        }
        
        _logger?.LogDebug("Cleared {Count} completed jobs", toRemove.Count);
    }

    public event EventHandler<JobStatusChangedEventArgs>? JobStatusChanged;
    public event EventHandler<JobProgressChangedEventArgs>? JobProgressChanged;

    private void OnJobStatusChanged(JobInfo job, TrackedJobStatus previousStatus)
    {
        JobStatusChanged?.Invoke(this, new JobStatusChangedEventArgs
        {
            Job = job,
            PreviousStatus = previousStatus
        });
    }

    private void OnJobProgressChanged(string jobId, double progress, string? statusMessage, double estimatedRemainingSeconds)
    {
        JobProgressChanged?.Invoke(this, new JobProgressChangedEventArgs
        {
            JobId = jobId,
            Progress = progress,
            StatusMessage = statusMessage,
            EstimatedRemainingSeconds = estimatedRemainingSeconds
        });
    }

    private void PublishJobStartedEvent(JobInfo job)
    {
        if (_eventAggregator == null) return;
        
        _eventAggregator.Publish(new JobStartedEvent(
            job.SourcePanelId ?? JobServicePanelId,
            job.JobId,
            job.JobType,
            job.Name));
    }

    private void PublishJobProgressEvent(JobInfo job)
    {
        if (_eventAggregator == null) return;
        
        _eventAggregator.Publish(new JobProgressEvent(
            job.SourcePanelId ?? JobServicePanelId,
            job.JobId,
            job.Progress,
            job.StatusMessage,
            job.EstimatedRemainingSeconds,
            job.JobType));
    }

    private void PublishJobCompletedEvent(JobInfo job, bool success, bool wasCancelled = false)
    {
        if (_eventAggregator == null) return;
        
        var errorMessage = wasCancelled ? "Cancelled by user" : job.ErrorMessage;
        
        if (success)
        {
            _eventAggregator.Publish(JobCompletedEvent.Succeeded(
                job.SourcePanelId ?? JobServicePanelId,
                job.JobId,
                job.JobType,
                job.Result,
                job.Duration));
        }
        else
        {
            _eventAggregator.Publish(JobCompletedEvent.Failed(
                job.SourcePanelId ?? JobServicePanelId,
                job.JobId,
                job.JobType,
                errorMessage ?? "Unknown error",
                job.Duration));
        }
    }
}
