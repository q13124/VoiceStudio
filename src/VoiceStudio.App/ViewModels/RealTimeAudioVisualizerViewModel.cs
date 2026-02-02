using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;

namespace VoiceStudio.App.ViewModels
{
    /// <summary>
    /// ViewModel for the RealTimeAudioVisualizerView panel - Real-time audio visualization.
    /// </summary>
    public partial class RealTimeAudioVisualizerViewModel : BaseViewModel, IPanelView
    {
        private readonly IBackendClient _backendClient;

        public string PanelId => "realtime-audio-visualizer";
        public string DisplayName => ResourceHelper.GetString("Panel.RealTimeAudioVisualizer.DisplayName", "Real-Time Audio Visualizer");
        public PanelRegion Region => PanelRegion.Center;

        [ObservableProperty]
        private string? sessionId;

        [ObservableProperty]
        private string visualizationType = "both";

        [ObservableProperty]
        private ObservableCollection<string> availableVisualizationTypes = new() { "waveform", "spectrogram", "spectrum", "both" };

        [ObservableProperty]
        private double updateRate = 30.0;

        [ObservableProperty]
        private int fftSize = 2048;

        [ObservableProperty]
        private string windowType = "hann";

        [ObservableProperty]
        private ObservableCollection<string> availableWindowTypes = new() { "hann", "hamming", "blackman", "rectangular" };

        [ObservableProperty]
        private bool showPhase = false;

        [ObservableProperty]
        private string selectedColorScheme = "default";

        [ObservableProperty]
        private ObservableCollection<string> availableColorSchemes = new() { "default", "heatmap", "spectral", "rainbow" };

        [ObservableProperty]
        private bool isStreaming = false;

        [ObservableProperty]
        private ObservableCollection<VisualizerFrameItem> frames = new();

        public RealTimeAudioVisualizerViewModel(IViewModelContext context, IBackendClient backendClient)
            : base(context)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

            StartSessionCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("StartSession");
                await StartSessionAsync(ct);
            }, () => !IsLoading);
            StopSessionCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("StopSession");
                await StopSessionAsync(ct);
            }, () => !IsLoading && !string.IsNullOrEmpty(SessionId));
            DeleteSessionCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("DeleteSession");
                await DeleteSessionAsync(ct);
            }, () => !IsLoading && !string.IsNullOrEmpty(SessionId));
            RefreshCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("Refresh");
                await RefreshAsync(ct);
            }, () => !IsLoading);
        }

        public IAsyncRelayCommand StartSessionCommand { get; }
        public IAsyncRelayCommand StopSessionCommand { get; }
        public IAsyncRelayCommand DeleteSessionCommand { get; }
        public IAsyncRelayCommand RefreshCommand { get; }

        private async Task StartSessionAsync(CancellationToken cancellationToken)
        {
            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var request = new
                {
                    visualization_type = VisualizationType,
                    update_rate = UpdateRate,
                    fft_size = FftSize,
                    window_type = WindowType,
                    show_phase = ShowPhase,
                    color_scheme = SelectedColorScheme
                };

                var response = await _backendClient.SendRequestAsync<object, VisualizerStartResponse>(
                    "/api/realtime-visualizer/start",
                    request,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                if (response != null)
                {
                    SessionId = response.SessionId;
                    IsStreaming = true;
                    StatusMessage = response.Message;
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "StartSession");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task StopSessionAsync(CancellationToken cancellationToken)
        {
            if (string.IsNullOrEmpty(SessionId))
            {
                ErrorMessage = ResourceHelper.GetString("RealTimeAudioVisualizer.SessionMustBeStarted", "Session must be started first");
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                await _backendClient.SendRequestAsync<object, object>(
                    $"/api/realtime-visualizer/{Uri.EscapeDataString(SessionId)}/stop",
                    null,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                IsStreaming = false;
                StatusMessage = ResourceHelper.GetString("RealTimeAudioVisualizer.SessionStopped", "Session stopped");
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "StopSession");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task DeleteSessionAsync(CancellationToken cancellationToken)
        {
            if (string.IsNullOrEmpty(SessionId))
            {
                ErrorMessage = ResourceHelper.GetString("RealTimeAudioVisualizer.SessionMustBeStarted", "Session must be started first");
                return;
            }

            try
            {
                IsLoading = true;
                ErrorMessage = null;

                await _backendClient.SendRequestAsync<object, object>(
                    $"/api/realtime-visualizer/{Uri.EscapeDataString(SessionId)}",
                    null,
                    System.Net.Http.HttpMethod.Delete,
                    cancellationToken
                );

                SessionId = null;
                IsStreaming = false;
                Frames.Clear();
                StatusMessage = ResourceHelper.GetString("RealTimeAudioVisualizer.SessionDeleted", "Session deleted");
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                await HandleErrorAsync(ex, "DeleteSession");
                ErrorMessage = ResourceHelper.FormatString("RealTimeAudioVisualizer.DeleteSessionFailed", ex.Message);
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
                StatusMessage = ResourceHelper.GetString("RealTimeAudioVisualizer.Refreshed", "Refreshed");
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
        private class VisualizerStartResponse
        {
            public string SessionId { get; set; } = string.Empty;
            public string Message { get; set; } = string.Empty;
        }
    }

    // Data models
    public class VisualizerFrameItem : ObservableObject
    {
        public double Timestamp { get; set; }
        public double[]? Samples { get; set; }
        public double[]? Frequencies { get; set; }
        public double[]? Magnitudes { get; set; }
        public double[][]? SpectrogramFrame { get; set; }
        public string TimestampDisplay => $"{Timestamp:F3}s";

        public VisualizerFrameItem(VisualizerFrame frame)
        {
            Timestamp = frame.Timestamp;
            Samples = frame.Samples;
            Frequencies = frame.Frequencies;
            Magnitudes = frame.Magnitudes;
            SpectrogramFrame = frame.SpectrogramFrame;
        }
    }

    public class VisualizerFrame
    {
        public double Timestamp { get; set; }
        public double[]? Samples { get; set; }
        public double[]? Frequencies { get; set; }
        public double[]? Magnitudes { get; set; }
        public double[][]? SpectrogramFrame { get; set; }
    }
}

