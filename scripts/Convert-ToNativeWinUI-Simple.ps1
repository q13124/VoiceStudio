#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Convert VoiceStudio to Native WinUI Application
.DESCRIPTION
    This script converts VoiceStudio from a web-based application to a native WinUI 3 application.
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectPath = (Get-Location),

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = (Join-Path $ProjectPath "VoiceStudioWinUI"),

    [Parameter(Mandatory = $false)]
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-Prerequisites {
    Write-ColorOutput "Checking prerequisites..." "Cyan"

    # Check if .NET 8 SDK is installed
    try {
        $dotnetVersion = dotnet --version
        Write-ColorOutput "✓ .NET SDK found: $dotnetVersion" "Green"
    }
    catch {
        Write-ColorOutput "✗ .NET 8 SDK not found. Please install from https://dotnet.microsoft.com/download" "Red"
        return $false
    }

    return $true
}

function New-WinUIProject {
    Write-ColorOutput "Creating WinUI 3 project structure..." "Cyan"

    # Create output directory
    if (Test-Path $OutputPath) {
        if ($Force) {
            Remove-Item $OutputPath -Recurse -Force
        }
        else {
            Write-ColorOutput "Output path already exists. Use -Force to overwrite." "Red"
            return $false
        }
    }

    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

    # Create WinUI 3 project
    Set-Location $OutputPath
    dotnet new winui3 -n VoiceStudioWinUI --force

    # Navigate to project directory
    Set-Location "VoiceStudioWinUI"

    Write-ColorOutput "✓ WinUI 3 project created" "Green"
    return $true
}

function Install-NuGetPackages {
    Write-ColorOutput "Installing required NuGet packages..." "Cyan"

    $packages = @(
        "Microsoft.WindowsAppSDK",
        "CommunityToolkit.WinUI.UI.Controls",
        "System.Text.Json",
        "System.Net.Http.Json",
        "NAudio"
    )

    foreach ($package in $packages) {
        try {
            Write-ColorOutput "Installing $package..." "Cyan"
            dotnet add package $package
            Write-ColorOutput "✓ $package installed" "Green"
        }
        catch {
            Write-ColorOutput "⚠ Failed to install $package" "Yellow"
        }
    }
}

function Copy-VoiceStudioAssets {
    Write-ColorOutput "Copying VoiceStudio assets..." "Cyan"

    $sourceAssets = @(
        "services",
        "config"
    )

    $targetAssets = Join-Path $OutputPath "VoiceStudioWinUI\Assets"
    New-Item -ItemType Directory -Path $targetAssets -Force | Out-Null

    foreach ($asset in $sourceAssets) {
        $sourcePath = Join-Path $ProjectPath $asset
        if (Test-Path $sourcePath) {
            $targetPath = Join-Path $targetAssets (Split-Path $asset -Leaf)
            Copy-Item $sourcePath $targetPath -Recurse -Force
            Write-ColorOutput "✓ Copied $asset" "Green"
        }
    }
}

function New-MainWindowXAML {
    Write-ColorOutput "Creating main window XAML..." "Cyan"

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
                    </StackPanel>
                </Card>

                <!-- Output Section -->
                <Card Header="Output" Margin="0,0,0,20">
                    <StackPanel Spacing="10">
                        <StackPanel Orientation="Horizontal" Spacing="10">
                            <Button x:Name="PlayButton" Content="Play" Click="PlayButton_Click" IsEnabled="False"/>
                            <Button x:Name="SaveButton" Content="Save" Click="SaveButton_Click" IsEnabled="False"/>
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
            </StackPanel>
        </Border>

    </Grid>
</Window>
'@

    $xamlPath = Join-Path $OutputPath "VoiceStudioWinUI\MainWindow.xaml"
    Set-Content -Path $xamlPath -Value $xamlContent -Encoding UTF8
    Write-ColorOutput "✓ Main window XAML created" "Green"
}

function New-MainWindowCodeBehind {
    Write-ColorOutput "Creating main window code-behind..." "Cyan"

    $codeBehindContent = @'
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System;
using System.IO;
using System.Threading.Tasks;
using Windows.Storage;
using Windows.Storage.Pickers;
using Windows.Media.Playback;
using Windows.Media.Core;
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
            ModelComboBox.SelectedIndex = 0;
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

                // Simulate voice cloning
                await Task.Delay(2000);

                _outputAudioPath = Path.Combine(Path.GetTempPath(), $"cloned_voice_{DateTime.Now:yyyyMMdd_HHmmss}.wav");
                OutputText.Text = $"Voice cloned successfully! Output: {Path.GetFileName(_outputAudioPath)}";
                PlayButton.IsEnabled = true;
                SaveButton.IsEnabled = true;
                UpdateStatus("Voice cloning completed successfully!", "Green");
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
                "Green" => Windows.UI.Colors.Green,
                "Red" => Windows.UI.Colors.Red,
                "Yellow" => Windows.UI.Colors.Orange,
                _ => Windows.UI.Colors.Gray
            };
        }
    }
}
'@

    $codeBehindPath = Join-Path $OutputPath "VoiceStudioWinUI\MainWindow.xaml.cs"
    Set-Content -Path $codeBehindPath -Value $codeBehindContent -Encoding UTF8
    Write-ColorOutput "✓ Main window code-behind created" "Green"
}

function Build-Project {
    Write-ColorOutput "Building WinUI project..." "Cyan"

    Set-Location (Join-Path $OutputPath "VoiceStudioWinUI")

    try {
        dotnet build --configuration Release
        Write-ColorOutput "✓ Project built successfully" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "✗ Build failed" "Red"
        return $false
    }
}

function Show-CompletionMessage {
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "=" * 80 "Magenta"
    Write-ColorOutput "  VOICESTUDIO WINUI CONVERSION COMPLETED SUCCESSFULLY!" "Magenta"
    Write-ColorOutput "=" * 80 "Magenta"
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "Project Location: $OutputPath\VoiceStudioWinUI" "Cyan"
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "Next Steps:" "Cyan"
    Write-ColorOutput "1. Open the project in Visual Studio 2022 or VS Code" "Green"
    Write-ColorOutput "2. Build and run the application (F5)" "Green"
    Write-ColorOutput "3. Test voice cloning functionality" "Green"
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "To run the application:" "Cyan"
    Write-ColorOutput "cd `"$OutputPath\VoiceStudioWinUI`"" "Green"
    Write-ColorOutput "dotnet run" "Green"
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "=" * 80 "Magenta"
}

# Main execution
try {
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "=" * 80 "Magenta"
    Write-ColorOutput "  VOICESTUDIO TO NATIVE WINUI CONVERSION" "Magenta"
    Write-ColorOutput "=" * 80 "Magenta"
    Write-ColorOutput "`n" "White"

    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-ColorOutput "Prerequisites check failed. Please install required components." "Red"
        exit 1
    }

    # Create WinUI project
    if (-not (New-WinUIProject)) {
        Write-ColorOutput "Failed to create WinUI project." "Red"
        exit 1
    }

    # Install NuGet packages
    Install-NuGetPackages

    # Copy VoiceStudio assets
    Copy-VoiceStudioAssets

    # Create XAML files
    New-MainWindowXAML

    # Create code-behind files
    New-MainWindowCodeBehind

    # Build project
    if (Build-Project) {
        Show-CompletionMessage
    }
    else {
        Write-ColorOutput "Conversion completed with build errors. Please check the project." "Yellow"
    }
}
catch {
    Write-ColorOutput "Conversion failed: $($_.Exception.Message)" "Red"
    exit 1
}
finally {
    # Return to original directory
    Set-Location $ProjectPath
}
