using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;
using VoiceStudio.App.Services.UndoableActions;
using VoiceStudio.App.Utilities;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Views.Panels
{
    public partial class BatchProcessingViewModel : BaseViewModel, IPanelView
    {
        private readonly IBackendClient _backendClient;
        private readonly ToastNotificationService? _toastNotificationService;
        private readonly UndoRedoService? _undoRedoService;
        private readonly MultiSelectService _multiSelectService;
        private MultiSelectState? _multiSelectState;
        private CancellationTokenSource? _pollingCts;
        private bool _isPolling = false;

        public string PanelId => "batch_processing";
        public string DisplayName => ResourceHelper.GetString("Panel.BatchProcessing.DisplayName", "Batch Processing");
        public PanelRegion Region => PanelRegion.Bottom;

        [ObservableProperty]
        private ObservableCollection<BatchJob> jobs = new();

        [ObservableProperty]
        private string? qualityMetrics;

        [ObservableProperty]
        private BatchJob? selectedJob;

        [ObservableProperty]
        private string? selectedProjectId;

        [ObservableProperty]
        private string? selectedVoiceProfileId;

        [ObservableProperty]
        private string? selectedEngineId;

        [ObservableProperty]
        private string batchText = string.Empty;

        [ObservableProperty]
        private string jobName = string.Empty;

        [ObservableProperty]
        private bool isLoading;

        [ObservableProperty]
        private string? errorMessage;

        [ObservableProperty]
        private BatchQueueStatus? queueStatus;

        [ObservableProperty]
        private bool autoRefresh = false;

        [ObservableProperty]
        private JobStatus? filterStatus;

        // Quality-Based Batch Processing (IDEA 57)
        [ObservableProperty]
        private double? qualityThreshold;

        [ObservableProperty]
        private bool enhanceQuality = false;

        [ObservableProperty]
        private bool showQualityMetrics = true;

        [ObservableProperty]
        private BatchQualityStatistics? qualityStatistics;

        [ObservableProperty]
        private BatchQualityReport? selectedJobQualityReport;

        [ObservableProperty]
        private bool isLoadingQualityReport = false;

        [ObservableProperty]
        private bool hasQualityReport = false;

        // Multi-select support
        [ObservableProperty]
        private int selectedJobCount = 0;

        [ObservableProperty]
        private bool hasMultipleJobSelection = false;

        public bool IsJobSelected(string jobId) => _multiSelectState?.SelectedIds.Contains(jobId) ?? false;

        public ObservableCollection<string> Engines { get; } = new()
        {
            "xtts_v2",
            "chatterbox",
            "tortoise"
        };

        public BatchProcessingViewModel(IViewModelContext context, IBackendClient backendClient)
            : base(context)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

            // Get multi-select service
            _multiSelectService = ServiceProvider.GetMultiSelectService();
            _multiSelectState = _multiSelectService.GetState(PanelId);

            // Get toast notification service (may be null if not initialized)
            try
            {
                _toastNotificationService = ServiceProvider.GetToastNotificationService();
            }
            catch
            {
                // Service may not be initialized yet - that's okay
                _toastNotificationService = null;
            }

            // Get undo/redo service (may be null if not initialized)
            try
            {
                _undoRedoService = ServiceProvider.GetUndoRedoService();
            }
            catch
            {
                // Service may not be initialized yet - that's okay
                _undoRedoService = null;
            }

            LoadJobsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadJobs");
                await LoadJobsAsync(ct);
            }, () => !IsLoading);
            RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("Refresh");
                await RefreshAsync(ct);
            }, () => !IsLoading);
            CreateJobCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CreateJob");
                await CreateJobAsync(ct);
            }, () => !IsLoading && CanCreateJob());
            DeleteJobCommand = new EnhancedAsyncRelayCommand<BatchJob>(async (job, ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("DeleteJob");
                await DeleteJobAsync(job, ct);
            }, job => job != null && !IsLoading);
            StartJobCommand = new EnhancedAsyncRelayCommand<BatchJob>(async (job, ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("StartJob");
                await StartJobAsync(job, ct);
            }, job => job != null && job.Status == JobStatus.Pending && !IsLoading);
            CancelJobCommand = new EnhancedAsyncRelayCommand<BatchJob>(async (job, ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CancelJob");
                await CancelJobAsync(job, ct);
            }, job => job != null && (job.Status == JobStatus.Pending || job.Status == JobStatus.Running) && !IsLoading);
            LoadQueueStatusCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadQueueStatus");
                await LoadQueueStatusAsync(ct);
            }, () => !IsLoading);

            // Quality-Based Batch Processing commands (IDEA 57)
            LoadQualityReportCommand = new EnhancedAsyncRelayCommand<BatchJob>(async (job, ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadQualityReport");
                await LoadQualityReportAsync(job, ct);
            }, job => job != null && !IsLoadingQualityReport);
            LoadQualityStatisticsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadQualityStatistics");
                await LoadQualityStatisticsAsync(ct);
            }, () => !IsLoading);
            RetryWithQualityCommand = new EnhancedAsyncRelayCommand<BatchJob>(async (job, ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("RetryJobWithQuality");
                await RetryJobWithQualityAsync(job, ct);
            }, job => job != null && job.Status == JobStatus.Failed && !IsLoading);

            // Multi-select commands
            SelectAllJobsCommand = new RelayCommand(SelectAllJobs, () => Jobs != null && Jobs.Count > 0);
            ClearJobSelectionCommand = new RelayCommand(ClearJobSelection);

            // Subscribe to selection changes
            _multiSelectService.SelectionChanged += (s, e) =>
            {
                if (e.PanelId == PanelId)
                {
                    UpdateJobSelectionProperties();
                    OnPropertyChanged(nameof(SelectedJobCount));
                    OnPropertyChanged(nameof(HasMultipleJobSelection));
                }
            };
        }

        public IAsyncRelayCommand LoadJobsCommand { get; }
        public IAsyncRelayCommand RefreshCommand { get; }
        public IAsyncRelayCommand CreateJobCommand { get; }
        public IAsyncRelayCommand<BatchJob> DeleteJobCommand { get; }
        public IAsyncRelayCommand<BatchJob> StartJobCommand { get; }
        public IAsyncRelayCommand<BatchJob> CancelJobCommand { get; }
        public IAsyncRelayCommand LoadQueueStatusCommand { get; }

        // Quality-Based Batch Processing commands (IDEA 57)
        public IAsyncRelayCommand<BatchJob> LoadQualityReportCommand { get; }
        public IAsyncRelayCommand LoadQualityStatisticsCommand { get; }
        public IAsyncRelayCommand<BatchJob> RetryWithQualityCommand { get; }

        // Multi-select commands
        public IRelayCommand SelectAllJobsCommand { get; }
        public IRelayCommand ClearJobSelectionCommand { get; }

        partial void OnAutoRefreshChanged(bool value)
        {
            if (value)
            {
                StartPolling();
            }
            else
            {
                StopPolling();
            }
        }

        partial void OnFilterStatusChanged(JobStatus? value)
        {
            _ = LoadJobsAsync(CancellationToken.None);
        }

        partial void OnSelectedProjectIdChanged(string? value)
        {
            _ = LoadJobsAsync(CancellationToken.None);
            CreateJobCommand.NotifyCanExecuteChanged();
        }

        private bool CanCreateJob()
        {
            return !string.IsNullOrWhiteSpace(JobName) &&
                   !string.IsNullOrWhiteSpace(SelectedProjectId) &&
                   !string.IsNullOrWhiteSpace(SelectedVoiceProfileId) &&
                   !string.IsNullOrWhiteSpace(SelectedEngineId) &&
                   !string.IsNullOrWhiteSpace(BatchText);
        }

        partial void OnJobNameChanged(string value)
        {
            CreateJobCommand.NotifyCanExecuteChanged();
        }

        partial void OnSelectedVoiceProfileIdChanged(string? value)
        {
            CreateJobCommand.NotifyCanExecuteChanged();
        }

        partial void OnSelectedEngineIdChanged(string? value)
        {
            CreateJobCommand.NotifyCanExecuteChanged();
        }

        partial void OnBatchTextChanged(string value)
        {
            CreateJobCommand.NotifyCanExecuteChanged();
        }

        private void StartPolling()
        {
            if (_isPolling)
                return;

            _isPolling = true;
            _pollingCts = new CancellationTokenSource();
            _ = PollJobsAsync(_pollingCts.Token);
        }

        private void StopPolling()
        {
            _isPolling = false;
            _pollingCts?.Cancel();
            _pollingCts?.Dispose();
            _pollingCts = null;
        }

        private async Task PollJobsAsync(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested && _isPolling)
            {
                try
                {
                    await LoadJobsAsync(cancellationToken);
                    await LoadQueueStatusAsync(cancellationToken);
                    await Task.Delay(2000, cancellationToken); // Poll every 2 seconds
                }
                catch (TaskCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error polling batch jobs: {ex.Message}");
                    await Task.Delay(5000, cancellationToken); // Wait longer on error
                }
            }
        }

        private async Task LoadJobsAsync(CancellationToken cancellationToken)
        {
            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var jobsList = await _backendClient.GetBatchJobsAsync(SelectedProjectId, FilterStatus, cancellationToken);

                Jobs.Clear();
                foreach (var job in jobsList.OrderByDescending(j => j.Created))
                {
                    Jobs.Add(job);
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to load batch jobs: {ex.Message}";
                await HandleErrorAsync(ex, "LoadJobs");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task RefreshAsync(CancellationToken cancellationToken)
        {
            await LoadJobsAsync(cancellationToken);
            await LoadQueueStatusAsync(cancellationToken);
        }

        private async Task CreateJobAsync(CancellationToken cancellationToken)
        {
            if (!CanCreateJob())
                return;

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var request = new BatchJobRequest
                {
                    Name = JobName,
                    ProjectId = SelectedProjectId!,
                    VoiceProfileId = SelectedVoiceProfileId!,
                    EngineId = SelectedEngineId!,
                    Text = BatchText,
                    Language = "en",
                    QualityThreshold = QualityThreshold, // IDEA 57
                    EnhanceQuality = EnhanceQuality // IDEA 57
                };

                var job = await _backendClient.CreateBatchJobAsync(request, cancellationToken);

                Jobs.Insert(0, job);
                SelectedJob = job;

                // Register undo action
                if (_undoRedoService != null)
                {
                    var action = new CreateBatchJobAction(
                        Jobs,
                        _backendClient,
                        job,
                        onUndo: (j) =>
                        {
                            if (SelectedJob?.Id == j.Id)
                            {
                                SelectedJob = Jobs.FirstOrDefault();
                            }
                        },
                        onRedo: (j) =>
                        {
                            SelectedJob = j;
                        });
                    _undoRedoService.RegisterAction(action);
                }

                // Clear form
                JobName = string.Empty;
                BatchText = string.Empty;

                await LoadQueueStatusAsync(cancellationToken);

                // Show success toast
                _toastNotificationService?.ShowSuccess($"Batch job '{job.Name}' created successfully", "Job Created");
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                var errorMsg = $"Failed to create batch job: {ex.Message}";
                ErrorMessage = errorMsg;
                await HandleErrorAsync(ex, "CreateJob");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task DeleteJobAsync(BatchJob? job, CancellationToken cancellationToken)
        {
            if (job == null)
                return;

            // Show confirmation dialog
            var confirmed = await Utilities.ConfirmationDialog.ShowDeleteConfirmationAsync(
                job.Name ?? "Unnamed Batch Job",
                "batch job"
            );

            if (!confirmed)
                return;

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var success = await _backendClient.DeleteBatchJobAsync(job.Id, cancellationToken);
                if (success)
                {
                    var originalIndex = Jobs.IndexOf(job);
                    Jobs.Remove(job);
                    var previousSelected = SelectedJob;
                    if (SelectedJob?.Id == job.Id)
                    {
                        SelectedJob = null;
                    }
                    await LoadQueueStatusAsync(cancellationToken);

                    // Register undo action
                    if (_undoRedoService != null)
                    {
                        var action = new DeleteBatchJobAction(
                            Jobs,
                            _backendClient,
                            job,
                            originalIndex,
                            onUndo: (j) =>
                            {
                                SelectedJob = j;
                            },
                            onRedo: (j) =>
                            {
                                if (SelectedJob?.Id == j.Id)
                                {
                                    SelectedJob = Jobs.FirstOrDefault();
                                }
                            });
                        _undoRedoService.RegisterAction(action);
                    }

                    // Show success toast
                    var jobName = job.Name ?? "Unnamed Job";
                    _toastNotificationService?.ShowSuccess($"Batch job '{jobName}' deleted", "Job Deleted");
                }
                else
                {
                    var errorMsg = "Failed to delete batch job";
                    ErrorMessage = errorMsg;
                    _toastNotificationService?.ShowError(errorMsg, "Delete Failed");
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                var errorMsg = $"Failed to delete batch job: {ex.Message}";
                ErrorMessage = errorMsg;
                await HandleErrorAsync(ex, "DeleteJob");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task StartJobAsync(BatchJob? job, CancellationToken cancellationToken)
        {
            if (job == null)
                return;

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var updatedJob = await _backendClient.StartBatchJobAsync(job.Id, cancellationToken);

                // Update job in collection
                var index = Jobs.IndexOf(job);
                if (index >= 0)
                {
                    Jobs[index] = updatedJob;
                    if (SelectedJob?.Id == job.Id)
                    {
                        SelectedJob = updatedJob;
                    }
                }

                await LoadQueueStatusAsync(cancellationToken);

                var jobName = job.Name ?? "Unnamed Job";
                _toastNotificationService?.ShowSuccess($"Batch job '{jobName}' started", "Job Started");
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to start batch job: {ex.Message}";
                await HandleErrorAsync(ex, "StartJob");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task CancelJobAsync(BatchJob? job, CancellationToken cancellationToken)
        {
            if (job == null)
                return;

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var updatedJob = await _backendClient.CancelBatchJobAsync(job.Id, cancellationToken);

                // Update job in collection
                var index = Jobs.IndexOf(job);
                if (index >= 0)
                {
                    Jobs[index] = updatedJob;
                    if (SelectedJob?.Id == job.Id)
                    {
                        SelectedJob = updatedJob;
                    }
                }

                await LoadQueueStatusAsync(cancellationToken);

                var jobName = job.Name ?? "Unnamed Job";
                _toastNotificationService?.ShowSuccess($"Batch job '{jobName}' cancelled", "Job Cancelled");
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to cancel batch job: {ex.Message}";
                await HandleErrorAsync(ex, "CancelJob");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task LoadQueueStatusAsync(CancellationToken cancellationToken)
        {
            try
            {
                QueueStatus = await _backendClient.GetBatchQueueStatusAsync(cancellationToken);
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = $"Failed to load queue status: {ex.Message}";
                await HandleErrorAsync(ex, "LoadQueueStatus");
            }
        }

        public string GetStatusDisplay(JobStatus status)
        {
            return status switch
            {
                JobStatus.Pending => "Pending",
                JobStatus.Running => "Running",
                JobStatus.Completed => "Completed",
                JobStatus.Failed => "Failed",
                JobStatus.Cancelled => "Cancelled",
                _ => status.ToString()
            };
        }

        public string FormatProgress(double progress)
        {
            return $"{progress * 100.0:F1}%";
        }

        /// <summary>
        /// Calculate estimated time remaining for a batch job.
        /// </summary>
        public string GetEstimatedTimeRemaining(BatchJob? job)
        {
            if (job == null || job.Started == null || job.Progress <= 0 || job.Progress >= 1.0)
                return string.Empty;

            var elapsed = DateTime.UtcNow - job.Started.Value;
            if (elapsed.TotalSeconds < 1)
                return "Calculating...";

            var estimatedTotal = TimeSpan.FromSeconds(elapsed.TotalSeconds / job.Progress);
            var remaining = estimatedTotal - elapsed;

            if (remaining.TotalSeconds < 0)
                return "Almost done";

            if (remaining.TotalHours >= 1)
                return $"~{remaining.TotalHours:F1}h remaining";
            else if (remaining.TotalMinutes >= 1)
                return $"~{remaining.TotalMinutes:F0}m remaining";
            else
                return $"~{remaining.TotalSeconds:F0}s remaining";
        }

        // Quality-Based Batch Processing helpers (IDEA 57)
        public string GetQualityScoreDisplay(BatchJob? job)
        {
            if (job?.QualityScore == null)
                return "—";
            return $"{job.QualityScore:P0}";
        }

        public string GetQualityStatusDisplay(BatchJob? job)
        {
            if (job?.QualityStatus == null)
                return string.Empty;

            return job.QualityStatus switch
            {
                "pass" => "✓ Pass",
                "fail" => "✗ Fail",
                "warning" => "⚠ Warning",
                _ => job.QualityStatus
            };
        }

        public string GetQualityStatusColor(BatchJob? job)
        {
            if (job?.QualityStatus == null)
                return "Gray";

            return job.QualityStatus switch
            {
                "pass" => "Green",
                "fail" => "Red",
                "warning" => "Orange",
                _ => "Gray"
            };
        }

        public bool HasQualityMetrics(BatchJob? job)
        {
            return job?.QualityScore != null || job?.QualityMetrics != null;
        }

        // Multi-select methods
        public void ToggleJobSelection(string jobId, bool isCtrlPressed, bool isShiftPressed)
        {
            if (_multiSelectState == null)
                return;

            if (isShiftPressed && !string.IsNullOrEmpty(_multiSelectState.RangeAnchorId))
            {
                // Range selection
                var allJobIds = Jobs.Select(j => j.Id).ToList();
                _multiSelectState.SetRange(_multiSelectState.RangeAnchorId, jobId, allJobIds);
            }
            else if (isCtrlPressed)
            {
                // Toggle selection
                _multiSelectState.Toggle(jobId);
            }
            else
            {
                // Single selection (clear others)
                _multiSelectState.SetSingle(jobId);
            }

            UpdateJobSelectionProperties();
            _multiSelectService.OnSelectionChanged(PanelId, _multiSelectState);
        }

        private void SelectAllJobs()
        {
            if (_multiSelectState == null)
                return;

            _multiSelectState.Clear();
            foreach (var job in Jobs)
            {
                _multiSelectState.Add(job.Id);
            }
            if (Jobs.Count > 0)
            {
                _multiSelectState.RangeAnchorId = Jobs[0].Id;
            }

            UpdateJobSelectionProperties();
            _multiSelectService.OnSelectionChanged(PanelId, _multiSelectState);
            SelectAllJobsCommand.NotifyCanExecuteChanged();
        }

        private void ClearJobSelection()
        {
            if (_multiSelectState == null)
                return;

            _multiSelectState.Clear();
            UpdateJobSelectionProperties();
            _multiSelectService.OnSelectionChanged(PanelId, _multiSelectState);
        }

        private void UpdateJobSelectionProperties()
        {
            if (_multiSelectState == null)
            {
                SelectedJobCount = 0;
                HasMultipleJobSelection = false;
            }
            else
            {
                SelectedJobCount = _multiSelectState.Count;
                HasMultipleJobSelection = _multiSelectState.IsMultipleSelection;
            }

            OnPropertyChanged(nameof(SelectedJobCount));
            OnPropertyChanged(nameof(HasMultipleJobSelection));
        }

        partial void OnSelectedJobChanged(BatchJob? value)
        {
            // Auto-load quality report when job is selected (IDEA 57)
            if (value != null && value.Status == JobStatus.Completed)
            {
                _ = LoadQualityReportAsync(value, System.Threading.CancellationToken.None);
            }
            else
            {
                SelectedJobQualityReport = null;
                HasQualityReport = false;
            }
        }

        // Quality-Based Batch Processing methods (IDEA 57)
        private async Task LoadQualityReportAsync(BatchJob? job, CancellationToken cancellationToken)
        {
            if (job == null)
                return;

            IsLoadingQualityReport = true;
            HasQualityReport = false;

            try
            {
                var report = await _backendClient.GetBatchQualityReportAsync(job.Id, cancellationToken);
                SelectedJobQualityReport = report;
                HasQualityReport = report != null;
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "LoadQualityReport");
                SelectedJobQualityReport = null;
                HasQualityReport = false;
            }
            finally
            {
                IsLoadingQualityReport = false;
            }
        }

        private async Task LoadQualityStatisticsAsync(CancellationToken cancellationToken)
        {
            IsLoading = true;

            try
            {
                var stats = await _backendClient.GetBatchQualityStatisticsAsync(SelectedProjectId, FilterStatus, cancellationToken);
                QualityStatistics = stats;
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "LoadQualityStatistics");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task RetryJobWithQualityAsync(BatchJob? job, CancellationToken cancellationToken)
        {
            if (job == null || job.Status != JobStatus.Failed)
                return;

            IsLoading = true;

            try
            {
                var request = new BatchRetryWithQualityRequest
                {
                    QualityThreshold = QualityThreshold ?? job.QualityThreshold,
                    EnhanceQuality = EnhanceQuality,
                    QualityMode = null
                };

                var retryJob = await _backendClient.RetryBatchJobWithQualityAsync(job.Id, request, cancellationToken);

                // Add to jobs list
                Jobs.Insert(0, retryJob);
                SelectedJob = retryJob;

                _toastNotificationService?.ShowSuccess($"Retry job '{retryJob.Name}' created with quality settings", "Job Retried");
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "RetryJobWithQuality");
            }
            finally
            {
                IsLoading = false;
            }
        }

    }
}

