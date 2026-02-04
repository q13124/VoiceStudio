using System;
using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;
using VoiceStudio.App.Utilities;
using Microsoft.UI.Xaml;

namespace VoiceStudio.App.ViewModels
{
  /// <summary>
  /// ViewModel for the RecordingView panel.
  /// </summary>
  public partial class RecordingViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;
    private readonly ToastNotificationService? _toastNotificationService;
    private readonly IErrorPresentationService? _errorService;
    private readonly IErrorLoggingService? _logService;
    private readonly DispatcherTimer _statusTimer;

    public string PanelId => "recording";
    public string DisplayName => ResourceHelper.GetString("Panel.Recording.DisplayName", "Recording");
    public PanelRegion Region => PanelRegion.Right;

    [ObservableProperty]
    private bool isRecording;

    [ObservableProperty]
    private string? recordingId;

    [ObservableProperty]
    private TimeSpan recordingDuration = TimeSpan.Zero;

    [ObservableProperty]
    private string recordingDurationDisplay = "00:00";

    [ObservableProperty]
    private int sampleRate = 44100;

    [ObservableProperty]
    private int channels = 1;

    [ObservableProperty]
    private int bitDepth = 16;

    [ObservableProperty]
    private string? selectedDevice;

    [ObservableProperty]
    private string? filename;

    [ObservableProperty]
    private string? projectId;

    [ObservableProperty]
    private string? recordedAudioId;

    [ObservableProperty]
    private string? recordedAudioUrl;

    [ObservableProperty]
    private ObservableCollection<string> availableDevices = new();

    [ObservableProperty]
    private ObservableCollection<float> waveformSamples = new();

    [ObservableProperty]
    private string selectedFormat = "wav";

    [ObservableProperty]
    private ObservableCollection<string> availableFormats = new() { "wav", "mp3", "flac", "ogg" };

    public ObservableCollection<int> AvailableSampleRates { get; } = new()
        {
            44100,
            48000,
            96000
        };

    public ObservableCollection<int> AvailableChannels { get; } = new()
        {
            1,  // Mono
            2   // Stereo
        };

    public ObservableCollection<int> AvailableBitDepths { get; } = new()
        {
            16,
            24
        };

    public RecordingViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      // Get services using helper (reduces code duplication)
      _toastNotificationService = ServiceInitializationHelper.TryGetService(() => ServiceProvider.GetToastNotificationService());

      // Get error services
      _errorService = ServiceProvider.TryGetErrorPresentationService();
      _logService = ServiceProvider.TryGetErrorLoggingService();

      _statusTimer = new DispatcherTimer
      {
        Interval = TimeSpan.FromMilliseconds(100)
      };
      _statusTimer.Tick += StatusTimer_Tick;

      StartRecordingCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("StartRecording");
        await StartRecordingAsync(ct);
      }, () => !IsRecording);

      StopRecordingCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("StopRecording");
        await StopRecordingAsync(ct);
      }, () => IsRecording);

      CancelRecordingCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("CancelRecording");
        await CancelRecordingAsync(ct);
      }, () => IsRecording);

      LoadDevicesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadDevices");
        await LoadDevicesAsync(ct);
      });

      // Load devices on initialization
      var loadCt = new CancellationTokenSource(TimeSpan.FromSeconds(30)).Token;
      _ = LoadDevicesAsync(loadCt).ContinueWith(t =>
      {
        if (t.IsFaulted)
          _logService?.LogError(t.Exception?.InnerException ?? new Exception("LoadDevices failed"), "LoadDevices");
      }, TaskScheduler.Default);
    }

    public EnhancedAsyncRelayCommand StartRecordingCommand { get; }
    public EnhancedAsyncRelayCommand StopRecordingCommand { get; }
    public EnhancedAsyncRelayCommand CancelRecordingCommand { get; }
    public EnhancedAsyncRelayCommand LoadDevicesCommand { get; }

    private async Task StartRecordingAsync(CancellationToken cancellationToken)
    {
      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var request = new
        {
          sample_rate = SampleRate,
          channels = Channels,
          bit_depth = BitDepth,
          format = SelectedFormat,
          project_id = ProjectId,
          filename = Filename,
          device = SelectedDevice
        };

        var response = await _backendClient.SendRequestAsync<object, RecordingStartResponse>(
            "/api/recording/start",
            request,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        if (response == null)
        {
          throw new InvalidOperationException("Backend returned no response when starting recording.");
        }

        RecordingId = response.RecordingId;
        IsRecording = true;
        RecordingDuration = TimeSpan.Zero;
        RecordedAudioId = null;
        RecordedAudioUrl = null;

        // Start status polling
        _statusTimer.Start();

        StatusMessage = ResourceHelper.GetString("Recording.RecordingStarted", "Recording started");
        _toastNotificationService?.ShowSuccess(
            ResourceHelper.FormatString("Recording.RecordingStartedDetail", SampleRate, Channels),
            ResourceHelper.GetString("Toast.Title.RecordingStarted", "Recording Started"));
      }
      catch (OperationCanceledException)
      {
        // User cancelled - expected
        return;
      }
      catch (Exception ex)
      {
        var errorMsg = ErrorHandler.GetUserFriendlyMessage(ex);
        ErrorMessage = ResourceHelper.FormatString("Recording.StartRecordingFailed", errorMsg);
        _errorService?.ShowError(ex, ResourceHelper.GetString("Recording.StartRecordingFailedTitle", "Failed to start recording"));
        _logService?.LogError(ex, "StartRecording");
        _toastNotificationService?.ShowError(
            ResourceHelper.FormatString("Recording.StartRecordingFailed", errorMsg),
            ResourceHelper.GetString("Toast.Title.StartFailed", "Start Failed"));
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task StopRecordingAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrEmpty(RecordingId))
        return;

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        _statusTimer.Stop();

        var response = await _backendClient.SendRequestAsync<object, RecordingStopResponse>(
            $"/api/recording/{RecordingId}/stop",
            null,
            System.Net.Http.HttpMethod.Post,
            cancellationToken
        );

        if (response == null)
        {
          throw new InvalidOperationException("Backend returned no response when stopping recording.");
        }

        RecordedAudioId = response.AudioId;
        RecordedAudioUrl = response.AudioUrl;
        IsRecording = false;

        StatusMessage = ResourceHelper.FormatString("Recording.RecordingStopped", response.Duration);
        _toastNotificationService?.ShowSuccess(
            ResourceHelper.FormatString("Recording.RecordingStoppedDetail", response.Duration),
            ResourceHelper.GetString("Toast.Title.RecordingComplete", "Recording Complete"));
      }
      catch (OperationCanceledException)
      {
        // User cancelled - expected
        return;
      }
      catch (Exception ex)
      {
        var errorMsg = ErrorHandler.GetUserFriendlyMessage(ex);
        ErrorMessage = ResourceHelper.FormatString("Recording.StopRecordingFailed", errorMsg);
        _errorService?.ShowError(ex, ResourceHelper.GetString("Recording.StopRecordingFailedTitle", "Failed to stop recording"));
        _logService?.LogError(ex, "StopRecording");
        _toastNotificationService?.ShowError(
            ResourceHelper.FormatString("Recording.StopRecordingFailed", errorMsg),
            ResourceHelper.GetString("Toast.Title.StopFailed", "Stop Failed"));
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task CancelRecordingAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrEmpty(RecordingId))
        return;

      IsLoading = true;
      ErrorMessage = null;

      try
      {
        _statusTimer.Stop();

        await _backendClient.SendRequestAsync<object, object>(
            $"/api/recording/{RecordingId}",
            null,
            System.Net.Http.HttpMethod.Delete,
            cancellationToken
        );

        RecordingId = null;
        IsRecording = false;
        RecordingDuration = TimeSpan.Zero;
        RecordedAudioId = null;
        RecordedAudioUrl = null;

        StatusMessage = ResourceHelper.GetString("Recording.RecordingCancelled", "Recording cancelled");
        _toastNotificationService?.ShowWarning(
            ResourceHelper.GetString("Recording.RecordingCancelled", "Recording cancelled"),
            ResourceHelper.GetString("Toast.Title.RecordingCancelled", "Recording Cancelled"));
      }
      catch (OperationCanceledException)
      {
        // User cancelled - expected
        return;
      }
      catch (Exception ex)
      {
        var errorMsg = ErrorHandler.GetUserFriendlyMessage(ex);
        ErrorMessage = ResourceHelper.FormatString("Recording.CancelRecordingFailed", errorMsg);
        _errorService?.ShowError(ex, ResourceHelper.GetString("Recording.CancelRecordingFailedTitle", "Failed to cancel recording"));
        _logService?.LogError(ex, "CancelRecording");
        _toastNotificationService?.ShowError(
            ResourceHelper.FormatString("Recording.CancelRecordingFailed", errorMsg),
            ResourceHelper.GetString("Toast.Title.CancelFailed", "Cancel Failed"));
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task LoadDevicesAsync(CancellationToken cancellationToken)
    {
      try
      {
        var response = await _backendClient.SendRequestAsync<object, RecordingDevicesResponse>(
            "/api/recording/devices",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        AvailableDevices.Clear();
        if (response?.Devices != null)
        {
          foreach (var device in response.Devices)
          {
            AvailableDevices.Add(device.Name);
          }
        }

        if (AvailableDevices.Count > 0 && string.IsNullOrEmpty(SelectedDevice))
        {
          SelectedDevice = AvailableDevices[0];
        }
      }
      catch (OperationCanceledException)
      {
        // User cancelled - expected
        return;
      }
      catch (Exception ex)
      {
        var errorMsg = ErrorHandler.GetUserFriendlyMessage(ex);
        ErrorMessage = ResourceHelper.FormatString("Recording.LoadDevicesFailed", errorMsg);
        _errorService?.ShowError(ex, ResourceHelper.GetString("Recording.LoadDevicesFailedTitle", "Failed to load recording devices"));
        _logService?.LogError(ex, "LoadDevices");
      }
    }

    private async void StatusTimer_Tick(object? sender, object e)
    {
      if (string.IsNullOrEmpty(RecordingId) || !IsRecording)
        return;

      try
      {
        var status = await _backendClient.SendRequestAsync<object, RecordingStatusResponse>(
            $"/api/recording/{RecordingId}/status",
            null,
            System.Net.Http.HttpMethod.Get
        );

        if (status == null)
        {
          return;
        }

        RecordingDuration = TimeSpan.FromSeconds(status.Duration);
        RecordingDurationDisplay = RecordingDuration.ToString(@"mm\:ss");

        // Update waveform samples if available
        if (status.WaveformSamples?.Length > 0)
        {
          WaveformSamples.Clear();
          foreach (var sample in status.WaveformSamples)
          {
            WaveformSamples.Add(sample);
          }
        }
      }
      catch (Exception ex)
      {
        // Silently handle errors during status polling
        System.Diagnostics.Debug.WriteLine($"Status polling error: {ex.Message}");
      }
    }

    // Response models
    private class RecordingStartResponse
    {
      public string RecordingId { get; set; } = string.Empty;
      public bool IsRecording { get; set; }
      public double Duration { get; set; }
      public int SampleRate { get; set; }
      public int Channels { get; set; }
      public int BitDepth { get; set; }
    }

    private class RecordingStatusResponse
    {
      public string RecordingId { get; set; } = string.Empty;
      public bool IsRecording { get; set; }
      public double Duration { get; set; }
      public float[]? WaveformSamples { get; set; }
    }

    private class RecordingStopResponse
    {
      public string RecordingId { get; set; } = string.Empty;
      public string AudioId { get; set; } = string.Empty;
      public string AudioUrl { get; set; } = string.Empty;
      public double Duration { get; set; }
    }

    private class RecordingDevicesResponse
    {
      public RecordingDevice[] Devices { get; set; } = Array.Empty<RecordingDevice>();
    }

    private class RecordingDevice
    {
      public string Id { get; set; } = string.Empty;
      public string Name { get; set; } = string.Empty;
    }
  }
}