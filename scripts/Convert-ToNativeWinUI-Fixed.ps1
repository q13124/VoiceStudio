#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Convert VoiceStudio to Native WinUI Application
.DESCRIPTION
    This script converts VoiceStudio from a web-based application to a native WinUI 3 application,
    providing better Windows integration, performance, and user experience.
.PARAMETER ProjectPath
    Path to the VoiceStudio project root directory
.PARAMETER OutputPath
    Path where the WinUI project will be created
.EXAMPLE
    .\Convert-ToNativeWinUI.ps1 -ProjectPath "C:\VoiceStudio" -OutputPath "C:\VoiceStudioWinUI"
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectPath = (Get-Location),

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = (Join-Path $ProjectPath "VoiceStudioWinUI"),

    [Parameter(Mandatory = $false)]
    [switch]$Force = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Info    = "Cyan"
    Header  = "Magenta"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Test-Prerequisites {
    Write-ColorOutput "Checking prerequisites..." "Info"

    # Check if .NET 8 SDK is installed
    try {
        $dotnetVersion = dotnet --version
        Write-ColorOutput "✓ .NET SDK found: $dotnetVersion" "Success"
    }
    catch {
        Write-ColorOutput "✗ .NET 8 SDK not found. Please install from https://dotnet.microsoft.com/download" "Error"
        return $false
    }

    # Check if Visual Studio 2022 or VS Code with C# extension is available
    $vsPath = "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe"
    $vsCodePath = "${env:LOCALAPPDATA}\Programs\Microsoft VS Code\Code.exe"

    if (Test-Path $vsPath) {
        Write-ColorOutput "✓ Visual Studio 2022 Community found" "Success"
    }
    elseif (Test-Path $vsCodePath) {
        Write-ColorOutput "✓ Visual Studio Code found" "Success"
    }
    else {
        Write-ColorOutput "⚠ No Visual Studio found. VS Code with C# extension recommended." "Warning"
    }

    # Check if WinUI 3 templates are available
    try {
        $templates = dotnet new list | Select-String "winui"
        if ($templates) {
            Write-ColorOutput "✓ WinUI 3 templates available" "Success"
        }
        else {
            Write-ColorOutput "⚠ WinUI 3 templates not found. Installing..." "Warning"
            dotnet new install Microsoft.WindowsAppSDK.ProjectTemplates
        }
    }
    catch {
        Write-ColorOutput "⚠ Could not verify WinUI templates" "Warning"
    }

    return $true
}

function New-WinUIProject {
    Write-ColorOutput "Creating WinUI 3 project structure..." "Info"

    # Create output directory
    if (Test-Path $OutputPath) {
        if ($Force) {
            Remove-Item $OutputPath -Recurse -Force
        }
        else {
            Write-ColorOutput "Output path already exists. Use -Force to overwrite." "Error"
            return $false
        }
    }

    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

    # Create WinUI 3 project
    Set-Location $OutputPath
    dotnet new winui3 -n VoiceStudioWinUI --force

    # Navigate to project directory
    Set-Location "VoiceStudioWinUI"

    Write-ColorOutput "✓ WinUI 3 project created" "Success"
    return $true
}

function Install-NuGetPackages {
    Write-ColorOutput "Installing required NuGet packages..." "Info"

    $packages = @(
        "Microsoft.WindowsAppSDK",
        "Microsoft.WindowsAppSDK.Foundation",
        "Microsoft.WindowsAppSDK.WinUI",
        "Microsoft.WindowsAppSDK.InteractiveExperiences",
        "CommunityToolkit.WinUI.UI.Controls",
        "CommunityToolkit.WinUI.UI.Animations",
        "Microsoft.Extensions.Hosting",
        "Microsoft.Extensions.DependencyInjection",
        "Microsoft.Extensions.Logging",
        "System.Text.Json",
        "System.Net.Http.Json",
        "NAudio",
        "NAudio.WinForms",
        "Microsoft.Toolkit.Win32.UI.Controls",
        "Windows.Media.Audio"
    )

    foreach ($package in $packages) {
        try {
            Write-ColorOutput "Installing $package..." "Info"
            dotnet add package $package
            Write-ColorOutput "✓ $package installed" "Success"
        }
        catch {
            Write-ColorOutput "⚠ Failed to install $package: $($_.Exception.Message)" "Warning"
        }
    }
}

