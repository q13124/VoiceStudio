# Comprehensive Panel Discovery Script
# Finds ALL panels in the workspace, regardless of location

param(
    [string]$WorkspaceRoot = "E:\VoiceStudio",
    [string]$OutputFile = "E:\VoiceStudio\app\core\PanelRegistry.Auto.cs"
)

$separator = "=" * 60
Write-Host $separator -ForegroundColor Cyan
Write-Host "Comprehensive Panel Discovery" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

$allPanels = @()

# Search patterns for panel files
$searchPatterns = @(
    "*View.xaml",
    "*Panel.xaml",
    "*View.cs",
    "*Panel.cs",
    "*ViewModel.cs",
    "*PanelViewModel.cs"
)

# Search directories (comprehensive list)
$searchDirs = @(
    "ui\Views\Panels",
    "ui\Views",
    "ui\Panels",
    "src\VoiceStudio.App\Views\Panels",
    "src\VoiceStudio.App\Views",
    "src\VoiceStudio.App\Panels",
    "app\ui\panels",
    "app\ui\views",
    "Views\Panels",
    "Views",
    "Panels"
)

Write-Host "Searching for panels..." -ForegroundColor Yellow

foreach ($dir in $searchDirs) {
    $fullPath = Join-Path $WorkspaceRoot $dir
    if (Test-Path $fullPath) {
        Write-Host "  Searching: $dir" -ForegroundColor Gray
        
        foreach ($pattern in $searchPatterns) {
            $files = Get-ChildItem -Path $fullPath -Recurse -Filter $pattern -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                # Only process XAML files for panel registry
                if ($file.Extension -eq ".xaml" -and ($file.Name -like "*View*" -or $file.Name -like "*Panel*")) {
                    $relativePath = $file.FullName.Replace($WorkspaceRoot, "").TrimStart("\").Replace("\", "/")
                    
                    # Avoid duplicates
                    if ($allPanels -notcontains $relativePath) {
                        $allPanels += $relativePath
                        Write-Host "    Found: $relativePath" -ForegroundColor Green
                    }
                }
            }
        }
    }
}

# Also search for ViewModels that might indicate panels
Write-Host ""
Write-Host "Searching for ViewModels..." -ForegroundColor Yellow

$vmPatterns = @("*ViewModel.cs", "*PanelViewModel.cs")
foreach ($dir in $searchDirs) {
    $fullPath = Join-Path $WorkspaceRoot $dir
    if (Test-Path $fullPath) {
        foreach ($pattern in $vmPatterns) {
            $files = Get-ChildItem -Path $fullPath -Recurse -Filter $pattern -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                # Try to find corresponding XAML
                $xamlPath = $file.FullName -replace "\.cs$", ".xaml"
                if (Test-Path $xamlPath) {
                    $relativePath = $xamlPath.Replace($WorkspaceRoot, "").TrimStart("\").Replace("\", "/")
                    if ($allPanels -notcontains $relativePath) {
                        $allPanels += $relativePath
                        Write-Host "    Found via ViewModel: $relativePath" -ForegroundColor Green
                    }
                }
            }
        }
    }
}

# Sort panels
$allPanels = $allPanels | Sort-Object

Write-Host ""
$separator = "=" * 60
Write-Host $separator -ForegroundColor Cyan
Write-Host "Found $($allPanels.Count) panels" -ForegroundColor Green
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

# Generate PanelRegistry.Auto.cs
if ($allPanels.Count -gt 0) {
    $panelList = $allPanels | ForEach-Object { 
      "      `"$_`","
    }
    
    $code = @"
using System.Collections.Generic;

namespace VoiceStudio.Core {

  public static class PanelRegistryAuto {

    public static IEnumerable<string> AllXaml() => new [] {
$($panelList -join "`n")
    };

  }

}
"@
    
    $outputDir = Split-Path $OutputFile -Parent
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    }
    
    $code | Set-Content -Path $OutputFile -Encoding UTF8
    Write-Host "Generated: $OutputFile" -ForegroundColor Green
    Write-Host "  Contains $($allPanels.Count) panels" -ForegroundColor Gray
} else {
    Write-Host "No panels found! Check search directories." -ForegroundColor Red
}

# Also generate a text list for reference
$textList = $allPanels -join "`n"
$textFile = $OutputFile -replace "\.cs$", ".txt"
$textList | Set-Content -Path $textFile -Encoding UTF8
Write-Host "Panel list saved to: $textFile" -ForegroundColor Gray

Write-Host ""
Write-Host "Discovery complete!" -ForegroundColor Cyan

