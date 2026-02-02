using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;
using AnalyticsSummaryModel = VoiceStudio.App.ViewModels.AnalyticsDashboardViewModel.AnalyticsSummary;
using AnalyticsCategoryModel = VoiceStudio.App.ViewModels.AnalyticsDashboardViewModel.AnalyticsCategory;
using AnalyticsMetricModel = VoiceStudio.App.ViewModels.AnalyticsDashboardViewModel.AnalyticsMetric;
using StatisticalAnalysisResponseModel = VoiceStudio.App.ViewModels.AnalyticsDashboardViewModel.StatisticalAnalysisResponse;
using StatisticalTestResultModel = VoiceStudio.App.ViewModels.AnalyticsDashboardViewModel.StatisticalTestResult;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// ViewModel for the AnalyticsDashboardView panel - Analytics dashboard.
  /// </summary>
  public partial class AnalyticsDashboardViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;

    public string PanelId => "analytics-dashboard";
    public string DisplayName => ResourceHelper.GetString("Panel.AnalyticsDashboard.DisplayName", "Analytics Dashboard");
    public PanelRegion Region => PanelRegion.Center;

    [ObservableProperty]
    private AnalyticsSummaryItem? summary;

    [ObservableProperty]
    private ObservableCollection<string> availableCategories = new();

    [ObservableProperty]
    private string? selectedCategory;

    [ObservableProperty]
    private ObservableCollection<AnalyticsMetricItem> categoryMetrics = new();

    [ObservableProperty]
    private string selectedTimeRange = "30d";

    [ObservableProperty]
    private ObservableCollection<string> availableTimeRanges = new() { "7d", "30d", "90d", "1y", "all" };

    [ObservableProperty]
    private string selectedInterval = "day";

    [ObservableProperty]
    private ObservableCollection<string> availableIntervals = new() { "hour", "day", "week", "month" };

    [ObservableProperty]
    private StatisticalAnalysisItem? statisticalAnalysis;

    [ObservableProperty]
    private bool showStatisticalAnalysis = false;

    public AnalyticsDashboardViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      LoadSummaryCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadSummary");
        await LoadSummaryAsync(ct);
      }, () => !IsLoading);
      LoadCategoryMetricsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadCategoryMetrics");
        await LoadCategoryMetricsAsync(ct);
      }, () => !IsLoading);
      LoadCategoriesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadCategories");
        await LoadCategoriesAsync(ct);
      }, () => !IsLoading);
      LoadStatisticalAnalysisCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadStatisticalAnalysis");
        await LoadStatisticalAnalysisAsync(ct);
      }, () => !IsLoading);
      RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("Refresh");
        await RefreshAsync(ct);
      }, () => !IsLoading);

      // Load initial data
      _ = LoadSummaryAsync(CancellationToken.None);
      _ = LoadCategoriesAsync(CancellationToken.None);
    }

    public IAsyncRelayCommand LoadSummaryCommand { get; }
    public IAsyncRelayCommand LoadCategoryMetricsCommand { get; }
    public IAsyncRelayCommand LoadCategoriesCommand { get; }
    public IAsyncRelayCommand LoadStatisticalAnalysisCommand { get; }
    public IAsyncRelayCommand RefreshCommand { get; }

    partial void OnSelectedCategoryChanged(string? value)
    {
      if (!string.IsNullOrEmpty(value))
      {
        _ = LoadCategoryMetricsAsync(CancellationToken.None);
        if (ShowStatisticalAnalysis)
        {
          _ = LoadStatisticalAnalysisAsync(CancellationToken.None);
        }
      }
    }

    partial void OnShowStatisticalAnalysisChanged(bool value)
    {
      if (value && !string.IsNullOrEmpty(SelectedCategory))
      {
        _ = LoadStatisticalAnalysisAsync(CancellationToken.None);
      }
    }

    private async Task LoadSummaryAsync(CancellationToken cancellationToken)
    {
      try
      {
        IsLoading = true;
        ErrorMessage = null;

        var summary = await _backendClient.SendRequestAsync<object, AnalyticsSummary>(
            "/api/analytics/summary",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (summary != null)
        {
          Summary = new AnalyticsSummaryItem(summary);
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadSummary");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task LoadCategoryMetricsAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrEmpty(SelectedCategory))
      {
        return;
      }

      try
      {
        IsLoading = true;
        ErrorMessage = null;

        var url = $"/api/analytics/metrics/{Uri.EscapeDataString(SelectedCategory)}?interval={Uri.EscapeDataString(SelectedInterval)}";

        var metrics = await _backendClient.SendRequestAsync<object, AnalyticsMetric[]>(
            url,
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (metrics != null)
        {
          CategoryMetrics.Clear();
          foreach (var metric in metrics)
          {
            CategoryMetrics.Add(new AnalyticsMetricItem(metric));
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadCategoryMetrics");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task LoadCategoriesAsync(CancellationToken cancellationToken)
    {
      try
      {
        var categories = await _backendClient.SendRequestAsync<object, string[]>(
            "/api/analytics/categories",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (categories != null)
        {
          AvailableCategories.Clear();
          foreach (var category in categories)
          {
            AvailableCategories.Add(category);
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadCategories");
      }
    }

    private async Task LoadStatisticalAnalysisAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrEmpty(SelectedCategory))
      {
        return;
      }

      try
      {
        IsLoading = true;
        ErrorMessage = null;

        var url = $"/api/analytics/statistical/{Uri.EscapeDataString(SelectedCategory)}?interval={Uri.EscapeDataString(SelectedInterval)}";

        try
        {
          var analysis = await _backendClient.SendRequestAsync<object, StatisticalAnalysisResponse>(
              url,
              null,
              System.Net.Http.HttpMethod.Get,
              cancellationToken
          );

          if (analysis != null)
          {
            StatisticalAnalysis = new StatisticalAnalysisItem(analysis);
          }
        }
        catch
        {
          // Statistical analysis endpoint may not be available yet - that's okay
          StatisticalAnalysis = null;
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception)
      {
        // Statistical analysis endpoint may not be available yet - that's okay
        StatisticalAnalysis = null;
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task RefreshAsync(CancellationToken cancellationToken)
    {
      try
      {
        await LoadSummaryAsync(cancellationToken);
        await LoadCategoriesAsync(cancellationToken);
        if (!string.IsNullOrEmpty(SelectedCategory))
        {
          await LoadCategoryMetricsAsync(cancellationToken);
          if (ShowStatisticalAnalysis)
          {
            await LoadStatisticalAnalysisAsync(cancellationToken);
          }
        }
        StatusMessage = ResourceHelper.GetString("AnalyticsDashboard.Refreshed", "Refreshed");
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "Refresh");
      }
    }

    // Response models
    public class AnalyticsSummary
    {
      public string PeriodStart { get; set; } = string.Empty;
      public string PeriodEnd { get; set; } = string.Empty;
      public int TotalSynthesis { get; set; }
      public int TotalProjects { get; set; }
      public int TotalAudioProcessed { get; set; }
      public double TotalProcessingTime { get; set; }
      public double AverageQualityScore { get; set; }
      public AnalyticsCategory[] Categories { get; set; } = Array.Empty<AnalyticsCategory>();
    }

    public class AnalyticsCategory
    {
      public string Category { get; set; } = string.Empty;
      public double Total { get; set; }
      public int Count { get; set; }
      public double Average { get; set; }
      public double MinValue { get; set; }
      public double MaxValue { get; set; }
      public string Trend { get; set; } = string.Empty;
    }

    public class AnalyticsMetric
    {
      public string Timestamp { get; set; } = string.Empty;
      public double Value { get; set; }
      public string? Label { get; set; }
    }

    public class StatisticalAnalysisResponse
    {
      public double Mean { get; set; }
      public double Median { get; set; }
      public double? Mode { get; set; }
      public double StandardDeviation { get; set; }
      public double Variance { get; set; }
      public double Min { get; set; }
      public double Max { get; set; }
      public double Range { get; set; }
      public double Q1 { get; set; }
      public double Q3 { get; set; }
      public double IQR { get; set; }
      public double Skewness { get; set; }
      public double Kurtosis { get; set; }
      public int SampleSize { get; set; }
      public Dictionary<string, double>? Correlations { get; set; }
      public Dictionary<string, StatisticalTestResultModel>? TestResults { get; set; }
    }

    public class StatisticalTestResult
    {
      public string TestName { get; set; } = string.Empty;
      public double TestStatistic { get; set; }
      public double PValue { get; set; }
      public bool Significant { get; set; }
      public string Interpretation { get; set; } = string.Empty;
    }
  }

  // Data models
  public class AnalyticsSummaryItem : ObservableObject
  {
    public string PeriodStart { get; set; }
    public string PeriodEnd { get; set; }
    public int TotalSynthesis { get; set; }
    public int TotalProjects { get; set; }
    public int TotalAudioProcessed { get; set; }
    public double TotalProcessingTime { get; set; }
    public double AverageQualityScore { get; set; }
    public ObservableCollection<AnalyticsCategoryItem> Categories { get; set; } = new();
    public string ProcessingTimeDisplay => $"{TotalProcessingTime:F1}s";
    public string QualityScoreDisplay => $"{AverageQualityScore:F1}/5.0";

    public AnalyticsSummaryItem(AnalyticsSummaryModel summary)
    {
      PeriodStart = summary.PeriodStart;
      PeriodEnd = summary.PeriodEnd;
      TotalSynthesis = summary.TotalSynthesis;
      TotalProjects = summary.TotalProjects;
      TotalAudioProcessed = summary.TotalAudioProcessed;
      TotalProcessingTime = summary.TotalProcessingTime;
      AverageQualityScore = summary.AverageQualityScore;
      foreach (var category in summary.Categories)
      {
        Categories.Add(new AnalyticsCategoryItem(category));
      }
    }
  }

  public class AnalyticsCategoryItem : ObservableObject
  {
    public string Category { get; set; }
    public double Total { get; set; }
    public int Count { get; set; }
    public double Average { get; set; }
    public double MinValue { get; set; }
    public double MaxValue { get; set; }
    public string Trend { get; set; }
    public string TrendDisplay => Trend.ToUpper();
    public string AverageDisplay => $"{Average:F2}";

    public AnalyticsCategoryItem(AnalyticsCategoryModel category)
    {
      Category = category.Category;
      Total = category.Total;
      Count = category.Count;
      Average = category.Average;
      MinValue = category.MinValue;
      MaxValue = category.MaxValue;
      Trend = category.Trend;
    }
  }

  public class AnalyticsMetricItem : ObservableObject
  {
    public string Timestamp { get; set; }
    public double Value { get; set; }
    public string? Label { get; set; }
    public string ValueDisplay => $"{Value:F1}";
    public string DisplayLabel => Label ?? Timestamp;

    public AnalyticsMetricItem(AnalyticsMetricModel metric)
    {
      Timestamp = metric.Timestamp;
      Value = metric.Value;
      Label = metric.Label;
    }
  }

  public class StatisticalAnalysisItem : ObservableObject
  {
    public double Mean { get; set; }
    public double Median { get; set; }
    public double? Mode { get; set; }
    public double StandardDeviation { get; set; }
    public double Variance { get; set; }
    public double Min { get; set; }
    public double Max { get; set; }
    public double Range { get; set; }
    public double Q1 { get; set; }
    public double Q3 { get; set; }
    public double IQR { get; set; }
    public double Skewness { get; set; }
    public double Kurtosis { get; set; }
    public int SampleSize { get; set; }
    public ObservableCollection<CorrelationItem> Correlations { get; set; } = new();
    public ObservableCollection<StatisticalTestResultItem> TestResults { get; set; } = new();

    public string MeanDisplay => $"{Mean:F3}";
    public string MedianDisplay => $"{Median:F3}";
    public string ModeDisplay => Mode.HasValue ? $"{Mode.Value:F3}" : "N/A";
    public string StandardDeviationDisplay => $"{StandardDeviation:F3}";
    public string VarianceDisplay => $"{Variance:F3}";
    public string RangeDisplay => $"{Range:F3}";
    public string IQRDisplay => $"{IQR:F3}";
    public string SkewnessDisplay => $"{Skewness:F3}";
    public string KurtosisDisplay => $"{Kurtosis:F3}";

    public StatisticalAnalysisItem(StatisticalAnalysisResponseModel response)
    {
      Mean = response.Mean;
      Median = response.Median;
      Mode = response.Mode;
      StandardDeviation = response.StandardDeviation;
      Variance = response.Variance;
      Min = response.Min;
      Max = response.Max;
      Range = response.Range;
      Q1 = response.Q1;
      Q3 = response.Q3;
      IQR = response.IQR;
      Skewness = response.Skewness;
      Kurtosis = response.Kurtosis;
      SampleSize = response.SampleSize;

      if (response.Correlations != null)
      {
        foreach (var correlation in response.Correlations)
        {
          Correlations.Add(new CorrelationItem(correlation.Key, correlation.Value));
        }
      }

      if (response.TestResults != null)
      {
        foreach (var testResult in response.TestResults)
        {
          TestResults.Add(new StatisticalTestResultItem(testResult.Value));
        }
      }
    }
  }

  public class CorrelationItem : ObservableObject
  {
    public string Variable { get; set; }
    public double Correlation { get; set; }
    public string CorrelationDisplay => $"{Correlation:F3}";
    public string Strength => Math.Abs(Correlation) switch
    {
      >= 0.9 => "Very Strong",
      >= 0.7 => "Strong",
      >= 0.5 => "Moderate",
      >= 0.3 => "Weak",
      _ => "Very Weak"
    };

    public CorrelationItem(string variable, double correlation)
    {
      Variable = variable;
      Correlation = correlation;
    }
  }

  public class StatisticalTestResultItem : ObservableObject
  {
    public string TestName { get; set; }
    public double TestStatistic { get; set; }
    public double PValue { get; set; }
    public bool Significant { get; set; }
    public string Interpretation { get; set; }
    public string TestStatisticDisplay => $"{TestStatistic:F4}";
    public string PValueDisplay => $"{PValue:F4}";
    public string SignificanceDisplay => Significant ? "Significant" : "Not Significant";

    public StatisticalTestResultItem(StatisticalTestResultModel result)
    {
      TestName = result.TestName;
      TestStatistic = result.TestStatistic;
      PValue = result.PValue;
      Significant = result.Significant;
      Interpretation = result.Interpretation;
    }
  }
}

