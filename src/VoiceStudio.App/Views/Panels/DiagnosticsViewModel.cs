using System;
using System.Collections.Generic;
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
using VoiceStudio.App.Utilities;
using VoiceStudio.App.ViewModels;
using Microsoft.UI.Dispatching;

namespace VoiceStudio.App.Views.Panels
{
    public partial class DiagnosticsViewModel : BaseViewModel, IPanelView, IDisposable
    {
        private readonly IBackendClient _backendClient;
        private readonly IErrorLoggingService? _errorLoggingService;
        private readonly IAnalyticsService? _analyticsService;
        private readonly IFeatureFlagsService? _featureFlagsService;
        private readonly MultiSelectService _multiSelectService;
        private readonly ToastNotificationService? _toastNotificationService;
        private MultiSelectState? _logsMultiSelectState;
        private MultiSelectState? _errorLogsMultiSelectState;
        private CancellationTokenSource? _telemetryCancellationTokenSource;
        private long _peakMemoryBytes = 0;
        private bool _disposed = false;
        private readonly List<BudgetViolationEventArgs> _budgetViolations = new();

        public string PanelId => "diagnostics";
        public string DisplayName => ResourceHelper.GetString("Panel.Diagnostics.DisplayName", "Diagnostics");
        public PanelRegion Region => PanelRegion.Bottom;

        [ObservableProperty]
        private bool isHealthy;

        [ObservableProperty]
        private string? healthStatus;

        [ObservableProperty]
        private bool isConnected;

        [ObservableProperty]
        private string connectionStatus = ResourceHelper.GetString("Diagnostics.ConnectionStatusUnknown", "Unknown");

        [ObservableProperty]
        private bool isLoading;

        [ObservableProperty]
        private string? errorMessage;

        [ObservableProperty]
        private Telemetry? telemetry;

        [ObservableProperty]
        private double cpuUsage;

        [ObservableProperty]
        private double gpuUsage;

        [ObservableProperty]
        private double ramUsage;

        [ObservableProperty]
        private long currentMemoryBytes;

        [ObservableProperty]
        private long peakMemoryBytes;

        [ObservableProperty]
        private long memoryByUI;

        [ObservableProperty]
        private long memoryByAudio;

        [ObservableProperty]
        private long memoryByEngines;

        [ObservableProperty]
        private string memoryFormatted;

        [ObservableProperty]
        private string peakMemoryFormatted;

        [ObservableProperty]
        private string vramWarning = string.Empty;

        [ObservableProperty]
        private bool showVramWarning;

        [ObservableProperty]
        private ObservableCollection<LogEntry> logs = new();

        [ObservableProperty]
        private ObservableCollection<ErrorLogEntryViewModel> errorLogs = new();

        [ObservableProperty]
        private bool autoRefreshTelemetry;

        [ObservableProperty]
        private string errorLogFilter = string.Empty;

        [ObservableProperty]
        private string selectedErrorLevel = "All"; // All, Error, Warning, Info

        [ObservableProperty]
        private int errorLogCount;

        [ObservableProperty]
        private int errorCount;

        [ObservableProperty]
        private int warningCount;

        [ObservableProperty]
        private int infoCount;

        [ObservableProperty]
        private bool isDegradedMode;

        [ObservableProperty]
        private string? degradationReason;

        [ObservableProperty]
        private int queuedOperationsCount;

        // Multi-select support for logs
        [ObservableProperty]
        private int selectedLogCount = 0;

        [ObservableProperty]
        private bool hasMultipleLogSelection = false;

        // Multi-select support for error logs
        [ObservableProperty]
        private int selectedErrorLogCount = 0;

        [ObservableProperty]
        private bool hasMultipleErrorLogSelection = false;

        // Analytics tab
        [ObservableProperty]
        private ObservableCollection<AnalyticsEvent> recentAnalyticsEvents = new();

        // Performance tab
        [ObservableProperty]
        private ObservableCollection<BudgetViolationViewModel> budgetViolations = new();

        // Feature flags tab
        [ObservableProperty]
        private ObservableCollection<FeatureFlagViewModel> featureFlags = new();

        // Environment tab
        [ObservableProperty]
        private string appVersion = string.Empty;

        [ObservableProperty]
        private string dotNetVersion = string.Empty;

        [ObservableProperty]
        private string osVersion = string.Empty;

        [ObservableProperty]
        private ObservableCollection<EnvironmentInfoItem> environmentInfo = new();

        public bool IsLogSelected(string logId) => _logsMultiSelectState?.SelectedIds.Contains(logId) ?? false;
        public bool IsErrorLogSelected(string errorLogId) => _errorLogsMultiSelectState?.SelectedIds.Contains(errorLogId) ?? false;

        public DiagnosticsViewModel(IBackendClient backendClient)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

