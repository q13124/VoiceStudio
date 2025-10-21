using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Navigation;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using System.Net.Http;
using System.Text.Json;
using System.Threading;
using System.Diagnostics;
using Windows.Storage;
using Windows.Storage.Pickers;
using Windows.Media.Playback;
using Windows.Media.Core;
using VoiceStudioWinUI.Services;
using VoiceStudioWinUI.Pages;

namespace VoiceStudioWinUI
{
    public sealed partial class MainWindow : Window
    {
        private string _selectedAudioPath;
        private string _outputAudioPath;
        private MediaPlayer _mediaPlayer;
        private VoiceCloningService _voiceService;
        private HttpClient _httpClient;
        private CancellationTokenSource _cancellationTokenSource;
        private bool _isProcessing = false;

        public MainWindow()
        {
            this.InitializeComponent();
            _mediaPlayer = new MediaPlayer();
            _voiceService = new VoiceCloningService();
            _httpClient = new HttpClient();
            _cancellationTokenSource = new CancellationTokenSource();
            InitializeUI();
            InitializeBackend();
        }

        private void InitializeUI()
        {
            ModelComboBox.SelectedIndex = 0;
            UpdateStatus("Ready", "Green");
        }

        private void InitializeBackend()
        {
            // Initialize backend services
            Task.Run(async () =>
            {
                try
                {
                    await _voiceService.InitializeAsync();
                    DispatcherQueue.TryEnqueue(() => UpdateStatus("Backend initialized", "Green"));
                }
                catch (Exception ex)
                {
                    DispatcherQueue.TryEnqueue(() => UpdateStatus($"Backend error: {ex.Message}", "Red"));
                }
            });
        }

        private void NavigateToPage(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is string pageTag)
            {
                switch (pageTag)
                {
                    case "Dashboard":
                        ContentFrame.Navigate(typeof(DashboardPage));
                        break;
                    case "MasteringRack":
                        ContentFrame.Navigate(typeof(MasteringRackPage));
                        break;
                    case "VoiceCloning":
                        // Navigate back to default content (Voice Cloning)
                        ContentFrame.Navigate(typeof(MainWindow));
                        break;
                    case "RealTime":
                        // TODO: Implement RealTime page
                        UpdateStatus("Real-Time page coming soon", "Yellow");
                        break;
                    case "Settings":
                        // TODO: Implement Settings page
                        UpdateStatus("Settings page coming soon", "Yellow");
                        break;
                }
            }
        }

        private void ContentFrame_NavigationFailed(object sender, NavigationFailedEventArgs e)
        {
            UpdateStatus($"Navigation failed: {e.Exception.Message}", "Red");
        }

        private async void OnGenSbom(object sender, RoutedEventArgs e)
        {
            try
            {
                var root = Directory.GetParent(Directory.GetParent(System.AppContext.BaseDirectory!)!.FullName)!.Parent!.FullName;
                var script = Path.Combine(root, "scripts", "Generate-SBOM.ps1");
                if (!File.Exists(script))
                {
                    var d = new ContentDialog { XamlRoot = this.XamlRoot, Title = "SBOM", Content = "Generate-SBOM.ps1 not found.", PrimaryButtonText = "OK" };
                    await d.ShowAsync();
                    return;
                }
                var psi = new ProcessStartInfo("powershell.exe", $"-ExecutionPolicy Bypass -File \"{script}\"") { UseShellExecute = true, Verb = "runas" };
                Process.Start(psi);
                UpdateStatus("SBOM generation started", "Green");
            }
            catch (Exception ex)
            {
                UpdateStatus($"SBOM generation failed: {ex.Message}", "Red");
            }
        }

