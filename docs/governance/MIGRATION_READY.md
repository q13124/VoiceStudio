# Migration Ready Checklist
## Pre-Migration Verification

**Status:** ✅ All systems ready for migration from C:\VoiceStudio → E:\VoiceStudio

---

## ✅ System Components Ready

### 1. Migration Script
- ✅ `tools/VS_MigrateToE.ps1` - Production-ready migration script
- ✅ Uses Robocopy for efficient copying
- ✅ Handles path updates (workspace, datasets, models)
- ✅ Rebuilds venv with pinned dependencies
- ✅ Auto-discovers panels
- ✅ Generates PanelRegistry.Auto.cs

### 2. Panel Discovery System
- ✅ `tools/Find-AllPanels.ps1` - Comprehensive discovery
- ✅ `app/cli/verify_panels.py` - Verification tool
- ✅ Enhanced migration script integration
- ✅ Searches 11+ directories
- ✅ Finds via ViewModels

### 3. Engine System
- ✅ Engine manifest system (`engines/*/engine.manifest.json`)
- ✅ Runtime engine system (`engines/*/runtime.manifest.json`)
- ✅ Engine configuration (`engines/config.json`)
- ✅ Engine router with manifest loading
- ✅ Runtime engine manager

### 4. Governor + Learners
- ✅ Preservation rules documented
- ✅ Path update mappings defined
- ✅ Integration points identified

### 5. Verification Tools
- ✅ `app/cli/verify_env.py` - Environment health check
- ✅ `app/cli/verify_panels.py` - Panel verification
- ✅ Post-migration checklist

---

## 📋 Current State

### Panels Found: 16
- Current skeleton panels in E:\VoiceStudio
- After migration: Expected ~200 panels from C:\VoiceStudio

### Engines Configured: 6
- xtts_v2 (audio/TTS)
- piper (audio/TTS)
- openvoice (audio/TTS)
- sdxl_comfy (image/generation)
- realesrgan (image/upscaling)
- svd (video/generation)

### Systems Ready:
- ✅ Panel discovery
- ✅ Engine routing
- ✅ Runtime engines
- ✅ Configuration management
- ✅ Migration automation

---

## 🚀 Ready to Migrate

### Pre-Migration Steps

1. **Verify Source:**
   ```powershell
   Test-Path "C:\VoiceStudio"
   ```

2. **Check Disk Space:**
   ```powershell
   Get-PSDrive E | Select-Object Used,Free
   ```
   Need: ~20-80 GB free

3. **Verify Python:**
   ```powershell
   python --version
   ```
   Need: Python 3.10+

### Migration Command

```powershell
cd E:\VoiceStudio
.\tools\VS_MigrateToE.ps1
```

**What it does:**
1. Copies all files (excludes venv, caches)
2. Rebuilds venv on E:
3. Installs dependencies
4. Updates all paths
5. Discovers all panels
6. Generates PanelRegistry.Auto.cs

### Post-Migration Verification

```powershell
# 1. Health check
.\.venv\Scripts\Activate.ps1
python app\cli\verify_env.py

# 2. Panel verification
python app\cli\verify_panels.py

# 3. Regenerate panel registry (if needed)
.\tools\Find-AllPanels.ps1
```

---

## 📊 Expected Results After Migration

### Panels
- **Before:** 16 panels (skeleton)
- **After:** ~200 panels (from C:\VoiceStudio)
- **Registry:** `PanelRegistry.Auto.cs` auto-generated

### Engines
- **Manifests:** All engine manifests copied
- **Config:** `engines/config.json` updated
- **Router:** All engines discoverable

### Governor + Learners
- **Files:** Copied and paths updated
- **Datasets:** `E:\VoiceStudio\library\` (quality, prosody, curated)
- **Models:** `E:\VoiceStudio\models\` or `%PROGRAMDATA%\VoiceStudio\models\`

### Paths
- **Workspace:** All `C:\VoiceStudio` → `E:\VoiceStudio`
- **Datasets:** All `C:\VoiceStudio\datasets\` → `E:\VoiceStudio\library\`
- **Models:** All `C:\VoiceStudio\models\` → `E:\VoiceStudio\models\`

---

## ✅ Success Criteria

Migration is successful when:

- [ ] All ~200 panels discovered and registered
- [ ] All engines detected and configured
- [ ] Governor + learners intact with updated paths
- [ ] App builds and launches
- [ ] Engine Manager shows all engines
- [ ] Panel Manager shows ~200 panels
- [ ] Premium UI contract maintained
- [ ] No C:\VoiceStudio references remain

---

## 🎯 Next Actions

1. **Run Migration:**
   ```powershell
   .\tools\VS_MigrateToE.ps1
   ```

2. **Verify Results:**
   ```powershell
   python app\cli\verify_env.py
   python app\cli\verify_panels.py
   ```

3. **Review Generated Files:**
   - `app/core/PanelRegistry.Auto.cs`
   - `docs/governance/PANEL_CATALOG.json`
   - `docs/governance/PANEL_CATALOG.md`

4. **Test App:**
   - Build WinUI 3 solution
   - Launch app
   - Verify Engine Manager
   - Verify Panel Manager

---

**All systems are ready. Run `.\tools\VS_MigrateToE.ps1` to begin migration!**

