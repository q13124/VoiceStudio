# Copy Old Project Libraries & Tools Plan
## VoiceStudio Quantum+ - Integrate from Old Projects Instead of Downloading

**Date:** 2025-01-28  
**Status:** 📋 **PLAN CREATED**  
**User Requirement:** Copy libraries and tools from old project instead of downloading everything

---

## 🎯 Goal

**Copy libraries and tools from old project directories:**
- `C:\VoiceStudio` - Old project (read-only reference)
- `C:\OldVoiceStudio` - Old project (read-only reference)  
- `X:\VoiceStudioGodTier` - God-tier modules (if accessible)

**Instead of:** Downloading everything from pip

---

## 📋 Old Project Directories

### Library Locations (Python Packages)

**Old Project Virtual Environments:**
- `C:\VoiceStudio\.venv\Lib\site-packages\` - Python packages
- `C:\OldVoiceStudio\.venv\Lib\site-packages\` - Python packages
- `C:\VoiceStudio\venv\Lib\site-packages\` - Alternative venv location
- `C:\OldVoiceStudio\venv\Lib\site-packages\` - Alternative venv location

**Tools & Scripts:**
- `C:\OldVoiceStudio\tools\` - Tools and scripts
- `C:\VoiceStudio\tools\` - Tools and scripts

**God-Tier Modules:**
- `X:\VoiceStudioGodTier\core\` - Advanced modules

---

## 🔍 Step 1: Identify What to Copy

### Libraries to Copy (from site-packages)

**Audio Quality Libraries:**
- `essentia_tensorflow/` - Advanced audio analysis
- `voicefixer/` - Voice restoration
- `deepfilternet/` - Speech enhancement
- `spleeter/` - Source separation
- `pedalboard/` - Audio effects chain
- `audiomentations/` - Dataset augmentation
- `resampy/` - High-quality resampling
- `pyrubberband/` - Time-stretching
- `pesq/` - Perceptual quality score
- `pystoi/` - Speech intelligibility

**RVC & Voice Conversion:**
- `fairseq/` - RVC HuBERT features
- `faiss/` or `faiss_cpu/` - Vector similarity search
- `pyworld/` - Vocoder features
- `parselmouth/` - Prosody analysis

**Performance Monitoring:**
- `py_cpuinfo/` - CPU information
- `GPUtil/` - GPU monitoring
- `nvidia_ml_py/` - NVIDIA GPU stats
- `wandb/` - Experiment tracking

**Advanced Utilities:**
- `webrtcvad/` - Voice activity detection
- `umap/` - Dimensionality reduction
- `spacy/` - NLP processing
- `tensorboard/` - Training visualization
- `prometheus_client/` - Metrics
- `prometheus_fastapi_instrumentator/` - FastAPI metrics

**Deepfake & Video:**
- `insightface/` - Face recognition
- `opencv_contrib_python/` - Extended OpenCV (if separate)

### Tools & Scripts to Copy

**From `C:\OldVoiceStudio\tools\`:**

1. **Audio Quality Tools:**
   - `audio_quality_benchmark.py`
   - `quality_dashboard.py`
   - `dataset_qa.py`
   - `dataset_report.py`
   - `benchmark_engines.py`

2. **System Health & Monitoring:**
   - `system_health_validator.py`
   - `system_monitor.py`
   - `performance-monitor.py`
   - `profile_engine_memory.py`

3. **Training & Optimization:**
   - `train_ultimate.py`
   - `train_voice_quality.py`
   - `config-optimizer.py`

4. **Audio Processing Utilities:**
   - `repair_wavs.py`
   - `mark_bad_clips.py`

---

## 🔧 Step 2: Copy Libraries from Old Project

### Method 1: Copy from site-packages (Recommended)

**PowerShell Script to Copy Libraries:**

```powershell
# Copy libraries from old project venv to current project venv
$oldVenv = "C:\OldVoiceStudio\.venv\Lib\site-packages"
$newVenv = "E:\VoiceStudio\.venv\Lib\site-packages"

