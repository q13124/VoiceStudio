using System;
using System.Collections.Generic;
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
using Windows.Storage;
using Windows.Storage.Pickers;

namespace VoiceStudio.App.ViewModels
{
    /// <summary>
    /// ViewModel for the VoiceCloningWizardView panel - Step-by-step voice cloning wizard.
    /// </summary>
    public partial class VoiceCloningWizardViewModel : BaseViewModel, IPanelView
    {
        private readonly IBackendClient _backendClient;
        private readonly ToastNotificationService? _toastNotificationService;

        public string PanelId => "voice-cloning-wizard";
        public string DisplayName => ResourceHelper.GetString("Panel.VoiceCloningWizard.DisplayName", "Voice Cloning Wizard");
        public PanelRegion Region => PanelRegion.Center;

        [ObservableProperty]
        private int currentStep = 1; // 1=Upload, 2=Configure, 3=Process, 4=Review

        [ObservableProperty]
        private StorageFile? selectedAudioFile;

        [ObservableProperty]
        private string? audioFileName;

        [ObservableProperty]
        private AudioValidationItem? audioValidation;

        [ObservableProperty]
        private string? selectedEngine = "xtts";

        [ObservableProperty]
        private string? selectedQualityMode = "standard";

        [ObservableProperty]
        private ObservableCollection<string> availableEngines = new() { "xtts", "chatterbox", "tortoise" };

        [ObservableProperty]
        private ObservableCollection<string> qualityModes = new() { "fast", "standard", "high", "ultra" };

        [ObservableProperty]
        private string? profileName;

        [ObservableProperty]
        private string? profileDescription;

        [ObservableProperty]
        private string? wizardJobId;

        [ObservableProperty]
        private float processingProgress;

        [ObservableProperty]
        private string? processingStatus;

        [ObservableProperty]
        private string? createdProfileId;

        [ObservableProperty]
        private QualityMetricsItem? qualityMetrics;

        [ObservableProperty]
        private string? testSynthesisAudioUrl;

        [ObservableProperty]
        private string? uploadedAudioId;

        public VoiceCloningWizardViewModel(IBackendClient backendClient)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
            
            // Get services using helper (reduces code duplication)
            _toastNotificationService = ServiceInitializationHelper.TryGetService(() => ServiceProvider.GetToastNotificationService());

            BrowseAudioCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("BrowseAudio");
                await BrowseAudioAsync(ct);
            });
            ValidateAudioCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("ValidateAudio");
                await ValidateAudioAsync(ct);
            }, () => SelectedAudioFile != null);
            NextStepCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("NextStep");
                await NextStepAsync(ct);
            }, () => CanProceedToNextStep);
            PreviousStepCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("PreviousStep");
                await PreviousStepAsync(ct);
            }, () => CurrentStep > 1);
            StartProcessingCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("StartProcessing");
                await StartProcessingAsync(ct);
            }, () => CanStartProcessing);
            FinalizeWizardCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("FinalizeWizard");
                await FinalizeWizardAsync(ct);
            }, () => CanFinalize);
            CancelWizardCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CancelWizard");
                await CancelWizardAsync(ct);
            });
        }

        public IAsyncRelayCommand BrowseAudioCommand { get; }
        public IAsyncRelayCommand ValidateAudioCommand { get; }
        public IAsyncRelayCommand NextStepCommand { get; }
        public IAsyncRelayCommand PreviousStepCommand { get; }
        public IAsyncRelayCommand StartProcessingCommand { get; }
        public IAsyncRelayCommand FinalizeWizardCommand { get; }
        public IAsyncRelayCommand CancelWizardCommand { get; }

        private bool CanProceedToNextStep
        {
            get
            {
                return CurrentStep switch
                {
                    1 => AudioValidation != null && AudioValidation.IsValid, // Step 1: Must have valid audio
                    2 => !string.IsNullOrWhiteSpace(ProfileName) && !string.IsNullOrWhiteSpace(SelectedEngine), // Step 2: Must have name and engine
                    3 => ProcessingStatus == "completed", // Step 3: Must be completed
                    _ => false
                };
            }
        }

        private bool CanStartProcessing => CurrentStep == 2 && !string.IsNullOrWhiteSpace(ProfileName) && !string.IsNullOrWhiteSpace(SelectedEngine);

        private bool CanFinalize => CurrentStep == 4 && ProcessingStatus == "completed" && !string.IsNullOrWhiteSpace(CreatedProfileId);

        partial void OnSelectedAudioFileChanged(StorageFile? value)
        {
            AudioFileName = value?.Name;
            ValidateAudioCommand.NotifyCanExecuteChanged();
        }

        partial void OnCurrentStepChanged(int value)
        {
            NextStepCommand.NotifyCanExecuteChanged();
            PreviousStepCommand.NotifyCanExecuteChanged();
            StartProcessingCommand.NotifyCanExecuteChanged();
            FinalizeWizardCommand.NotifyCanExecuteChanged();
        }

        partial void OnProfileNameChanged(string? value)
        {
            NextStepCommand.NotifyCanExecuteChanged();
            StartProcessingCommand.NotifyCanExecuteChanged();
        }

        partial void OnSelectedEngineChanged(string? value)
        {
            NextStepCommand.NotifyCanExecuteChanged();
            StartProcessingCommand.NotifyCanExecuteChanged();
        }

        partial void OnProcessingStatusChanged(string? value)
        {
            NextStepCommand.NotifyCanExecuteChanged();
            FinalizeWizardCommand.NotifyCanExecuteChanged();
        }

        private async Task BrowseAudioAsync(CancellationToken cancellationToken)
        {
            try
            {
                var picker = new FileOpenPicker();
                picker.ViewMode = PickerViewMode.List;
                picker.SuggestedStartLocation = PickerLocationId.MusicLibrary;
                picker.FileTypeFilter.Add(".wav");
                picker.FileTypeFilter.Add(".mp3");
                picker.FileTypeFilter.Add(".flac");
                picker.FileTypeFilter.Add(".m4a");

                var file = await picker.PickSingleFileAsync();
                cancellationToken.ThrowIfCancellationRequested();

                if (file != null)
                {
                    SelectedAudioFile = file;
                    AudioFileName = file.Name;
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("VoiceCloningWizard.BrowseAudioFileFailed", ex.Message);
                await HandleErrorAsync(ex, "BrowseAudio");
            }
        }

        private async Task ValidateAudioAsync(CancellationToken cancellationToken)
        {
            if (SelectedAudioFile == null)
            {
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                if (string.IsNullOrEmpty(UploadedAudioId))
                {
                    UploadedAudioId = await UploadAudioFileAsync(SelectedAudioFile, cancellationToken);
                    if (string.IsNullOrEmpty(UploadedAudioId))
                    {
                        ErrorMessage = ResourceHelper.GetString("VoiceCloningWizard.UploadAudioFailed", "Failed to upload audio file");
                        return;
                    }
                }

                var request = new AudioValidationRequest
                {
                    AudioId = UploadedAudioId
                };

                var validation = await _backendClient.SendRequestAsync<AudioValidationRequest, AudioValidationResponse>(
                    "/api/voice/clone/wizard/validate-audio",
                    request,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                if (validation != null)
                {
                    AudioValidation = new AudioValidationItem(validation);
                    StatusMessage = validation.IsValid 
                        ? ResourceHelper.GetString("VoiceCloningWizard.AudioValidatedSuccess", "Audio validated successfully")
                        : ResourceHelper.GetString("VoiceCloningWizard.AudioValidationFoundIssues", "Audio validation found issues");
                    
                    if (validation.IsValid)
                    {
                        _toastNotificationService?.ShowSuccess(
                            ResourceHelper.GetString("VoiceCloningWizard.AudioValidated", "Audio Validated"),
                            ResourceHelper.GetString("VoiceCloningWizard.AudioValidationPassed", "Audio file validation passed"));
                    }
                    else
                    {
                        var issueCount = validation.Issues?.Length ?? 0;
                        _toastNotificationService?.ShowError(
                            ResourceHelper.GetString("VoiceCloningWizard.ValidationFailed", "Validation Failed"),
                            ResourceHelper.FormatString("VoiceCloningWizard.ValidationFoundIssues", issueCount));
                    }
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("VoiceCloningWizard.ValidateAudioFailed", ex.Message);
                _toastNotificationService?.ShowError(
                    ResourceHelper.GetString("VoiceCloningWizard.ValidationFailed", "Validation Failed"),
                    ex.Message);
                await HandleErrorAsync(ex, "ValidateAudio");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task<string?> UploadAudioFileAsync(StorageFile file, CancellationToken cancellationToken)
        {
            try
            {
                const string baseUrl = "http://localhost:8001";
                using var httpClient = new HttpClient();
                httpClient.BaseAddress = new Uri(baseUrl);
                
                using var fileStream = await file.OpenStreamForReadAsync();
                cancellationToken.ThrowIfCancellationRequested();

                var fileName = file.Name;
                var contentType = "audio/wav";
                
                if (fileName.EndsWith(".mp3", StringComparison.OrdinalIgnoreCase))
                    contentType = "audio/mpeg";
                else if (fileName.EndsWith(".flac", StringComparison.OrdinalIgnoreCase))
                    contentType = "audio/flac";
                else if (fileName.EndsWith(".m4a", StringComparison.OrdinalIgnoreCase))
                    contentType = "audio/mp4";
                
                using var content = new MultipartFormDataContent();
                var streamContent = new StreamContent(fileStream);
                streamContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(contentType);
                content.Add(streamContent, "file", fileName);
                
                using var cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
                var response = await httpClient.PostAsync("/api/audio/upload", content, cts.Token);
                response.EnsureSuccessStatusCode();
                
                var responseJson = await response.Content.ReadAsStringAsync(cts.Token);
                var uploadResponse = System.Text.Json.JsonSerializer.Deserialize<AudioUploadResponse>(responseJson);
                
                return uploadResponse?.AudioId;
            }
            catch (OperationCanceledException)
            {
                return null;
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("VoiceCloningWizard.UploadAudioFileFailed", ex.Message);
                return null;
            }
        }

        private async Task NextStepAsync(CancellationToken cancellationToken)
        {
            try
            {
                if (CurrentStep == 2 && CanStartProcessing)
                {
                    // Start processing before moving to step 3
                    await StartProcessingAsync(cancellationToken);
                }
                else if (CurrentStep < 4)
                {
                    CurrentStep++;
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
        }

        private Task PreviousStepAsync(CancellationToken cancellationToken)
        {
            cancellationToken.ThrowIfCancellationRequested();

            if (CurrentStep > 1)
            {
                CurrentStep--;
            }

            return Task.CompletedTask;
        }

        private async Task StartProcessingAsync(CancellationToken cancellationToken)
        {
            if (SelectedAudioFile == null || string.IsNullOrWhiteSpace(ProfileName))
            {
                return;
            }

            IsLoading = true;
            ErrorMessage = null;
            ProcessingStatus = ResourceHelper.GetString("VoiceCloningWizard.Processing", "processing");
            ProcessingProgress = 0.0f;

            try
            {
                if (string.IsNullOrEmpty(UploadedAudioId))
                {
                    UploadedAudioId = await UploadAudioFileAsync(SelectedAudioFile, cancellationToken);
                    if (string.IsNullOrEmpty(UploadedAudioId))
                    {
                        ErrorMessage = ResourceHelper.GetString("VoiceCloningWizard.UploadAudioFailed", "Failed to upload audio file");
                        ProcessingStatus = ResourceHelper.GetString("VoiceCloningWizard.Failed", "failed");
                        return;
                    }
                }

                var request = new WizardStartRequest
                {
                    ReferenceAudioId = UploadedAudioId,
                    Engine = SelectedEngine ?? "xtts",
                    QualityMode = SelectedQualityMode ?? "standard",
                    ProfileName = ProfileName,
                    ProfileDescription = ProfileDescription
                };

                var response = await _backendClient.SendRequestAsync<WizardStartRequest, WizardStartResponse>(
                    "/api/voice/clone/wizard/start",
                    request,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                if (response != null)
                {
                    WizardJobId = response.JobId;
                    CurrentStep = 3;

                    // Start processing
                    await _backendClient.SendRequestAsync<object, object>(
                        $"/api/voice/clone/wizard/{WizardJobId}/process",
                        null,
                        System.Net.Http.HttpMethod.Post,
                        cancellationToken
                    );

                    // Poll for status (with linked cancellation token)
                    _toastNotificationService?.ShowSuccess(
                        ResourceHelper.GetString("VoiceCloningWizard.ProcessingStarted", "Voice cloning processing has started"),
                        ResourceHelper.GetString("Toast.Title.ProcessingStarted", "Processing Started"));
                    await PollProcessingStatusAsync(cancellationToken);
                }
            }
            catch (OperationCanceledException)
            {
                ProcessingStatus = ResourceHelper.GetString("VoiceCloningWizard.Cancelled", "cancelled");
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("VoiceCloningWizard.StartProcessingFailed", ex.Message);
                ProcessingStatus = ResourceHelper.GetString("VoiceCloningWizard.Failed", "failed");
                _toastNotificationService?.ShowError(
                    ResourceHelper.GetString("VoiceCloningWizard.ProcessingFailed", "Processing Failed"),
                    ex.Message);
                await HandleErrorAsync(ex, "StartProcessing");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task PollProcessingStatusAsync(CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(WizardJobId))
            {
                return;
            }

            try
            {
                while (ProcessingStatus == "processing" && !cancellationToken.IsCancellationRequested)
                {
                    await Task.Delay(1000, cancellationToken); // Poll every second

                    var status = await _backendClient.SendRequestAsync<object, WizardStatusResponse>(
                        $"/api/voice/clone/wizard/{WizardJobId}/status",
                        null,
                        System.Net.Http.HttpMethod.Get,
                        cancellationToken
                    );

                    if (status != null)
                    {
                        ProcessingProgress = status.Progress;
                        ProcessingStatus = status.Status;

                        if (status.Status == "completed")
                        {
                            CreatedProfileId = status.ProfileId;
                            if (status.QualityMetrics != null)
                            {
                                QualityMetrics = new QualityMetricsItem(status.QualityMetrics);
                            }
                            TestSynthesisAudioUrl = status.TestSynthesisAudioUrl;
                            CurrentStep = 4;
                            StatusMessage = ResourceHelper.GetString("VoiceCloningWizard.CloningCompleted", "Voice cloning completed successfully");
                            
                            var dispatcherQueue = App.MainWindowInstance?.DispatcherQueue;
                            dispatcherQueue?.TryEnqueue(() =>
                            {
                                var profileName = ProfileName ?? "Unknown Profile";
                                _toastNotificationService?.ShowSuccess(
                                    ResourceHelper.FormatString("VoiceCloningWizard.CloningCompletedForProfile", profileName),
                                    ResourceHelper.GetString("Toast.Title.ProcessingComplete", "Processing Complete"));
                            });
                            break;
                        }
                        else if (status.Status == "failed")
                        {
                            ErrorMessage = status.ErrorMessage ?? ResourceHelper.GetString("VoiceCloningWizard.ProcessingFailedStatus", "Processing failed");
                            
                            var dispatcherQueue = App.MainWindowInstance?.DispatcherQueue;
                            dispatcherQueue?.TryEnqueue(() =>
                            {
                                _toastNotificationService?.ShowError(
                                    ResourceHelper.GetString("VoiceCloningWizard.ProcessingFailed", "Processing Failed"),
                                    status.ErrorMessage ?? ResourceHelper.GetString("VoiceCloningWizard.ProcessingFailedDetail", "Voice cloning processing failed"));
                            });
                            break;
                        }
                    }
                }
            }
            catch (OperationCanceledException)
            {
                ProcessingStatus = ResourceHelper.GetString("VoiceCloningWizard.Cancelled", "cancelled");
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("VoiceCloningWizard.PollStatusFailed", ex.Message);
                ProcessingStatus = ResourceHelper.GetString("VoiceCloningWizard.Failed", "failed");
                await HandleErrorAsync(ex, "PollProcessingStatus");
            }
        }

        private async Task FinalizeWizardAsync(CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(WizardJobId))
            {
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var request = new WizardFinalizeRequest
                {
                    JobId = WizardJobId,
                    ProfileName = ProfileName,
                    ProfileDescription = ProfileDescription
                };

                var response = await _backendClient.SendRequestAsync<WizardFinalizeRequest, WizardFinalizeResponse>(
                    $"/api/voice/clone/wizard/{WizardJobId}/finalize",
                    request,
                    System.Net.Http.HttpMethod.Post,
                    cancellationToken
                );

                if (response != null && response.Success)
                {
                    StatusMessage = ResourceHelper.FormatString("VoiceCloningWizard.ProfileCreatedSuccess", response.ProfileName);
                    _toastNotificationService?.ShowSuccess(
                        ResourceHelper.GetString("VoiceCloningWizard.WizardComplete", "Wizard Complete"),
                        ResourceHelper.FormatString("VoiceCloningWizard.ProfileCreatedSuccess", response.ProfileName));
                    // Reset wizard for next use
                    await ResetWizardAsync();
                }
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("VoiceCloningWizard.FinalizeWizardFailed", ex.Message);
                _toastNotificationService?.ShowError(
                    ResourceHelper.GetString("Toast.Title.FinalizationFailed", "Finalization Failed"),
                    ex.Message);
                await HandleErrorAsync(ex, "FinalizeWizard");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task CancelWizardAsync(CancellationToken cancellationToken)
        {
            try
            {
                if (!string.IsNullOrWhiteSpace(WizardJobId))
                {
                    try
                    {
                        await _backendClient.SendRequestAsync<object, object>(
                            $"/api/voice/clone/wizard/{WizardJobId}",
                            null,
                            System.Net.Http.HttpMethod.Delete,
                            cancellationToken
                        );
                    }
                    catch (OperationCanceledException)
                    {
                        // Ignore cancellation when canceling
                    }
                    catch
                    {
                        // Ignore errors when canceling
                    }
                }

                await ResetWizardAsync();
            }
            catch (OperationCanceledException)
            {
                return; // User cancelled
            }
        }

        private Task ResetWizardAsync()
        {
            CurrentStep = 1;
            SelectedAudioFile = null;
            AudioFileName = null;
            AudioValidation = null;
            SelectedEngine = "xtts";
            SelectedQualityMode = "standard";
            ProfileName = null;
            ProfileDescription = null;
            WizardJobId = null;
            ProcessingProgress = 0.0f;
            ProcessingStatus = null;
            CreatedProfileId = null;
            QualityMetrics = null;
            TestSynthesisAudioUrl = null;
            UploadedAudioId = null;
            ErrorMessage = null;
            StatusMessage = null;

            return Task.CompletedTask;
        }

        // Request/Response models
        private class AudioValidationRequest
        {
            public string AudioId { get; set; } = string.Empty;
        }

        public class AudioValidationResponse
        {
            public bool IsValid { get; set; }
            public double Duration { get; set; }
            public int SampleRate { get; set; }
            public int Channels { get; set; }
            public string[] Issues { get; set; } = Array.Empty<string>();
            public string[] Recommendations { get; set; } = Array.Empty<string>();
            public double? QualityScore { get; set; }
        }

        private class WizardStartRequest
        {
            public string ReferenceAudioId { get; set; } = string.Empty;
            public string Engine { get; set; } = "xtts";
            public string QualityMode { get; set; } = "standard";
            public string ProfileName { get; set; } = string.Empty;
            public string? ProfileDescription { get; set; }
        }

        private class WizardStartResponse
        {
            public string JobId { get; set; } = string.Empty;
            public int Step { get; set; }
            public string Status { get; set; } = string.Empty;
        }

        private class WizardStatusResponse
        {
            public string JobId { get; set; } = string.Empty;
            public int Step { get; set; }
            public string Status { get; set; } = string.Empty;
            public float Progress { get; set; }
            public string? ProfileId { get; set; }
            public Dictionary<string, object>? QualityMetrics { get; set; }
            public string? TestSynthesisAudioUrl { get; set; }
            public string? ErrorMessage { get; set; }
        }

        private class WizardFinalizeRequest
        {
            public string JobId { get; set; } = string.Empty;
            public string? ProfileName { get; set; }
            public string? ProfileDescription { get; set; }
        }

        private class WizardFinalizeResponse
        {
            public string ProfileId { get; set; } = string.Empty;
            public string ProfileName { get; set; } = string.Empty;
            public bool Success { get; set; }
        }

        private class AudioUploadResponse
        {
            public string AudioId { get; set; } = string.Empty;
            public string? FileName { get; set; }
            public long? FileSize { get; set; }
        }
    }

    // Data models
    public class AudioValidationItem : ObservableObject
    {
        public bool IsValid { get; set; }
        public double Duration { get; set; }
        public int SampleRate { get; set; }
        public int Channels { get; set; }
        public string[] Issues { get; set; }
        public string[] Recommendations { get; set; }
        public double? QualityScore { get; set; }

        public string DurationDisplay => $"{Duration:F1}s";
        public string SampleRateDisplay => $"{SampleRate} Hz";
        public string ChannelsDisplay => Channels == 1 ? "Mono" : $"{Channels} channels";

        public AudioValidationItem(VoiceCloningWizardViewModel.AudioValidationResponse validation)
        {
            IsValid = validation.IsValid;
            Duration = validation.Duration;
            SampleRate = validation.SampleRate;
            Channels = validation.Channels;
            Issues = validation.Issues ?? Array.Empty<string>();
            Recommendations = validation.Recommendations ?? Array.Empty<string>();
            QualityScore = validation.QualityScore;
        }
    }

    public class QualityMetricsItem : ObservableObject
    {
        public double? MosScore { get; set; }
        public double? Similarity { get; set; }
        public double? Naturalness { get; set; }
        public double? SnrDb { get; set; }

        public string MosScoreDisplay => MosScore.HasValue ? $"{MosScore.Value:F2}/5.0" : "N/A";
        public string SimilarityDisplay => Similarity.HasValue ? $"{Similarity.Value:P0}" : "N/A";
        public string NaturalnessDisplay => Naturalness.HasValue ? $"{Naturalness.Value:P0}" : "N/A";
        public string SnrDbDisplay => SnrDb.HasValue ? $"{SnrDb.Value:F1} dB" : "N/A";

        public QualityMetricsItem(Dictionary<string, object> metrics)
        {
            if (metrics.TryGetValue("mos_score", out var mos) && mos != null)
            {
                MosScore = Convert.ToDouble(mos);
            }
            if (metrics.TryGetValue("similarity", out var sim) && sim != null)
            {
                Similarity = Convert.ToDouble(sim);
            }
            if (metrics.TryGetValue("naturalness", out var nat) && nat != null)
            {
                Naturalness = Convert.ToDouble(nat);
            }
            if (metrics.TryGetValue("snr_db", out var snr) && snr != null)
            {
                SnrDb = Convert.ToDouble(snr);
            }
        }
    }
}