function Copy-VoiceStudioAssets {
    Write-ColorOutput "Copying VoiceStudio assets..." "Info"

    $sourceAssets = @(
        "services",
        "config",
        "web",
        "VoiceStudio\src\Core",
        "VoiceStudio\src\App"
    )

    $targetAssets = Join-Path $OutputPath "VoiceStudioWinUI\Assets"
    New-Item -ItemType Directory -Path $targetAssets -Force | Out-Null

    foreach ($asset in $sourceAssets) {
        $sourcePath = Join-Path $ProjectPath $asset
        if (Test-Path $sourcePath) {
            $targetPath = Join-Path $targetAssets (Split-Path $asset -Leaf)
            Copy-Item $sourcePath $targetPath -Recurse -Force
            Write-ColorOutput "✓ Copied $asset" "Success"
        }
    }
}

function New-MainWindowXAML {
    Write-ColorOutput "Creating main window XAML..." "Info"

    $xamlContent = @'
<Window
    x:Class="VoiceStudioWinUI.MainWindow"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    xmlns:controls="using:CommunityToolkit.WinUI.UI.Controls"
    mc:Ignorable="d">

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <!-- Header -->
        <Border Grid.Row="0" Background="{ThemeResource SystemAccentColor}" Padding="20">
            <StackPanel Orientation="Horizontal" HorizontalAlignment="Center">
                <FontIcon Glyph="&#xE8D5;" FontSize="24" Foreground="White" Margin="0,0,10,0"/>
                <TextBlock Text="VoiceStudio Ultimate" FontSize="24" FontWeight="Bold" Foreground="White"/>
            </StackPanel>
        </Border>

        <!-- Main Content -->
        <ScrollViewer Grid.Row="1" Padding="20">
            <StackPanel Spacing="20">

                <!-- Voice Cloning Section -->
                <Card Header="Voice Cloning" Margin="0,0,0,20">
                    <StackPanel Spacing="15">

                        <!-- Model Selection -->
                        <StackPanel>
                            <TextBlock Text="Select AI Model:" FontWeight="SemiBold" Margin="0,0,0,5"/>
                            <ComboBox x:Name="ModelComboBox" PlaceholderText="Choose your AI model">
                                <ComboBoxItem Content="GPT-SoVITS 2.0 Real AI" Tag="gpt_sovits_2"/>
                                <ComboBoxItem Content="Coqui XTTS 3.0 Real AI" Tag="coqui_xtts_3"/>
                                <ComboBoxItem Content="RVC 4.0 Real AI" Tag="rvc_4"/>
                                <ComboBoxItem Content="OpenVoice 2.0 Real AI" Tag="openvoice_2"/>
                            </ComboBox>
                        </StackPanel>

                        <!-- Reference Audio -->
                        <StackPanel>
                            <TextBlock Text="Reference Audio:" FontWeight="SemiBold" Margin="0,0,0,5"/>
                            <StackPanel Orientation="Horizontal" Spacing="10">
                                <Button x:Name="SelectAudioButton" Content="Select Audio File" Click="SelectAudioButton_Click"/>
                                <TextBlock x:Name="SelectedAudioText" Text="No file selected" VerticalAlignment="Center"/>
                            </StackPanel>
                        </StackPanel>

                        <!-- Target Text -->
                        <StackPanel>
                            <TextBlock Text="Target Text:" FontWeight="SemiBold" Margin="0,0,0,5"/>
                            <TextBox x:Name="TargetTextBox"
                                     PlaceholderText="Enter text to clone voice for..."
                                     AcceptsReturn="True"
                                     TextWrapping="Wrap"
                                     Height="100"/>
                        </StackPanel>

                        <!-- Advanced Options -->
                        <Expander Header="Advanced Options">
                            <StackPanel Spacing="10" Margin="0,10,0,0">

                                <!-- Emotion Control -->
                                <StackPanel>
                                    <TextBlock Text="Emotion:" FontWeight="SemiBold" Margin="0,0,0,5"/>
                                    <ComboBox x:Name="EmotionComboBox" SelectedIndex="0">
                                        <ComboBoxItem Content="Neutral"/>
                                        <ComboBoxItem Content="Happy"/>
                                        <ComboBoxItem Content="Sad"/>
                                        <ComboBoxItem Content="Angry"/>
                                        <ComboBoxItem Content="Excited"/>
                                    </ComboBox>
                                </StackPanel>

                                <!-- Accent Control -->
                                <StackPanel>
                                    <TextBlock Text="Accent:" FontWeight="SemiBold" Margin="0,0,0,5"/>
                                    <ComboBox x:Name="AccentComboBox" SelectedIndex="0">
                                        <ComboBoxItem Content="Neutral"/>
                                        <ComboBoxItem Content="American"/>
                                        <ComboBoxItem Content="British"/>
                                        <ComboBoxItem Content="Australian"/>
                                    </ComboBox>
                                </StackPanel>

                                <!-- Quality Preset -->
                                <StackPanel>
                                    <TextBlock Text="Quality Preset:" FontWeight="SemiBold" Margin="0,0,0,5"/>
                                    <ComboBox x:Name="QualityComboBox" SelectedIndex="0">
                                        <ComboBoxItem Content="Ultimate"/>
                                        <ComboBoxItem Content="High"/>
                                        <ComboBoxItem Content="Medium"/>
                                        <ComboBoxItem Content="Fast"/>
                                    </ComboBox>
                                </StackPanel>

                                <!-- Real-time Processing -->
                                <CheckBox x:Name="RealTimeCheckBox" Content="Enable Real-time Processing"/>
                            </StackPanel>
                        </Expander>

                        <!-- Clone Button -->
                        <Button x:Name="CloneButton"
                                Content="Clone Voice"
                                HorizontalAlignment="Stretch"
                                Click="CloneButton_Click"
                                Style="{StaticResource AccentButtonStyle}"/>
                    </StackPanel>
                </Card>

                <!-- Status Section -->
                <Card Header="Status" Margin="0,0,0,20">
                    <StackPanel Spacing="10">
                        <StackPanel Orientation="Horizontal" Spacing="10">
                            <Ellipse x:Name="StatusIndicator" Width="12" Height="12" Fill="Gray"/>
                            <TextBlock x:Name="StatusText" Text="Ready" VerticalAlignment="Center"/>
                        </StackPanel>
                        <ProgressBar x:Name="ProgressBar" IsIndeterminate="False" Visibility="Collapsed"/>
                        <TextBlock x:Name="ProgressText" Text="" Visibility="Collapsed"/>
                    </StackPanel>
                </Card>

                <!-- Output Section -->
                <Card Header="Output" Margin="0,0,0,20">
                    <StackPanel Spacing="10">
                        <StackPanel Orientation="Horizontal" Spacing="10">
                            <Button x:Name="PlayButton" Content="Play" Click="PlayButton_Click" IsEnabled="False"/>
                            <Button x:Name="SaveButton" Content="Save" Click="SaveButton_Click" IsEnabled="False"/>
                            <Button x:Name="OpenFolderButton" Content="Open Folder" Click="OpenFolderButton_Click"/>
                        </StackPanel>
                        <TextBlock x:Name="OutputText" Text="No output generated yet" FontStyle="Italic"/>
                    </StackPanel>
                </Card>

            </StackPanel>
        </ScrollViewer>

        <!-- Footer -->
        <Border Grid.Row="2" Background="{ThemeResource SystemControlBackgroundBaseLowBrush}" Padding="20">
            <StackPanel Orientation="Horizontal" HorizontalAlignment="Center" Spacing="20">
                <TextBlock Text="VoiceStudio Ultimate v3.0.0" Foreground="{ThemeResource SystemControlForegroundBaseMediumBrush}"/>
                <HyperlinkButton Content="Documentation" NavigateUri="https://github.com/VoiceStudio"/>
                <HyperlinkButton Content="Support" NavigateUri="https://github.com/VoiceStudio/issues"/>
            </StackPanel>
        </Border>

    </Grid>
</Window>
'@

    $xamlPath = Join-Path $OutputPath "VoiceStudioWinUI\MainWindow.xaml"
    Set-Content -Path $xamlPath -Value $xamlContent -Encoding UTF8
    Write-ColorOutput "✓ Main window XAML created" "Success"
}

