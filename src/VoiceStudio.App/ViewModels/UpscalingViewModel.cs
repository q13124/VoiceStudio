using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Net.Http;
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
  /// ViewModel for the UpscalingView panel - Image and video upscaling.
  /// </summary>
  public partial class UpscalingViewModel : BaseViewModel, IPanelView
  {
    private readonly IBackendClient _backendClient;
    private readonly ToastNotificationService? _toastNotificationService;

    public string PanelId => "upscaling";
    public string DisplayName => ResourceHelper.GetString("Panel.Upscaling.DisplayName", "Upscaling");
    public PanelRegion Region => PanelRegion.Center;

    [ObservableProperty]
    private ObservableCollection<UpscalingEngineItem> availableEngines = new();

    [ObservableProperty]
    private ObservableCollection<UpscalingJobItem> upscalingJobs = new();

    [ObservableProperty]
    private UpscalingEngineItem? selectedEngine;

    [ObservableProperty]
    private UpscalingJobItem? selectedJob;

    [ObservableProperty]
    private string selectedMediaType = "image";

    [ObservableProperty]
    private ObservableCollection<string> availableMediaTypes = new() { "image", "video" };

    [ObservableProperty]
    private double selectedScaleFactor = 2.0;

    [ObservableProperty]
    private ObservableCollection<double> availableScaleFactors = new() { 2.0, 4.0, 8.0 };

    [ObservableProperty]
    private string? selectedFilePath;

    [ObservableProperty]
    private bool isProcessing;

    [ObservableProperty]
    private string? outputFormat;

    [ObservableProperty]
    private double uploadProgress;

    [ObservableProperty]
    private bool isUploading;

    public UpscalingViewModel(IViewModelContext context, IBackendClient backendClient)
        : base(context)
    {
      _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

      // Get services (may be null if not initialized)
      try
      {
        _toastNotificationService = ServiceProvider.GetToastNotificationService();
      }
      catch
      {
        // Services may not be initialized yet - that's okay
        _toastNotificationService = null;
      }

      LoadEnginesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadEngines");
        await LoadEnginesAsync(ct);
      }, () => !IsLoading);
      UpscaleCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("Upscale");
        await UpscaleAsync(ct);
      }, () => !IsProcessing && !string.IsNullOrWhiteSpace(SelectedFilePath) && SelectedEngine != null && !IsLoading);
      LoadJobsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("LoadJobs");
        await LoadJobsAsync(ct);
      }, () => !IsLoading);
      DeleteJobCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("DeleteJob");
        await DeleteJobAsync(ct);
      }, () => SelectedJob != null && !IsLoading);
      RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
      {
        using var profiler = PerformanceProfiler.StartCommand("Refresh");
        await RefreshAsync(ct);
      }, () => !IsLoading);

      // Load initial data
      _ = LoadEnginesAsync(CancellationToken.None);
      _ = LoadJobsAsync(CancellationToken.None);
    }

    public IAsyncRelayCommand LoadEnginesCommand { get; }
    public IAsyncRelayCommand UpscaleCommand { get; }
    public IAsyncRelayCommand LoadJobsCommand { get; }
    public IAsyncRelayCommand DeleteJobCommand { get; }
    public IAsyncRelayCommand RefreshCommand { get; }

    partial void OnIsProcessingChanged(bool value)
    {
      UpscaleCommand.NotifyCanExecuteChanged();
    }

    partial void OnSelectedFilePathChanged(string? value)
    {
      UpscaleCommand.NotifyCanExecuteChanged();

      // Auto-detect media type from file extension
      if (!string.IsNullOrWhiteSpace(value))
      {
        var ext = Path.GetExtension(value).ToLowerInvariant();
        if (ext == ".jpg" || ext == ".jpeg" || ext == ".png" || ext == ".bmp" || ext == ".gif" || ext == ".webp")
        {
          SelectedMediaType = "image";
        }
        else if (ext == ".mp4" || ext == ".avi" || ext == ".mov" || ext == ".mkv" || ext == ".webm")
        {
          SelectedMediaType = "video";
        }
      }
    }

    partial void OnSelectedEngineChanged(UpscalingEngineItem? value)
    {
      ((System.Windows.Input.ICommand)UpscaleCommand).NotifyCanExecuteChanged();

      // Update available scale factors based on engine
      if (value != null)
      {
        AvailableScaleFactors.Clear();
        foreach (var scale in value.SupportedScales)
        {
          AvailableScaleFactors.Add(scale);
        }

        // Reset scale factor if current is not supported
        if (!AvailableScaleFactors.Contains(SelectedScaleFactor))
        {
          SelectedScaleFactor = AvailableScaleFactors.FirstOrDefault();
        }
      }
    }

    partial void OnSelectedJobChanged(UpscalingJobItem? value)
    {
      ((System.Windows.Input.ICommand)DeleteJobCommand).NotifyCanExecuteChanged();
    }

    partial void OnSelectedMediaTypeChanged(string value)
    {
      // Filter engines based on media type
      if (SelectedEngine != null && !SelectedEngine.SupportedTypes.Contains(value))
      {
        SelectedEngine = AvailableEngines.FirstOrDefault(e => e.SupportedTypes.Contains(value));
      }
    }

    private async Task LoadEnginesAsync(CancellationToken cancellationToken = default)
    {
      try
      {
        IsLoading = true;
        ErrorMessage = null;

        var engines = await _backendClient.SendRequestAsync<object, UpscalingEngine[]>(
            "/api/upscaling/engines",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (engines != null)
        {
          AvailableEngines.Clear();
          foreach (var engine in engines)
          {
            AvailableEngines.Add(new UpscalingEngineItem(
                engine.EngineId,
                engine.Name,
                engine.Description,
                engine.SupportedTypes,
                engine.SupportedScales,
                engine.IsAvailable
            ));
          }

          // Select first available engine for current media type
          SelectedEngine = AvailableEngines.FirstOrDefault(e => e.SupportedTypes.Contains(SelectedMediaType));
          _toastNotificationService?.ShowInfo(
              ResourceHelper.FormatString("Upscaling.EnginesLoadedDetail", AvailableEngines.Count),
              ResourceHelper.GetString("Toast.Title.EnginesLoaded", "Engines Loaded"));
        }
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("Upscaling.LoadEnginesFailed", ex.Message);
        _toastNotificationService?.ShowError(
            ResourceHelper.GetString("Toast.Title.LoadFailed", "Load Failed"),
            ResourceHelper.FormatString("Upscaling.LoadEnginesFailed", ex.Message));
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task UpscaleAsync(CancellationToken cancellationToken)
    {
      if (string.IsNullOrWhiteSpace(SelectedFilePath) || SelectedEngine == null)
      {
        ErrorMessage = ResourceHelper.GetString("Upscaling.SelectionRequired", "Please select a file and engine");
        return;
      }

      if (!File.Exists(SelectedFilePath))
      {
        ErrorMessage = ResourceHelper.GetString("Upscaling.FileDoesNotExist", "Selected file does not exist");
        return;
      }

      // Validate file size (max 500MB for images, 2GB for videos)
      var fileInfo = new FileInfo(SelectedFilePath);
      var maxSize = SelectedMediaType == "image" ? 500 * 1024 * 1024L : 2L * 1024 * 1024 * 1024;
      if (fileInfo.Length > maxSize)
      {
        ErrorMessage = ResourceHelper.FormatString("Upscaling.FileSizeExceeded", maxSize / (1024.0 * 1024.0));
        return;
      }

      // Validate file format
      var ext = Path.GetExtension(SelectedFilePath).ToLowerInvariant();
      var validExtensions = SelectedMediaType == "image"
          ? new[] { ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp" }
          : new[] { ".mp4", ".avi", ".mov", ".mkv", ".webm" };

      if (!validExtensions.Contains(ext))
      {
        ErrorMessage = ResourceHelper.FormatString("Upscaling.InvalidFileFormat", string.Join(", ", validExtensions));
        return;
      }

      IsProcessing = true;
      ErrorMessage = null;

      try
      {
        var request = new
        {
          media_type = SelectedMediaType,
          engine = SelectedEngine.EngineId,
          scale_factor = SelectedScaleFactor,
          output_format = OutputFormat
        };

        var jobResponse = await UploadFileAndUpscaleAsync(SelectedFilePath, request, cancellationToken);

        if (jobResponse != null)
        {
          await LoadJobsAsync(cancellationToken);
          StatusMessage = ResourceHelper.FormatString("Upscaling.UpscalingStarted", SelectedScaleFactor, SelectedMediaType);
          _toastNotificationService?.ShowSuccess(
              ResourceHelper.FormatString("Upscaling.UpscalingStartedDetail", SelectedScaleFactor, SelectedMediaType),
              ResourceHelper.GetString("Toast.Title.UpscalingStarted", "Upscaling Started"));
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "Upscale");
        _toastNotificationService?.ShowError(
            ResourceHelper.GetString("Toast.Title.StartFailed", "Start Failed"),
            ResourceHelper.FormatString("Upscaling.StartUpscalingFailed", ex.Message));
      }
      finally
      {
        IsProcessing = false;
      }
    }

    private async Task<UpscalingJobResponse?> UploadFileAndUpscaleAsync(string filePath, object requestData, CancellationToken cancellationToken = default)
    {
      const string baseUrl = "http://localhost:8001";
      using var httpClient = new HttpClient();
      httpClient.BaseAddress = new Uri(baseUrl);
      httpClient.Timeout = TimeSpan.FromMinutes(30); // Allow longer timeout for large files

      IsUploading = true;
      UploadProgress = 0.0;

      try
      {
        await using var fileStream = File.OpenRead(filePath);
        var fileName = Path.GetFileName(filePath);
        var contentType = SelectedMediaType == "image" ? "image/jpeg" : "video/mp4";
        var fileSize = fileStream.Length;

        // Create progress tracking stream
        var progressStream = new ProgressStream(fileStream, (bytesRead, totalBytes) => UploadProgress = bytesRead / (double)totalBytes * 100.0);

        using var content = new MultipartFormDataContent();
        var streamContent = new StreamContent(progressStream);
        streamContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(contentType);
        content.Add(streamContent, "file", fileName);

        var requestJson = System.Text.Json.JsonSerializer.Serialize(requestData);
        content.Add(new StringContent(requestJson, System.Text.Encoding.UTF8, "application/json"), "request");

        var response = await httpClient.PostAsync("/api/upscaling/upscale", content, cancellationToken);
        response.EnsureSuccessStatusCode();

        var responseJson = await response.Content.ReadAsStringAsync();
        return System.Text.Json.JsonSerializer.Deserialize<UpscalingJobResponse>(responseJson);
      }
      finally
      {
        IsUploading = false;
        UploadProgress = 0.0;
      }
    }

    // Progress tracking stream wrapper
    private class ProgressStream : Stream
    {
      private readonly Stream _baseStream;
      private readonly Action<long, long> _progressCallback;
      private long _bytesRead;

      public ProgressStream(Stream baseStream, Action<long, long> progressCallback)
      {
        _baseStream = baseStream;
        _progressCallback = progressCallback;
      }

      public override bool CanRead => _baseStream.CanRead;
      public override bool CanSeek => _baseStream.CanSeek;
      public override bool CanWrite => _baseStream.CanWrite;
      public override long Length => _baseStream.Length;
      public override long Position
      {
        get => _baseStream.Position;
        set => _baseStream.Position = value;
      }

      public override void Flush() => _baseStream.Flush();
      public override long Seek(long offset, SeekOrigin origin) => _baseStream.Seek(offset, origin);
      public override void SetLength(long value) => _baseStream.SetLength(value);
      public override void Write(byte[] buffer, int offset, int count) => _baseStream.Write(buffer, offset, count);

      public override int Read(byte[] buffer, int offset, int count)
      {
        var bytesRead = _baseStream.Read(buffer, offset, count);
        _bytesRead += bytesRead;
        _progressCallback(_bytesRead, Length);
        return bytesRead;
      }

      protected override void Dispose(bool disposing)
      {
        if (disposing)
        {
          _baseStream.Dispose();
        }
        base.Dispose(disposing);
      }
    }

    private async Task LoadJobsAsync(CancellationToken cancellationToken)
    {
      IsLoading = true;
      ErrorMessage = null;

      try
      {
        var jobs = await _backendClient.SendRequestAsync<object, UpscalingJob[]>(
            "/api/upscaling/jobs",
            null,
            System.Net.Http.HttpMethod.Get,
            cancellationToken
        );

        if (jobs != null)
        {
          UpscalingJobs.Clear();
          foreach (var job in jobs)
          {
            UpscalingJobs.Add(new UpscalingJobItem(
                job.JobId,
                job.Status,
                job.Progress,
                job.OutputFile,
                job.OriginalWidth,
                job.OriginalHeight,
                job.UpscaledWidth,
                job.UpscaledHeight,
                job.ErrorMessage
            ));
          }
        }
      }
      catch (OperationCanceledException)
      {
        return; // User cancelled
      }
      catch (Exception ex)
      {
        await HandleErrorAsync(ex, "LoadJobs");
      }
      finally
      {
        IsLoading = false;
      }
    }

    private async Task DeleteJobAsync(CancellationToken cancellationToken = default)
    {
      if (SelectedJob == null)
      {
        return;
      }

      try
      {
        IsLoading = true;
        ErrorMessage = null;

        await _backendClient.SendRequestAsync<object, object>(
            $"/api/upscaling/jobs/{Uri.EscapeDataString(SelectedJob.JobId)}",
            null,
            System.Net.Http.HttpMethod.Delete,
            cancellationToken
        );

        UpscalingJobs.Remove(SelectedJob);
        SelectedJob = null;

        StatusMessage = ResourceHelper.GetString("Upscaling.JobDeleted", "Job deleted successfully");
        _toastNotificationService?.ShowSuccess(
            ResourceHelper.GetString("Upscaling.JobDeletedDetail", "Upscaling job deleted"),
            ResourceHelper.GetString("Toast.Title.JobDeleted", "Job Deleted"));
      }
      catch (Exception ex)
      {
        ErrorMessage = ResourceHelper.FormatString("Upscaling.DeleteJobFailed", ex.Message);
        _toastNotificationService?.ShowError(
            ResourceHelper.GetString("Toast.Title.DeleteFailed", "Delete Failed"),
            ResourceHelper.FormatString("Upscaling.DeleteJobFailed", ex.Message));
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
        await LoadEnginesAsync(cancellationToken);
        await LoadJobsAsync(cancellationToken);
        StatusMessage = ResourceHelper.GetString("Upscaling.Refreshed", "Refreshed");
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

    // Request/Response models
    private class UpscalingJobResponse
    {
      public string JobId { get; set; } = string.Empty;
      public string Status { get; set; } = string.Empty;
    }

    private class UpscalingEngine
    {
      public string EngineId { get; set; } = string.Empty;
      public string Name { get; set; } = string.Empty;
      public string Description { get; set; } = string.Empty;
      public string[] SupportedTypes { get; set; } = Array.Empty<string>();
      public double[] SupportedScales { get; set; } = Array.Empty<double>();
      public bool IsAvailable { get; set; }
    }

    private class UpscalingJob
    {
      public string JobId { get; set; } = string.Empty;
      public string Status { get; set; } = string.Empty;
      public double Progress { get; set; }
      public string? OutputFile { get; set; }
      public int? OriginalWidth { get; set; }
      public int? OriginalHeight { get; set; }
      public int? UpscaledWidth { get; set; }
      public int? UpscaledHeight { get; set; }
      public string? ErrorMessage { get; set; }
    }
  }

  // Data models
  public class UpscalingEngineItem : ObservableObject
  {
    public string EngineId { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public string[] SupportedTypes { get; set; }
    public double[] SupportedScales { get; set; }
    public bool IsAvailable { get; set; }

    public string DisplayName => $"{Name} ({string.Join(", ", SupportedTypes)})";
    public string ScalesDisplay => string.Join("×, ", SupportedScales) + "×";

    public UpscalingEngineItem(string engineId, string name, string description, string[] supportedTypes, double[] supportedScales, bool isAvailable)
    {
      EngineId = engineId;
      Name = name;
      Description = description;
      SupportedTypes = supportedTypes;
      SupportedScales = supportedScales;
      IsAvailable = isAvailable;
    }
  }

  public class UpscalingJobItem : ObservableObject
  {
    public string JobId { get; set; }
    public string Status { get; set; }
    public double Progress { get; set; }
    public string? OutputFile { get; set; }
    public int? OriginalWidth { get; set; }
    public int? OriginalHeight { get; set; }
    public int? UpscaledWidth { get; set; }
    public int? UpscaledHeight { get; set; }
    public string? ErrorMessage { get; set; }

    public string ProgressDisplay => $"{Progress:F1}%";
    public string DimensionsDisplay => OriginalWidth.HasValue && OriginalHeight.HasValue
        ? $"{OriginalWidth}×{OriginalHeight} → {UpscaledWidth}×{UpscaledHeight}"
        : ResourceHelper.GetString("Upscaling.Unknown", "Unknown");

    public UpscalingJobItem(string jobId, string status, double progress, string? outputFile, int? originalWidth, int? originalHeight, int? upscaledWidth, int? upscaledHeight, string? errorMessage)
    {
      JobId = jobId;
      Status = status;
      Progress = progress;
      OutputFile = outputFile;
      OriginalWidth = originalWidth;
      OriginalHeight = originalHeight;
      UpscaledWidth = upscaledWidth;
      UpscaledHeight = upscaledHeight;
      ErrorMessage = errorMessage;
    }
  }
}