# Libraries to copy
$libraries = @(
    "essentia_tensorflow",
    "voicefixer",
    "deepfilternet",
    "spleeter",
    "pedalboard",
    "audiomentations",
    "resampy",
    "pyrubberband",
    "pesq",
    "pystoi",
    "fairseq",
    "faiss",
    "faiss_cpu",
    "pyworld",
    "parselmouth",
    "py_cpuinfo",
    "GPUtil",
    "nvidia_ml_py",
    "wandb",
    "webrtcvad",
    "umap",
    "spacy",
    "tensorboard",
    "prometheus_client",
    "prometheus_fastapi_instrumentator",
    "insightface"
)

foreach ($lib in $libraries) {
    $source = Join-Path $oldVenv $lib
    $dest = Join-Path $newVenv $lib
    
    if (Test-Path $source) {
        Write-Host "Copying $lib..."
        Copy-Item -Path $source -Destination $dest -Recurse -Force
        Write-Host "✅ Copied $lib"
    } else {
        Write-Host "⚠️ Not found: $lib"
    }
}
```

### Method 2: Copy .dist-info directories

**Also copy package metadata:**

```powershell
# Copy .dist-info directories for package metadata
$distInfos = Get-ChildItem -Path $oldVenv -Filter "*.dist-info" | Where-Object {
    $name = $_.Name -replace "-.*", ""
    $libraries -contains $name
}

foreach ($distInfo in $distInfos) {
    Copy-Item -Path $distInfo.FullName -Destination $newVenv -Recurse -Force
}
```

---

## 🛠️ Step 3: Copy Tools & Scripts

### Copy Tools from Old Project

```powershell
# Copy tools from old project
$oldTools = "C:\OldVoiceStudio\tools"
$newTools = "E:\VoiceStudio\tools"

$toolsToCopy = @(
    "audio_quality_benchmark.py",
    "quality_dashboard.py",
    "dataset_qa.py",
    "dataset_report.py",
    "benchmark_engines.py",
    "system_health_validator.py",
    "system_monitor.py",
    "performance-monitor.py",
    "profile_engine_memory.py",
    "train_ultimate.py",
    "train_voice_quality.py",
    "config-optimizer.py",
    "repair_wavs.py",
    "mark_bad_clips.py"
)

foreach ($tool in $toolsToCopy) {
    $source = Join-Path $oldTools $tool
    $dest = Join-Path $newTools $tool
    
    if (Test-Path $source) {
        Write-Host "Copying $tool..."
        Copy-Item -Path $source -Destination $dest -Force
        Write-Host "✅ Copied $tool"
    } else {
        Write-Host "⚠️ Not found: $tool"
    }
}
```

---

## 📝 Step 4: Verify & Test

### Verify Copied Libraries

```powershell
# Test imports
python -c "import essentia_tensorflow; print('✅ essentia-tensorflow')"
python -c "import voicefixer; print('✅ voicefixer')"
python -c "import deepfilternet; print('✅ deepfilternet')"
python -c "import spleeter; print('✅ spleeter')"
python -c "import pedalboard; print('✅ pedalboard')"
python -c "import audiomentations; print('✅ audiomentations')"
python -c "import resampy; print('✅ resampy')"
python -c "import pyrubberband; print('✅ pyrubberband')"
python -c "import pesq; print('✅ pesq')"
python -c "import pystoi; print('✅ pystoi')"
python -c "import fairseq; print('✅ fairseq')"
python -c "import faiss; print('✅ faiss')"
python -c "import pyworld; print('✅ pyworld')"
python -c "import parselmouth; print('✅ parselmouth')"
```

### Update Requirements File

**After copying, update `requirements_engines.txt` to reflect installed versions:**

```bash
# Generate requirements from installed packages
pip freeze | Select-String "essentia|voicefixer|deepfilternet|spleeter|pedalboard|audiomentations|resampy|pyrubberband|pesq|pystoi|fairseq|faiss|pyworld|parselmouth|py-cpuinfo|GPUtil|nvidia-ml-py|wandb|webrtcvad|umap-learn|spacy|tensorboard|prometheus|insightface" > copied_libraries_versions.txt
```

---

## 🚀 Complete Integration Script

**Create: `tools/Copy-OldProjectLibraries.ps1`**

```powershell
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
#>