            // Get error logging service using helper (reduces code duplication)
            _errorLoggingService = ServiceInitializationHelper.TryGetService(() => ServiceProvider.GetErrorLoggingService());
            if (_errorLoggingService != null)
            {
                _errorLoggingService.ErrorLogged += OnErrorLogged;
                LoadErrorLogs();
            }

            // Get analytics service using helper
            _analyticsService = ServiceInitializationHelper.TryGetService(() => ServiceProvider.TryGetAnalyticsService());
            if (_analyticsService != null)
            {
                _analyticsService.EventTracked += OnAnalyticsEventTracked;
                LoadAnalyticsEvents();
            }

            // Get feature flags service
            // Get feature flags service using helper (reduces code duplication)
            _featureFlagsService = ServiceInitializationHelper.TryGetService(() => ServiceProvider.GetFeatureFlagsService());
            if (_featureFlagsService != null)
            {
                LoadFeatureFlags();
            }

            // Subscribe to performance profiler budget violations
            PerformanceProfiler.BudgetViolated += OnBudgetViolated;

            // Load environment info
            LoadEnvironmentInfo();

            // Show Errors tab by default
            // (Tab visibility is handled in XAML code-behind)

            CheckHealthCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CheckHealth");
                await CheckHealthAsync(ct);
            });
            LoadTelemetryCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadTelemetry");
                await LoadTelemetryAsync(ct);
            });
            ClearLogsCommand = new RelayCommand(ClearLogs);
            LoadErrorLogsCommand = new RelayCommand(LoadErrorLogs);
            ClearErrorLogsCommand = new RelayCommand(ClearErrorLogs);
            ExportErrorLogsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("ExportErrorLogs");
                await ExportErrorLogsAsync(ct);
            });
            RefreshAnalyticsCommand = new RelayCommand(LoadAnalyticsEvents);
            RefreshPerformanceCommand = new RelayCommand(LoadPerformanceData);
            RefreshFeatureFlagsCommand = new RelayCommand(LoadFeatureFlags);
            RefreshEnvironmentCommand = new RelayCommand(LoadEnvironmentInfo);
            ToggleFeatureFlagCommand = new RelayCommand<string>(ToggleFeatureFlag);

            // Get multi-select service
            _multiSelectService = ServiceProvider.GetMultiSelectService();
            _logsMultiSelectState = _multiSelectService.GetState($"{PanelId}_logs");
            _errorLogsMultiSelectState = _multiSelectService.GetState($"{PanelId}_errorlogs");

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

            // Multi-select commands for logs
            SelectAllLogsCommand = new RelayCommand(SelectAllLogs, () => Logs != null && Logs.Count > 0);
            ClearLogSelectionCommand = new RelayCommand(ClearLogSelection);
            DeleteSelectedLogsCommand = new RelayCommand(DeleteSelectedLogs, () => SelectedLogCount > 0);

            // Multi-select commands for error logs
            SelectAllErrorLogsCommand = new RelayCommand(SelectAllErrorLogs, () => ErrorLogs != null && ErrorLogs.Count > 0);
            ClearErrorLogSelectionCommand = new RelayCommand(ClearErrorLogSelection);
            DeleteSelectedErrorLogsCommand = new RelayCommand(DeleteSelectedErrorLogs, () => SelectedErrorLogCount > 0);
            ExportSelectedErrorLogsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("ExportSelectedErrorLogs");
                await ExportSelectedErrorLogsAsync(ct);
            }, () => SelectedErrorLogCount > 0);

            // Subscribe to selection changes
            _multiSelectService.SelectionChanged += (s, e) =>
            {
                if (e.PanelId == $"{PanelId}_logs")
                {
                    UpdateLogSelectionProperties();
                    OnPropertyChanged(nameof(SelectedLogCount));
                    OnPropertyChanged(nameof(HasMultipleLogSelection));
                }
                else if (e.PanelId == $"{PanelId}_errorlogs")
                {
                    UpdateErrorLogSelectionProperties();
                    OnPropertyChanged(nameof(SelectedErrorLogCount));
                    OnPropertyChanged(nameof(HasMultipleErrorLogSelection));
                }
            };

            // Initialize memory monitoring
            UpdateMemoryMetrics();

            // Subscribe to graceful degradation service
            try
            {
                var degradationService = ServiceProvider.GetGracefulDegradationService();
                if (degradationService != null)
                {
                    degradationService.DegradedModeChanged += (s, isDegraded) =>
                    {
                        IsDegradedMode = isDegraded;
                        DegradationReason = degradationService.DegradationReason;
                    };
                    IsDegradedMode = degradationService.IsDegradedMode;
                    DegradationReason = degradationService.DegradationReason;
                }

                var queueService = ServiceProvider.GetOperationQueueService();
                if (queueService != null)
                {
                    queueService.QueueCountChanged += (s, count) =>
                    {
                        QueuedOperationsCount = count;
                    };
                    QueuedOperationsCount = queueService.QueueCount;
                }
            }
            catch
            {
                // Services may not be available
            }
        }

        public IAsyncRelayCommand CheckHealthCommand { get; }
        public IAsyncRelayCommand LoadTelemetryCommand { get; }
        public IRelayCommand ClearLogsCommand { get; }
        public IRelayCommand LoadErrorLogsCommand { get; }
        public IRelayCommand ClearErrorLogsCommand { get; }
        public IAsyncRelayCommand ExportErrorLogsCommand { get; }
        public IRelayCommand RefreshAnalyticsCommand { get; }
        public IRelayCommand RefreshPerformanceCommand { get; }
        public IRelayCommand RefreshFeatureFlagsCommand { get; }
        public IRelayCommand RefreshEnvironmentCommand { get; }
        public IRelayCommand<string> ToggleFeatureFlagCommand { get; }

        // Multi-select commands for logs
        public IRelayCommand SelectAllLogsCommand { get; }
        public IRelayCommand ClearLogSelectionCommand { get; }
        public IRelayCommand DeleteSelectedLogsCommand { get; }

        // Multi-select commands for error logs
        public IRelayCommand SelectAllErrorLogsCommand { get; }
        public IRelayCommand ClearErrorLogSelectionCommand { get; }
        public IRelayCommand DeleteSelectedErrorLogsCommand { get; }
        public IAsyncRelayCommand ExportSelectedErrorLogsCommand { get; }

        partial void OnAutoRefreshTelemetryChanged(bool value)
        {
            if (value)
            {
                StartTelemetryRefresh();
            }
            else
            {
                StopTelemetryRefresh();
            }
        }

        private void StartTelemetryRefresh()
        {
            StopTelemetryRefresh();
            _telemetryCancellationTokenSource = new CancellationTokenSource();
            _ = RefreshTelemetryLoop(_telemetryCancellationTokenSource.Token);
        }

        private void StopTelemetryRefresh()
        {
            _telemetryCancellationTokenSource?.Cancel();
            _telemetryCancellationTokenSource?.Dispose();
            _telemetryCancellationTokenSource = null;
        }

        private async Task RefreshTelemetryLoop(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    await LoadTelemetryAsync(cancellationToken);
                    // Also update memory metrics (doesn't require backend call)
                    UpdateMemoryMetrics();
                }
                catch
                {
                    // Silently fail - telemetry refresh should not break the UI
                }
                await Task.Delay(2000, cancellationToken); // Refresh every 2 seconds
            }
        }

        private async Task CheckHealthAsync(CancellationToken cancellationToken)
        {
            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var healthy = await _backendClient.CheckHealthAsync(cancellationToken);
                IsHealthy = healthy;

                // Update connection status
                IsConnected = _backendClient.IsConnected;
                UpdateConnectionStatus();

                HealthStatus = healthy ? "Backend API is healthy" : "Backend API is not responding";

                AddLog("INFO", HealthStatus ?? "Health check completed");

                // Show toast notification
                if (healthy)
                {
                    _toastNotificationService?.ShowSuccess(
                        "Health Check",
                        "Backend API is healthy and responding");
                    // Auto-load telemetry after health check
                    _ = LoadTelemetryAsync(CancellationToken.None);
                }
                else
                {
                    _toastNotificationService?.ShowWarning(
                        "Health Check",
                        "Backend API is not responding. Check connection and try again.");
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                IsHealthy = false;
                IsConnected = false;
                UpdateConnectionStatus();
                HealthStatus = ResourceHelper.GetString("Diagnostics.ErrorCheckingHealth", "Error checking health");
                ErrorMessage = ResourceHelper.FormatString("Diagnostics.CheckHealthFailed", ex.Message);
                AddLog("ERROR", ResourceHelper.FormatString("Diagnostics.HealthCheckFailed", ex.Message));
                await HandleErrorAsync(ex, "CheckHealth");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private void UpdateConnectionStatus()
        {
            if (!IsConnected)
            {
                ConnectionStatus = "Offline";
            }
            else
            {
                // Try to get circuit breaker state if available
                try
                {
                    if (_backendClient is Services.BackendClient client)
                    {
                        var circuitState = client.CircuitState;
                        ConnectionStatus = circuitState switch
                        {
                            Utilities.CircuitState.Open => "Circuit Open (Temporarily Unavailable)",
                            Utilities.CircuitState.HalfOpen => "Testing Connection...",
                            Utilities.CircuitState.Closed => "Connected",
                            _ => "Connected"
                        };
                    }
                    else
                    {
                        ConnectionStatus = IsHealthy ? "Connected" : "Disconnected";
                    }
                }
                catch
                {
                    ConnectionStatus = IsHealthy ? "Connected" : "Disconnected";
                }
            }
        }

        private async Task LoadTelemetryAsync(CancellationToken cancellationToken)
        {
            try
            {
                Telemetry = await _backendClient.GetTelemetryAsync(cancellationToken);

                // Update individual properties for UI binding
                CpuUsage = Telemetry.CpuPct ?? 0.0;
                GpuUsage = Telemetry.VramPct;
                RamUsage = Telemetry.RamPct ?? 0.0;

                // Update VRAM warning
                UpdateVramWarning();

                // Update connection status
                IsConnected = _backendClient.IsConnected;
                UpdateConnectionStatus();

                // Update memory metrics
                UpdateMemoryMetrics();

                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("Toast.Title.TelemetryUpdated", "Telemetry Updated"),
                    ResourceHelper.GetString("Diagnostics.TelemetryRefreshed", "System telemetry data has been refreshed"));
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                // Log error but don't break the UI
                AddLog("WARNING", $"Failed to load telemetry: {ex.Message}");
                await HandleErrorAsync(ex, "LoadTelemetry");
            }
        }

        private void UpdateMemoryMetrics()
        {
            try
            {
                // Get current process memory usage
                var process = System.Diagnostics.Process.GetCurrentProcess();
                var workingSet = process.WorkingSet64;
                var privateMemory = process.PrivateMemorySize64;

                CurrentMemoryBytes = workingSet;

                // Update peak memory
                if (workingSet > _peakMemoryBytes)
                {
                    _peakMemoryBytes = workingSet;
                }
                PeakMemoryBytes = _peakMemoryBytes;

                // Format memory for display
                MemoryFormatted = FormatBytes(workingSet);
                PeakMemoryFormatted = FormatBytes(_peakMemoryBytes);

                // Estimate memory by category (simplified - would need more detailed tracking)
                // For now, use heuristics based on process memory
                var totalMemory = GC.GetTotalMemory(false);
                MemoryByUI = (long)(totalMemory * 0.3); // Estimate 30% for UI
                MemoryByAudio = (long)(totalMemory * 0.2); // Estimate 20% for audio
                MemoryByEngines = (long)(totalMemory * 0.5); // Estimate 50% for engines
            }
            catch (Exception ex)
            {
                // Silently fail - memory monitoring should not break the UI
                System.Diagnostics.Debug.WriteLine($"Failed to update memory metrics: {ex.Message}");
            }
        }

        private static string FormatBytes(long bytes)
        {
            string[] sizes = { "B", "KB", "MB", "GB", "TB" };
            double len = bytes;
            int order = 0;
            while (len >= 1024 && order < sizes.Length - 1)
            {
                order++;
                len = len / 1024;
            }
            return $"{len:0.##} {sizes[order]}";
        }

        private void UpdateVramWarning()
        {
            if (Telemetry == null)
            {
                ShowVramWarning = false;
                VramWarning = string.Empty;
                return;
            }

            var vramPct = Telemetry.VramPct;

            if (vramPct >= 95)
            {
                ShowVramWarning = true;
                VramWarning = ResourceHelper.GetString("Diagnostics.VramCritical", "⚠️ CRITICAL: VRAM usage is very high. Close other applications or reduce audio processing load.");
            }
            else if (vramPct >= 85)
            {
                ShowVramWarning = true;
                VramWarning = ResourceHelper.GetString("Diagnostics.VramWarning", "⚠️ WARNING: VRAM usage is high. Consider closing other GPU applications.");
            }
            else if (vramPct >= 75)
            {
                ShowVramWarning = true;
                VramWarning = ResourceHelper.GetString("Diagnostics.VramElevated", "ℹ️ VRAM usage is elevated. Monitor usage if you experience performance issues.");
            }
            else
            {
                ShowVramWarning = false;
                VramWarning = string.Empty;
            }
        }

        private void AddLog(string level, string message)
        {
            var logEntry = new LogEntry
            {
                Timestamp = DateTime.Now,
                Level = level,
                Message = message
            };

            // Add to beginning of list (newest first)
            Logs.Insert(0, logEntry);

            // Keep only last 100 entries
            if (Logs.Count > 100)
            {
                Logs.RemoveAt(Logs.Count - 1);
            }
        }

        private void ClearLogs()
        {
            var count = Logs.Count;
            Logs.Clear();

            if (count > 0)
            {
                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("Toast.Title.LogsCleared", "Logs Cleared"),
                    ResourceHelper.FormatString("Diagnostics.LogsCleared", count, count == 1 ? "y" : "ies"));
            }
        }

        private void OnErrorLogged(object? sender, ErrorLogEntry entry)
        {
            // Add to error logs collection on UI thread
            Microsoft.UI.Dispatching.DispatcherQueue.GetForCurrentThread().TryEnqueue(() =>
            {
                var viewModel = new ErrorLogEntryViewModel(entry);
                ErrorLogs.Insert(0, viewModel);
                UpdateErrorCounts();
                ApplyFilters();
            });
        }

        private void OnAnalyticsEventTracked(object? sender, AnalyticsEvent evt)
        {
            Microsoft.UI.Dispatching.DispatcherQueue.GetForCurrentThread().TryEnqueue(() =>
            {
                RecentAnalyticsEvents.Insert(0, evt);
                // Keep only last 100 events
                while (RecentAnalyticsEvents.Count > 100)
                {
                    RecentAnalyticsEvents.RemoveAt(RecentAnalyticsEvents.Count - 1);
                }
            });
        }

        private void OnBudgetViolated(object? sender, BudgetViolationEventArgs args)
        {
            lock (_budgetViolations)
            {
                _budgetViolations.Add(args);
                // Keep only last 50 violations
                if (_budgetViolations.Count > 50)
                {
                    _budgetViolations.RemoveAt(0);
                }
            }
            Microsoft.UI.Dispatching.DispatcherQueue.GetForCurrentThread().TryEnqueue(() =>
            {
                LoadPerformanceData();
            });
        }

        private void LoadAnalyticsEvents()
        {
            if (_analyticsService == null)
                return;

            var events = _analyticsService.GetRecentEvents(100);
            RecentAnalyticsEvents.Clear();
            foreach (var evt in events.OrderByDescending(e => e.Timestamp))
            {
                RecentAnalyticsEvents.Add(evt);
            }
        }

        private void LoadPerformanceData()
        {
            lock (_budgetViolations)
            {
                BudgetViolations.Clear();
                foreach (var violation in _budgetViolations.OrderByDescending(v => v.Timestamp))
                {
                    BudgetViolations.Add(new BudgetViolationViewModel(violation));
                }
            }
        }

        private void LoadFeatureFlags()
        {
            if (_featureFlagsService == null)
                return;

            var flags = _featureFlagsService.GetAllFlags();
            FeatureFlags.Clear();

            // Get descriptions if available
            foreach (var flag in flags)
            {
                var description = _featureFlagsService.GetDescription(flag.Key) ?? "No description available";
                FeatureFlags.Add(new FeatureFlagViewModel(flag.Key, flag.Value, description, _featureFlagsService));
            }
        }

        private void ToggleFeatureFlag(string? flagName)
        {
            if (string.IsNullOrWhiteSpace(flagName) || _featureFlagsService == null)
                return;

            var flag = FeatureFlags.FirstOrDefault(f => f.FlagName == flagName);
            if (flag != null)
            {
                flag.IsEnabled = !flag.IsEnabled;
            }
        }

        private void LoadEnvironmentInfo()
        {
            AppVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version?.ToString() ?? ResourceHelper.GetString("Diagnostics.Unknown", "Unknown");
            DotNetVersion = System.Environment.Version.ToString();
            OsVersion = System.Runtime.InteropServices.RuntimeInformation.OSDescription;

            EnvironmentInfo.Clear();
            EnvironmentInfo.Add(new EnvironmentInfoItem { Key = ResourceHelper.GetString("Diagnostics.EnvAppVersion", "App Version"), Value = AppVersion });
            EnvironmentInfo.Add(new EnvironmentInfoItem { Key = ResourceHelper.GetString("Diagnostics.EnvDotNetVersion", ".NET Version"), Value = DotNetVersion });
            EnvironmentInfo.Add(new EnvironmentInfoItem { Key = ResourceHelper.GetString("Diagnostics.EnvOSVersion", "OS Version"), Value = OsVersion });
            EnvironmentInfo.Add(new EnvironmentInfoItem { Key = ResourceHelper.GetString("Diagnostics.EnvOSArchitecture", "OS Architecture"), Value = System.Runtime.InteropServices.RuntimeInformation.OSArchitecture.ToString() });
            EnvironmentInfo.Add(new EnvironmentInfoItem { Key = ResourceHelper.GetString("Diagnostics.EnvProcessArchitecture", "Process Architecture"), Value = System.Runtime.InteropServices.RuntimeInformation.ProcessArchitecture.ToString() });
            EnvironmentInfo.Add(new EnvironmentInfoItem { Key = ResourceHelper.GetString("Diagnostics.EnvMachineName", "Machine Name"), Value = System.Environment.MachineName });
            EnvironmentInfo.Add(new EnvironmentInfoItem { Key = ResourceHelper.GetString("Diagnostics.EnvUserName", "User Name"), Value = System.Environment.UserName });
            EnvironmentInfo.Add(new EnvironmentInfoItem { Key = ResourceHelper.GetString("Diagnostics.EnvWorkingSet", "Working Set"), Value = $"{System.Environment.WorkingSet / (1024 * 1024)} MB" });
            EnvironmentInfo.Add(new EnvironmentInfoItem { Key = ResourceHelper.GetString("Diagnostics.EnvProcessorCount", "Processor Count"), Value = System.Environment.ProcessorCount.ToString() });
        }

        private void LoadErrorLogs()
        {
            if (_errorLoggingService == null)
                return;

            var entries = _errorLoggingService.GetRecentErrors(1000);
            ErrorLogs.Clear();

            foreach (var entry in entries.OrderByDescending(e => e.Timestamp))
            {
                ErrorLogs.Add(new ErrorLogEntryViewModel(entry));
            }

            UpdateErrorCounts();
            ApplyFilters();
        }

        private void ClearErrorLogs()
        {
            var count = ErrorLogs.Count;
            _errorLoggingService?.ClearLogs();
            ErrorLogs.Clear();
            UpdateErrorCounts();

            if (count > 0)
            {
                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("Toast.Title.ErrorLogsCleared", "Error Logs Cleared"),
                    ResourceHelper.FormatString("Diagnostics.ErrorLogsCleared", count, count == 1 ? "y" : "ies"));
            }
        }

        private async Task ExportErrorLogsAsync(CancellationToken cancellationToken)
        {
            try
            {
                cancellationToken.ThrowIfCancellationRequested();

                var picker = new Windows.Storage.Pickers.FileSavePicker();
                picker.SuggestedFileName = $"voicestudio_errors_{DateTime.Now:yyyyMMdd_HHmmss}";
                picker.FileTypeChoices.Add(ResourceHelper.GetString("Diagnostics.FileTypeJSON", "JSON File"), new[] { ".json" });
                picker.FileTypeChoices.Add(ResourceHelper.GetString("Diagnostics.FileTypeKeyValue", "Key-Value File"), new[] { ".txt" });
                picker.FileTypeChoices.Add(ResourceHelper.GetString("Diagnostics.FileTypeText", "Text File"), new[] { ".txt" });

                var file = await picker.PickSaveFileAsync();
                cancellationToken.ThrowIfCancellationRequested();

                if (file == null)
                    return;

                if (_errorLoggingService == null)
                {
                    AddLog("ERROR", "Error logging service not available");
                    return;
                }

                // Export based on file extension
                if (file.Name.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                {
                    // Export as structured JSON
                    var json = _errorLoggingService.ExportLogsAsJson();
                    await Windows.Storage.FileIO.WriteTextAsync(file, json);
                }
                else
                {
                    // Export as key-value or text format
                    var content = _errorLoggingService.ExportLogsAsKeyValue();
                    await Windows.Storage.FileIO.WriteTextAsync(file, content);
                }

                AddLog("INFO", ResourceHelper.FormatString("Diagnostics.ErrorLogsExported", file.Name));

                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("Toast.Title.ExportComplete", "Export Complete"),
                    ResourceHelper.FormatString("Diagnostics.ErrorLogsExported", file.Name));
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                AddLog("ERROR", $"Failed to export error logs: {ex.Message}");
                await HandleErrorAsync(ex, "ExportErrorLogs");
            }
        }

        partial void OnErrorLogFilterChanged(string value)
        {
            ApplyFilters();
        }

        partial void OnSelectedErrorLevelChanged(string value)
        {
            ApplyFilters();
        }

        private void ApplyFilters()
        {
            // This would filter the displayed error logs
            // For now, we'll just update counts
            UpdateErrorCounts();
        }

        private void UpdateErrorCounts()
        {
            ErrorLogCount = ErrorLogs.Count;
            ErrorCount = ErrorLogs.Count(e => e.Level == "Error");
            WarningCount = ErrorLogs.Count(e => e.Level == "Warning");
            InfoCount = ErrorLogs.Count(e => e.Level == "Info");
        }

        public void Dispose()
        {
            if (_disposed)
                return;

            // Stop telemetry refresh
            StopTelemetryRefresh();

            // Unsubscribe from error logging service
            if (_errorLoggingService != null)
            {
                _errorLoggingService.ErrorLogged -= OnErrorLogged;
            }

            // Unsubscribe from analytics service
            if (_analyticsService != null)
            {
                _analyticsService.EventTracked -= OnAnalyticsEventTracked;
            }

            // Unsubscribe from performance profiler
            PerformanceProfiler.BudgetViolated -= OnBudgetViolated;

            // Clear collections
            Logs.Clear();
            ErrorLogs.Clear();
            RecentAnalyticsEvents.Clear();
            BudgetViolations.Clear();
            FeatureFlags.Clear();
            EnvironmentInfo.Clear();

            _disposed = true;
        }

        // Multi-select methods for logs
        private void SelectAllLogs()
        {
            if (_logsMultiSelectState == null)
                return;

            var state = _multiSelectService?.GetState($"{PanelId}_logs");
            if (state != null)
            {
                foreach (var log in Logs)
                {
                    var logId = GetLogId(log);
                    state.Add(logId);
                }
            }
            UpdateLogSelectionProperties();
            _multiSelectService.OnSelectionChanged($"{PanelId}_logs", _logsMultiSelectState);
        }

        private void ClearLogSelection()
        {
            if (_logsMultiSelectState == null)
                return;

            _logsMultiSelectState.Clear();
            UpdateLogSelectionProperties();
            _multiSelectService.OnSelectionChanged($"{PanelId}_logs", _logsMultiSelectState);
            DeleteSelectedLogsCommand.NotifyCanExecuteChanged();
        }

        private void DeleteSelectedLogs()
        {
            if (_logsMultiSelectState == null || _logsMultiSelectState.SelectedIds.Count == 0)
                return;

            var selectedIds = new System.Collections.Generic.List<string>(_logsMultiSelectState.SelectedIds);
            var logsToRemove = Logs.Where(log => selectedIds.Contains(GetLogId(log))).ToList();
            var count = logsToRemove.Count;

            foreach (var log in logsToRemove)
            {
                Logs.Remove(log);
            }

            ClearLogSelection();

            _toastNotificationService?.ShowSuccess(
                "Logs Deleted",
                $"Removed {count} selected log entr{(count == 1 ? "y" : "ies")}");
        }

        private void UpdateLogSelectionProperties()
        {
            if (_logsMultiSelectState == null)
            {
                SelectedLogCount = 0;
                HasMultipleLogSelection = false;
            }
            else
            {
                SelectedLogCount = _logsMultiSelectState.Count;
                HasMultipleLogSelection = _logsMultiSelectState.Count > 1;
            }
            DeleteSelectedLogsCommand.NotifyCanExecuteChanged();
        }

        private string GetLogId(LogEntry log)
        {
            return $"log_{log.Timestamp.Ticks}";
        }

        // Multi-select methods for error logs
        private void SelectAllErrorLogs()
        {
            if (_errorLogsMultiSelectState == null)
                return;

            foreach (var errorLog in ErrorLogs)
            {
                var errorLogId = GetErrorLogId(errorLog);
                _errorLogsMultiSelectState.Add(errorLogId);
            }
            UpdateErrorLogSelectionProperties();
            _multiSelectService.OnSelectionChanged($"{PanelId}_errorlogs", _errorLogsMultiSelectState);
        }

        private void ClearErrorLogSelection()
        {
            if (_errorLogsMultiSelectState == null)
                return;

            _errorLogsMultiSelectState.Clear();
            UpdateErrorLogSelectionProperties();
            _multiSelectService.OnSelectionChanged($"{PanelId}_errorlogs", _errorLogsMultiSelectState);
            DeleteSelectedErrorLogsCommand.NotifyCanExecuteChanged();
            ExportSelectedErrorLogsCommand.NotifyCanExecuteChanged();
        }

        private void DeleteSelectedErrorLogs()
        {
            if (_errorLogsMultiSelectState == null || _errorLogsMultiSelectState.SelectedIds.Count == 0)
                return;

            var selectedIds = new System.Collections.Generic.List<string>(_errorLogsMultiSelectState.SelectedIds);
            var errorLogsToRemove = ErrorLogs.Where(errorLog => selectedIds.Contains(GetErrorLogId(errorLog))).ToList();
            var count = errorLogsToRemove.Count;

            foreach (var errorLog in errorLogsToRemove)
            {
                ErrorLogs.Remove(errorLog);
            }

            UpdateErrorCounts();
            ClearErrorLogSelection();

            _toastNotificationService?.ShowSuccess(
                ResourceHelper.GetString("Toast.Title.ErrorLogsDeleted", "Error Logs Deleted"),
                ResourceHelper.FormatString("Diagnostics.ErrorLogsDeleted", count, count == 1 ? "y" : "ies"));
        }

        private async Task ExportSelectedErrorLogsAsync(CancellationToken cancellationToken)
        {
            if (_errorLogsMultiSelectState == null || _errorLogsMultiSelectState.SelectedIds.Count == 0)
                return;

            try
            {
                cancellationToken.ThrowIfCancellationRequested();

                var picker = new Windows.Storage.Pickers.FileSavePicker();
                picker.SuggestedFileName = $"voicestudio_selected_errors_{DateTime.Now:yyyyMMdd_HHmmss}";
                picker.FileTypeChoices.Add(ResourceHelper.GetString("Diagnostics.FileTypeJSON", "JSON File"), new[] { ".json" });
                picker.FileTypeChoices.Add(ResourceHelper.GetString("Diagnostics.FileTypeText", "Text File"), new[] { ".txt" });

                var file = await picker.PickSaveFileAsync();
                cancellationToken.ThrowIfCancellationRequested();

                if (file == null)
                    return;

                var selectedIds = new System.Collections.Generic.List<string>(_errorLogsMultiSelectState.SelectedIds);
                var selectedErrorLogs = ErrorLogs.Where(errorLog => selectedIds.Contains(GetErrorLogId(errorLog))).ToList();

                if (file.Name.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                {
                    // Export selected logs as JSON
                    var json = System.Text.Json.JsonSerializer.Serialize(
                        selectedErrorLogs.Select(e => new
                        {
                            e.Timestamp,
                            e.Level,
                            e.Message,
                            e.Context,
                            e.ExceptionType,
                            e.StackTrace,
                            e.Metadata
                        }),
                        new System.Text.Json.JsonSerializerOptions { WriteIndented = true }
                    );
                    await Windows.Storage.FileIO.WriteTextAsync(file, json);
                }
                else
                {
                    // Export as text format
                    var lines = selectedErrorLogs.Select(e => e.FormattedLineWithContext);
                    await Windows.Storage.FileIO.WriteLinesAsync(file, lines);
                }

                var count = selectedErrorLogs.Count;
                AddLog("INFO", ResourceHelper.FormatString("Diagnostics.SelectedErrorLogsExported", count, file.Name));

                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("Toast.Title.ExportComplete", "Export Complete"),
                    ResourceHelper.FormatString("Diagnostics.SelectedErrorLogsExported", count, file.Name));
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                AddLog("ERROR", $"Failed to export selected error logs: {ex.Message}");
                await HandleErrorAsync(ex, "ExportSelectedErrorLogs");
            }
        }

        private void UpdateErrorLogSelectionProperties()
        {
            if (_errorLogsMultiSelectState == null)
            {
                SelectedErrorLogCount = 0;
                HasMultipleErrorLogSelection = false;
            }
            else
            {
                SelectedErrorLogCount = _errorLogsMultiSelectState.Count;
                HasMultipleErrorLogSelection = _errorLogsMultiSelectState.Count > 1;
            }
            DeleteSelectedErrorLogsCommand.NotifyCanExecuteChanged();
            ExportSelectedErrorLogsCommand.NotifyCanExecuteChanged();
        }

        private string GetErrorLogId(ErrorLogEntryViewModel errorLog)
        {
            return $"errorlog_{errorLog.Timestamp.Ticks}";
        }
    }

    /// <summary>
    /// Represents a single log entry.
    /// </summary>
    public class LogEntry : ObservableObject
    {
        public DateTime Timestamp { get; set; }
        public string Level { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;

        public string FormattedLine => $"[{Timestamp:HH:mm:ss}] [{Level}] {Message}";
    }

    /// <summary>
    /// ViewModel for error log entries.
    /// </summary>
    public class ErrorLogEntryViewModel : ObservableObject
    {
        public ErrorLogEntryViewModel(ErrorLogEntry entry)
        {
            Timestamp = entry.Timestamp;
            Level = entry.Level;
            Message = entry.Message;
            Context = entry.Context ?? string.Empty;
            ExceptionType = entry.ExceptionType ?? string.Empty;
            StackTrace = entry.StackTrace ?? string.Empty;
            Metadata = entry.Metadata;
        }

        public DateTime Timestamp { get; }
        public string Level { get; }
        public string Message { get; }
        public string Context { get; }
        public string ExceptionType { get; }
        public string StackTrace { get; }
        public System.Collections.Generic.Dictionary<string, object>? Metadata { get; }

        public string FormattedLine => $"[{Timestamp:HH:mm:ss.fff}] [{Level}] {Message}";
        public string FormattedLineWithContext =>
            string.IsNullOrWhiteSpace(Context)
                ? FormattedLine
                : $"{FormattedLine} (Context: {Context})";
    }

    /// <summary>
    /// ViewModel for budget violation display.
    /// </summary>
    public class BudgetViolationViewModel
    {
        public BudgetViolationViewModel(BudgetViolationEventArgs args)
        {
            OperationName = args.OperationName;
            BudgetMs = args.BudgetMs;
            ActualMs = args.ActualMs;
            ViolationAmount = ActualMs - BudgetMs;
            ViolationPercent = args.ViolationPercent;
            Timestamp = DateTime.UtcNow; // Note: BudgetViolationEventArgs doesn't have Timestamp, so we use current time
        }

        public string OperationName { get; }
        public int BudgetMs { get; }
        public long ActualMs { get; }
        public long ViolationAmount { get; }
        public double ViolationPercent { get; }
        public DateTime Timestamp { get; }

        public string FormattedViolation => $"{OperationName}: {ActualMs}ms (budget: {BudgetMs}ms, exceeded by {ViolationAmount}ms / {ViolationPercent:F1}%)";
    }

    /// <summary>
    /// ViewModel for feature flag display.
    /// </summary>
    public class FeatureFlagViewModel : ObservableObject
    {
        private bool _isEnabled;
        private readonly IFeatureFlagsService? _featureFlagsService;

        public FeatureFlagViewModel(string flagName, bool isEnabled, string description, IFeatureFlagsService? featureFlagsService)
        {
            FlagName = flagName;
            _isEnabled = isEnabled;
            Description = description;
            _featureFlagsService = featureFlagsService;
        }

        public string FlagName { get; }
        public string Description { get; }

        public bool IsEnabled
        {
            get => _isEnabled;
            set
            {
                if (_isEnabled != value)
                {
                    _isEnabled = value;
                    _featureFlagsService?.SetFlag(FlagName, value);
                    OnPropertyChanged();
                }
            }
        }
    }

    /// <summary>
    /// Item for environment info display.
    /// </summary>
    public class EnvironmentInfoItem
    {
        public string Key { get; set; } = string.Empty;
        public string Value { get; set; } = string.Empty;
    }
}

