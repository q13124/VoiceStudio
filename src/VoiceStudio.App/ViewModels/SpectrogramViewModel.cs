using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;
using VoiceStudio.App.Utilities;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// ViewModel for the SpectrogramView panel - Advanced spectrogram visualization.
  /// </summary>
  public partial class SpectrogramViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;
    private readonly ToastNotificationService? _toastNotificationService;

    public string PanelId => "spectrogram";
    public string DisplayName => ResourceHelper.GetString("Panel.Spectrogram.DisplayName", "Spectrogram");
    public PanelRegion Region => PanelRegion.Center;

    [ObservableProperty]
    private string? selectedAudioId;

    [ObservableProperty]
    private ObservableCollection<string> availableAudioIds = new();

    [ObservableProperty]
    private int windowSize = 2048;

    [ObservableProperty]
    private int hopLength = 512;

    [ObservableProperty]
    private int nFft = 2048;

    [ObservableProperty]
    private double frequencyMin = double.NaN;

    [ObservableProperty]
    private double frequencyMax = double.NaN;

    [ObservableProperty]
    private double timeStart = double.NaN;

    [ObservableProperty]
    private double timeEnd = double.NaN;

    [ObservableProperty]
    private bool logScale = true;

    [ObservableProperty]
    private string selectedColorScheme = "viridis";

    [ObservableProperty]
    private ObservableCollection<ColorSchemeInfo> availableColorSchemes = new();

    [ObservableProperty]
    private SpectrogramDataItem? spectrogramData;

    [ObservableProperty]
    private bool showPhase;

    [ObservableProperty]
    private bool showMagnitude = true;

    public SpectrogramViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      // Get services (may be null if not initialized)
      try
      {
        _toastNotificationService = AppServices.TryGetToastNotificationService();
      }
      catch
      {
        // Services may not be initialized yet - that's okay
        _toastNotificationService = null;
      }

      LoadSpectrogramCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadSpectrogram");
        await LoadSpectrogramAsync(ct);
      }, () => !string.IsNullOrEmpty(SelectedAudioId) && !IsLoading);
      UpdateConfigCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("UpdateConfig");
        await UpdateConfigAsync(ct);
      }, () => !string.IsNullOrEmpty(SelectedAudioId) && !IsLoading);
      ExportSpectrogramCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("ExportSpectrogram");
        await ExportSpectrogramAsync(ct);
      }, () => !string.IsNullOrEmpty(SelectedAudioId) && !IsLoading);
      LoadColorSchemesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadColorSchemes");
        await LoadColorSchemesAsync(ct);
      }, () => !IsLoading);

      // Load initial data
      _ = LoadColorSchemesAsync(CancellationToken.None);
    }

    public IAsyncRelayCommand LoadSpectrogramCommand { get; }
    public IAsyncRelayCommand UpdateConfigCommand { get; }
    public IAsyncRelayCommand ExportSpectrogramCommand { get; }
    public IAsyncRelayCommand LoadColorSchemesCommand { get; }

    private async Task LoadSpectrogramAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrEmpty(SelectedAudioId))
      {
        ErrorMessage = ResourceHelper.GetString("Spectrogram.AudioFileRequired", "Audio file must be selected");
        return;
      }

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var queryParams = new System.Collections.Specialized.NameValueCollection();
        queryParams.Add("window_size", WindowSize.ToString());
        queryParams.Add("hop_length", HopLength.ToString());
        queryParams.Add("n_fft", NFft.ToString());
        if (!double.IsNaN(FrequencyMin))
          queryParams.Add("frequency_min", FrequencyMin.ToString());
        if (!double.IsNaN(FrequencyMax))
          queryParams.Add("frequency_max", FrequencyMax.ToString());
        if (!double.IsNaN(TimeStart))
          queryParams.Add("time_start", TimeStart.ToString());
        if (!double.IsNaN(TimeEnd))
          queryParams.Add("time_end", TimeEnd.ToString());
        queryParams.Add("log_scale", LogScale.ToString().ToLower());

        var queryString = string.Join("&",
            queryParams.AllKeys.SelectMany(key =>
                queryParams.GetValues(key)?.Select(value => $"{key}={Uri.EscapeDataString(value)}") ?? Array.Empty<string>()
            )
        );

        var url = $"/api/spectrogram/data/{Uri.EscapeDataString(SelectedAudioId)}";
        if (!string.IsNullOrEmpty(queryString))
          url += $"?{queryString}";

        var data = await _backendClient.SendRequestAsync<object, SpectrogramData>(
            url,
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (data != null)
        {
          SpectrogramData = new SpectrogramDataItem(data);
          StatusMessage = ResourceHelper.GetString("Spectrogram.SpectrogramLoaded", "Spectrogram loaded");
          _toastNotificationService?.ShowSuccess(
              ResourceHelper.FormatString("Spectrogram.SpectrogramLoadedDetail", data.Duration.ToString("F2")),
              ResourceHelper.GetString("Toast.Title.LoadComplete", "Load Complete"));
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadSpectrogram");
        _toastNotificationService?.ShowError(
            ResourceHelper.GetString("Toast.Title.LoadFailed", "Load Failed"),
            ex.Message);
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task UpdateConfigAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrEmpty(SelectedAudioId))
        return;

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var config = new
        {
          audio_id = SelectedAudioId,
          window_size = WindowSize,
          hop_length = HopLength,
          n_fft = NFft,
          frequency_range = (!double.IsNaN(FrequencyMin) || !double.IsNaN(FrequencyMax)) ? new
          {
            min = double.IsNaN(FrequencyMin) ? 0.0 : FrequencyMin,
            max = double.IsNaN(FrequencyMax) ? 22050.0 : FrequencyMax
          } : null,
          time_range = (!double.IsNaN(TimeStart) || !double.IsNaN(TimeEnd)) ? new
          {
            start = double.IsNaN(TimeStart) ? 0.0 : TimeStart,
            end = double.IsNaN(TimeEnd) ? 10.0 : TimeEnd
          } : null,
          color_scheme = SelectedColorScheme,
          show_phase = ShowPhase,
          show_magnitude = ShowMagnitude,
          log_scale = LogScale
        };

        await _backendClient.SendRequestAsync<object, object>(
            $"/api/spectrogram/config/{Uri.EscapeDataString(SelectedAudioId)}",
            config,
            System.Net.Http.HttpMethod.Put,
            cancellationToken
        );

        await LoadSpectrogramAsync(cancellationToken);
        StatusMessage = ResourceHelper.GetString("Spectrogram.ConfigurationUpdated", "Configuration updated");
        _toastNotificationService?.ShowSuccess(
            ResourceHelper.GetString("Spectrogram.ConfigurationUpdatedDetail", "Spectrogram configuration updated"),
            ResourceHelper.GetString("Toast.Title.ConfigUpdated", "Config Updated"));
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "UpdateConfig");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task ExportSpectrogramAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrEmpty(SelectedAudioId))
      {
        ErrorMessage = ResourceHelper.GetString("Spectrogram.AudioFileRequired", "Audio file must be selected");
        return;
      }

      try
      {
        IsLoading = true;
        ErrorMessage = null;

        // In a real implementation, this would open a file picker
        // and download the exported image
        var response = await _backendClient.SendRequestAsync<object, SpectrogramExportResponse>(
            $"/api/spectrogram/export/{Uri.EscapeDataString(SelectedAudioId)}?format=png&width=1920&height=1080",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        StatusMessage = ResourceHelper.GetString("Spectrogram.ExportInitiated", "Spectrogram export initiated");
        if (response != null)
        {
          _toastNotificationService?.ShowSuccess(
              ResourceHelper.FormatString("Spectrogram.SpectrogramExportedDetail", response.Width, response.Height, response.Format.ToUpper()),
              ResourceHelper.GetString("Toast.Title.ExportComplete", "Export Complete"));
        }
        else
        {
          _toastNotificationService?.ShowSuccess(
              ResourceHelper.GetString("Spectrogram.ExportInitiatedDetail", "Spectrogram export initiated"),
              ResourceHelper.GetString("Toast.Title.ExportStarted", "Export Started"));
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "ExportSpectrogram");
        _toastNotificationService?.ShowError(
            ResourceHelper.GetString("Toast.Title.ExportFailed", "Export Failed"),
            ex.Message);
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task LoadColorSchemesAsync(CancellationToken cancellationToken)
    {
      try
      {
        var response = await _backendClient.SendRequestAsync<object, ColorSchemesResponse>(
            "/api/spectrogram/color-schemes",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        AvailableColorSchemes.Clear();
        if (response?.Schemes != null)
        {
          foreach (var scheme in response.Schemes)
          {
            AvailableColorSchemes.Add(new ColorSchemeInfo
            {
              Id = scheme.Id,
              Name = scheme.Name,
              Description = scheme.Description
            });
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadColorSchemes");
      }
    }

    partial void OnSelectedAudioIdChanged(string? value)
    {
      if (!string.IsNullOrEmpty(value))
      {
        _ = LoadSpectrogramAsync(CancellationToken.None);
      }
    }

    // Response models
    private class ColorSchemesResponse
    {
      public ColorScheme[] Schemes { get; set; } = Array.Empty<ColorScheme>();
    }

    private class ColorScheme
    {
      public string Id { get; set; } = string.Empty;
      public string Name { get; set; } = string.Empty;
      public string Description { get; set; } = string.Empty;
    }

    private class SpectrogramExportResponse
    {
      public string AudioId { get; set; } = string.Empty;
      public string Format { get; set; } = string.Empty;
      public int Width { get; set; }
      public int Height { get; set; }
    }
  }

  // Data models
  public class SpectrogramData
  {
    public string AudioId { get; set; } = string.Empty;
    public int SampleRate { get; set; }
    public double Duration { get; set; }
    public System.Collections.Generic.List<SpectrogramFrame> Frames { get; set; } = new();
    public double FrequencyResolution { get; set; }
    public double TimeResolution { get; set; }
    public SpectrogramConfig Config { get; set; } = new();
  }

  public class SpectrogramFrame
  {
    public double Time { get; set; }
    public System.Collections.Generic.List<double> Frequencies { get; set; } = new();
    public System.Collections.Generic.List<double> Magnitudes { get; set; } = new();
    public System.Collections.Generic.List<double>? Phases { get; set; }
  }

  public class SpectrogramConfig
  {
    public string AudioId { get; set; } = string.Empty;
    public int WindowSize { get; set; }
    public int HopLength { get; set; }
    public int NFft { get; set; }
    public System.Collections.Generic.Dictionary<string, double>? FrequencyRange { get; set; }
    public System.Collections.Generic.Dictionary<string, double>? TimeRange { get; set; }
    public string ColorScheme { get; set; } = "viridis";
    public System.Collections.Generic.Dictionary<string, double>? ColormapRange { get; set; }
    public bool ShowPhase { get; set; }
    public bool ShowMagnitude { get; set; }
    public bool LogScale { get; set; }
  }

  public class SpectrogramDataItem : ObservableObject
  {
    public string AudioId { get; set; }
    public int SampleRate { get; set; }
    public double Duration { get; set; }
    public System.Collections.Generic.List<SpectrogramFrame> Frames { get; set; }
    public double FrequencyResolution { get; set; }
    public double TimeResolution { get; set; }
    public SpectrogramConfig Config { get; set; }
    public int FrameCount => Frames?.Count ?? 0;

    public SpectrogramDataItem(SpectrogramData data)
    {
      AudioId = data.AudioId;
      SampleRate = data.SampleRate;
      Duration = data.Duration;
      Frames = data.Frames;
      FrequencyResolution = data.FrequencyResolution;
      TimeResolution = data.TimeResolution;
      Config = data.Config;
    }
  }

  public class ColorSchemeInfo : ObservableObject
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
  }
}