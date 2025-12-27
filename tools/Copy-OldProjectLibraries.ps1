<#
.SYNOPSIS
    Copy libraries and tools from old VoiceStudio projects
    
.DESCRIPTION
    Copies Python packages and tools from old project directories
    instead of downloading from pip.
    
.PARAMETER SourceProject
    Source project directory (C:\VoiceStudio or C:\OldVoiceStudio)
    
.PARAMETER ToolsOnly
    Only copy tools, not libraries
    
.PARAMETER LibrariesOnly
    Only copy libraries, not tools
    
.EXAMPLE
    .\Copy-OldProjectLibraries.ps1 -SourceProject "C:\OldVoiceStudio"
    
.EXAMPLE
    .\Copy-OldProjectLibraries.ps1 -SourceProject "C:\VoiceStudio" -ToolsOnly
#>

param(
    [string]$SourceProject = "C:\OldVoiceStudio",
    [switch]$ToolsOnly,
    [switch]$LibrariesOnly
)

$ErrorActionPreference = "Stop"
$currentProject = "E:\VoiceStudio"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Copy Old Project Libraries & Tools" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Source: $SourceProject" -ForegroundColor Yellow
Write-Host "Target: $currentProject" -ForegroundColor Yellow
Write-Host ""

# Check source exists
if (!(Test-Path $SourceProject)) {
    Write-Host "❌ Source project not found: $SourceProject" -ForegroundColor Red
    Write-Host "Available options:" -ForegroundColor Yellow
    Write-Host "  - C:\VoiceStudio" -ForegroundColor Gray
    Write-Host "  - C:\OldVoiceStudio" -ForegroundColor Gray
    exit 1
}

# Libraries to copy
$libraries = @(
    "essentia_tensorflow", "voicefixer", "deepfilternet", "spleeter",
    "pedalboard", "audiomentations", "resampy", "pyrubberband",
    "pesq", "pystoi", "fairseq", "faiss", "faiss_cpu", "pyworld",
    "parselmouth", "py_cpuinfo", "GPUtil", "nvidia_ml_py", "wandb",
    "webrtcvad", "umap", "spacy", "tensorboard", "prometheus_client",
    "prometheus_fastapi_instrumentator", "insightface"
)

# Tools to copy
$tools = @(
    "audio_quality_benchmark.py", "quality_dashboard.py", "dataset_qa.py",
    "dataset_report.py", "benchmark_engines.py", "system_health_validator.py",
    "system_monitor.py", "performance-monitor.py", "profile_engine_memory.py",
    "train_ultimate.py", "train_voice_quality.py", "config-optimizer.py",
    "repair_wavs.py", "mark_bad_clips.py"
)

$copiedLibraries = @()
$copiedTools = @()
$missingLibraries = @()
$missingTools = @()

