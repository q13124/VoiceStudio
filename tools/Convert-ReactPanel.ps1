# Convert React Panel to WinUI 3 XAML
# Generates XAML, ViewModel, and code-behind from React component

param(
    [Parameter(Mandatory = $true)]
    [string]$SourceFile,
    
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,
    
    [Parameter(Mandatory = $true)]
    [string]$PanelName,
    
    [string]$Namespace = "VoiceStudio.App",
    [string]$Region = "Left",
    [string]$Tier = "Core"
)

$ErrorActionPreference = "Stop"

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "React to WinUI 3 Panel Converter" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

if (-not (Test-Path $SourceFile)) {
    throw "Source file not found: $SourceFile"
}

Write-Host "Source: $SourceFile" -ForegroundColor Yellow
Write-Host "Output: $OutputDir" -ForegroundColor Yellow
Write-Host "Panel: $PanelName" -ForegroundColor Yellow
Write-Host ""

# Read React component
$reactContent = Get-Content $SourceFile -Raw

# Create output directory
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# Generate ViewModel
$viewModelName = "${PanelName}ViewModel"
$viewModelFile = Join-Path $OutputDir "$viewModelName.cs"

$viewModelCode = @"
using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;

namespace $Namespace.ViewModels;

public partial class $viewModelName : ObservableObject
{
    // Note: Add properties based on React component state
    // Example:
    // [ObservableProperty]
    // private ObservableCollection<Item> items = new();
    
    public $viewModelName()
    {
        // TODO: Initialize from React useEffect hooks
    }
}
"@

$viewModelCode | Set-Content -Path $viewModelFile -Encoding UTF8
Write-Host "Generated: $viewModelName.cs" -ForegroundColor Green

# Generate XAML View
$viewName = "${PanelName}View"
$viewFile = Join-Path $OutputDir "$viewName.xaml"

$xamlCode = @"
<UserControl x:Class="$Namespace.Views.Panels.$viewName"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:vm="using:$Namespace.ViewModels">
    <UserControl.DataContext>
        <vm:$viewModelName />
    </UserControl.DataContext>
    
    <Grid>
        <!-- Note: Convert React JSX structure to XAML -->
        <!-- Example React div -> Grid or StackPanel -->
        <!-- Example React button -> Button -->
        <!-- Example React input -> TextBox or NumberBox -->
        
        <TextBlock Text="$PanelName" 
                   Style="{StaticResource VSQ.Text.Heading}"
                   Margin="8"/>
    </Grid>
</UserControl>
"@

$xamlCode | Set-Content -Path $viewFile -Encoding UTF8
Write-Host "Generated: $viewName.xaml" -ForegroundColor Green

# Generate Code-Behind
$codeBehindFile = Join-Path $OutputDir "$viewName.xaml.cs"

$codeBehindCode = @"
using Microsoft.UI.Xaml.Controls;
using $Namespace.ViewModels;

namespace $Namespace.Views.Panels;

public sealed partial class $viewName : UserControl
{
    public $viewModelName ViewModel { get; }

    public $viewName()
    {
        InitializeComponent();
        ViewModel = new $viewModelName();
        DataContext = ViewModel;
    }
}
"@

$codeBehindCode | Set-Content -Path $codeBehindFile -Encoding UTF8
Write-Host "Generated: $viewName.xaml.cs" -ForegroundColor Green

# Generate registration snippet
$registrationSnippet = @"
// Add to PanelRegistry.cs:
new PanelDescriptor
{
    PanelId = "$($PanelName.ToLower())",
    DisplayName = "$PanelName",
    Region = PanelRegion.$Region,
    Tier = PanelTier.$Tier,
    ViewType = typeof($viewName),
    ViewModelType = typeof($viewModelName)
}
"@

$snippetFile = Join-Path $OutputDir "${PanelName}_Registration.txt"
$registrationSnippet | Set-Content -Path $snippetFile -Encoding UTF8
Write-Host "Generated: ${PanelName}_Registration.txt" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Conversion complete!" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review generated files and complete TODO items" -ForegroundColor Gray
Write-Host "2. Convert React JSX to XAML structure" -ForegroundColor Gray
Write-Host "3. Map React state to ViewModel properties" -ForegroundColor Gray
Write-Host "4. Convert CSS styles to XAML styles" -ForegroundColor Gray
Write-Host "5. Register panel in PanelRegistry.cs" -ForegroundColor Gray
Write-Host "6. Run panel discovery: .\tools\Find-AllPanels.ps1" -ForegroundColor Gray
Write-Host ""

