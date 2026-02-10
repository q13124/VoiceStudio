// Phase 5.2: Power User Features
// Task 5.2.4: Batch Processing - Multi-file queue with progress tracking

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services;

/// <summary>
/// Status of a batch job item.
/// </summary>
public enum BatchItemStatus
{
    Pending,
    Processing,
    Completed,
    Failed,
    Cancelled,
    Skipped
}

/// <summary>
/// Represents an item in the batch processing queue.
/// </summary>
public class BatchItem
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = string.Empty;
    public string SourcePath { get; set; } = string.Empty;
    public string? OutputPath { get; set; }
    public BatchItemStatus Status { get; set; } = BatchItemStatus.Pending;
    public double Progress { get; set; }
    public string? ErrorMessage { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public Dictionary<string, object?> Parameters { get; set; } = new();
    
    public TimeSpan? Duration => StartedAt.HasValue && CompletedAt.HasValue 
        ? CompletedAt.Value - StartedAt.Value 
        : null;
}

/// <summary>
/// Represents a local batch job containing multiple items.
/// Named LocalBatchJob to avoid conflict with VoiceStudio.Core.Models.LocalBatchJob.
/// </summary>
public class LocalBatchJob
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = string.Empty;
    public string Operation { get; set; } = string.Empty;
    public ObservableCollection<BatchItem> Items { get; set; } = new();
    public BatchItemStatus Status { get; set; } = BatchItemStatus.Pending;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public int ConcurrencyLimit { get; set; } = 1;
    public bool StopOnError { get; set; }
    
    public int CompletedCount => Items.Count(i => i.Status == BatchItemStatus.Completed);
    public int FailedCount => Items.Count(i => i.Status == BatchItemStatus.Failed);
    public int TotalCount => Items.Count;
    public double OverallProgress => TotalCount > 0 ? (double)CompletedCount / TotalCount * 100 : 0;
}

/// <summary>
/// Event args for batch processing progress.
/// </summary>
public class BatchProgressEventArgs : EventArgs
{
    public LocalBatchJob Job { get; set; } = null!;
    public BatchItem? CurrentItem { get; set; }
    public int ProcessedCount { get; set; }
    public int TotalCount { get; set; }
    public double OverallProgress { get; set; }
}

/// <summary>
/// Event args for batch item completion.
/// </summary>
public class BatchItemCompletedEventArgs : EventArgs
{
    public LocalBatchJob Job { get; set; } = null!;
    public BatchItem Item { get; set; } = null!;
    public bool Success { get; set; }
    public Exception? Error { get; set; }
}

/// <summary>
/// Service for batch processing multiple files with progress tracking.
/// </summary>
public class BatchProcessingService
{
    private readonly ObservableCollection<LocalBatchJob> _jobs = new();
    private readonly SemaphoreSlim _jobSemaphore = new(1, 1);
    private LocalBatchJob? _currentJob;
    private CancellationTokenSource? _cts;

    public event EventHandler<BatchProgressEventArgs>? Progress;
    public event EventHandler<BatchItemCompletedEventArgs>? ItemCompleted;
    public event EventHandler<LocalBatchJob>? JobStarted;
    public event EventHandler<LocalBatchJob>? JobCompleted;

    /// <summary>
    /// Gets all batch jobs.
    /// </summary>
    public ObservableCollection<LocalBatchJob> Jobs => _jobs;

    /// <summary>
    /// Gets the currently running job.
    /// </summary>
    public LocalBatchJob? CurrentJob => _currentJob;

    /// <summary>
    /// Gets whether a batch job is currently running.
    /// </summary>
    public bool IsProcessing => _currentJob != null && _currentJob.Status == BatchItemStatus.Processing;

    /// <summary>
    /// Creates a new batch job.
    /// </summary>
    public LocalBatchJob CreateJob(string name, string operation)
    {
        var job = new LocalBatchJob
        {
            Name = name,
            Operation = operation
        };
        _jobs.Add(job);
        return job;
    }

    /// <summary>
    /// Adds an item to a batch job.
    /// </summary>
    public BatchItem AddItem(LocalBatchJob job, string name, string sourcePath, Dictionary<string, object?>? parameters = null)
    {
        var item = new BatchItem
        {
            Name = name,
            SourcePath = sourcePath,
            Parameters = parameters ?? new()
        };
        job.Items.Add(item);
        return item;
    }

    /// <summary>
    /// Adds multiple items to a batch job.
    /// </summary>
    public void AddItems(LocalBatchJob job, IEnumerable<(string Name, string SourcePath)> items)
    {
        foreach (var (name, sourcePath) in items)
        {
            AddItem(job, name, sourcePath);
        }
    }

    /// <summary>
    /// Removes an item from a batch job.
    /// </summary>
    public void RemoveItem(LocalBatchJob job, string itemId)
    {
        var item = job.Items.FirstOrDefault(i => i.Id == itemId);
        if (item != null && item.Status == BatchItemStatus.Pending)
        {
            job.Items.Remove(item);
        }
    }

    /// <summary>
    /// Clears completed items from a job.
    /// </summary>
    public void ClearCompleted(LocalBatchJob job)
    {
        var completed = job.Items.Where(i => 
            i.Status == BatchItemStatus.Completed || 
            i.Status == BatchItemStatus.Failed ||
            i.Status == BatchItemStatus.Skipped).ToList();
        
        foreach (var item in completed)
        {
            job.Items.Remove(item);
        }
    }

