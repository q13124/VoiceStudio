using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Utilities;

namespace VoiceStudio.App.ViewModels
{
    /// <summary>
    /// ViewModel for the SpatialAudioView panel - 3D audio positioning and spatialization.
    /// </summary>
    public partial class SpatialAudioViewModel : BaseViewModel, IPanelView
    {
        private readonly IBackendClient _backendClient;

        public string PanelId => "spatial-audio";
        public string DisplayName => ResourceHelper.GetString("Panel.SpatialAudio.DisplayName", "Spatial Audio");
        public PanelRegion Region => PanelRegion.Right;

        [ObservableProperty]
        private string? audioId;

        [ObservableProperty]
        private float positionX;

        [ObservableProperty]
        private float positionY;

        [ObservableProperty]
        private float positionZ;

        [ObservableProperty]
        private float distance = 1.0f;

        [ObservableProperty]
        private float roomSize = 1.0f;

        [ObservableProperty]
        private string selectedMaterial = "concrete";

        [ObservableProperty]
        private ObservableCollection<string> availableMaterials = new() { "concrete", "wood", "carpet", "metal", "glass", "fabric", "outdoor" };

        [ObservableProperty]
        private float reverbAmount;

        [ObservableProperty]
        private bool enableDoppler;

        [ObservableProperty]
        private bool enableHRTF = true;

        [ObservableProperty]
        private string? selectedPreset = "None";

        [ObservableProperty]
        private ObservableCollection<string> availablePresets = new() { "None", "Small Room", "Concert Hall", "Outdoor", "Studio", "Cathedral" };

        [ObservableProperty]
        private string? processedAudioId;

        [ObservableProperty]
        private string? processedAudioUrl;

        [ObservableProperty]
        private bool isPreviewing;

        public SpatialAudioViewModel(IBackendClient backendClient)
        {
            _backendClient = backendClient ?? throw new ArgumentNullException(nameof(backendClient));

            SetPositionCommand = new AsyncRelayCommand(SetPositionAsync, () => !string.IsNullOrWhiteSpace(AudioId));
            ConfigureEnvironmentCommand = new AsyncRelayCommand(ConfigureEnvironmentAsync);
            ProcessAudioCommand = new AsyncRelayCommand(ProcessAudioAsync, () => !string.IsNullOrWhiteSpace(AudioId));
            PreviewAudioCommand = new AsyncRelayCommand(PreviewAudioAsync, () => !string.IsNullOrWhiteSpace(AudioId));
            ApplyPresetCommand = new AsyncRelayCommand(ApplyPresetAsync);
            ResetCommand = new AsyncRelayCommand(ResetAsync);
        }

        public IAsyncRelayCommand SetPositionCommand { get; }
        public IAsyncRelayCommand ConfigureEnvironmentCommand { get; }
        public IAsyncRelayCommand ProcessAudioCommand { get; }
        public IAsyncRelayCommand PreviewAudioCommand { get; }
        public IAsyncRelayCommand ApplyPresetCommand { get; }
        public IAsyncRelayCommand ResetCommand { get; }

        partial void OnAudioIdChanged(string? value)
        {
            SetPositionCommand.NotifyCanExecuteChanged();
            ProcessAudioCommand.NotifyCanExecuteChanged();
            PreviewAudioCommand.NotifyCanExecuteChanged();
        }

        partial void OnSelectedPresetChanged(string? value)
        {
            if (!string.IsNullOrWhiteSpace(value) && value != "None")
            {
                ApplyPresetAsync();
            }
        }

