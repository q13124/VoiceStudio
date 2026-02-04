using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Services.Stores
{
  /// <summary>
  /// Centralized store for job-related state.
  /// Implements React/TypeScript jobStore pattern in C#.
  /// </summary>
  public partial class JobStore : ObservableObject
  {
    private readonly IBackendClient _backendClient;
    private readonly StateCacheService? _stateCacheService;

    [ObservableProperty]
    private ObservableCollection<Job> jobs = new();

    [ObservableProperty]
    private Job? selectedJob;

    [ObservableProperty]
    private bool isLoading;

    [ObservableProperty]
    private string? errorMessage;

    [ObservableProperty]
    private DateTime? lastUpdated;

    [ObservableProperty]
    private int pendingCount;

    [ObservableProperty]
    private int runningCount;

    [ObservableProperty]
    private int completedCount;

    [ObservableProperty]
    private int failedCount;

    public JobStore(IBackendClient backendClient, StateCacheService? stateCacheService = null)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
      _stateCacheService = stateCacheService;
    }

    /// <summary>
    /// Loads all jobs.
    /// </summary>
    public async Task LoadJobsAsync(string? jobType = null, string? status = null)
    {
      try
      {
        IsLoading = true;
        ErrorMessage = null;

        // Try to load from cache first
        if (_stateCacheService != null)
        {
          var cacheKey = $"jobs_{jobType ?? "all"}_{status ?? "all"}";
          var cached = await _stateCacheService.GetCachedStateAsync<ObservableCollection<Job>>(cacheKey);
          if (cached != null)
          {
            Jobs = cached;
            UpdateCounts();
            IsLoading = false;
            // Still fetch from backend in background to update
            _ = RefreshJobsAsync(jobType, status);
            return;
          }
        }

        await RefreshJobsAsync(jobType, status);
      }
      catch (Exception ex)
      {
        ErrorMessage = $"Failed to load jobs: {ex.Message}";
      }
      finally
      {
        IsLoading = false;
      }
    }

    /// <summary>
    /// Refreshes jobs from backend.
    /// </summary>
    public async Task RefreshJobsAsync(string? jobType = null, string? status = null)
    {
      try
      {
        // Build query parameters
        var queryParams = new System.Collections.Specialized.NameValueCollection();
        if (!string.IsNullOrEmpty(jobType))
          queryParams.Add("job_type", jobType);
        if (!string.IsNullOrEmpty(status))
          queryParams.Add("status", status);

        var queryString = string.Join("&",
            queryParams.AllKeys.SelectMany(key =>
                queryParams.GetValues(key)?.Select(value => $"{key}={Uri.EscapeDataString(value)}") ?? Array.Empty<string>()
            )
        );

        var url = "/api/jobs";
        if (!string.IsNullOrEmpty(queryString))
          url += $"?{queryString}";

        var jobsArray = await _backendClient.SendRequestAsync<object, Job[]>(
            url,
            null,
            System.Net.Http.HttpMethod.Get
        );

        Jobs.Clear();
        if (jobsArray != null)
        {
          foreach (var job in jobsArray)
          {
            Jobs.Add(job);
          }
        }

        UpdateCounts();
        LastUpdated = DateTime.UtcNow;

        // Cache the result
        if (_stateCacheService != null)
        {
          var cacheKey = $"jobs_{jobType ?? "all"}_{status ?? "all"}";
          await _stateCacheService.CacheStateAsync(cacheKey, Jobs);
        }
      }
      catch (Exception ex)
      {
        ErrorMessage = $"Failed to refresh jobs: {ex.Message}";
      }
    }

    /// <summary>
    /// Updates a job in the store.
    /// </summary>
    public void UpdateJob(Job job)
    {
      var existing = Jobs.FirstOrDefault(j => j.Id == job.Id);
      if (existing != null)
      {
        var index = Jobs.IndexOf(existing);
        Jobs[index] = job;
      }
      else
      {
        Jobs.Add(job);
      }

      UpdateCounts();
      LastUpdated = DateTime.UtcNow;
    }

    /// <summary>
    /// Removes a job from the store.
    /// </summary>
    public void RemoveJob(string jobId)
    {
      var job = Jobs.FirstOrDefault(j => j.Id == jobId);
      if (job != null)
      {
        Jobs.Remove(job);
        UpdateCounts();
        LastUpdated = DateTime.UtcNow;
      }
    }

    /// <summary>
    /// Updates job progress.
    /// </summary>
    public void UpdateJobProgress(string jobId, double progress, string? status = null)
    {
      var job = Jobs.FirstOrDefault(j => j.Id == jobId);
      if (job != null)
      {
        job.Progress = progress;
        if (!string.IsNullOrEmpty(status))
        {
          job.Status = status;
        }
        OnPropertyChanged(nameof(Jobs));
        UpdateCounts();
        LastUpdated = DateTime.UtcNow;
      }
    }

    private void UpdateCounts()
    {
      PendingCount = Jobs.Count(j => j.Status == "pending");
      RunningCount = Jobs.Count(j => j.Status == "running");
      CompletedCount = Jobs.Count(j => j.Status == "completed");
      FailedCount = Jobs.Count(j => j.Status == "failed");
    }

    /// <summary>
    /// Clears all job state.
    /// </summary>
    public void Clear()
    {
      Jobs.Clear();
      SelectedJob = null;
      PendingCount = 0;
      RunningCount = 0;
      CompletedCount = 0;
      FailedCount = 0;
      LastUpdated = null;
    }
  }
}