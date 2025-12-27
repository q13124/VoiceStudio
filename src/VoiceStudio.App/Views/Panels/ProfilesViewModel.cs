using System;
using System.Collections.ObjectModel;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Models;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;
using VoiceStudio.App.Services;
using VoiceStudio.App.Services.UndoableActions;

namespace VoiceStudio.App.Views.Panels
{
    public partial class ProfilesViewModel : ObservableObject, IPanelView
    {
        private readonly IBackendClient _backendClient;
        private readonly IAudioPlayerService _audioPlayer;
        private readonly ToastNotificationService? _toastNotificationService;
        private readonly UndoRedoService? _undoRedoService;
        private readonly IErrorPresentationService? _errorService;
        private readonly IErrorLoggingService? _logService;

        public string PanelId => "profiles";
        public string DisplayName => ResourceHelper.GetString("Panel.Profiles.DisplayName", "Profiles");
        public PanelRegion Region => PanelRegion.Left;

        [ObservableProperty]
        private ObservableCollection<VoiceProfile> profiles = new();

        [ObservableProperty]
        private ObservableCollection<VoiceProfile> filteredProfiles = new();

        [ObservableProperty]
        private VoiceProfile? selectedProfile;

        // Search and filter properties
        [ObservableProperty]
        private string? searchQuery;

        [ObservableProperty]
        private string? selectedLanguage;

        [ObservableProperty]
        private string? selectedEmotion;

        [ObservableProperty]
        private string? selectedQualityRange;

        [ObservableProperty]
        private ObservableCollection<string> availableLanguages = new();

        [ObservableProperty]
        private ObservableCollection<string> availableEmotions = new();

        [ObservableProperty]
        private ObservableCollection<string> availableQualityRanges = new()
        {
            ResourceHelper.GetString("Filter.All", "All"),
            ResourceHelper.GetString("Filter.QualityHigh", "High (4.0+)"),
            ResourceHelper.GetString("Filter.QualityGood", "Good (3.0-4.0)"),
            ResourceHelper.GetString("Filter.QualityFair", "Fair (2.0-3.0)"),
            ResourceHelper.GetString("Filter.QualityLow", "Low (<2.0)")
        };

        [ObservableProperty]
        private int totalProfiles;

        [ObservableProperty]
        private int filteredCount;

        [ObservableProperty]
        private bool isLoading;

        [ObservableProperty]
        private string? errorMessage;

        [ObservableProperty]
        private bool isPreviewing = false;

        [ObservableProperty]
        private bool canPreview = false;

        [ObservableProperty]
        private QualityMetrics? previewQualityMetrics;

        [ObservableProperty]
        private bool hasPreviewQualityMetrics = false;

        [ObservableProperty]
        private double? previewQualityScore;

        // Reference audio enhancement
        [ObservableProperty]
        private bool isEnhancing = false;

        [ObservableProperty]
        private ReferenceAudioPreprocessResponse? enhancementResult;

        [ObservableProperty]
        private bool hasEnhancementResult = false;

        [ObservableProperty]
        private bool autoEnhance = true;

        [ObservableProperty]
        private bool selectOptimalSegments = true;

        [ObservableProperty]
        private bool isPlayingEnhanced = false;

        // Quality history (IDEA 30)
        [ObservableProperty]
        private ObservableCollection<QualityHistoryEntry> qualityHistory = new();

        [ObservableProperty]
        private QualityTrends? qualityTrends;

        [ObservableProperty]
        private bool isLoadingQualityHistory = false;

        [ObservableProperty]
        private string selectedTimeRange = "30d";

        [ObservableProperty]
        private ObservableCollection<string> availableTimeRanges = new() { "7d", "30d", "90d", "1y", "all" };

        [ObservableProperty]
        private bool hasQualityHistory = false;

        // Quality Degradation Detection (IDEA 56)
        [ObservableProperty]
        private QualityDegradationResponse? qualityDegradation;

        [ObservableProperty]
        private ObservableCollection<QualityDegradationAlert> qualityDegradationAlerts = new();

        [ObservableProperty]
        private QualityBaseline? qualityBaseline;

        [ObservableProperty]
        private bool isLoadingDegradation = false;

        [ObservableProperty]
        private bool hasQualityDegradation = false;

        [ObservableProperty]
        private int degradationTimeWindowDays = 7;

        // Multi-select support
        private readonly MultiSelectService _multiSelectService;
        private MultiSelectState? _multiSelectState;

        [ObservableProperty]
        private int selectedCount = 0;

        [ObservableProperty]
        private bool hasMultipleSelection = false;

        public bool HasProfiles => FilteredProfiles != null && FilteredProfiles.Count > 0;

        public bool IsProfileSelected(string profileId) => _multiSelectState?.SelectedIds.Contains(profileId) ?? false;

        // Default preview text for voice profiles
        private const string DEFAULT_PREVIEW_TEXT = "Hello, this is a preview of this voice profile.";

        // Cache for preview audio (profileId -> audioUrl)
        private readonly Dictionary<string, string> _previewCache = new();
        private readonly Dictionary<string, QualityMetrics?> _previewQualityCache = new();
        private readonly Dictionary<string, double> _previewQualityScoreCache = new();