    /// <summary>
    /// Starts processing a batch job.
    /// </summary>
    public async Task StartJobAsync(LocalBatchJob job, Func<BatchItem, IProgress<double>, CancellationToken, Task<string?>> processItem)
    {
        if (IsProcessing)
            throw new InvalidOperationException("A batch job is already running");

        await _jobSemaphore.WaitAsync();
        try
        {
            _currentJob = job;
            _cts = new CancellationTokenSource();
            
            job.Status = BatchItemStatus.Processing;
            job.StartedAt = DateTime.UtcNow;
            JobStarted?.Invoke(this, job);

            var semaphore = new SemaphoreSlim(job.ConcurrencyLimit, job.ConcurrencyLimit);
            var tasks = new List<Task>();

            foreach (var item in job.Items.Where(i => i.Status == BatchItemStatus.Pending))
            {
                if (_cts.Token.IsCancellationRequested)
                    break;

                await semaphore.WaitAsync(_cts.Token);
                
                var itemTask = ProcessItemAsync(job, item, processItem, semaphore, _cts.Token);
                tasks.Add(itemTask);

                if (job.StopOnError && job.FailedCount > 0)
                    break;
            }

            await Task.WhenAll(tasks);

            job.Status = job.FailedCount > 0 ? BatchItemStatus.Failed : BatchItemStatus.Completed;
            job.CompletedAt = DateTime.UtcNow;
            
            JobCompleted?.Invoke(this, job);
        }
        finally
        {
            _currentJob = null;
            _cts?.Dispose();
            _cts = null;
            _jobSemaphore.Release();
        }
    }

    private async Task ProcessItemAsync(
        LocalBatchJob job,
        BatchItem item,
        Func<BatchItem, IProgress<double>, CancellationToken, Task<string?>> processItem,
        SemaphoreSlim semaphore,
        CancellationToken cancellationToken)
    {
        try
        {
            item.Status = BatchItemStatus.Processing;
            item.StartedAt = DateTime.UtcNow;
            item.Progress = 0;

            RaiseProgress(job, item);

            var progress = new Progress<double>(p =>
            {
                item.Progress = p;
                RaiseProgress(job, item);
            });

            var outputPath = await processItem(item, progress, cancellationToken);

            item.OutputPath = outputPath;
            item.Status = BatchItemStatus.Completed;
            item.Progress = 100;
            item.CompletedAt = DateTime.UtcNow;

            ItemCompleted?.Invoke(this, new BatchItemCompletedEventArgs
            {
                Job = job,
                Item = item,
                Success = true
            });
        }
        catch (OperationCanceledException)
        {
            item.Status = BatchItemStatus.Cancelled;
            item.CompletedAt = DateTime.UtcNow;
        }
        catch (Exception ex)
        {
            item.Status = BatchItemStatus.Failed;
            item.ErrorMessage = ex.Message;
            item.CompletedAt = DateTime.UtcNow;

            ItemCompleted?.Invoke(this, new BatchItemCompletedEventArgs
            {
                Job = job,
                Item = item,
                Success = false,
                Error = ex
            });
        }
        finally
        {
            semaphore.Release();
            RaiseProgress(job, item);
        }
    }

    /// <summary>
    /// Cancels the current batch job.
    /// </summary>
    public void CancelJob()
    {
        _cts?.Cancel();
        
        if (_currentJob != null)
        {
            foreach (var item in _currentJob.Items.Where(i => i.Status == BatchItemStatus.Pending))
            {
                item.Status = BatchItemStatus.Cancelled;
            }
        }
    }

    /// <summary>
    /// Retries failed items in a job.
    /// </summary>
    public void RetryFailed(LocalBatchJob job)
    {
        foreach (var item in job.Items.Where(i => i.Status == BatchItemStatus.Failed))
        {
            item.Status = BatchItemStatus.Pending;
            item.ErrorMessage = null;
            item.Progress = 0;
            item.StartedAt = null;
            item.CompletedAt = null;
        }
    }

    /// <summary>
    /// Deletes a job.
    /// </summary>
    public void DeleteJob(string jobId)
    {
        var job = _jobs.FirstOrDefault(j => j.Id == jobId);
        if (job != null && job != _currentJob)
        {
            _jobs.Remove(job);
        }
    }

    /// <summary>
    /// Clears all completed jobs.
    /// </summary>
    public void ClearCompletedJobs()
    {
        var completed = _jobs.Where(j => 
            j.Status == BatchItemStatus.Completed || 
            j.Status == BatchItemStatus.Failed ||
            j.Status == BatchItemStatus.Cancelled).ToList();
        
        foreach (var job in completed)
        {
            if (job != _currentJob)
            {
                _jobs.Remove(job);
            }
        }
    }

    private void RaiseProgress(LocalBatchJob job, BatchItem? currentItem)
    {
        Progress?.Invoke(this, new BatchProgressEventArgs
        {
            Job = job,
            CurrentItem = currentItem,
            ProcessedCount = job.CompletedCount + job.FailedCount,
            TotalCount = job.TotalCount,
            OverallProgress = job.OverallProgress
        });
    }
}