if (!$ToolsOnly) {
    # Copy libraries
    Write-Host "[Libraries] Copying Python packages..." -ForegroundColor Cyan
    Write-Host ""
    
    # Try .venv first, then venv
    $oldVenv = Join-Path $SourceProject ".venv\Lib\site-packages"
    if (!(Test-Path $oldVenv)) {
        $oldVenv = Join-Path $SourceProject "venv\Lib\site-packages"
    }
    
    $newVenv = Join-Path $currentProject ".venv\Lib\site-packages"
    
    if (Test-Path $oldVenv) {
        Write-Host "  Source venv: $oldVenv" -ForegroundColor Gray
        Write-Host "  Target venv: $newVenv" -ForegroundColor Gray
        Write-Host ""
        
        # Ensure target directory exists
        if (!(Test-Path $newVenv)) {
            New-Item -ItemType Directory -Path $newVenv -Force | Out-Null
            Write-Host "  Created target venv directory" -ForegroundColor Gray
        }
        
        foreach ($lib in $libraries) {
            $source = Join-Path $oldVenv $lib
            $dest = Join-Path $newVenv $lib
            
            if (Test-Path $source) {
                Write-Host "  Copying $lib..." -ForegroundColor Gray -NoNewline
                try {
                    Copy-Item -Path $source -Destination $dest -Recurse -Force -ErrorAction Stop
                    $copiedLibraries += $lib
                    Write-Host " ✅" -ForegroundColor Green
                } catch {
                    Write-Host " ❌ Error: $_" -ForegroundColor Red
                }
            } else {
                $missingLibraries += $lib
                Write-Host "  ⚠️  Not found: $lib" -ForegroundColor Yellow
            }
        }
        
        # Copy .dist-info directories
        Write-Host ""
        Write-Host "[Metadata] Copying package metadata..." -ForegroundColor Cyan
        $distInfoCount = 0
        Get-ChildItem -Path $oldVenv -Filter "*.dist-info" -ErrorAction SilentlyContinue | ForEach-Object {
            $name = $_.Name -replace "-.*", ""
            $name = $name -replace "_", "-"
            if ($libraries -contains ($name -replace "-", "_")) {
                try {
                    Copy-Item -Path $_.FullName -Destination $newVenv -Recurse -Force -ErrorAction Stop
                    $distInfoCount++
                } catch {
                    # Silently continue
                }
            }
        }
        Write-Host "  Copied $distInfoCount .dist-info directories" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠️  Virtual environment not found: $oldVenv" -ForegroundColor Yellow
        Write-Host "     Trying alternative locations..." -ForegroundColor Gray
        
        # Try alternative locations
        $altLocations = @(
            "C:\VoiceStudio\.venv\Lib\site-packages",
            "C:\VoiceStudio\venv\Lib\site-packages",
            "C:\OldVoiceStudio\.venv\Lib\site-packages",
            "C:\OldVoiceStudio\venv\Lib\site-packages"
        )
        
        foreach ($altLoc in $altLocations) {
            if (Test-Path $altLoc) {
                Write-Host "  Found: $altLoc" -ForegroundColor Green
                $oldVenv = $altLoc
                break
            }
        }
    }
}

if (!$LibrariesOnly) {
    # Copy tools
    Write-Host ""
    Write-Host "[Tools] Copying scripts..." -ForegroundColor Cyan
    Write-Host ""
    
    $oldTools = Join-Path $SourceProject "tools"
    $newTools = Join-Path $currentProject "tools"
    
    # Ensure tools directory exists
    if (!(Test-Path $newTools)) {
        New-Item -ItemType Directory -Path $newTools -Force | Out-Null
    }
    
    if (Test-Path $oldTools) {
        Write-Host "  Source tools: $oldTools" -ForegroundColor Gray
        Write-Host "  Target tools: $newTools" -ForegroundColor Gray
        Write-Host ""
        
        foreach ($tool in $tools) {
            $source = Join-Path $oldTools $tool
            $dest = Join-Path $newTools $tool
            
            if (Test-Path $source) {
                Write-Host "  Copying $tool..." -ForegroundColor Gray -NoNewline
                try {
                    Copy-Item -Path $source -Destination $dest -Force -ErrorAction Stop
                    $copiedTools += $tool
                    Write-Host " ✅" -ForegroundColor Green
                } catch {
                    Write-Host " ❌ Error: $_" -ForegroundColor Red
                }
            } else {
                $missingTools += $tool
                Write-Host "  ⚠️  Not found: $tool" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "  ⚠️  Tools directory not found: $oldTools" -ForegroundColor Yellow
    }
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Libraries copied: $($copiedLibraries.Count)" -ForegroundColor Green
if ($copiedLibraries.Count -gt 0) {
    $copiedLibraries | ForEach-Object { Write-Host "  ✅ $_" -ForegroundColor Gray }
}

Write-Host ""
Write-Host "Tools copied: $($copiedTools.Count)" -ForegroundColor Green
if ($copiedTools.Count -gt 0) {
    $copiedTools | ForEach-Object { Write-Host "  ✅ $_" -ForegroundColor Gray }
}

if ($missingLibraries.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing libraries: $($missingLibraries.Count)" -ForegroundColor Yellow
    $missingLibraries | ForEach-Object { Write-Host "  ⚠️  $_" -ForegroundColor Gray }
}

if ($missingTools.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing tools: $($missingTools.Count)" -ForegroundColor Yellow
    $missingTools | ForEach-Object { Write-Host "  ⚠️  $_" -ForegroundColor Gray }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Test imports:" -ForegroundColor Yellow
Write-Host "   python -c 'import essentia_tensorflow'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Update requirements_engines.txt with actual versions" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Verify all tools work in new project" -ForegroundColor Yellow
Write-Host ""

