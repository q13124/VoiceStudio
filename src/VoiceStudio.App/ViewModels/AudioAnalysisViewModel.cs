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
    /// ViewModel for the AudioAnalysisView panel - Advanced audio analysis.
    /// </summary>
    public partial class AudioAnalysisViewModel : BaseViewModel, IPanelView
    {
        private readonly IBackendClient _backendClient;
        private readonly ToastNotificationService? _toastNotificationService;

        public string PanelId => "audio-analysis";
        public string DisplayName => ResourceHelper.GetString("Panel.AudioAnalysis.DisplayName", "Audio Analysis");
        public PanelRegion Region => PanelRegion.Right;

        [ObservableProperty]
        private string? selectedAudioId;

        [ObservableProperty]
        private ObservableCollection<string> availableAudioIds = new();

        [ObservableProperty]
        private AudioAnalysisResultItem? analysisResult;

        [ObservableProperty]
        private bool includeSpectral = true;

        [ObservableProperty]
        private bool includeTemporal = true;

        [ObservableProperty]
        private bool includePerceptual = true;

        [ObservableProperty]
        private string? referenceAudioId;

        [ObservableProperty]
        private bool isLoading;

        [ObservableProperty]
        private string? errorMessage;

        [ObservableProperty]
        private string? statusMessage;

        public AudioAnalysisViewModel(IBackendClient backendClient)
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

            LoadAnalysisCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadAnalysis");
                await LoadAnalysisAsync(ct);
            }, () => !IsLoading);
            AnalyzeAudioCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("AnalyzeAudio");
                await AnalyzeAudioAsync(ct);
            }, () => !IsLoading);
            CompareAudioCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CompareAudio");
                await CompareAudioAsync(ct);
            }, () => !IsLoading);
            RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("Refresh");
                await RefreshAsync(ct);
            }, () => !IsLoading);
        }

        public IAsyncRelayCommand LoadAnalysisCommand { get; }
        public IAsyncRelayCommand AnalyzeAudioCommand { get; }
        public IAsyncRelayCommand CompareAudioCommand { get; }
        public IAsyncRelayCommand RefreshCommand { get; }

        private async Task LoadAnalysisAsync(CancellationToken cancellationToken)
        {
            if (string.IsNullOrEmpty(SelectedAudioId))
            {
                ErrorMessage = ResourceHelper.GetString("AudioAnalysis.AudioFileRequired", "Audio file must be selected");
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var queryParams = new System.Collections.Specialized.NameValueCollection();
                queryParams.Add("include_spectral", IncludeSpectral.ToString().ToLower());
                queryParams.Add("include_temporal", IncludeTemporal.ToString().ToLower());
                queryParams.Add("include_perceptual", IncludePerceptual.ToString().ToLower());

                var queryString = string.Join("&",
                    queryParams.AllKeys.SelectMany(key =>
                        queryParams.GetValues(key)?.Select(value => $"{key}={Uri.EscapeDataString(value)}") ?? Array.Empty<string>()
                    )
                );

                var url = $"/api/audio-analysis/{Uri.EscapeDataString(SelectedAudioId)}";
                if (!string.IsNullOrEmpty(queryString))
                    url += $"?{queryString}";

                var result = await _backendClient.SendRequestAsync<object, AudioAnalysisResult>(
                    url,
                    null,
                    System.Net.Http.HttpMethod.Get,
                    cancellationToken
                );

                if (result != null)
                {
                    AnalysisResult = new AudioAnalysisResultItem(result);
                }

                StatusMessage = ResourceHelper.GetString("AudioAnalysis.AnalysisLoaded", "Analysis loaded");
                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("AudioAnalysis.AnalysisLoadedDetail", "Audio analysis loaded successfully"),
                    ResourceHelper.GetString("Toast.Title.AnalysisLoaded", "Analysis Loaded"));
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "LoadAnalysis");
                _toastNotificationService?.ShowError(
                    ResourceHelper.GetString("Toast.Title.LoadAnalysisFailed", "Failed to Load Analysis"),
                    ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task AnalyzeAudioAsync(CancellationToken cancellationToken)
        {
            if (string.IsNullOrEmpty(SelectedAudioId))
            {
                ErrorMessage = ResourceHelper.GetString("AudioAnalysis.AudioFileRequired", "Audio file must be selected");
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var response = await _backendClient.SendRequestAsync<object, AudioAnalysisQueueResponse>(
                    $"/api/audio-analysis/{Uri.EscapeDataString(SelectedAudioId)}/analyze",
                    null,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                StatusMessage = response?.Message ?? "Analysis queued";
                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("AudioAnalysis.AnalysisStartedDetail", "Audio analysis started successfully"),
                    ResourceHelper.GetString("Toast.Title.AnalysisStarted", "Analysis Started"));
                
                // Wait a bit then reload
                await Task.Delay(1000, cancellationToken);
                await LoadAnalysisAsync(cancellationToken);
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "AnalyzeAudio");
                _toastNotificationService?.ShowError(
                    ResourceHelper.GetString("Toast.Title.AnalysisFailed", "Analysis Failed"),
                    ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task CompareAudioAsync(CancellationToken cancellationToken)
        {
            if (string.IsNullOrEmpty(SelectedAudioId) || string.IsNullOrEmpty(ReferenceAudioId))
            {
                ErrorMessage = ResourceHelper.GetString("AudioAnalysis.BothAudioFilesRequired", "Both audio files must be selected");
                return;
            }

            try
            {
                IsLoading = true;
                ErrorMessage = null;

                var response = await _backendClient.SendRequestAsync<object, AudioComparisonResponse>(
                    $"/api/audio-analysis/{Uri.EscapeDataString(SelectedAudioId)}/compare?reference_audio_id={Uri.EscapeDataString(ReferenceAudioId)}",
                    null,
                    System.Net.Http.HttpMethod.Get,
                    cancellationToken
                );

                StatusMessage = response?.Message ?? ResourceHelper.GetString("AudioAnalysis.ComparisonComplete", "Comparison complete");
                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("AudioAnalysis.ComparisonCompleteDetail", "Audio comparison completed successfully"),
                    ResourceHelper.GetString("Toast.Title.ComparisonComplete", "Comparison Complete"));
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "CompareAudio");
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
                await LoadAnalysisAsync(cancellationToken);
                StatusMessage = ResourceHelper.GetString("AudioAnalysis.AnalysisRefreshed", "Analysis refreshed");
                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("AudioAnalysis.AnalysisRefreshedSuccessfully", "Analysis refreshed successfully"),
                    ResourceHelper.GetString("Toast.Title.Refreshed", "Refreshed"));
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "Refresh");
                _toastNotificationService?.ShowError(
                    ResourceHelper.GetString("Toast.Title.RefreshFailed", "Refresh Failed"),
                    ex.Message);
            }
        }

        partial void OnSelectedAudioIdChanged(string? value)
        {
            if (!string.IsNullOrEmpty(value))
            {
                _ = LoadAnalysisAsync(CancellationToken.None);
            }
        }

        // Response models
        private class AudioAnalysisQueueResponse
        {
            public string AudioId { get; set; } = string.Empty;
            public string Status { get; set; } = string.Empty;
            public string Message { get; set; } = string.Empty;
        }

        private class AudioComparisonResponse
        {
            public string AudioId { get; set; } = string.Empty;
            public string ReferenceAudioId { get; set; } = string.Empty;
            public System.Collections.Generic.Dictionary<string, double> Differences { get; set; } = new();
            public string Message { get; set; } = string.Empty;
        }
    }

    // Data models
    public class AudioAnalysisResult
    {
        public string AudioId { get; set; } = string.Empty;
        public int SampleRate { get; set; }
        public double Duration { get; set; }
        public int Channels { get; set; }
        public SpectralAnalysis Spectral { get; set; } = new();
        public TemporalAnalysis Temporal { get; set; } = new();
        public PerceptualAnalysis Perceptual { get; set; } = new();
        public string Created { get; set; } = string.Empty;
    }

    public class SpectralAnalysis
    {
        public double Centroid { get; set; }
        public double Rolloff { get; set; }
        public double Flux { get; set; }
        public double ZeroCrossingRate { get; set; }
        public double Bandwidth { get; set; }
        public double Flatness { get; set; }
        public double Kurtosis { get; set; }
        public double Skewness { get; set; }
    }

    public class TemporalAnalysis
    {
        public double Rms { get; set; }
        public double ZeroCrossingRate { get; set; }
        public double? AttackTime { get; set; }
        public double? DecayTime { get; set; }
        public double? SustainLevel { get; set; }
        public double? ReleaseTime { get; set; }
    }

    public class PerceptualAnalysis
    {
        public double LoudnessLufs { get; set; }
        public double PeakLufs { get; set; }
        public double TruePeakDb { get; set; }
        public double DynamicRange { get; set; }
        public double CrestFactor { get; set; }
        public double? Lra { get; set; }
    }

    public class AudioAnalysisResultItem : ObservableObject
    {
        public string AudioId { get; set; }
        public int SampleRate { get; set; }
        public double Duration { get; set; }
        public int Channels { get; set; }
        public SpectralAnalysis Spectral { get; set; }
        public TemporalAnalysis Temporal { get; set; }
        public PerceptualAnalysis Perceptual { get; set; }
        public string Created { get; set; }

        public AudioAnalysisResultItem(AudioAnalysisResult result)
        {
            AudioId = result.AudioId;
            SampleRate = result.SampleRate;
            Duration = result.Duration;
            Channels = result.Channels;
            Spectral = result.Spectral;
            Temporal = result.Temporal;
            Perceptual = result.Perceptual;
            Created = result.Created;
        }
    }
}

