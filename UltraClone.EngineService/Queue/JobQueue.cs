using System.Collections.Concurrent;
using System.Threading.Channels;
using Microsoft.Extensions.Logging;
using VoiceStudio.Contracts;
using Newtonsoft.Json;

namespace UltraClone.EngineService.Queue;

public class JobItem
{
    public string Id { get; set; } = string.Empty;
    public JobType Type { get; set; }
    public string Data { get; set; } = string.Empty;
    public int Priority { get; set; }
    public string ClientId { get; set; } = string.Empty;
    public DateTime SubmittedAt { get; set; } = DateTime.UtcNow;
    public JobStatus Status { get; set; } = JobStatus.Queued;
    public int ProgressPercentage { get; set; }
    public string? ResultData { get; set; }
    public string? ErrorMessage { get; set; }
    public ProcessingMetrics? Metrics { get; set; }
}

public class JobProgressUpdate
{
    public string JobId { get; set; } = string.Empty;
    public JobStatus Status { get; set; }
    public int ProgressPercentage { get; set; }
    public string? ErrorMessage { get; set; }
    public double ProcessingTime { get; set; }
    public int WorkersUsed { get; set; }
    public string AgentUsed { get; set; } = string.Empty;
}

public class QueueStatus
{
    public int QueuedCount { get; set; }
    public int ProcessingCount { get; set; }
    public int CompletedCount { get; set; }
    public int FailedCount { get; set; }
}

public class JobQueue : IHostedService
{
    private readonly ILogger<JobQueue> _logger;
    private readonly Channel<JobItem> _jobChannel;
    private readonly ConcurrentDictionary<string, JobItem> _jobs;
    private readonly ConcurrentDictionary<string, TaskCompletionSource<JobItem>> _jobCompletions;
    private readonly ConcurrentDictionary<string, Channel<JobProgressUpdate>> _progressChannels;
    private readonly WorkerRouter _workerRouter;
    private readonly CancellationTokenSource _cancellationTokenSource;
    private Task? _processingTask;

