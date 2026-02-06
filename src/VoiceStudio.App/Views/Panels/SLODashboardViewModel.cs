using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.UI;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Media;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Views.Panels
{
    /// <summary>
    /// ViewModel for SLO Dashboard panel.
    /// Phase 5.2.1: SLO Dashboard with gauge chart visualization.
    /// </summary>
    public partial class SLODashboardViewModel : BaseViewModel, IPanelView
    {
        private readonly IBackendClient _backendClient;

        /// <inheritdoc/>
        public string PanelId => "slo_dashboard";

        /// <inheritdoc/>
        public string DisplayName => ResourceHelper.GetString(
            "Panel.SLODashboard.DisplayName",
            "SLO Dashboard");

        /// <inheritdoc/>
        public PanelRegion Region => PanelRegion.Center;

        /// <summary>Gets or sets the collection of SLO metrics.</summary>
        [ObservableProperty]
        private ObservableCollection<SloMetric> sloMetrics = new();

        /// <summary>Gets or sets whether data is loading.</summary>
        [ObservableProperty]
        private bool isLoading;

        /// <summary>Gets or sets the error message.</summary>
        [ObservableProperty]
        private string? errorMessage;

        /// <summary>Gets or sets the status message.</summary>
        [ObservableProperty]
        private string? statusMessage;

        /// <summary>Gets or sets the total SLO count.</summary>
        [ObservableProperty]
        private int totalSloCount;

        /// <summary>Gets or sets the healthy SLO count.</summary>
        [ObservableProperty]
        private int healthySloCount;

        /// <summary>Gets or sets the warning SLO count.</summary>
        [ObservableProperty]
        private int warningSloCount;

        /// <summary>Gets or sets the critical SLO count.</summary>
        [ObservableProperty]
        private int criticalSloCount;

        /// <summary>
        /// Gets visibility for the "All SLOs Healthy" badge.
        /// </summary>
        public Visibility AllSlosHealthy => CriticalSloCount == 0 && WarningSloCount == 0
            ? Visibility.Visible
            : Visibility.Collapsed;

        /// <summary>Command to refresh SLO data.</summary>
        public IAsyncRelayCommand RefreshCommand { get; }

        /// <summary>
        /// Initializes a new instance of the SLODashboardViewModel.
        /// </summary>
        /// <param name="context">The ViewModel context.</param>
        /// <param name="backendClient">The backend client.</param>
        public SLODashboardViewModel(
            IViewModelContext context,
            IBackendClient backendClient)
            : base(context)
        {
            _backendClient = backendClient
                ?? throw new ArgumentNullException(nameof(backendClient));

            RefreshCommand = new AsyncRelayCommand(LoadSloDataAsync);
        }

        /// <summary>
        /// Loads SLO data from the backend.
        /// </summary>
        public async Task LoadSloDataAsync()
        {
            if (IsLoading) return;

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var response = await _backendClient.GetAsync<SloDataResponse>(
                    "/api/v1/diagnostics/slo");

                if (response?.Slos != null)
                {
                    SloMetrics.Clear();
                    foreach (var slo in response.Slos)
                    {
                        SloMetrics.Add(slo);
                    }
                }

                UpdateSummaryStats();
                StatusMessage = $"Loaded {TotalSloCount} SLOs";
            }
            catch (HttpRequestException)
            {
                // Backend unavailable - load sample data for development
                LoadSampleData();
                StatusMessage = "Using sample data (backend unavailable)";
            }
            catch (JsonException ex)
            {
                // JSON parsing failed - use sample data
                ErrorMessage = $"Failed to parse SLO data: {ex.Message}";
                LoadSampleData();
            }
            catch (InvalidOperationException ex)
            {
                // Backend returned unexpected response
                ErrorMessage = $"Invalid SLO response: {ex.Message}";
                LoadSampleData();
            }
            finally
            {
                IsLoading = false;
                OnPropertyChanged(nameof(AllSlosHealthy));
            }
        }

        private void UpdateSummaryStats()
        {
            TotalSloCount = SloMetrics.Count;
            HealthySloCount = SloMetrics.Count(s => s.Status == "Healthy");
            WarningSloCount = SloMetrics.Count(s => s.Status == "Warning");
            CriticalSloCount = SloMetrics.Count(s => s.Status == "Critical");
        }

        private void LoadSampleData()
        {
            SloMetrics.Clear();

            // Synthesis latency SLO
            SloMetrics.Add(new SloMetric
            {
                Name = "Synthesis Latency P95",
                CurrentValue = 1850,
                Target = 2000,
                WarningThreshold = 1800,
                Unit = "ms",
                MetricType = "latency"
            });

            // Transcription latency SLO
            SloMetrics.Add(new SloMetric
            {
                Name = "Transcription Latency P95",
                CurrentValue = 450,
                Target = 500,
                WarningThreshold = 450,
                Unit = "ms",
                MetricType = "latency"
            });

            // API availability SLO
            SloMetrics.Add(new SloMetric
            {
                Name = "API Availability",
                CurrentValue = 99.85,
                Target = 99.9,
                WarningThreshold = 99.5,
                Unit = "%",
                MetricType = "availability"
            });

            // Synthesis success rate SLO
            SloMetrics.Add(new SloMetric
            {
                Name = "Synthesis Success Rate",
                CurrentValue = 98.5,
                Target = 99.0,
                WarningThreshold = 98.0,
                Unit = "%",
                MetricType = "success_rate"
            });

            // Engine startup SLO
            SloMetrics.Add(new SloMetric
            {
                Name = "Engine Startup Time",
                CurrentValue = 4.2,
                Target = 5.0,
                WarningThreshold = 4.5,
                Unit = "s",
                MetricType = "latency"
            });

            // Quality score SLO
            SloMetrics.Add(new SloMetric
            {
                Name = "Audio Quality MOS",
                CurrentValue = 4.1,
                Target = 4.0,
                WarningThreshold = 3.8,
                Unit = "score",
                MetricType = "quality"
            });

            UpdateSummaryStats();
        }
    }

    /// <summary>
    /// Represents a single SLO metric with gauge visualization support.
    /// Phase 5.2.1: SLO Dashboard.
    /// </summary>
    public partial class SloMetric : ObservableObject
    {
        /// <summary>Gets or sets the SLO name.</summary>
        [ObservableProperty]
        private string name = string.Empty;

        /// <summary>Gets or sets the current metric value.</summary>
        [ObservableProperty]
        private double currentValue;

        /// <summary>Gets or sets the target value.</summary>
        [ObservableProperty]
        private double target;

        /// <summary>Gets or sets the warning threshold.</summary>
        [ObservableProperty]
        private double warningThreshold;

        /// <summary>Gets or sets the unit of measurement.</summary>
        [ObservableProperty]
        private string unit = string.Empty;

        /// <summary>Gets or sets the metric type (latency, availability, etc.).</summary>
        [ObservableProperty]
        private string metricType = string.Empty;

        /// <summary>Gets the current value as a percentage of target.</summary>
        public double CurrentValuePercent
        {
            get
            {
                if (Target == 0) return 0;

                // For latency metrics, lower is better
                if (MetricType == "latency")
                {
                    // If under target, show as percentage toward 100%
                    return Math.Min(100, ((1 - (CurrentValue / Target)) * 100) + 50);
                }

                // For other metrics (availability, success_rate), higher is better
                return Math.Min(100, (CurrentValue / Target) * 100);
            }
        }

        /// <summary>Gets the formatted current value.</summary>
        public string CurrentValueFormatted
        {
            get
            {
                return CurrentValue switch
                {
                    < 10 => $"{CurrentValue:F2}",
                    < 100 => $"{CurrentValue:F1}",
                    _ => $"{CurrentValue:F0}"
                };
            }
        }

        /// <summary>Gets the formatted target value.</summary>
        public string TargetFormatted => $"{Target:F1} {Unit}";

        /// <summary>Gets the formatted warning threshold.</summary>
        public string WarningThresholdFormatted => $"{WarningThreshold:F1} {Unit}";

        /// <summary>Gets the current status based on thresholds.</summary>
        public string Status
        {
            get
            {
                if (MetricType == "latency")
                {
                    // For latency, lower is better
                    if (CurrentValue >= Target) return "Critical";
                    if (CurrentValue >= WarningThreshold) return "Warning";
                    return "Healthy";
                }

                // For other metrics, higher is better
                if (CurrentValue < WarningThreshold) return "Critical";
                if (CurrentValue < Target) return "Warning";
                return "Healthy";
            }
        }

        /// <summary>Gets the status color brush.</summary>
        public SolidColorBrush StatusColor
        {
            get
            {
                return Status switch
                {
                    "Healthy" => new SolidColorBrush(Microsoft.UI.ColorHelper.FromArgb(255, 76, 175, 80)),
                    "Warning" => new SolidColorBrush(Microsoft.UI.ColorHelper.FromArgb(255, 255, 193, 7)),
                    "Critical" => new SolidColorBrush(Microsoft.UI.ColorHelper.FromArgb(255, 244, 67, 54)),
                    _ => new SolidColorBrush(Microsoft.UI.ColorHelper.FromArgb(255, 158, 158, 158))
                };
            }
        }

        /// <summary>Gets the status border brush.</summary>
        public SolidColorBrush StatusBorderBrush => StatusColor;

        /// <summary>Gets the status badge background brush.</summary>
        public SolidColorBrush StatusBadgeBackground => StatusColor;
    }

    /// <summary>
    /// Response model for SLO data API.
    /// </summary>
    public class SloDataResponse
    {
        /// <summary>Gets or sets the SLO metrics list.</summary>
        public List<SloMetric> Slos { get; set; } = new();

        /// <summary>Gets or sets the timestamp.</summary>
        public DateTime Timestamp { get; set; }
    }
}
