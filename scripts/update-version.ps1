# Update Version Numbers Across Project
# Usage: .\scripts\update-version.ps1 -NewVersion "1.1.0"

param(
    [Parameter(Mandatory=$true)]
    [string]$NewVersion
)

Write-Host "Updating version to $NewVersion..." -ForegroundColor Cyan

# Validate version format (SemVer: MAJOR.MINOR.PATCH)
if ($NewVersion -notmatch '^\d+\.\d+\.\d+') {
    Write-Error "Invalid version format. Expected format: MAJOR.MINOR.PATCH (e.g., 1.1.0)"
    exit 1
}

$filesUpdated = 0

# Update AssemblyInfo.cs (if exists)
$assemblyInfoPath = "src/VoiceStudio.App/Properties/AssemblyInfo.cs"
if (Test-Path $assemblyInfoPath) {
    $content = Get-Content $assemblyInfoPath -Raw
    $newContent = $content -replace 'AssemblyVersion\(".*?"\)', "AssemblyVersion(`"$NewVersion.0`")"
    $newContent = $newContent -replace 'AssemblyFileVersion\(".*?"\)', "AssemblyFileVersion(`"$NewVersion.0`")"
    
    if ($content -ne $newContent) {
        $newContent | Set-Content $assemblyInfoPath -NoNewline
        Write-Host "  Updated: $assemblyInfoPath" -ForegroundColor Green
        $filesUpdated++
    }
}

# Update .csproj file (if exists)
$csprojPath = "src/VoiceStudio.App/VoiceStudio.App.csproj"
if (Test-Path $csprojPath) {
    $content = Get-Content $csprojPath -Raw
    $newContent = $content -replace '<Version>.*?</Version>', "<Version>$NewVersion</Version>"
    
    if ($content -ne $newContent) {
        $newContent | Set-Content $csprojPath -NoNewline
        Write-Host "  Updated: $csprojPath" -ForegroundColor Green
        $filesUpdated++
    }
}

# Update package.json (if exists)
$packageJsonPath = "package.json"
if (Test-Path $packageJsonPath) {
    $content = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
    $content.version = $NewVersion
    $content | ConvertTo-Json -Depth 10 | Set-Content $packageJsonPath
    Write-Host "  Updated: $packageJsonPath" -ForegroundColor Green
    $filesUpdated++
}

# Update README.md (if exists)
$readmePath = "README.md"
if (Test-Path $readmePath) {
    $content = Get-Content $readmePath -Raw
    $newContent = $content -replace 'Version:.*?(\d+\.\d+\.\d+)', "Version: $NewVersion"
    $newContent = $newContent -replace 'v\d+\.\d+\.\d+', "v$NewVersion"
    
    if ($content -ne $newContent) {
        $newContent | Set-Content $readmePath -NoNewline
        Write-Host "  Updated: $readmePath" -ForegroundColor Green
        $filesUpdated++
    }
}

# Update backend version (if exists)
$backendMainPath = "backend/api/main.py"
if (Test-Path $backendMainPath) {
    $content = Get-Content $backendMainPath -Raw
    $newContent = $content -replace 'version=".*?"', "version=`"$NewVersion`""
    
    if ($content -ne $newContent) {
        $newContent | Set-Content $backendMainPath -NoNewline
        Write-Host "  Updated: $backendMainPath" -ForegroundColor Green
        $filesUpdated++
    }
}

if ($filesUpdated -eq 0) {
    Write-Warning "No version files found or updated"
} else {
    Write-Host "Version updated in $filesUpdated file(s)" -ForegroundColor Green
}