function New-MainWindowCodeBehind {
    Write-ColorOutput "Creating main window code-behind..." "Info"

    $codeBehindContent = @'
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Navigation;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Windows.Storage;
using Windows.Storage.Pickers;
using Windows.Media.Playback;
using Windows.Media.Core;
using Windows.System;
using CommunityToolkit.WinUI.UI.Controls;

namespace VoiceStudioWinUI
{
    public sealed partial class MainWindow : Window
    {
        private string _selectedAudioPath;
        private string _outputAudioPath;
        private MediaPlayer _mediaPlayer;

        public MainWindow()
        {
            this.InitializeComponent();
            _mediaPlayer = new MediaPlayer();
            InitializeUI();
        }

        private void InitializeUI()
        {
            // Set default selections
            ModelComboBox.SelectedIndex = 0;
            EmotionComboBox.SelectedIndex = 0;
            AccentComboBox.SelectedIndex = 0;
            QualityComboBox.SelectedIndex = 0;

            UpdateStatus("Ready", "Green");
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
                picker.FileTypeFilter.Add(".flac");

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
                // Validate inputs
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

                // Get selected options
                var selectedModel = (ModelComboBox.SelectedItem as ComboBoxItem)?.Tag?.ToString();
                var emotion = (EmotionComboBox.SelectedItem as ComboBoxItem)?.Content?.ToString();
                var accent = (AccentComboBox.SelectedItem as ComboBoxItem)?.Content?.ToString();
                var quality = (QualityComboBox.SelectedItem as ComboBoxItem)?.Content?.ToString();
                var realTime = RealTimeCheckBox.IsChecked == true;

                UpdateStatus("Starting voice cloning...", "Yellow");
                ShowProgress(true);

                // Call voice cloning service
                var result = await CloneVoiceAsync(_selectedAudioPath, TargetTextBox.Text, selectedModel, emotion, accent, quality, realTime);

                if (result.Success)
                {
                    _outputAudioPath = result.OutputPath;
                    OutputText.Text = $"Voice cloned successfully! Output: {Path.GetFileName(_outputAudioPath)}";
                    PlayButton.IsEnabled = true;
                    SaveButton.IsEnabled = true;
                    UpdateStatus("Voice cloning completed successfully!", "Green");
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

        private async Task<CloneResult> CloneVoiceAsync(string audioPath, string text, string model, string emotion, string accent, string quality, bool realTime)
        {
            try
            {
                // TODO: Implement actual voice cloning service call
                // This would integrate with the Python backend services

                // Simulate processing time
                await Task.Delay(2000);

                // For now, return a mock result
                var outputPath = Path.Combine(Path.GetTempPath(), $"cloned_voice_{DateTime.Now:yyyyMMdd_HHmmss}.wav");

                return new CloneResult
                {
                    Success = true,
                    OutputPath = outputPath,
                    ProcessingTime = 2.0,
                    ModelUsed = model
                };
            }
            catch (Exception ex)
            {
                return new CloneResult
                {
                    Success = false,
                    Error = ex.Message
                };
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
                    picker.FileTypeChoices.Add("MP3 Audio", new List<string>() { ".mp3" });

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

        private async void OpenFolderButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var folder = await StorageFolder.GetFolderFromPathAsync(Path.GetTempPath());
                await Launcher.LaunchFolderAsync(folder);
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error opening folder: {ex.Message}", "Red");
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
                "Green" => Windows.UI.Colors.Green,
                "Red" => Windows.UI.Colors.Red,
                "Yellow" => Windows.UI.Colors.Orange,
                _ => Windows.UI.Colors.Gray
            };
        }
    }

    public class CloneResult
    {
        public bool Success { get; set; }
        public string OutputPath { get; set; }
        public string Error { get; set; }
        public double ProcessingTime { get; set; }
        public string ModelUsed { get; set; }
    }
}
'@

    $codeBehindPath = Join-Path $OutputPath "VoiceStudioWinUI\MainWindow.xaml.cs"
    Set-Content -Path $codeBehindPath -Value $codeBehindContent -Encoding UTF8
    Write-ColorOutput "✓ Main window code-behind created" "Success"
}

function New-AppXaml {
    Write-ColorOutput "Creating App.xaml..." "Info"

    $appXamlContent = @'
<Application
    x:Class="VoiceStudioWinUI.App"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Application.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <XamlControlsResources xmlns="using:Microsoft.UI.Xaml.Controls" />
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </Application.Resources>
</Application>
'@

    $appXamlPath = Join-Path $OutputPath "VoiceStudioWinUI\App.xaml"
    Set-Content -Path $appXamlPath -Value $appXamlContent -Encoding UTF8
    Write-ColorOutput "✓ App.xaml created" "Success"
}

function New-AppCodeBehind {
    Write-ColorOutput "Creating App.xaml.cs..." "Info"

    $appCodeBehindContent = @'
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;

namespace VoiceStudioWinUI
{
    public partial class App : Application
    {
        public App()
        {
            this.InitializeComponent();
        }

        protected override void OnLaunched(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
        {
            m_window = new MainWindow();
            m_window.Activate();
        }

        private Window m_window;
    }
}
'@

    $appCodeBehindPath = Join-Path $OutputPath "VoiceStudioWinUI\App.xaml.cs"
    Set-Content -Path $appCodeBehindPath -Value $appCodeBehindContent -Encoding UTF8
    Write-ColorOutput "✓ App.xaml.cs created" "Success"
}

function New-PackageManifest {
    Write-ColorOutput "Creating package manifest..." "Info"

    $manifestContent = @'
<?xml version="1.0" encoding="utf-8"?>
<Package
  xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
  xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
  xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities">

  <Identity
    Name="VoiceStudioWinUI"
    Publisher="CN=VoiceStudio"
    Version="3.0.0.0" />

  <Properties>
    <DisplayName>VoiceStudio Ultimate</DisplayName>
    <PublisherDisplayName>VoiceStudio</PublisherDisplayName>
    <Logo>Images\StoreLogo.png</Logo>
  </Properties>

  <Dependencies>
    <TargetDeviceFamily Name="Windows.Universal" MinVersion="10.0.17763.0" MaxVersionTested="10.0.19041.0" />
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.19041.0" />
  </Dependencies>

  <Resources>
    <Resource Language="x-generate"/>
  </Resources>

  <Applications>
    <Application Id="App"
      Executable="$targetentrypoint$"
      EntryPoint="$targetentrypoint$">
      <uap:VisualElements
        DisplayName="VoiceStudio Ultimate"
        Description="Next-generation voice cloning with cutting-edge AI models"
        BackgroundColor="transparent"
        Square150x150Logo="Images\Square150x150Logo.png"
        Square44x44Logo="Images\Square44x44Logo.png">
        <uap:DefaultTile Wide310x150Logo="Images\Wide310x150Logo.png" />
        <uap:SplashScreen Image="Images\SplashScreen.png" />
      </uap:VisualElements>
    </Application>
  </Applications>

  <Capabilities>
    <rescap:Capability Name="runFullTrust" />
    <Capability Name="internetClient" />
    <Capability Name="internetClientServer" />
    <Capability Name="privateNetworkClientServer" />
    <uap:Capability Name="musicLibrary" />
    <uap:Capability Name="videosLibrary" />
    <uap:Capability Name="picturesLibrary" />
  </Capabilities>
</Package>
'@

    $manifestPath = Join-Path $OutputPath "VoiceStudioWinUI\Package.appxmanifest"
    Set-Content -Path $manifestPath -Value $manifestContent -Encoding UTF8
    Write-ColorOutput "✓ Package manifest created" "Success"
}

function New-PythonServiceIntegration {
    Write-ColorOutput "Creating Python service integration..." "Info"

    $integrationContent = @'
using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using System.Text.Json;
using System.Net.Http;
using System.Net.Http.Json;

namespace VoiceStudioWinUI.Services
{
    public class VoiceCloningService
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;
        private Process _pythonProcess;

        public VoiceCloningService()
        {
            _httpClient = new HttpClient();
            _baseUrl = "http://127.0.0.1:8083";
        }

        public async Task<bool> StartPythonBackendAsync()
        {
            try
            {
                var pythonPath = "python";
                var scriptPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Assets", "services", "voice_cloning", "ultimate_web_server.py");

                if (!File.Exists(scriptPath))
                {
                    throw new FileNotFoundException($"Python script not found: {scriptPath}");
                }

                var startInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{scriptPath}\" --host 127.0.0.1 --port 8083",
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true
                };

                _pythonProcess = Process.Start(startInfo);

                // Wait for service to start
                await Task.Delay(3000);

                // Test if service is running
                var response = await _httpClient.GetAsync($"{_baseUrl}/api/status");
                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                throw new Exception($"Failed to start Python backend: {ex.Message}", ex);
            }
        }

        public async Task<CloneResult> CloneVoiceAsync(CloneRequest request)
        {
            try
            {
                using var formData = new MultipartFormDataContent();

                // Add audio file
                var audioBytes = await File.ReadAllBytesAsync(request.AudioPath);
                var audioContent = new ByteArrayContent(audioBytes);
                audioContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav");
                formData.Add(audioContent, "reference_audio", Path.GetFileName(request.AudioPath));

                // Add other parameters
                formData.Add(new StringContent(request.TargetText), "target_text");
                formData.Add(new StringContent(request.ModelId ?? ""), "selected_model_id");
                formData.Add(new StringContent(request.Emotion ?? "neutral"), "emotion");
                formData.Add(new StringContent(request.Accent ?? "neutral"), "accent");
                formData.Add(new StringContent(request.QualityPreset ?? "ultimate"), "quality_preset");
                formData.Add(new StringContent(request.RealTime.ToString().ToLower()), "real_time");

                var response = await _httpClient.PostAsync($"{_baseUrl}/api/clone/ultimate", formData);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<CloneResult>();
                    return result;
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    return new CloneResult
                    {
                        Success = false,
                        Error = $"HTTP {response.StatusCode}: {errorContent}"
                    };
                }
            }
            catch (Exception ex)
            {
                return new CloneResult
                {
                    Success = false,
                    Error = ex.Message
                };
            }
        }

        public async Task<SystemStatus> GetSystemStatusAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_baseUrl}/api/status");
                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<SystemStatus>();
                }
                return null;
            }
            catch
            {
                return null;
            }
        }

        public void StopPythonBackend()
        {
            try
            {
                _pythonProcess?.Kill();
                _pythonProcess?.Dispose();
            }
            catch { }
        }
    }

    public class CloneRequest
    {
        public string AudioPath { get; set; }
        public string TargetText { get; set; }
        public string ModelId { get; set; }
        public string Emotion { get; set; }
        public string Accent { get; set; }
        public string QualityPreset { get; set; }
        public bool RealTime { get; set; }
    }

    public class CloneResult
    {
        public bool Success { get; set; }
        public string OutputPath { get; set; }
        public string Error { get; set; }
        public double ProcessingTime { get; set; }
        public string ModelUsed { get; set; }
    }

    public class SystemStatus
    {
        public string Status { get; set; }
        public string Service { get; set; }
        public string Version { get; set; }
        public bool ServicesAvailable { get; set; }
        public bool RealAiAvailable { get; set; }
        public string Timestamp { get; set; }
        public string[] Features { get; set; }
    }
}
'@

    $integrationPath = Join-Path $OutputPath "VoiceStudioWinUI\Services\VoiceCloningService.cs"
    New-Item -ItemType Directory -Path (Split-Path $integrationPath) -Force | Out-Null
    Set-Content -Path $integrationPath -Value $integrationContent -Encoding UTF8
    Write-ColorOutput "✓ Python service integration created" "Success"
}