        private async Task SetPositionAsync()
        {
            if (string.IsNullOrWhiteSpace(AudioId))
            {
                return;
            }

            try
            {
                IsLoading = true;
                ErrorMessage = null;

                var request = new SpatialPositionRequest
                {
                    AudioId = AudioId,
                    X = PositionX,
                    Y = PositionY,
                    Z = PositionZ,
                    Distance = Distance
                };

                var response = await _backendClient.SendRequestAsync<SpatialPositionRequest, SpatialConfigResponse>(
                    "/api/spatial-audio/position",
                    request,
                    System.Net.Http.HttpMethod.Post
                );

                if (response != null)
                {
                    StatusMessage = ResourceHelper.FormatString("SpatialAudio.PositionSet", PositionX, PositionY, PositionZ, Distance);
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("SpatialAudio.SetPositionFailed", ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task ConfigureEnvironmentAsync()
        {
            try
            {
                IsLoading = true;
                ErrorMessage = null;

                var request = new SpatialEnvironmentRequest
                {
                    RoomSize = RoomSize,
                    Material = SelectedMaterial,
                    ReverbAmount = ReverbAmount,
                    Doppler = EnableDoppler
                };

                var response = await _backendClient.SendRequestAsync<SpatialEnvironmentRequest, Dictionary<string, object>>(
                    "/api/spatial-audio/environment",
                    request,
                    System.Net.Http.HttpMethod.Post
                );

                if (response != null)
                {
                    StatusMessage = ResourceHelper.FormatString("SpatialAudio.EnvironmentConfigured", SelectedMaterial, RoomSize);
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("SpatialAudio.ConfigureEnvironmentFailed", ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task ProcessAudioAsync()
        {
            if (string.IsNullOrWhiteSpace(AudioId))
            {
                return;
            }

            try
            {
                IsLoading = true;
                ErrorMessage = null;

                var request = new SpatialProcessRequest
                {
                    AudioId = AudioId,
                    Position = new SpatialPositionData
                    {
                        X = PositionX,
                        Y = PositionY,
                        Z = PositionZ,
                        Distance = Distance
                    },
                    Environment = new SpatialEnvironmentData
                    {
                        RoomSize = RoomSize,
                        Material = SelectedMaterial,
                        ReverbAmount = ReverbAmount,
                        Doppler = EnableDoppler
                    }
                };

                var response = await _backendClient.SendRequestAsync<SpatialProcessRequest, SpatialProcessResponse>(
                    "/api/spatial-audio/process",
                    request,
                    System.Net.Http.HttpMethod.Post
                );

                if (response != null)
                {
                    ProcessedAudioId = response.ProcessedAudioId;
                    ProcessedAudioUrl = response.ProcessedAudioUrl;
                    StatusMessage = ResourceHelper.GetString("SpatialAudio.ProcessingCompleted", "Spatial audio processing completed");
                }
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("SpatialAudio.ProcessAudioFailed", ex.Message);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task PreviewAudioAsync()
        {
            if (string.IsNullOrWhiteSpace(AudioId))
            {
                return;
            }

            try
            {
                IsPreviewing = true;
                ErrorMessage = null;

                // Preview uses the preview endpoint
                var response = await _backendClient.SendRequestAsync<object, Dictionary<string, object>>(
                    $"/api/spatial-audio/preview?audio_id={Uri.EscapeDataString(AudioId)}&x={PositionX}&y={PositionY}&z={PositionZ}&distance={Distance}",
                    null,
                    System.Net.Http.HttpMethod.Post
                );

                StatusMessage = ResourceHelper.GetString("SpatialAudio.PreviewStarted", "Preview started (requires spatial audio libraries)");
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("SpatialAudio.PreviewAudioFailed", ex.Message);
            }
            finally
            {
                IsPreviewing = false;
            }
        }

        private async Task ApplyPresetAsync()
        {
            if (string.IsNullOrWhiteSpace(SelectedPreset) || SelectedPreset == "None")
            {
                return;
            }

            try
            {
                // Apply preset values
                switch (SelectedPreset)
                {
                    case "Small Room":
                        RoomSize = 0.5f;
                        SelectedMaterial = "concrete";
                        ReverbAmount = 0.3f;
                        EnableDoppler = false;
                        break;
                    case "Concert Hall":
                        RoomSize = 3.0f;
                        SelectedMaterial = "wood";
                        ReverbAmount = 0.8f;
                        EnableDoppler = false;
                        break;
                    case "Outdoor":
                        RoomSize = 10.0f;
                        SelectedMaterial = "outdoor";
                        ReverbAmount = 0.1f;
                        EnableDoppler = true;
                        break;
                    case "Studio":
                        RoomSize = 0.3f;
                        SelectedMaterial = "fabric";
                        ReverbAmount = 0.1f;
                        EnableDoppler = false;
                        break;
                    case "Cathedral":
                        RoomSize = 5.0f;
                        SelectedMaterial = "concrete";
                        ReverbAmount = 0.9f;
                        EnableDoppler = false;
                        break;
                }

                await ConfigureEnvironmentAsync();
                StatusMessage = ResourceHelper.FormatString("SpatialAudio.PresetApplied", SelectedPreset);
            }
            catch (Exception ex)
            {
                ErrorMessage = ResourceHelper.FormatString("SpatialAudio.ApplyPresetFailed", ex.Message);
            }
        }

        private async Task ResetAsync()
        {
            PositionX = 0.0f;
            PositionY = 0.0f;
            PositionZ = 0.0f;
            Distance = 1.0f;
            RoomSize = 1.0f;
            SelectedMaterial = "concrete";
            ReverbAmount = 0.0f;
            EnableDoppler = false;
            SelectedPreset = "None";
            StatusMessage = ResourceHelper.GetString("SpatialAudio.ResetToDefaults", "Reset to defaults");
        }

        // Request/Response models
        private class SpatialPositionRequest
        {
            public string AudioId { get; set; } = string.Empty;
            public float X { get; set; }
            public float Y { get; set; }
            public float Z { get; set; }
            public float Distance { get; set; }
        }

        private class SpatialConfigResponse
        {
            public string ConfigId { get; set; } = string.Empty;
            public string Name { get; set; } = string.Empty;
            public SpatialPositionData Position { get; set; } = new();
        }

        private class SpatialPositionData
        {
            public float X { get; set; }
            public float Y { get; set; }
            public float Z { get; set; }
            public float Distance { get; set; }
        }

        private class SpatialEnvironmentRequest
        {
            public float RoomSize { get; set; }
            public string Material { get; set; } = string.Empty;
            public float ReverbAmount { get; set; }
            public bool Doppler { get; set; }
        }

        private class SpatialProcessRequest
        {
            public string AudioId { get; set; } = string.Empty;
            public SpatialPositionData? Position { get; set; }
            public SpatialEnvironmentData? Environment { get; set; }
        }

        private class SpatialEnvironmentData
        {
            public float RoomSize { get; set; }
            public string Material { get; set; } = string.Empty;
            public float ReverbAmount { get; set; }
            public bool Doppler { get; set; }
        }

        private class SpatialProcessResponse
        {
            public string ProcessedAudioId { get; set; } = string.Empty;
            public string ProcessedAudioUrl { get; set; } = string.Empty;
        }
    }
}

