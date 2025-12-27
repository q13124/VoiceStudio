# Panel Discovery Script
# Scans C:\VoiceStudio for all panel files and generates catalog

param(
    [string]$SourcePath = "C:\VoiceStudio",
    [string]$OutputPath = "E:\VoiceStudio\docs\governance\PANEL_CATALOG.json"
)

Write-Host "Discovering panels in $SourcePath..." -ForegroundColor Cyan

$panels = @()

# Search for panel files
$patterns = @(
    "*panel*.py",
    "*Panel*.py",
    "*view*.py",
    "*View*.py",
    "*panel*.xaml",
    "*Panel*.xaml"
)

$directories = @(
    "ui",
    "app\ui",
    "src",
    "panels",
    "views"
)

foreach ($dir in $directories) {
    $searchPath = Join-Path $SourcePath $dir
    if (Test-Path $searchPath) {
        Write-Host "Searching in: $searchPath" -ForegroundColor Yellow
        
        foreach ($pattern in $patterns) {
            $files = Get-ChildItem -Path $searchPath -Recurse -Filter $pattern -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                $relativePath = $file.FullName.Replace($SourcePath, "").TrimStart("\")
                $name = $file.BaseName
                
                # Determine panel type
                $type = "Unknown"
                if ($file.Extension -eq ".py") {
                    $type = "Python"
                } elseif ($file.Extension -eq ".xaml") {
                    $type = "WinUI3"
                }
                
                # Determine tier (heuristic)
                $tier = "Core"
                if ($relativePath -like "*pro*" -or $relativePath -like "*Pro*") {
                    $tier = "Pro"
                } elseif ($relativePath -like "*advanced*" -or $relativePath -like "*Advanced*") {
                    $tier = "Advanced"
                } elseif ($relativePath -like "*tech*" -or $relativePath -like "*Tech*" -or $relativePath -like "*debug*") {
                    $tier = "Technical"
                } elseif ($relativePath -like "*meta*" -or $relativePath -like "*Meta*") {
                    $tier = "Meta"
                }
                
                # Determine category
                $category = "Studio"
                if ($relativePath -like "*profile*") { $category = "Profiles" }
                elseif ($relativePath -like "*library*") { $category = "Library" }
                elseif ($relativePath -like "*effect*" -or $relativePath -like "*mixer*") { $category = "Effects" }
                elseif ($relativePath -like "*analyze*") { $category = "Analyze" }
                elseif ($relativePath -like "*diagnostic*" -or $relativePath -like "*log*") { $category = "Diagnostics" }
                
                # Determine target path
                $targetPath = $relativePath
                if ($type -eq "Python") {
                    # Python panels go to app/ui/panels/
                    $targetPath = "app\ui\panels\$($file.Name)"
                } elseif ($type -eq "WinUI3") {
                    # XAML panels go to src/VoiceStudio.App/Views/Panels/
                    $targetPath = "src\VoiceStudio.App\Views\Panels\$($file.Name)"
                }
                
                $panel = @{
                    name = $name
                    source = $relativePath
                    target = $targetPath
                    type = $type
                    tier = $tier
                    category = $category
                    region = "Center"  # Default, will be determined during migration
                    status = "pending"
                    dependencies = @()
                    notes = ""
                }
                
                $panels += $panel
                Write-Host "  Found: $name ($type, $tier)" -ForegroundColor Green
            }
        }
    }
}

# Sort by tier, then name
$panels = $panels | Sort-Object -Property tier, name

# Generate output
$output = @{
    total = $panels.Count
    discovered = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    panels = $panels
}

# Group by tier for summary
$byTier = $panels | Group-Object -Property tier
Write-Host "`nSummary:" -ForegroundColor Cyan
foreach ($group in $byTier) {
    Write-Host "  $($group.Name): $($group.Count) panels" -ForegroundColor Yellow
}

# Save JSON catalog
$output | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8
Write-Host "`nCatalog saved to: $OutputPath" -ForegroundColor Green

# Generate markdown catalog
$mdPath = $OutputPath -replace "\.json$", ".md"
$mdContent = @"
# VoiceStudio Panel Catalog
## Complete Inventory of All Panels

**Total Panels:** $($panels.Count)  
**Discovered:** $(Get-Date -Format "yyyy-MM-dd")

---

"@

foreach ($tier in @("Core", "Pro", "Advanced", "Technical", "Meta")) {
    $tierPanels = $panels | Where-Object { $_.tier -eq $tier }
    if ($tierPanels.Count -gt 0) {
        $mdContent += "`n## $tier Panels ($($tierPanels.Count) panels)`n`n"
        foreach ($panel in $tierPanels) {
            $mdContent += "- [ ] **$($panel.name)**  `n"
            $mdContent += "  Source: ``$($panel.source)``  `n"
            $mdContent += "  Target: ``$($panel.target)``  `n"
            $mdContent += "  Type: $($panel.type) | Category: $($panel.category) | Status: $($panel.status)  `n"
        }
    }
}

$mdContent | Set-Content -Path $mdPath -Encoding UTF8
Write-Host "Markdown catalog saved to: $mdPath" -ForegroundColor Green

Write-Host "`nDiscovery complete! Found $($panels.Count) panels." -ForegroundColor Cyan