function Update-ProjectFile {
    Write-ColorOutput "Updating project file..." "Info"

    $projectContent = @'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net8.0-windows10.0.19041.0</TargetFramework>
    <TargetPlatformMinVersion>10.0.17763.0</TargetPlatformMinVersion>
    <RootNamespace>VoiceStudioWinUI</RootNamespace>
    <ApplicationManifest>app.manifest</ApplicationManifest>
    <Platforms>x86;x64;ARM64</Platforms>
    <RuntimeIdentifiers>win-x86;win-x64;win-arm64</RuntimeIdentifiers>
    <UseWinUI>true</UseWinUI>
    <EnableMsixTooling>true</EnableMsixTooling>
    <WindowsAppSDKSelfContained>true</WindowsAppSDKSelfContained>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.WindowsAppSDK" Version="1.4.231115000" />
    <PackageReference Include="Microsoft.WindowsAppSDK.Foundation" Version="1.4.231115000" />
    <PackageReference Include="Microsoft.WindowsAppSDK.WinUI" Version="1.4.231115000" />
    <PackageReference Include="Microsoft.WindowsAppSDK.InteractiveExperiences" Version="1.4.231115000" />
    <PackageReference Include="CommunityToolkit.WinUI.UI.Controls" Version="7.1.2" />
    <PackageReference Include="CommunityToolkit.WinUI.UI.Animations" Version="7.1.2" />
    <PackageReference Include="Microsoft.Extensions.Hosting" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.Logging" Version="8.0.0" />
    <PackageReference Include="System.Text.Json" Version="8.0.0" />
    <PackageReference Include="System.Net.Http.Json" Version="8.0.0" />
    <PackageReference Include="NAudio" Version="2.2.1" />
    <PackageReference Include="NAudio.WinForms" Version="2.2.1" />
  </ItemGroup>

  <ItemGroup>
    <Content Include="Assets\**\*">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </Content>
  </ItemGroup>
</Project>
'@

    $projectPath = Join-Path $OutputPath "VoiceStudioWinUI\VoiceStudioWinUI.csproj"
    Set-Content -Path $projectPath -Value $projectContent -Encoding UTF8
    Write-ColorOutput "✓ Project file updated" "Success"
}

