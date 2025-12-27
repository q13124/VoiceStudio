# Discover React/Electron Panels in C:\VoiceStudio
# Generates catalog for conversion planning

param(
    [string]$SourcePath = "C:\VoiceStudio",
    [string]$OutputDir = "E:\VoiceStudio\docs\governance"
)

$ErrorActionPreference = "Continue"

$separator = "=" * 60
Write-Host $separator -ForegroundColor Cyan
Write-Host "React/Electron Panel Discovery" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $SourcePath)) {
    Write-Host "ERROR: Source path not found: $SourcePath" -ForegroundColor Red
    exit 1
}

Write-Host "Searching: $SourcePath" -ForegroundColor Yellow
Write-Host ""

$panels = @()

# Search for React components
Write-Host "Searching for React components..." -ForegroundColor Yellow
$jsxFiles = Get-ChildItem -Path $SourcePath -Recurse -Filter "*.jsx" -ErrorAction SilentlyContinue
$tsxFiles = Get-ChildItem -Path $SourcePath -Recurse -Filter "*.tsx" -ErrorAction SilentlyContinue

foreach ($file in ($jsxFiles + $tsxFiles)) {
    $relativePath = $file.FullName.Replace($SourcePath, "").TrimStart("\")
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    
    # Try to extract component name
    $componentName = $null
    if ($content -match 'export\s+(?:default\s+)?(?:function|const)\s+(\w+)') {
        $componentName = $matches[1]
    } elseif ($content -match 'export\s+(?:default\s+)?class\s+(\w+)') {
        $componentName = $matches[1]
    } else {
        $componentName = $file.BaseName
    }
    
    # Check if it's a panel/view
    $isPanel = $file.Name -like "*Panel*" -or 
               $file.Name -like "*View*" -or
               $file.Name -like "*Component*" -or
               $relativePath -like "*panel*" -or
               $relativePath -like "*view*" -or
               $relativePath -like "*component*"
    
    if ($isPanel) {
        $panels += [PSCustomObject]@{
            Name = $componentName
            File = $relativePath
            FullPath = $file.FullName
            Type = if ($file.Extension -eq ".tsx") { "TypeScript" } else { "JavaScript" }
            Size = $file.Length
            LastModified = $file.LastWriteTime
        }
        Write-Host "  Found: $relativePath ($componentName)" -ForegroundColor Green
    }
}

# Search for Electron main files
Write-Host ""
Write-Host "Searching for Electron files..." -ForegroundColor Yellow
$electronFiles = @()
$mainFiles = Get-ChildItem -Path $SourcePath -Recurse -Filter "main.js" -ErrorAction SilentlyContinue
$preloadFiles = Get-ChildItem -Path $SourcePath -Recurse -Filter "preload.js" -ErrorAction SilentlyContinue
$packageFiles = Get-ChildItem -Path $SourcePath -Recurse -Filter "package.json" -ErrorAction SilentlyContinue

if ($packageFiles) {
    Write-Host "  Found package.json files (Electron project detected)" -ForegroundColor Green
    foreach ($pkg in $packageFiles) {
        $pkgContent = Get-Content $pkg.FullName -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($pkgContent) {
            Write-Host "    Project: $($pkgContent.name)" -ForegroundColor Gray
            Write-Host "    Version: $($pkgContent.version)" -ForegroundColor Gray
        }
    }
}

# Generate JSON catalog
$catalog = @{
    source = $SourcePath
    discovered = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    totalPanels = $panels.Count
    panels = $panels | ForEach-Object {
        @{
            name = $_.Name
            file = $_.File
            type = $_.Type
            size = $_.Size
            lastModified = $_.LastModified.ToString("yyyy-MM-dd HH:mm:ss")
        }
    }
    electron = @{
        hasElectron = ($packageFiles.Count -gt 0)
        packageFiles = $packageFiles | ForEach-Object { $_.FullName.Replace($SourcePath, "").TrimStart("\") }
    }
}

$jsonFile = Join-Path $OutputDir "REACT_PANEL_CATALOG.json"
$catalog | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonFile -Encoding UTF8
Write-Host ""
Write-Host "Generated: $jsonFile" -ForegroundColor Green

# Generate Markdown catalog
$mdFile = Join-Path $OutputDir "REACT_PANEL_CATALOG.md"
$md = @"
# React/Electron Panel Catalog

**Source:** $SourcePath  
**Discovered:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Total Panels:** $($panels.Count)

---

## Panels Found

"@

if ($panels.Count -eq 0) {
    $md += @"

**No React panels found.**

This could mean:
- Panels are in a different location
- Panels use a different framework (Vue, Angular, etc.)
- Panels are in a separate repository
- Panels need to be created from scratch

"@
} else {
    $md += @"
| Name | File | Type | Size | Last Modified |
|------|------|------|------|---------------|
"@
    foreach ($panel in $panels) {
        $sizeKB = [math]::Round($panel.Size / 1KB, 2)
        $md += "| $($panel.Name) | ``$($panel.File)`` | $($panel.Type) | $sizeKB KB | $($panel.LastModified.ToString('yyyy-MM-dd')) |`n"
    }
}

$md += @"

---

## Electron Project Info

"@

if ($packageFiles) {
    foreach ($pkg in $packageFiles) {
        $pkgContent = Get-Content $pkg.FullName -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($pkgContent) {
            $md += @"
### $($pkg.FullName.Replace($SourcePath, "").TrimStart("\"))

- **Name:** $($pkgContent.name)
- **Version:** $($pkgContent.version)
- **Description:** $($pkgContent.description)

"@
        }
    }
} else {
    $md += "No Electron project files found."
}

$md | Set-Content -Path $mdFile -Encoding UTF8
Write-Host "Generated: $mdFile" -ForegroundColor Green

Write-Host ""
Write-Host $separator -ForegroundColor Cyan
Write-Host "Discovery complete!" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan
Write-Host ""
Write-Host "Found $($panels.Count) React panels" -ForegroundColor $(if ($panels.Count -gt 0) { "Green" } else { "Yellow" })
Write-Host ""