    public JobQueue(ILogger<JobQueue> logger, WorkerRouter workerRouter)
    {
        _logger = logger;
        _workerRouter = workerRouter;
        _jobChannel = Channel.CreateUnbounded<JobItem>();
        _jobs = new ConcurrentDictionary<string, JobItem>();
        _jobCompletions = new ConcurrentDictionary<string, TaskCompletionSource<JobItem>>();
        _progressChannels = new ConcurrentDictionary<string, Channel<JobProgressUpdate>>();
        _cancellationTokenSource = new CancellationTokenSource();
    }

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Starting JobQueue service");
        _processingTask = ProcessJobsAsync(_cancellationTokenSource.Token);
        await Task.CompletedTask;
    }

    public async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Stopping JobQueue service");
        _cancellationTokenSource.Cancel();
        if (_processingTask != null)
        {
            await _processingTask;
        }
    }

    public async Task<string> SubmitJobAsync(JobItem job)
    {
        _logger.LogInformation("Submitting job {JobId} of type {JobType}", job.Id, job.Type);
        
        _jobs[job.Id] = job;
        _jobCompletions[job.Id] = new TaskCompletionSource<JobItem>();
        _progressChannels[job.Id] = Channel.CreateUnbounded<JobProgressUpdate>();
        
        await _jobChannel.Writer.WriteAsync(job);
        return job.Id;
    }

    public async Task<JobItem> WaitForJobCompletionAsync(string jobId, TimeSpan timeout)
    {
        if (_jobCompletions.TryGetValue(jobId, out var completionSource))
        {
            using var cts = new CancellationTokenSource(timeout);
            cts.Token.Register(() => completionSource.TrySetCanceled());
            
            try
            {
                return await completionSource.Task;
            }
            catch (OperationCanceledException)
            {
                _logger.LogWarning("Job {JobId} timed out after {Timeout}", jobId, timeout);
                return new JobItem
                {
                    Id = jobId,
                    Status = JobStatus.Timeout,
                    ErrorMessage = "Job timed out"
                };
            }
        }
        
        return new JobItem
        {
            Id = jobId,
            Status = JobStatus.Failed,
            ErrorMessage = "Job not found"
        };
    }

    public async IAsyncEnumerable<JobProgressUpdate> GetJobProgressStreamAsync(string jobId)
    {
        if (_progressChannels.TryGetValue(jobId, out var channel))
        {
            await foreach (var update in channel.Reader.ReadAllAsync())
            {
                yield return update;
            }
        }
    }

    public async Task<JobItem> GetJobStatusAsync(string jobId)
    {
        if (_jobs.TryGetValue(jobId, out var job))
        {
            return job;
        }
        
        return new JobItem
        {
            Id = jobId,
            Status = JobStatus.Failed,
            ErrorMessage = "Job not found"
        };
    }

    public async Task<bool> CancelJobAsync(string jobId)
    {
        if (_jobs.TryGetValue(jobId, out var job))
        {
            if (job.Status == JobStatus.Queued || job.Status == JobStatus.Processing)
            {
                job.Status = JobStatus.Cancelled;
                _logger.LogInformation("Cancelled job {JobId}", jobId);
                return true;
            }
        }
        return false;
    }

    public async Task<int> GetEstimatedWaitTimeAsync()
    {
        var queuedJobs = _jobs.Values.Count(j => j.Status == JobStatus.Queued);
        var processingJobs = _jobs.Values.Count(j => j.Status == JobStatus.Processing);
        
        // Estimate based on current load (simplified calculation)
        var estimatedSeconds = (queuedJobs * 30) + (processingJobs * 15);
        return Math.Max(estimatedSeconds, 5); // Minimum 5 seconds
    }

    public async Task<QueueStatus> GetQueueStatusAsync()
    {
        var jobs = _jobs.Values.ToList();
        return new QueueStatus
        {
            QueuedCount = jobs.Count(j => j.Status == JobStatus.Queued),
            ProcessingCount = jobs.Count(j => j.Status == JobStatus.Processing),
            CompletedCount = jobs.Count(j => j.Status == JobStatus.Completed),
            FailedCount = jobs.Count(j => j.Status == JobStatus.Failed)
        };
    }

    private async Task ProcessJobsAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Job processing started");

        await foreach (var job in _jobChannel.Reader.ReadAllAsync(cancellationToken))
        {
            try
            {
                _logger.LogInformation("Processing job {JobId} of type {JobType}", job.Id, job.Type);
                
                job.Status = JobStatus.Processing;
                await UpdateJobProgressAsync(job.Id, JobStatus.Processing, 0);

                // Route job to appropriate worker
                var result = await _workerRouter.ProcessJobAsync(job);

                if (result.Success)
                {
                    job.Status = JobStatus.Completed;
                    job.ResultData = result.ResultData;
                    job.Metrics = result.Metrics;
                    await UpdateJobProgressAsync(job.Id, JobStatus.Completed, 100);
                    
                    _logger.LogInformation("Job {JobId} completed successfully", job.Id);
                }
                else
                {
                    job.Status = JobStatus.Failed;
                    job.ErrorMessage = result.ErrorMessage;
                    await UpdateJobProgressAsync(job.Id, JobStatus.Failed, 0, result.ErrorMessage);
                    
                    _logger.LogWarning("Job {JobId} failed: {Error}", job.Id, result.ErrorMessage);
                }

                // Complete the job
                if (_jobCompletions.TryGetValue(job.Id, out var completionSource))
                {
                    completionSource.SetResult(job);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing job {JobId}", job.Id);
                
                job.Status = JobStatus.Failed;
                job.ErrorMessage = ex.Message;
                await UpdateJobProgressAsync(job.Id, JobStatus.Failed, 0, ex.Message);

                if (_jobCompletions.TryGetValue(job.Id, out var completionSource))
                {
                    completionSource.SetResult(job);
                }
            }
        }

        _logger.LogInformation("Job processing stopped");
    }

    private async Task UpdateJobProgressAsync(string jobId, JobStatus status, int progress, string? errorMessage = null)
    {
        if (_progressChannels.TryGetValue(jobId, out var channel))
        {
            var update = new JobProgressUpdate
            {
                JobId = jobId,
                Status = status,
                ProgressPercentage = progress,
                ErrorMessage = errorMessage
            };

            await channel.Writer.WriteAsync(update);
        }
    }
}
