using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using System.Net.Http;
using System.Text.Json;
using Windows.Storage;
using Windows.Storage.Pickers;
using Windows.Media.Playback;
using Windows.Media.Core;
using VoiceStudioWinUI.Services;

namespace VoiceStudioWinUI
{
    public sealed partial class MainWindow : Window
    {
        private string _selectedAudioPath;
        private string _outputAudioPath;
        private MediaPlayer _mediaPlayer;
        private VoiceCloningService _voiceService;
        private HttpClient _httpClient;
        private System.Threading.Timer _agentStatusTimer;

        public MainWindow()
        {
            this.InitializeComponent();
            _mediaPlayer = new MediaPlayer();
            _voiceService = new VoiceCloningService();
            _httpClient = new HttpClient();
            InitializeUI();
            InitializeBackend();
            StartAgentMonitoring();
        }

        private void InitializeUI()
        {
            ModelComboBox.SelectedIndex = 0;
            UpdateStatus("Initializing...", "Yellow");
        }

        private async void InitializeBackend()
        {
            try
            {
                UpdateStatus("Starting Python backend...", "Yellow");
                var success = await _voiceService.StartPythonBackendAsync();
                if (success)
                {
                    UpdateStatus("Backend ready - Voice cloning available", "Green");
                    await LoadAvailableModels();
                }
                else
                {
                    UpdateStatus("Backend failed to start - Using simulation mode", "Red");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Backend error: {ex.Message}", "Red");
            }
        }

        private async Task LoadAvailableModels()
        {
            try
            {
                var models = await _voiceService.GetAvailableModelsAsync();
                // Update UI with available models
                UpdateStatus($"Loaded {models.Count} AI models", "Green");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to load models: {ex.Message}", "Red");
            }
        }

        private async void SelectAudioButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var picker = new FileOpenPicker();
                picker.ViewMode = PickerViewMode.List;
                picker.SuggestedStartLocation = PickerLocationId.MusicLibrary;
                picker.FileTypeFilter.Add(".wav");
                picker.FileTypeFilter.Add(".mp3");
                picker.FileTypeFilter.Add(".m4a");

                var file = await picker.PickSingleFileAsync();
                if (file != null)
                {
                    _selectedAudioPath = file.Path;
                    SelectedAudioText.Text = Path.GetFileName(file.Path);
                    UpdateStatus("Audio file selected", "Green");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error selecting audio: {ex.Message}", "Red");
            }
        }

        private async void CloneButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (string.IsNullOrEmpty(_selectedAudioPath))
                {
                    UpdateStatus("Please select a reference audio file", "Red");
                    return;
                }

                if (string.IsNullOrEmpty(TargetTextBox.Text))
                {
                    UpdateStatus("Please enter target text", "Red");
                    return;
                }

                UpdateStatus("Starting voice cloning...", "Yellow");
                ShowProgress(true);

                // Get selected options
                var selectedModel = (ModelComboBox.SelectedItem as ComboBoxItem)?.Tag?.ToString();
                var emotion = "neutral"; // Default emotion
                var accent = "neutral"; // Default accent
                var quality = "ultimate"; // Default quality
                var realTime = false; // Default real-time setting

                // Create clone request
                var request = new CloneRequest
                {
                    AudioPath = _selectedAudioPath,
                    TargetText = TargetTextBox.Text,
                    ModelId = selectedModel,
                    Emotion = emotion,
                    Accent = accent,
                    QualityPreset = quality,
                    RealTime = realTime
                };

                // Call real voice cloning service
                var result = await _voiceService.CloneVoiceAsync(request);

                if (result.Success)
                {
                    _outputAudioPath = result.OutputPath;
                    OutputText.Text = $"Voice cloned successfully! Output: {Path.GetFileName(_outputAudioPath)}";
                    PlayButton.IsEnabled = true;
                    SaveButton.IsEnabled = true;
                    UpdateStatus($"Voice cloning completed in {result.ProcessingTime:F1}s using {result.ModelUsed}!", "Green");
                }
                else
                {
                    UpdateStatus($"Voice cloning failed: {result.Error}", "Red");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error: {ex.Message}", "Red");
            }
            finally
            {
                ShowProgress(false);
            }
        }

        private async void PlayButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (!string.IsNullOrEmpty(_outputAudioPath) && File.Exists(_outputAudioPath))
                {
                    var file = await StorageFile.GetFileFromPathAsync(_outputAudioPath);
                    _mediaPlayer.Source = MediaSource.CreateFromStorageFile(file);
                    _mediaPlayer.Play();
                    UpdateStatus("Playing output audio...", "Green");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error playing audio: {ex.Message}", "Red");
            }
        }

        private async void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (!string.IsNullOrEmpty(_outputAudioPath) && File.Exists(_outputAudioPath))
                {
                    var picker = new FileSavePicker();
                    picker.SuggestedStartLocation = PickerLocationId.MusicLibrary;
                    picker.SuggestedFileName = $"cloned_voice_{DateTime.Now:yyyyMMdd_HHmmss}";
                    picker.FileTypeChoices.Add("WAV Audio", new List<string>() { ".wav" });

                    var file = await picker.PickSaveFileAsync();
                    if (file != null)
                    {
                        var sourceFile = await StorageFile.GetFileFromPathAsync(_outputAudioPath);
                        await sourceFile.CopyAndReplaceAsync(file);
                        UpdateStatus($"Audio saved to: {file.Path}", "Green");
                    }
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error saving audio: {ex.Message}", "Red");
            }
        }

        private void UpdateStatus(string message, string color)
        {
            StatusText.Text = message;
            StatusIndicator.Fill = new SolidColorBrush(GetColorFromName(color));
        }

        private void ShowProgress(bool show)
        {
            ProgressBar.Visibility = show ? Visibility.Visible : Visibility.Collapsed;
            ProgressBar.IsIndeterminate = show;
        }

        private Windows.UI.Color GetColorFromName(string colorName)
        {
            return colorName switch
            {
                "Green" => Microsoft.UI.Colors.Green,
                "Red" => Microsoft.UI.Colors.Red,
                "Yellow" => Microsoft.UI.Colors.Orange,
                _ => Microsoft.UI.Colors.Gray
            };
        }

        private void Cleanup()
        {
            _voiceService?.Dispose();
        }
    }
}
