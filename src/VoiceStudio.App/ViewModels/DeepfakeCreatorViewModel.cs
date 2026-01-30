using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;

namespace VoiceStudio.App.ViewModels
{
    /// <summary>
    /// ViewModel for the DeepfakeCreatorView panel - Face swapping and face replacement.
    /// </summary>
    public partial class DeepfakeCreatorViewModel : BaseViewModel, IPanelView
    {
        private readonly IBackendClient _backendClient;

        public string PanelId => "deepfake-creator";
        public string DisplayName => ResourceHelper.GetString("Panel.DeepfakeCreator.DisplayName", "Deepfake Creator");
        public PanelRegion Region => PanelRegion.Center;

        [ObservableProperty]
        private ObservableCollection<DeepfakeEngineItem> availableEngines = new();

        [ObservableProperty]
        private ObservableCollection<DeepfakeJobItem> deepfakeJobs = new();

        [ObservableProperty]
        private DeepfakeEngineItem? selectedEngine;

        [ObservableProperty]
        private DeepfakeJobItem? selectedJob;

        [ObservableProperty]
        private string selectedMediaType = "image";

        [ObservableProperty]
        private ObservableCollection<string> availableMediaTypes = new() { "image", "video" };

        [ObservableProperty]
        private string? sourceFaceFilePath;

        [ObservableProperty]
        private string? targetMediaFilePath;

        [ObservableProperty]
        private bool consentGiven;

        [ObservableProperty]
        private bool applyWatermark = true;

        [ObservableProperty]
        private string selectedQuality = "high";

        [ObservableProperty]
        private ObservableCollection<string> availableQualities = new() { "low", "medium", "high" };

        [ObservableProperty]
        private bool isProcessing;

        [ObservableProperty]
        private double uploadProgress = 0.0;

        [ObservableProperty]
        private bool isUploading = false;

        public DeepfakeCreatorViewModel(IBackendClient backendClient)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

            LoadEnginesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadEngines");
                await LoadEnginesAsync(ct);
            }, () => !IsLoading);
            CreateDeepfakeCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CreateDeepfake");
                await CreateDeepfakeAsync(ct);
            }, () => !IsProcessing && !string.IsNullOrWhiteSpace(SourceFaceFilePath) && !string.IsNullOrWhiteSpace(TargetMediaFilePath) && SelectedEngine != null && ConsentGiven && !IsLoading);
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
        public IAsyncRelayCommand CreateDeepfakeCommand { get; }
        public IAsyncRelayCommand LoadJobsCommand { get; }
        public IAsyncRelayCommand DeleteJobCommand { get; }
        public IAsyncRelayCommand RefreshCommand { get; }

        partial void OnIsProcessingChanged(bool value)
        {
            ((System.Windows.Input.ICommand)CreateDeepfakeCommand).NotifyCanExecuteChanged();
        }

        partial void OnSourceFaceFilePathChanged(string? value)
        {
            ((System.Windows.Input.ICommand)CreateDeepfakeCommand).NotifyCanExecuteChanged();
        }

        partial void OnTargetMediaFilePathChanged(string? value)
        {
            CreateDeepfakeCommand.NotifyCanExecuteChanged();

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

        partial void OnSelectedEngineChanged(DeepfakeEngineItem? value)
        {
            CreateDeepfakeCommand.NotifyCanExecuteChanged();

            // Update media type options based on engine
            if (value != null)
            {
                // Filter available media types based on engine support
                var supportedTypes = value.SupportedTypes.ToList();
                if (!supportedTypes.Contains(SelectedMediaType))
                {
                    SelectedMediaType = supportedTypes.FirstOrDefault() ?? "image";
                }
            }
        }

        partial void OnSelectedJobChanged(DeepfakeJobItem? value)
        {
            ((System.Windows.Input.ICommand)DeleteJobCommand).NotifyCanExecuteChanged();
        }

        partial void OnConsentGivenChanged(bool value)
        {
            ((System.Windows.Input.ICommand)CreateDeepfakeCommand).NotifyCanExecuteChanged();
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

                var engines = await _backendClient.SendRequestAsync<object, DeepfakeEngine[]>(
                    "/api/deepfake-creator/engines",
                    null,
                    System.Net.Http.HttpMethod.Get,
                    cancellationToken
                );

                if (engines != null)
                {
                    AvailableEngines.Clear();
                    foreach (var engine in engines)
                    {
                        AvailableEngines.Add(new DeepfakeEngineItem(
                            engine.EngineId,
                            engine.Name,
                            engine.Description,
                            engine.SupportedTypes,
                            engine.RequiresConsent,
                            engine.WatermarkRequired,
                            engine.IsAvailable
                        ));
                    }

                    // Select first available engine for current media type
                    SelectedEngine = AvailableEngines.FirstOrDefault(e => e.SupportedTypes.Contains(SelectedMediaType));
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("DeepfakeCreator.LoadEnginesFailed", ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task CreateDeepfakeAsync(CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(SourceFaceFilePath) || string.IsNullOrWhiteSpace(TargetMediaFilePath) || SelectedEngine == null)
            {
                ErrorMessage = ResourceHelper.GetString("DeepfakeCreator.SelectionRequired", "Please select source face, target media, and engine");
                return;
            }

            if (!ConsentGiven)
            {
                ErrorMessage = ResourceHelper.GetString("DeepfakeCreator.ConsentRequired", "Consent is required for deepfake creation");
                return;
            }

            if (!File.Exists(SourceFaceFilePath) || !File.Exists(TargetMediaFilePath))
            {
                ErrorMessage = ResourceHelper.GetString("DeepfakeCreator.FilesDoNotExist", "Selected files do not exist");
                return;
            }

            // Validate source face file (image only, max 10MB)
            var sourceFileInfo = new FileInfo(SourceFaceFilePath);
            var sourceExt = Path.GetExtension(SourceFaceFilePath).ToLowerInvariant();
            var validImageExtensions = new[] { ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp" };

            if (!validImageExtensions.Contains(sourceExt))
            {
                ErrorMessage = ResourceHelper.FormatString("DeepfakeCreator.SourceFaceFormatInvalid", string.Join(", ", validImageExtensions));
                return;
            }

            if (sourceFileInfo.Length > 10 * 1024 * 1024) // 10MB
            {
                ErrorMessage = ResourceHelper.GetString("DeepfakeCreator.SourceFaceSizeExceeded", "Source face file size exceeds maximum allowed size (10MB)");
                return;
            }

            // Validate target media file
            var targetFileInfo = new FileInfo(TargetMediaFilePath);
            var targetExt = Path.GetExtension(TargetMediaFilePath).ToLowerInvariant();

            if (SelectedMediaType == "image")
            {
                if (!validImageExtensions.Contains(targetExt))
                {
                    ErrorMessage = ResourceHelper.FormatString("DeepfakeCreator.TargetImageFormatInvalid", string.Join(", ", validImageExtensions));
                    return;
                }
                if (targetFileInfo.Length > 500 * 1024 * 1024) // 500MB
                {
                    ErrorMessage = ResourceHelper.GetString("DeepfakeCreator.TargetImageSizeExceeded", "Target image file size exceeds maximum allowed size (500MB)");
                    return;
                }
            }
            else // video
            {
                var validVideoExtensions = new[] { ".mp4", ".avi", ".mov", ".mkv", ".webm" };
                if (!validVideoExtensions.Contains(targetExt))
                {
                    ErrorMessage = $"Target video file format not supported. Supported formats: {string.Join(", ", validVideoExtensions)}";
                    return;
                }
                if (targetFileInfo.Length > 2L * 1024 * 1024 * 1024) // 2GB
                {
                    ErrorMessage = ResourceHelper.GetString("DeepfakeCreator.TargetVideoSizeExceeded", "Target video file size exceeds maximum allowed size (2GB)");
                    return;
                }
            }

            try
            {
                IsProcessing = true;
                ErrorMessage = null;

                var request = new DeepfakeRequest
                {
                    MediaType = SelectedMediaType,
                    Engine = SelectedEngine.EngineId,
                    ConsentGiven = ConsentGiven,
                    ApplyWatermark = ApplyWatermark,
                    Quality = SelectedQuality
                };

                var jobResponse = await UploadFilesAndCreateDeepfakeAsync(SourceFaceFilePath, TargetMediaFilePath, request, cancellationToken);

                if (jobResponse != null)
                {
                    await LoadJobsAsync(cancellationToken);
                    StatusMessage = ResourceHelper.FormatString("DeepfakeCreator.CreationStarted", SelectedQuality);
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("DeepfakeCreator.CreateFailed", ex.Message);
            }
            finally
            {
                IsProcessing = false;
            }
        }

        private async Task LoadJobsAsync(CancellationToken cancellationToken = default)
        {
            try
            {
                IsLoading = true;
                ErrorMessage = null;

                var jobs = await _backendClient.SendRequestAsync<object, DeepfakeJob[]>(
                    "/api/deepfake-creator/jobs",
                    null,
                    System.Net.Http.HttpMethod.Get,
                    cancellationToken
                );

                if (jobs != null)
                {
                    DeepfakeJobs.Clear();
                    foreach (var job in jobs)
                    {
                        DeepfakeJobs.Add(new DeepfakeJobItem(
                            job.JobId,
                            job.Status,
                            job.Progress,
                            job.OutputFile,
                            job.ConsentGiven,
                            job.WatermarkApplied,
                            job.ErrorMessage
                        ));
                    }
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("DeepfakeCreator.LoadJobsFailed", ex.Message);
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
                    $"/api/deepfake-creator/jobs/{Uri.EscapeDataString(SelectedJob.JobId)}",
                    null,
                    System.Net.Http.HttpMethod.Delete,
                    cancellationToken
                );

                DeepfakeJobs.Remove(SelectedJob);
                SelectedJob = null;

                StatusMessage = ResourceHelper.GetString("DeepfakeCreator.JobDeleted", "Job deleted successfully");
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("DeepfakeCreator.DeleteJobFailed", ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task RefreshAsync(CancellationToken cancellationToken = default)
        {
            await LoadEnginesAsync(cancellationToken);
            await LoadJobsAsync(cancellationToken);
            StatusMessage = ResourceHelper.GetString("DeepfakeCreator.Refreshed", "Refreshed");
        }

        private async Task<DeepfakeJobResponse?> UploadFilesAndCreateDeepfakeAsync(string sourceFacePath, string targetMediaPath, DeepfakeRequest requestData, CancellationToken cancellationToken = default)
        {
            const string baseUrl = "http://localhost:8001";
            using var httpClient = new HttpClient();
            httpClient.BaseAddress = new Uri(baseUrl);
            httpClient.Timeout = TimeSpan.FromMinutes(30); // Allow longer timeout for large files

            IsUploading = true;
            UploadProgress = 0.0;

            try
            {
                using var sourceStream = File.OpenRead(sourceFacePath);
                using var targetStream = File.OpenRead(targetMediaPath);
                var sourceFileName = Path.GetFileName(sourceFacePath);
                var targetFileName = Path.GetFileName(targetMediaPath);

                var totalSize = sourceStream.Length + targetStream.Length;
                var uploadedBytes = 0L;

                // Create progress tracking streams
                var sourceProgressStream = new ProgressStream(sourceStream, (bytesRead, totalBytes) =>
                {
                    uploadedBytes += bytesRead;
                    UploadProgress = uploadedBytes / (double)totalSize * 100.0;
                });

                var targetProgressStream = new ProgressStream(targetStream, (bytesRead, totalBytes) =>
                {
                    uploadedBytes += bytesRead;
                    UploadProgress = uploadedBytes / (double)totalSize * 100.0;
                });

                using var content = new MultipartFormDataContent();
                var sourceContent = new StreamContent(sourceProgressStream);
                sourceContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("image/jpeg");
                content.Add(sourceContent, "source_face", sourceFileName);

                var targetContentType = SelectedMediaType == "image" ? "image/jpeg" : "video/mp4";
                var targetContent = new StreamContent(targetProgressStream);
                targetContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(targetContentType);
                content.Add(targetContent, "target_media", targetFileName);

                var requestJson = System.Text.Json.JsonSerializer.Serialize(requestData);
                content.Add(new StringContent(requestJson, System.Text.Encoding.UTF8, "application/json"), "request");

                var response = await httpClient.PostAsync("/api/deepfake-creator/create", content, cancellationToken);
                response.EnsureSuccessStatusCode();

                var responseJson = await response.Content.ReadAsStringAsync();
                return System.Text.Json.JsonSerializer.Deserialize<DeepfakeJobResponse>(responseJson);
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
            private long _bytesRead = 0;

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

        // Request/Response models
        private class DeepfakeJobResponse
        {
            public string JobId { get; set; } = string.Empty;
            public string Status { get; set; } = string.Empty;
        }
        private class DeepfakeRequest
        {
            public string MediaType { get; set; } = string.Empty;
            public string Engine { get; set; } = string.Empty;
            public bool ConsentGiven { get; set; }
            public bool ApplyWatermark { get; set; } = true;
            public string Quality { get; set; } = "high";
        }

        private class DeepfakeEngine
        {
            public string EngineId { get; set; } = string.Empty;
            public string Name { get; set; } = string.Empty;
            public string Description { get; set; } = string.Empty;
            public string[] SupportedTypes { get; set; } = Array.Empty<string>();
            public bool RequiresConsent { get; set; }
            public bool WatermarkRequired { get; set; }
            public bool IsAvailable { get; set; }
        }

        private class DeepfakeJob
        {
            public string JobId { get; set; } = string.Empty;
            public string Status { get; set; } = string.Empty;
            public double Progress { get; set; }
            public string? OutputFile { get; set; }
            public bool ConsentGiven { get; set; }
            public bool WatermarkApplied { get; set; }
            public string? ErrorMessage { get; set; }
        }
    }

    // Data models
    public class DeepfakeEngineItem : ObservableObject
    {
        public string EngineId { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string[] SupportedTypes { get; set; }
        public bool RequiresConsent { get; set; }
        public bool WatermarkRequired { get; set; }
        public bool IsAvailable { get; set; }

        public string DisplayName => $"{Name} ({string.Join(", ", SupportedTypes)})";
        public string RequirementsDisplay => $"Consent: {(RequiresConsent ? "Required" : "Not Required")}, Watermark: {(WatermarkRequired ? "Required" : "Optional")}";

        public DeepfakeEngineItem(string engineId, string name, string description, string[] supportedTypes, bool requiresConsent, bool watermarkRequired, bool isAvailable)
        {
            EngineId = engineId;
            Name = name;
            Description = description;
            SupportedTypes = supportedTypes;
            RequiresConsent = requiresConsent;
            WatermarkRequired = watermarkRequired;
            IsAvailable = isAvailable;
        }
    }

    public class DeepfakeJobItem : ObservableObject
    {
        public string JobId { get; set; }
        public string Status { get; set; }
        public double Progress { get; set; }
        public string? OutputFile { get; set; }
        public bool ConsentGiven { get; set; }
        public bool WatermarkApplied { get; set; }
        public string? ErrorMessage { get; set; }

        public string ProgressDisplay => $"{Progress:F1}%";
        public string ConsentDisplay => ConsentGiven ? "✓ Consent Given" : "✗ No Consent";
        public string WatermarkDisplay => WatermarkApplied ? "✓ Watermarked" : "✗ No Watermark";

        public DeepfakeJobItem(string jobId, string status, double progress, string? outputFile, bool consentGiven, bool watermarkApplied, string? errorMessage)
        {
            JobId = jobId;
            Status = status;
            Progress = progress;
            OutputFile = outputFile;
            ConsentGiven = consentGiven;
            WatermarkApplied = watermarkApplied;
            ErrorMessage = errorMessage;
        }
    }
}