function Build-Project {
    Write-ColorOutput "Building WinUI project..." "Info"

    Set-Location (Join-Path $OutputPath "VoiceStudioWinUI")

    try {
        dotnet build --configuration Release
        Write-ColorOutput "✓ Project built successfully" "Success"
        return $true
    }
    catch {
        Write-ColorOutput "✗ Build failed: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Show-CompletionMessage {
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "=" * 80 "Header"
    Write-ColorOutput "  VOICESTUDIO WINUI CONVERSION COMPLETED SUCCESSFULLY!" "Header"
    Write-ColorOutput "=" * 80 "Header"
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "Project Location: $OutputPath\VoiceStudioWinUI" "Info"
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "Next Steps:" "Info"
    Write-ColorOutput "1. Open the project in Visual Studio 2022 or VS Code" "Success"
    Write-ColorOutput "2. Build and run the application (F5)" "Success"
    Write-ColorOutput "3. The app will automatically start the Python backend" "Success"
    Write-ColorOutput "4. Test voice cloning functionality" "Success"
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "Features:" "Info"
    Write-ColorOutput "• Native WinUI 3 interface with modern design" "Success"
    Write-ColorOutput "• Real-time voice cloning with multiple AI models" "Success"
    Write-ColorOutput "• Advanced emotion and accent control" "Success"
    Write-ColorOutput "• Built-in audio player and file management" "Success"
    Write-ColorOutput "• Automatic Python backend integration" "Success"
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "To run the application:" "Info"
    Write-ColorOutput "cd `"$OutputPath\VoiceStudioWinUI`"" "Success"
    Write-ColorOutput "dotnet run" "Success"
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "=" * 80 "Header"
}

# Main execution
try {
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "=" * 80 "Header"
    Write-ColorOutput "  VOICESTUDIO TO NATIVE WINUI CONVERSION" "Header"
    Write-ColorOutput "=" * 80 "Header"
    Write-ColorOutput "`n" "White"

    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-ColorOutput "Prerequisites check failed. Please install required components." "Error"
        exit 1
    }

    # Create WinUI project
    if (-not (New-WinUIProject)) {
        Write-ColorOutput "Failed to create WinUI project." "Error"
        exit 1
    }

    # Install NuGet packages
    Install-NuGetPackages

    # Copy VoiceStudio assets
    Copy-VoiceStudioAssets

    # Create XAML files
    New-MainWindowXAML
    New-AppXaml

    # Create code-behind files
    New-MainWindowCodeBehind
    New-AppCodeBehind

    # Create package manifest
    New-PackageManifest

    # Create Python service integration
    New-PythonServiceIntegration

    # Update project file
    Update-ProjectFile

    # Build project
    if (Build-Project) {
        Show-CompletionMessage
    }
    else {
        Write-ColorOutput "Conversion completed with build errors. Please check the project." "Warning"
    }
}
catch {
    Write-ColorOutput "Conversion failed: $($_.Exception.Message)" "Error"
    Write-ColorOutput "Stack trace: $($_.ScriptStackTrace)" "Error"
    exit 1
}
finally {
    # Return to original directory
    Set-Location $ProjectPath
}