        private async void OnOpenSbomFolder(object sender, RoutedEventArgs e)
        {
            try
            {
                var dir = Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.CommonApplicationData), "VoiceStudio", "artifacts", "sbom");
                Directory.CreateDirectory(dir);
                Process.Start("explorer.exe", dir);
                UpdateStatus($"Opened SBOM folder: {dir}", "Green");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Failed to open SBOM folder: {ex.Message}", "Red");
            }
        }

        private void UpdateStatus(string message, string color)
        {
            StatusText.Text = message;
            StatusIndicator.Fill = new SolidColorBrush(GetColorFromString(color));
        }

        private Windows.UI.Color GetColorFromString(string color)
        {
            return color switch
            {
                "Green" => Windows.UI.Colors.LimeGreen,
                "Yellow" => Windows.UI.Colors.Yellow,
                "Red" => Windows.UI.Colors.Red,
                _ => Windows.UI.Colors.Gray
            };
        }

        // Voice Cloning Event Handlers
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
                    SelectedAudioText.Text = file.Name;
                    PreviewAudioButton.IsEnabled = true;
                    UpdateStatus($"Selected audio: {file.Name}", "Green");
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error selecting audio: {ex.Message}", "Red");
            }
        }

        private async void PreviewAudioButton_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(_selectedAudioPath))
            {
                try
                {
                    var file = await StorageFile.GetFileFromPathAsync(_selectedAudioPath);
                    _mediaPlayer.Source = MediaSource.CreateFromStorageFile(file);
                    _mediaPlayer.Play();
                    UpdateStatus("Playing preview...", "Yellow");
                }
                catch (Exception ex)
                {
                    UpdateStatus($"Error playing preview: {ex.Message}", "Red");
                }
            }
        }

        private void TargetTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            TextAnalysisButton.IsEnabled = !string.IsNullOrEmpty(TargetTextBox.Text);
        }

        private async void TextAnalysisButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var text = TargetTextBox.Text;
                // TODO: Implement text analysis
                TextAnalysisResult.Text = $"Analysis: {text.Length} characters, estimated duration: {text.Length * 0.1:F1}s";
                UpdateStatus("Text analyzed", "Green");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Text analysis failed: {ex.Message}", "Red");
            }
        }

        private async void CloneButton_Click(object sender, RoutedEventArgs e)
        {
            if (_isProcessing) return;

            try
            {
                _isProcessing = true;
                CloneButton.IsEnabled = false;
                CancelButton.IsEnabled = true;
                ProgressBar.Visibility = Visibility.Visible;
                ProgressBar.IsIndeterminate = true;

                UpdateStatus("Starting voice cloning...", "Yellow");

                // TODO: Implement actual voice cloning
                await Task.Delay(2000); // Simulate processing

                _outputAudioPath = "output.wav";
                PlayButton.IsEnabled = true;
                SaveButton.IsEnabled = true;
                OutputText.Text = $"Voice cloned successfully: {_outputAudioPath}";
                UpdateStatus("Voice cloning completed", "Green");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Voice cloning failed: {ex.Message}", "Red");
            }
            finally
            {
                _isProcessing = false;
                CloneButton.IsEnabled = true;
                CancelButton.IsEnabled = false;
                ProgressBar.Visibility = Visibility.Collapsed;
            }
        }

        private async void BatchCloneButton_Click(object sender, RoutedEventArgs e)
        {
            UpdateStatus("Batch cloning feature coming soon", "Yellow");
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            _cancellationTokenSource.Cancel();
            _isProcessing = false;
            CloneButton.IsEnabled = true;
            CancelButton.IsEnabled = false;
            ProgressBar.Visibility = Visibility.Collapsed;
            UpdateStatus("Operation cancelled", "Yellow");
        }

        private async void PlayButton_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(_outputAudioPath))
            {
                try
                {
                    var file = await StorageFile.GetFileFromPathAsync(_outputAudioPath);
                    _mediaPlayer.Source = MediaSource.CreateFromStorageFile(file);
                    _mediaPlayer.Play();
                    UpdateStatus("Playing output...", "Yellow");
                }
                catch (Exception ex)
                {
                    UpdateStatus($"Error playing output: {ex.Message}", "Red");
                }
            }
        }

        private async void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(_outputAudioPath))
            {
                try
                {
                    var picker = new FileSavePicker();
                    picker.SuggestedStartLocation = PickerLocationId.MusicLibrary;
                    picker.FileTypeChoices.Add("Audio files", new List<string> { ".wav", ".mp3" });
                    picker.SuggestedFileName = "cloned_voice";

                    var file = await picker.PickSaveFileAsync();
                    if (file != null)
                    {
                        var sourceFile = await StorageFile.GetFileFromPathAsync(_outputAudioPath);
                        await sourceFile.CopyAndReplaceAsync(file);
                        UpdateStatus($"Saved to: {file.Name}", "Green");
                    }
                }
                catch (Exception ex)
                {
                    UpdateStatus($"Error saving file: {ex.Message}", "Red");
                }
            }
        }
    }
}