param(
    [string]$SourceProject = "C:\OldVoiceStudio",
    [switch]$ToolsOnly,
    [switch]$LibrariesOnly
)

$ErrorActionPreference = "Stop"
$currentProject = "E:\VoiceStudio"

Write-Host "Copying from: $SourceProject" -ForegroundColor Yellow
Write-Host "To: $currentProject" -ForegroundColor Yellow

# Check source exists
if (!(Test-Path $SourceProject)) {
    throw "Source project not found: $SourceProject"
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

if (!$ToolsOnly) {
    # Copy libraries
    Write-Host "`n[Libraries] Copying Python packages..." -ForegroundColor Cyan
    
    $oldVenv = Join-Path $SourceProject ".venv\Lib\site-packages"
    if (!(Test-Path $oldVenv)) {
        $oldVenv = Join-Path $SourceProject "venv\Lib\site-packages"
    }
    
    $newVenv = Join-Path $currentProject ".venv\Lib\site-packages"
    
    if (Test-Path $oldVenv) {
        foreach ($lib in $libraries) {
            $source = Join-Path $oldVenv $lib
            $dest = Join-Path $newVenv $lib
            
            if (Test-Path $source) {
                Write-Host "  Copying $lib..." -ForegroundColor Gray
                Copy-Item -Path $source -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  ✅ $lib" -ForegroundColor Green
            }
        }
        
        # Copy .dist-info directories
        Write-Host "`n[Metadata] Copying package metadata..." -ForegroundColor Cyan
        Get-ChildItem -Path $oldVenv -Filter "*.dist-info" | ForEach-Object {
            $name = $_.Name -replace "-.*", ""
            if ($libraries -contains $name) {
                Copy-Item -Path $_.FullName -Destination $newVenv -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    } else {
        Write-Host "⚠️ Virtual environment not found: $oldVenv" -ForegroundColor Yellow
    }
}

if (!$LibrariesOnly) {
    # Copy tools
    Write-Host "`n[Tools] Copying scripts..." -ForegroundColor Cyan
    
    $oldTools = Join-Path $SourceProject "tools"
    $newTools = Join-Path $currentProject "tools"
    
    if (Test-Path $oldTools) {
        foreach ($tool in $tools) {
            $source = Join-Path $oldTools $tool
            $dest = Join-Path $newTools $tool
            
            if (Test-Path $source) {
                Write-Host "  Copying $tool..." -ForegroundColor Gray
                Copy-Item -Path $source -Destination $dest -Force
                Write-Host "  ✅ $tool" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "⚠️ Tools directory not found: $oldTools" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Copy complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Test imports: python -c 'import essentia_tensorflow'"
Write-Host "2. Update requirements_engines.txt with actual versions"
Write-Host "3. Verify all tools work in new project"
```

---

## ✅ Success Criteria

1. ✅ All libraries copied from old project venv
2. ✅ All tools copied from old project tools directory
3. ✅ All imports work in new project
4. ✅ Requirements file updated with actual versions
5. ✅ No need to download from pip

---

## 📝 Next Steps

1. **Run the copy script:**
   ```powershell
   .\tools\Copy-OldProjectLibraries.ps1
   ```

2. **Verify imports:**
   ```powershell
   .\tools\Test-CopiedLibraries.ps1
   ```

3. **Update requirements:**
   - Generate versions from copied packages
   - Update `requirements_engines.txt`

4. **Test tools:**
   - Run each copied tool
   - Verify they work in new project structure

---

**Document Created:** 2025-01-28  
**Status:** Ready for Execution  
**Script:** `tools/Copy-OldProjectLibraries.ps1` (to be created)