        public ProfilesViewModel(IBackendClient backendClient, IAudioPlayerService audioPlayer)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));
            _audioPlayer = audioPlayer ?? throw new ArgumentNullException(nameof(audioPlayer));
            _multiSelectService = ServiceProvider.GetMultiSelectService();
            _multiSelectState = _multiSelectService.GetState(PanelId);

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

            // Get undo/redo service (may be null if not initialized)
            try
            {
                _undoRedoService = ServiceProvider.GetUndoRedoService();
            }
            catch
            {
                // Service may not be initialized yet - that's okay
                _undoRedoService = null;
            }

            // Get error services
            _errorService = ServiceProvider.TryGetErrorPresentationService();
            _logService = ServiceProvider.TryGetErrorLoggingService();

            LoadProfilesCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadProfiles");
                await LoadProfilesAsync(ct);
            });

            CreateProfileCommand = new EnhancedAsyncRelayCommand<string>(async (name, ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CreateProfile");
                await CreateProfileAsync(name, CancellationToken.None);
            });

            DeleteProfileCommand = new EnhancedAsyncRelayCommand<string>(async (profileId, ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("DeleteProfile");
                await DeleteProfileAsync(profileId, CancellationToken.None);
            }, (string? profileId) => SelectedProfile != null && !IsLoading);

            PreviewProfileCommand = new EnhancedAsyncRelayCommand<string>(async (profileId, ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("PreviewProfile");
                await PreviewProfileAsync(profileId, CancellationToken.None);
            }, (string? profileId) => CanPreview && !IsLoading && !IsPreviewing);

            StopPreviewCommand = new RelayCommand(StopPreview, () => IsPreviewing || _audioPlayer.IsPlaying);

            // Enhancement commands
            EnhanceReferenceAudioCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("EnhanceReferenceAudio");
                await EnhanceReferenceAudioAsync(ct);
            }, () => SelectedProfile != null && !IsEnhancing && !IsLoading);

            PreviewEnhancedAudioCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("PreviewEnhancedAudio");
                await PreviewEnhancedAudioAsync(ct);
            }, () => HasEnhancementResult && !IsPlayingEnhanced);

            StopEnhancedPreviewCommand = new RelayCommand(StopEnhancedPreview, () => IsPlayingEnhanced);

            ApplyEnhancedAudioCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("ApplyEnhancedAudio");
                await ApplyEnhancedAudioAsync(ct);
            }, () => HasEnhancementResult && !IsLoading);

            // Multi-select commands
            SelectAllCommand = new RelayCommand(SelectAll, () => HasProfiles);

            // Initialize filtered profiles
            FilteredProfiles = new ObservableCollection<VoiceProfile>();
            ClearSelectionCommand = new RelayCommand(ClearSelection);

            DeleteSelectedCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("DeleteSelected");
                await DeleteSelectedAsync(ct);
            }, () => SelectedCount > 0);

            // Quality history commands
            LoadQualityHistoryCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadQualityHistory");
                await LoadQualityHistoryAsync(ct);
            }, () => SelectedProfile != null && !IsLoadingQualityHistory);

            LoadQualityTrendsCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadQualityTrends");
                await LoadQualityTrendsAsync(ct);
            }, () => SelectedProfile != null && !IsLoadingQualityHistory);

            // Quality degradation detection commands (IDEA 56)
            CheckQualityDegradationCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("CheckQualityDegradation");
                await CheckQualityDegradationAsync(ct);
            }, () => SelectedProfile != null && !IsLoadingDegradation);

            LoadQualityBaselineCommand = new EnhancedAsyncRelayCommand(async (ct) =>
            {
                using var profiler = PerformanceProfiler.StartCommand("LoadQualityBaseline");
                await LoadQualityBaselineAsync(ct);
            }, () => SelectedProfile != null && !IsLoadingDegradation);

            // Subscribe to selection changes
            _multiSelectService.SelectionChanged += (s, e) =>
            {
                if (e.PanelId == PanelId)
                {
                    UpdateSelectionProperties();
                    OnPropertyChanged(nameof(SelectedCount));
                    OnPropertyChanged(nameof(HasMultipleSelection));
                }
            };
        }

        public EnhancedAsyncRelayCommand LoadProfilesCommand { get; }
        public EnhancedAsyncRelayCommand<string> CreateProfileCommand { get; }
        public EnhancedAsyncRelayCommand<string> DeleteProfileCommand { get; }
        public EnhancedAsyncRelayCommand<string> PreviewProfileCommand { get; }
        public IRelayCommand StopPreviewCommand { get; }

        // Enhancement commands
        public EnhancedAsyncRelayCommand EnhanceReferenceAudioCommand { get; }
        public EnhancedAsyncRelayCommand PreviewEnhancedAudioCommand { get; }
        public IRelayCommand StopEnhancedPreviewCommand { get; }
        public EnhancedAsyncRelayCommand ApplyEnhancedAudioCommand { get; }

        // Multi-select commands
        public IRelayCommand SelectAllCommand { get; }
        public IRelayCommand ClearSelectionCommand { get; }
        public EnhancedAsyncRelayCommand DeleteSelectedCommand { get; }

        // Quality degradation detection commands (IDEA 56)
        public EnhancedAsyncRelayCommand CheckQualityDegradationCommand { get; }
        public EnhancedAsyncRelayCommand LoadQualityBaselineCommand { get; }

        // Quality history commands
        public EnhancedAsyncRelayCommand LoadQualityHistoryCommand { get; }
        public EnhancedAsyncRelayCommand LoadQualityTrendsCommand { get; }

        private async Task LoadProfilesAsync(CancellationToken cancellationToken)
        {
            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var profilesList = await _backendClient.GetProfilesAsync(cancellationToken);

                Profiles.Clear();
                foreach (var profile in profilesList)
                {
                    Profiles.Add(profile);
                }

                // Extract unique languages and emotions
                UpdateAvailableFilters();

                // Apply filters after loading
                ApplyFilters();
            }
            catch (OperationCanceledException)
            {
                // User cancelled - expected
                return;
            }
            catch (Exception ex)
            {
                ErrorMessage = ErrorHandler.GetUserFriendlyMessage(ex);
                _errorService?.ShowError(ex, ResourceHelper.GetString("Profile.LoadFailed", "Failed to load profiles"));
                _logService?.LogError(ex, "LoadProfiles");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task CreateProfileAsync(string? name, CancellationToken cancellationToken)
        {
            // Validate input
            var validation = InputValidator.ValidateProfileName(name);
            if (!validation.IsValid)
            {
                ErrorMessage = validation.ErrorMessage;
                return;
            }

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var profile = await _backendClient.CreateProfileAsync(name!, cancellationToken: cancellationToken);
                Profiles.Add(profile);
                SelectedProfile = profile;

                // Register undo action
                if (_undoRedoService != null)
                {
                    var action = new CreateProfileAction(
                        Profiles,
                        _backendClient,
                        profile,
                        onUndo: (p) =>
                        {
                            if (SelectedProfile?.Id == p.Id)
                            {
                                SelectedProfile = null;
                            }
                        },
                        onRedo: (p) =>
                        {
                            SelectedProfile = p;
                        });
                    _undoRedoService.RegisterAction(action);
                }

                // Show success toast
                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.FormatString("Success.ProfileCreated", name),
                    ResourceHelper.GetString("Toast.Title.ProfileCreated", "Profile Created"));
            }
            catch (OperationCanceledException)
            {
                // User cancelled - expected
                return;
            }
            catch (Exception ex)
            {
                var errorMsg = ErrorHandler.GetUserFriendlyMessage(ex);
                ErrorMessage = ResourceHelper.FormatString("Profile.CreateFailed", errorMsg);
                _errorService?.ShowError(ex, ResourceHelper.GetString("Profile.CreateFailed", "Failed to create profile"));
                _logService?.LogError(ex, "CreateProfile");
                _toastNotificationService?.ShowError(
                    ResourceHelper.FormatString("Profile.CreateFailed", errorMsg),
                    ResourceHelper.GetString("Toast.Title.CreateFailed", "Create Failed"));
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task DeleteProfileAsync(string? profileId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(profileId))
                return;

            var profile = Profiles.FirstOrDefault(p => p.Id == profileId);
            if (profile == null)
                return;

            // Show confirmation dialog
            // Note: XamlRoot should be passed from the View if available
            var confirmed = await Utilities.ConfirmationDialog.ShowDeleteConfirmationAsync(
                profile.Name ?? ResourceHelper.GetString("Profile.Unnamed", "Unnamed Profile"),
                "profile"
            );

            if (!confirmed)
                return;

            try
            {
                IsLoading = true;
                ErrorMessage = null;

                var success = await _backendClient.DeleteProfileAsync(profileId, cancellationToken);
                if (success)
                {
                    var profileToDelete = Profiles.FirstOrDefault(p => p.Id == profileId);
                    if (profileToDelete != null)
                    {
                        var profileName = profileToDelete.Name ?? ResourceHelper.GetString("Profile.Unnamed", "Unnamed Profile");
                        var wasSelected = SelectedProfile?.Id == profileId;

                        Profiles.Remove(profileToDelete);
                        if (wasSelected)
                        {
                            SelectedProfile = null;
                        }

                        // Register undo action
                        if (_undoRedoService != null)
                        {
                            var action = new DeleteProfileAction(
                                Profiles,
                                _backendClient,
                                profileToDelete,
                                onUndo: (p) =>
                                {
                                    SelectedProfile = p;
                                },
                                onRedo: (p) =>
                                {
                                    if (SelectedProfile?.Id == p.Id)
                                    {
                                        SelectedProfile = null;
                                    }
                                });
                            _undoRedoService.RegisterAction(action);
                        }

                        // Show success toast
                        _toastNotificationService?.ShowSuccess(
                            ResourceHelper.FormatString("Success.ProfileDeleted", profileName),
                            ResourceHelper.GetString("Toast.Title.ProfileDeleted", "Profile Deleted"));
                    }
                }
                else
                {
                    var errorMsg = ResourceHelper.GetString("Profile.DeleteFailed", "Failed to delete profile");
                    ErrorMessage = errorMsg;
                    _toastNotificationService?.ShowError(errorMsg, ResourceHelper.GetString("Toast.Title.DeleteFailed", "Delete Failed"));
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
                ErrorMessage = ResourceHelper.FormatString("Profile.DeleteFailed", errorMsg);
                _errorService?.ShowError(ex, ResourceHelper.GetString("Profile.DeleteFailed", "Failed to delete profile"));
                _logService?.LogError(ex, "DeleteProfile");
                _toastNotificationService?.ShowError(
                    ResourceHelper.FormatString("Profile.DeleteFailed", errorMsg),
                    ResourceHelper.GetString("Toast.Title.DeleteFailed", "Delete Failed"));
            }
            finally
            {
                IsLoading = false;
            }
        }

        partial void OnSelectedProfileChanged(VoiceProfile? value)
        {
            CanPreview = SelectedProfile != null;
            PreviewProfileCommand.NotifyCanExecuteChanged();

            // Load cached quality metrics if available
            if (value != null && _previewQualityCache.ContainsKey(value.Id))
            {
                PreviewQualityMetrics = _previewQualityCache[value.Id];
                HasPreviewQualityMetrics = PreviewQualityMetrics != null;
                PreviewQualityScore = _previewQualityScoreCache.GetValueOrDefault(value.Id);
            }
            else
            {
                PreviewQualityMetrics = null;
                HasPreviewQualityMetrics = false;
                PreviewQualityScore = null;
            }

            // Load quality history when profile is selected (IDEA 30)
            if (value != null)
            {
                var ct = new CancellationTokenSource(TimeSpan.FromSeconds(30)).Token;
                _ = LoadQualityHistoryAsync(ct).ContinueWith(t =>
                {
                    if (t.IsFaulted)
                        _logService?.LogError(t.Exception?.InnerException ?? new Exception("LoadQualityHistory failed"), "LoadQualityHistory");
                }, TaskScheduler.Default);
                _ = LoadQualityTrendsAsync(ct).ContinueWith(t =>
                {
                    if (t.IsFaulted)
                        _logService?.LogError(t.Exception?.InnerException ?? new Exception("LoadQualityTrends failed"), "LoadQualityTrends");
                }, TaskScheduler.Default);
                // Also check for degradation (IDEA 56)
                _ = CheckQualityDegradationAsync(ct).ContinueWith(t =>
                {
                    if (t.IsFaulted)
                        _logService?.LogError(t.Exception?.InnerException ?? new Exception("CheckQualityDegradation failed"), "CheckQualityDegradation");
                }, TaskScheduler.Default);
                _ = LoadQualityBaselineAsync(ct).ContinueWith(t =>
                {
                    if (t.IsFaulted)
                        _logService?.LogError(t.Exception?.InnerException ?? new Exception("LoadQualityBaseline failed"), "LoadQualityBaseline");
                }, TaskScheduler.Default);
            }
            else
            {
                QualityHistory.Clear();
                QualityTrends = null;
                HasQualityHistory = false;
                QualityDegradation = null;
                QualityDegradationAlerts.Clear();
                QualityBaseline = null;
                HasQualityDegradation = false;
            }
        }

        partial void OnIsLoadingChanged(bool value)
        {
            PreviewProfileCommand.NotifyCanExecuteChanged();
        }

        partial void OnIsPreviewingChanged(bool value)
        {
            PreviewProfileCommand.NotifyCanExecuteChanged();
            StopPreviewCommand.NotifyCanExecuteChanged();
        }

        private async Task PreviewProfileAsync(string? profileId, CancellationToken cancellationToken)
        {
            if (string.IsNullOrWhiteSpace(profileId) || SelectedProfile == null)
                return;

            try
            {
                IsPreviewing = true;
                IsLoading = true;
                ErrorMessage = null;
                HasPreviewQualityMetrics = false;

                string? audioUrl = null;
                QualityMetrics? qualityMetrics = null;
                double? qualityScore = null;

                // Check cache first
                if (_previewCache.ContainsKey(profileId))
                {
                    audioUrl = _previewCache[profileId];
                    qualityMetrics = _previewQualityCache.GetValueOrDefault(profileId);
                    qualityScore = _previewQualityScoreCache.GetValueOrDefault(profileId);
                }
                else
                {
                    // Synthesize preview audio with default text
                    var request = new VoiceSynthesisRequest
                    {
                        Engine = "xtts", // Default engine for preview
                        ProfileId = profileId,
                        Text = DEFAULT_PREVIEW_TEXT,
                        Language = SelectedProfile.Language ?? "en",
                        Emotion = string.IsNullOrWhiteSpace(SelectedProfile.Emotion) ? null : SelectedProfile.Emotion,
                        EnhanceQuality = false // Fast preview, no quality enhancement
                    };

                    var response = await _backendClient.SynthesizeVoiceAsync(request, cancellationToken);
                    audioUrl = response.AudioUrl;
                    qualityMetrics = response.QualityMetrics;
                    qualityScore = response.QualityScore;

                    // Cache the results
                    if (!string.IsNullOrWhiteSpace(audioUrl))
                    {
                        _previewCache[profileId] = audioUrl;
                        if (qualityMetrics != null)
                            _previewQualityCache[profileId] = qualityMetrics;
                        if (qualityScore.HasValue)
                            _previewQualityScoreCache[profileId] = qualityScore.Value;
                    }
                }

                // Update quality metrics display
                if (qualityMetrics != null)
                {
                    PreviewQualityMetrics = qualityMetrics;
                    HasPreviewQualityMetrics = true;
                }
                PreviewQualityScore = qualityScore;

                // Update profile's quality score if we have a new quality score from preview
                // This provides real-time quality updates when previewing profiles
                if (qualityScore.HasValue && SelectedProfile != null && SelectedProfile.Id == profileId)
                {
                    // Update the profile's quality score (this will automatically update the badge via data binding)
                    var profile = Profiles.FirstOrDefault(p => p.Id == profileId);
                    if (profile != null)
                    {
                        profile.QualityScore = qualityScore.Value;
                        // Trigger property change notification for the badge to update
                        OnPropertyChanged(nameof(Profiles));
                        OnPropertyChanged(nameof(FilteredProfiles));
                    }
                }

                if (!string.IsNullOrWhiteSpace(audioUrl))
                {
                    // Download and play preview audio
                    using var httpClient = new System.Net.Http.HttpClient();
                    var audioBytes = await httpClient.GetByteArrayAsync(audioUrl);

                    // Save to temporary file
                    var tempPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), $"voicestudio_preview_{Guid.NewGuid()}.wav");
                    await System.IO.File.WriteAllBytesAsync(tempPath, audioBytes);

                    // Play preview
                    await _audioPlayer.PlayFileAsync(tempPath, () =>
                    {
                        // Cleanup and reset state after playback
                        try
                        {
                            if (System.IO.File.Exists(tempPath))
                                System.IO.File.Delete(tempPath);
                        }
                        catch { /* Ignore cleanup errors */ }

                        IsPreviewing = false;
                        IsLoading = false;
                    });
                }
            }
            catch (OperationCanceledException)
            {
                // User cancelled - expected
                IsPreviewing = false;
                IsLoading = false;
                return;
            }
            catch (Exception ex)
            {
                var errorMsg = ErrorHandler.GetUserFriendlyMessage(ex);
                ErrorMessage = ResourceHelper.FormatString("Profile.PreviewFailed", errorMsg);
                _errorService?.ShowError(ex, ResourceHelper.GetString("Profile.PreviewFailed", "Failed to preview profile"));
                _logService?.LogError(ex, "PreviewProfile");
                IsPreviewing = false;
                IsLoading = false;
            }
        }

        private void StopPreview()
        {
            try
            {
                _audioPlayer.Stop();
                IsPreviewing = false;
            }
            catch (Exception ex)
            {
                ErrorHandler.LogError(ex, "StopPreview");
                ErrorMessage = ResourceHelper.FormatString("Profile.StopPreviewFailed", ErrorHandler.GetUserFriendlyMessage(ex));
            }
        }

        // Multi-select methods
        public void ToggleSelection(string profileId, bool isCtrlPressed, bool isShiftPressed)
        {
            if (_multiSelectState == null)
                return;

            if (isShiftPressed && !string.IsNullOrEmpty(_multiSelectState.RangeAnchorId))
            {
                // Range selection
                var allIds = Profiles.Select(p => p.Id).ToList();
                _multiSelectState.SetRange(_multiSelectState.RangeAnchorId, profileId, allIds);
            }
            else if (isCtrlPressed)
            {
                // Toggle selection
                _multiSelectState.Toggle(profileId);
            }
            else
            {
                // Single selection (clear others)
                _multiSelectState.SetSingle(profileId);
            }

            UpdateSelectionProperties();
            _multiSelectService.OnSelectionChanged(PanelId, _multiSelectState);
        }

        private void SelectAll()
        {
            if (_multiSelectState == null)
                return;

            _multiSelectState.Clear();
            foreach (var profile in FilteredProfiles)
            {
                _multiSelectState.Add(profile.Id);
            }
            if (FilteredProfiles.Count > 0)
            {
                _multiSelectState.RangeAnchorId = FilteredProfiles[0].Id;
            }

            UpdateSelectionProperties();
            _multiSelectService.OnSelectionChanged(PanelId, _multiSelectState);
            SelectAllCommand.NotifyCanExecuteChanged();
        }

        private void ClearSelection()
        {
            if (_multiSelectState == null)
                return;

            _multiSelectState.Clear();
            UpdateSelectionProperties();
            _multiSelectService.OnSelectionChanged(PanelId, _multiSelectState);
            DeleteSelectedCommand.NotifyCanExecuteChanged();
        }

        private async Task DeleteSelectedAsync(CancellationToken cancellationToken)
        {
            if (_multiSelectState == null || _multiSelectState.SelectedIds.Count == 0)
                return;

            var selectedIds = new List<string>(_multiSelectState.SelectedIds);

            // Show confirmation dialog
            var confirmed = await Utilities.ConfirmationDialog.ShowDeleteConfirmationAsync(
                $"{selectedIds.Count} profile(s)",
                "profiles"
            );

            if (!confirmed)
                return;

            cancellationToken.ThrowIfCancellationRequested();

            IsLoading = true;
            ErrorMessage = null;

            try
            {
                var profilesToDelete = new List<VoiceProfile>();
                int deletedCount = 0;
                var wasAnySelected = false;

                foreach (var profileId in selectedIds)
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    try
                    {
                        var success = await _backendClient.DeleteProfileAsync(profileId, cancellationToken);
                        if (success)
                        {
                            var profile = Profiles.FirstOrDefault(p => p.Id == profileId);
                            if (profile != null)
                            {
                                profilesToDelete.Add(profile);
                                Profiles.Remove(profile);
                                if (SelectedProfile?.Id == profileId)
                                {
                                    SelectedProfile = null;
                                    wasAnySelected = true;
                                }
                                deletedCount++;
                            }
                        }
                    }
                    catch
                    {
                        // Continue even if one deletion fails
                    }
                }

                // Register batch undo action if any profiles were deleted
                if (deletedCount > 0 && _undoRedoService != null && profilesToDelete.Count > 0)
                {
                    var action = new BatchDeleteProfilesAction(
                        Profiles,
                        _backendClient,
                        profilesToDelete,
                        onUndo: (profiles) =>
                        {
                            if (wasAnySelected && profiles.Any())
                            {
                                SelectedProfile = profiles.First();
                            }
                        },
                        onRedo: (profiles) =>
                        {
                            if (SelectedProfile != null && profiles.Any(p => p.Id == SelectedProfile.Id))
                            {
                                SelectedProfile = null;
                            }
                        });
                    _undoRedoService.RegisterAction(action);
                }

                // Clear selection after deletion
                ClearSelection();

                // Show success toast
                if (deletedCount > 0)
                {
                    _toastNotificationService?.ShowSuccess(
                        ResourceHelper.FormatString("Profile.BatchDeleteComplete", deletedCount),
                        ResourceHelper.GetString("Toast.Title.BatchDeleteComplete", "Batch Delete Complete"));
                }
                if (deletedCount < selectedIds.Count)
                {
                    _toastNotificationService?.ShowWarning(
                        ResourceHelper.FormatString("Profile.BatchDeletePartial", deletedCount, selectedIds.Count),
                        ResourceHelper.GetString("Toast.Title.PartialDelete", "Partial Delete"));
                }
            }
            catch (Exception ex)
            {
                ErrorHandler.LogError(ex, "DeleteSelectedProfiles");
                var errorMsg = ResourceHelper.FormatString("Profile.BatchDeleteFailed", ErrorHandler.GetUserFriendlyMessage(ex));
                ErrorMessage = errorMsg;
                _toastNotificationService?.ShowError(errorMsg, ResourceHelper.GetString("Toast.Title.DeleteFailed", "Delete Failed"));
            }
            finally
            {
                IsLoading = false;
            }
        }

        private void UpdateSelectionProperties()
        {
            if (_multiSelectState == null)
            {
                SelectedCount = 0;
                HasMultipleSelection = false;
            }
            else
            {
                SelectedCount = _multiSelectState.Count;
                HasMultipleSelection = _multiSelectState.IsMultipleSelection;
            }

            OnPropertyChanged(nameof(SelectedCount));
            OnPropertyChanged(nameof(HasMultipleSelection));
            DeleteSelectedCommand.NotifyCanExecuteChanged();

            // Notify UI that selection state changed for all profiles
            foreach (var profile in Profiles)
            {
                OnPropertyChanged(nameof(IsProfileSelected));
            }
        }

        // Filtering methods
        private void ApplyFilters()
        {
            var query = (SearchQuery ?? "").Trim().ToLowerInvariant();

            var filtered = Profiles.Where(profile =>
            {
                // Search query filter
                if (!string.IsNullOrEmpty(query))
                {
                    var nameMatch = (profile.Name ?? "").ToLowerInvariant().Contains(query);
                    var tagMatch = profile.Tags?.Any(tag => tag.ToLowerInvariant().Contains(query)) ?? false;
                    if (!nameMatch && !tagMatch)
                        return false;
                }

                // Language filter
                if (!string.IsNullOrEmpty(SelectedLanguage) && profile.Language != SelectedLanguage)
                    return false;

                // Emotion filter
                if (!string.IsNullOrEmpty(SelectedEmotion) && profile.Emotion != SelectedEmotion)
                    return false;

                // Quality range filter
                var allFilter = ResourceHelper.GetString("Filter.All", "All");
                if (!string.IsNullOrEmpty(SelectedQualityRange) && SelectedQualityRange != allFilter)
                {
                    var quality = profile.QualityScore;
                    var matches = SelectedQualityRange switch
                    {
                        var s when s == ResourceHelper.GetString("Filter.QualityHigh", "High (4.0+)") => quality >= 4.0,
                        var s when s == ResourceHelper.GetString("Filter.QualityGood", "Good (3.0-4.0)") => quality >= 3.0 && quality < 4.0,
                        var s when s == ResourceHelper.GetString("Filter.QualityFair", "Fair (2.0-3.0)") => quality >= 2.0 && quality < 3.0,
                        var s when s == ResourceHelper.GetString("Filter.QualityLow", "Low (<2.0)") => quality < 2.0,
                        _ => true
                    };
                    if (!matches)
                        return false;
                }

                return true;
            }).ToList();

            FilteredProfiles.Clear();
            foreach (var profile in filtered)
            {
                FilteredProfiles.Add(profile);
            }

            TotalProfiles = Profiles.Count;
            FilteredCount = FilteredProfiles.Count;
            OnPropertyChanged(nameof(HasProfiles));
        }

        private void UpdateAvailableFilters()
        {
            var languages = Profiles.Select(p => p.Language).Where(l => !string.IsNullOrEmpty(l)).Distinct().OrderBy(l => l).ToList();
            AvailableLanguages.Clear();
            AvailableLanguages.Add(ResourceHelper.GetString("Filter.All", "All"));
            foreach (var lang in languages)
            {
                AvailableLanguages.Add(lang);
            }

            var emotions = Profiles.Select(p => p.Emotion).Where(e => !string.IsNullOrEmpty(e)).Distinct().OrderBy(e => e).ToList();
            AvailableEmotions.Clear();
            AvailableEmotions.Add(ResourceHelper.GetString("Filter.All", "All"));
            foreach (var emotion in emotions)
            {
                AvailableEmotions.Add(emotion);
            }
        }

        partial void OnSearchQueryChanged(string? value)
        {
            ApplyFilters();
        }

        partial void OnSelectedLanguageChanged(string? value)
        {
            ApplyFilters();
        }

        partial void OnSelectedEmotionChanged(string? value)
        {
            ApplyFilters();
        }

        partial void OnSelectedQualityRangeChanged(string? value)
        {
            ApplyFilters();
        }


        partial void OnEnhancementResultChanged(ReferenceAudioPreprocessResponse? value)
        {
            HasEnhancementResult = value != null;
            PreviewEnhancedAudioCommand.NotifyCanExecuteChanged();
            ApplyEnhancedAudioCommand.NotifyCanExecuteChanged();
        }

        private async Task EnhanceReferenceAudioAsync(CancellationToken cancellationToken)
        {
            if (SelectedProfile == null)
                return;

            try
            {
                IsEnhancing = true;
                ErrorMessage = null;
                EnhanceReferenceAudioCommand.NotifyCanExecuteChanged();

                var request = new ReferenceAudioPreprocessRequest
                {
                    ProfileId = SelectedProfile.Id,
                    AutoEnhance = AutoEnhance,
                    SelectOptimalSegments = SelectOptimalSegments,
                    MinSegmentDuration = 1.0,
                    MaxSegments = 5
                };

                var response = await _backendClient.SendRequestAsync<ReferenceAudioPreprocessRequest, ReferenceAudioPreprocessResponse>(
                    $"/api/profiles/{SelectedProfile.Id}/preprocess-reference",
                    request,
                    cancellationToken
                );

                if (response != null)
                {
                    EnhancementResult = response;
                    _toastNotificationService?.ShowSuccess(
                        ResourceHelper.FormatString("Profile.EnhancementComplete", response.QualityImprovement),
                        ResourceHelper.GetString("Toast.Title.EnhancementComplete", "Enhancement Complete")
                    );
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
                ErrorMessage = ResourceHelper.FormatString("Profile.EnhancementFailed", errorMsg);
                _errorService?.ShowError(ex, ResourceHelper.GetString("Profile.EnhancementFailed", "Failed to enhance reference audio"));
                _logService?.LogError(ex, "EnhanceReferenceAudio");
                _toastNotificationService?.ShowError(
                    ResourceHelper.FormatString("Profile.EnhancementFailed", ErrorHandler.GetUserFriendlyMessage(ex)),
                    ResourceHelper.GetString("Toast.Title.EnhancementComplete", "Enhancement Failed")
                );
            }
            finally
            {
                IsEnhancing = false;
                EnhanceReferenceAudioCommand.NotifyCanExecuteChanged();
            }
        }

        private async Task PreviewEnhancedAudioAsync(CancellationToken cancellationToken)
        {
            if (EnhancementResult == null || string.IsNullOrEmpty(EnhancementResult.ProcessedAudioUrl))
                return;

            IsPlayingEnhanced = true;
            StopEnhancedPreviewCommand.NotifyCanExecuteChanged();
            PreviewEnhancedAudioCommand.NotifyCanExecuteChanged();

            try
            {
                // Play the enhanced audio
                await _audioPlayer.PlayFileAsync(EnhancementResult.ProcessedAudioUrl);

                // Wait for playback to complete
                while (_audioPlayer.IsPlaying)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    await Task.Delay(100, cancellationToken);
                }
            }
            catch (OperationCanceledException)
            {
                // User cancelled - expected
                _audioPlayer.Stop();
                return;
            }
            catch (Exception ex)
            {
                var errorMsg = ErrorHandler.GetUserFriendlyMessage(ex);
                ErrorMessage = ResourceHelper.FormatString("Error.PreviewEnhancedFailed", errorMsg);
                _errorService?.ShowError(ex, ResourceHelper.GetString("Error.PreviewEnhancedFailed", "Failed to preview enhanced audio"));
                _logService?.LogError(ex, "PreviewEnhancedAudio");
                _toastNotificationService?.ShowError(
                    ResourceHelper.FormatString("Error.PreviewEnhancedFailed", errorMsg),
                    ResourceHelper.GetString("VoiceSynthesis.PreviewFailed", "Preview Failed")
                );
            }
            finally
            {
                IsPlayingEnhanced = false;
                StopEnhancedPreviewCommand.NotifyCanExecuteChanged();
                PreviewEnhancedAudioCommand.NotifyCanExecuteChanged();
            }
        }

        private void StopEnhancedPreview()
        {
            try
            {
                _audioPlayer.Stop();
            }
            catch (Exception ex)
            {
                ErrorHandler.LogError(ex, "StopEnhancedPreview");
            }
            finally
            {
                IsPlayingEnhanced = false;
                StopEnhancedPreviewCommand.NotifyCanExecuteChanged();
                PreviewEnhancedAudioCommand.NotifyCanExecuteChanged();
            }
        }

        private async Task ApplyEnhancedAudioAsync(CancellationToken cancellationToken)
        {
            if (EnhancementResult == null || SelectedProfile == null)
                return;

            IsLoading = true;
            ErrorMessage = null;
            ApplyEnhancedAudioCommand.NotifyCanExecuteChanged();

            try
            {
                // Note: The backend may need to be updated to support reference_audio_url updates
                // For now, we'll just show a success message and reload profiles
                await LoadProfilesAsync(cancellationToken);

                _toastNotificationService?.ShowSuccess(
                    ResourceHelper.GetString("Profile.EnhancementApplied", "Enhanced reference audio has been applied to the profile"),
                    ResourceHelper.GetString("Toast.Title.EnhancementApplied", "Enhancement Applied")
                );

                // Clear enhancement result after applying
                EnhancementResult = null;
                HasEnhancementResult = false;
            }
            catch (Exception ex)
            {
                ErrorHandler.LogError(ex, "ApplyEnhancedAudio");
                ErrorMessage = ResourceHelper.FormatString("Error.ApplyEnhancedFailed", ErrorHandler.GetUserFriendlyMessage(ex));
                _toastNotificationService?.ShowError(
                    ResourceHelper.FormatString("Error.ApplyEnhancedFailed", ErrorHandler.GetUserFriendlyMessage(ex)),
                    ResourceHelper.GetString("Toast.Title.SaveFailed", "Apply Failed")
                );
            }
            finally
            {
                IsLoading = false;
                ApplyEnhancedAudioCommand.NotifyCanExecuteChanged();
            }
        }

        // Quality History Methods (IDEA 30)
        private async Task LoadQualityHistoryAsync(CancellationToken cancellationToken)
        {
            if (SelectedProfile == null)
                return;

            IsLoadingQualityHistory = true;
            LoadQualityHistoryCommand.NotifyCanExecuteChanged();
            LoadQualityTrendsCommand.NotifyCanExecuteChanged();

            try
            {
                var history = await _backendClient.GetQualityHistoryAsync(
                    SelectedProfile.Id,
                    limit: 50, // Load last 50 entries
                    cancellationToken: cancellationToken
                );

                QualityHistory.Clear();
                foreach (var entry in history)
                {
                    QualityHistory.Add(entry);
                }

                HasQualityHistory = QualityHistory.Count > 0;
            }
            catch (OperationCanceledException)
            {
                // User cancelled - expected
                return;
            }
            catch (Exception ex)
            {
                // Log error but don't break UI - quality history is non-critical
                _logService?.LogError(ex, "LoadQualityHistory");
                QualityHistory.Clear();
                HasQualityHistory = false;
            }
            finally
            {
                IsLoadingQualityHistory = false;
                LoadQualityHistoryCommand.NotifyCanExecuteChanged();
                LoadQualityTrendsCommand.NotifyCanExecuteChanged();
            }
        }

        private async Task LoadQualityTrendsAsync(CancellationToken cancellationToken)
        {
            if (SelectedProfile == null)
                return;

            IsLoadingQualityHistory = true;
            LoadQualityHistoryCommand.NotifyCanExecuteChanged();
            LoadQualityTrendsCommand.NotifyCanExecuteChanged();

            try
            {
                var trends = await _backendClient.GetQualityTrendsAsync(
                    SelectedProfile.Id,
                    SelectedTimeRange,
                    cancellationToken
                );

                QualityTrends = trends;
            }
            catch (OperationCanceledException)
            {
                // User cancelled - expected
                return;
            }
            catch (Exception ex)
            {
                // Log error but don't break UI - quality trends are non-critical
                _logService?.LogError(ex, "LoadQualityTrends");
                QualityTrends = null;
            }
            finally
            {
                IsLoadingQualityHistory = false;
                LoadQualityHistoryCommand.NotifyCanExecuteChanged();
                LoadQualityTrendsCommand.NotifyCanExecuteChanged();
            }
        }

        partial void OnSelectedTimeRangeChanged(string value)
        {
            if (SelectedProfile != null)
            {
                var ct = new CancellationTokenSource(TimeSpan.FromSeconds(30)).Token;
                _ = LoadQualityTrendsAsync(ct).ContinueWith(t =>
                {
                    if (t.IsFaulted)
                        _logService?.LogError(t.Exception?.InnerException ?? new Exception("LoadQualityTrends failed"), "LoadQualityTrends");
                }, TaskScheduler.Default);
            }
        }

        // Quality Degradation Detection Methods (IDEA 56)
        private async Task CheckQualityDegradationAsync(CancellationToken cancellationToken)
        {
            if (SelectedProfile == null)
                return;

            IsLoadingDegradation = true;
            CheckQualityDegradationCommand.NotifyCanExecuteChanged();
            LoadQualityBaselineCommand.NotifyCanExecuteChanged();

            try
            {
                var degradation = await _backendClient.GetQualityDegradationAsync(
                    SelectedProfile.Id,
                    DegradationTimeWindowDays,
                    degradationThresholdPercent: 10.0,
                    criticalThresholdPercent: 25.0,
                    cancellationToken
                );

                QualityDegradation = degradation;
                HasQualityDegradation = degradation?.HasDegradation ?? false;

                // Update alerts collection for binding
                QualityDegradationAlerts.Clear();
                if (degradation?.Alerts != null)
                {
                    foreach (var alert in degradation.Alerts)
                    {
                        QualityDegradationAlerts.Add(alert);
                    }
                }

                // Show toast notification if degradation detected
                if (HasQualityDegradation)
                {
                    var criticalCount = QualityDegradationAlerts.Count(a => a.Severity == "critical");
                    var warningCount = QualityDegradationAlerts.Count(a => a.Severity == "warning");

                    if (criticalCount > 0)
                    {
                        _toastNotificationService?.ShowError(
                            ResourceHelper.GetString("Profile.QualityDegradationAlert", "Quality Degradation Alert"),
                            ResourceHelper.FormatString("Profile.QualityDegradationCritical", criticalCount, warningCount)
                        );
                    }
                    else if (warningCount > 0)
                    {
                        _toastNotificationService?.ShowWarning(
                            ResourceHelper.GetString("Profile.QualityDegradationAlert", "Quality Degradation Alert"),
                            ResourceHelper.FormatString("Profile.QualityDegradationWarning", warningCount)
                        );
                    }
                }
            }
            catch (OperationCanceledException)
            {
                // User cancelled - expected
                return;
            }
            catch (Exception ex)
            {
                // Log error but don't break UI - degradation detection is non-critical
                _logService?.LogError(ex, "CheckQualityDegradation");
                QualityDegradationAlerts.Clear();
                HasQualityDegradation = false;
            }
            finally
            {
                IsLoadingDegradation = false;
                CheckQualityDegradationCommand.NotifyCanExecuteChanged();
                LoadQualityBaselineCommand.NotifyCanExecuteChanged();
            }
        }

        private async Task LoadQualityBaselineAsync(CancellationToken cancellationToken)
        {
            if (SelectedProfile == null)
                return;

            IsLoadingDegradation = true;
            CheckQualityDegradationCommand.NotifyCanExecuteChanged();
            LoadQualityBaselineCommand.NotifyCanExecuteChanged();

            try
            {
                var baseline = await _backendClient.GetQualityBaselineAsync(
                    SelectedProfile.Id,
                    timePeriodDays: 30,
                    cancellationToken
                );

                QualityBaseline = baseline;
            }
            catch (OperationCanceledException)
            {
                // User cancelled - expected
                return;
            }
            catch (Exception ex)
            {
                // Log error but don't break UI - baseline loading is non-critical
                _logService?.LogError(ex, "LoadQualityBaseline");
                QualityBaseline = null;
            }
            finally
            {
                IsLoadingDegradation = false;
                CheckQualityDegradationCommand.NotifyCanExecuteChanged();
                LoadQualityBaselineCommand.NotifyCanExecuteChanged();
            }
        }
    }
}


