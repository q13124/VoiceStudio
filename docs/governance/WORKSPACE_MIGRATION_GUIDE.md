# Complete Workspace Migration Guide
## Migrating C:\VoiceStudio → E:\VoiceStudio

**Purpose:** Comprehensive guide for migrating the entire workspace, including all panels, engines, dependencies, and configurations.

**What This Does:**
1. Copies entire workspace from C:\VoiceStudio → E:\VoiceStudio (without deleting C)
2. Rebuilds fresh venv on E: and reinstalls pinned deps (offline-first)
3. Finds & rewrites old absolute paths in configs/manifests to point to E:\VoiceStudio
4. Updates dataset paths: `C:\VoiceStudio\datasets\` → `E:\VoiceStudio\library\`
5. Updates model paths: `C:\VoiceStudio\models\` → `E:\VoiceStudio\models\`
6. Re-syncs Panel Registry to include all ~200 panels (auto-discovery)
7. Installs modular engine layer for runtime engine selection
8. Preserves Governor + learners orchestration and hooks to engine router
9. Maintains premium UI characteristics (dense, dockable, pro-DAW layouts)

---

## 🚀 Quick Start

### Run Master Migration Script

```powershell
cd E:\VoiceStudio
.\tools\VS_MigrateToE.ps1
```

This will perform complete workspace migration automatically.

**Alternative (original script):**
```powershell
.\tools\Migrate-Workspace.ps1
```

### Options

```powershell
# Dry run / List only (see what would be copied without making changes)
.\tools\VS_MigrateToE.ps1 -ListOnly

# Custom source/target paths
.\tools\VS_MigrateToE.ps1 -Src "C:\VoiceStudio" -Dst "E:\VoiceStudio"

# Original script with more options
.\tools\Migrate-Workspace.ps1 -DryRun
.\tools\Migrate-Workspace.ps1 -SkipVenv
.\tools\Migrate-Workspace.ps1 -SkipEngines
```

---

## 📋 Migration Steps Explained

### Step 1: Copy Workspace Files

**What it does:**
- Uses **Robocopy** for efficient file copying
- Copies all files from `C:\VoiceStudio` to `E:\VoiceStudio`
- Excludes: `.venv`, `venv`, `__pycache__`, `.git`, `node_modules`, build artifacts, etc.
- Preserves directory structure and timestamps
- Multi-threaded (16 threads) for faster copying

**What gets copied:**
- All Python source files
- All UI files (XAML, C#)
- Configuration files
- Documentation
- Tools and scripts

**What gets excluded:**
- Virtual environments (`.venv`, `venv`)
- Cache directories (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`)
- Build artifacts (`dist`, `build`, `out`, `bin`, `obj`)
- IDE directories (`.git`, `.idea`, `.vs`)
- Node modules (`node_modules`)
- System files (`Thumbs.db`, `desktop.ini`)

**Disk Space Check:**
- Script checks available disk space before copying
- Requires ~20-80 GB depending on models/assets

### Step 2: Rebuild Virtual Environment

**What it does:**
- Removes old venv (if exists)
- Creates fresh Python virtual environment
- Upgrades pip
- Installs pinned dependencies from `requirements.txt`
- Uses pip cache for offline-first installation (if available)

**Requirements:**
- Python 3.10.15 installed
- `requirements.txt` in project root
- Internet connection (or pip cache)

**Offline-first:**
- Script checks for pip cache in `%APPDATA%\pip\cache`
- Uses cache if available for faster, offline installation

### Step 3: Rewrite Absolute Paths

**What it does:**
- Scans all text-based files (configs, code, docs)
- Finds references to `C:\VoiceStudio` using regex
- Replaces with `E:\VoiceStudio`
- Safe for text files only (skips binary/locked files)

**Files updated:**
- `*.json` - Configuration files
- `*.yaml`, `*.yml` - YAML configs
- `*.toml` - TOML configs
- `*.ps1`, `*.psm1` - PowerShell scripts
- `*.cs`, `*.csproj`, `*.sln` - C# files
- `*.xaml` - XAML UI files
- `*.md` - Markdown documentation

**Path replacements:**
- Uses regex escaping for safe replacement
- `C:\VoiceStudio` → `E:\VoiceStudio`
- Handles all path variations
- Skips binary files and locked files gracefully

### Step 4: Re-sync Panel Registry

**What it does:**
- Auto-generates `app/core/PanelRegistry.Auto.cs` with all discovered XAML panels
- Runs `Discover-Panels.ps1` to find all panels (if script exists)
- Generates `PANEL_CATALOG.json` and `PANEL_CATALOG.md`
- Searches multiple paths: `ui\Views\Panels`, `src\VoiceStudio.App\Views\Panels`, `app\ui\panels`

**Auto-Generated Panel Registry:**
- Creates `PanelRegistryAuto` class with `AllXaml()` method
- Lists all `*View.xaml` files found in panel directories
- Can be used to auto-register panels in PanelRegistry

**After this step:**
- Review `app/core/PanelRegistry.Auto.cs`
- Review `docs/governance/PANEL_CATALOG.md`
- Register panels in `PanelRegistry.cs` (manual or using auto-generated list)
- See `BULK_PANEL_MIGRATION_GUIDE.md` for details

### Step 5: Install Modular Engine Layer

**What it does:**
- Ensures `app/core/engines/protocols.py` exists (EngineProtocol)
- Copies/adapts engines from source
- Creates `app/core/engines/router.py` (EngineRouter)
- Sets up runtime engine selection system

**Engine Router Features:**
- Register multiple engine types
- Get engine instances on demand
- List available engines
- Manage engine lifecycle

**Usage:**
```python
from app.core.engines.router import router

# Register engine
router.register_engine("xtts", XTTSEngine)

# Get engine instance
engine = router.get_engine("xtts", gpu=True)

# List available engines
engines = router.list_engines()
```

### Step 6: Preserve Governor + Learners

**What it does:**
- Looks for Governor files in common locations
- Copies Governor orchestration files
- Creates `app/core/runtime/engine_hook.py`
- Hooks Governor to engine router

**Governor Integration:**
- Governor can access engines via `EngineHook`
- Maintains orchestration logic
- Preserves learner connections

**Engine Hook:**
```python
from app.core.runtime.engine_hook import hook

# Get engine for Governor use
engine = hook.get_engine("xtts", gpu=True)

# List available engines
engines = hook.list_available_engines()
```

### Step 7: Verify Premium UI

**What it does:**
- Checks for essential UI components:
  - Design Tokens (`DesignTokens.xaml`)
  - PanelHost control
  - PanelRegistry
  - Theme Manager
- Verifies premium UI structure is intact

**Premium UI Characteristics Maintained:**
- ✅ Dense, dockable layouts
- ✅ Pro-DAW style interface
- ✅ High-fidelity meters
- ✅ Panel hierarchy
- ✅ Design token consistency
- ✅ Micro-interactions
- ✅ Performance optimizations

---

## 🔧 Manual Steps After Migration

### 1. Review Migrated Files

```powershell
# Check what was copied
Get-ChildItem -Path E:\VoiceStudio -Recurse -File | Measure-Object

# Review panel catalog
code E:\VoiceStudio\docs\governance\PANEL_CATALOG.md
```

### 2. Register Panels

See `BULK_PANEL_MIGRATION_GUIDE.md` for panel registration:
- Review discovered panels
- Register in `PanelRegistry.cs`
- Add DataTemplates for WinUI 3 panels
- Test panel loading

### 3. Test Engine Router

```python
# Test engine router
from app.core.engines.router import router
from app.core.engines.xtts_engine import XTTSEngine

router.register_engine("xtts", XTTSEngine)
engine = router.get_engine("xtts", gpu=True)
print(f"Engine initialized: {engine.is_initialized()}")
```

### 4. Test Governor Integration

```python
# Test Governor hook
from app.core.runtime.engine_hook import hook

engines = hook.list_available_engines()
print(f"Available engines: {engines}")
```

### 5. Verify UI

- Launch WinUI 3 app
- Verify panels load
- Test theme switching
- Verify design tokens apply
- Check panel docking

---

## ⚠️ Important Notes

### What Gets Preserved

- ✅ All source code
- ✅ All configurations (with path updates)
- ✅ All documentation
- ✅ All tools and scripts
- ✅ Governor + learners orchestration
- ✅ Premium UI structure

### What Gets Rebuilt

- 🔄 Virtual environment (fresh)
- 🔄 Panel Registry (re-synced)
- 🔄 Engine layer (modularized)
- 🔄 Path references (updated)

### What Requires Manual Work

- 📝 Panel registration in PanelRegistry.cs
- 📝 Testing each migrated component
- 📝 Adapting panels to new architecture (if needed)
- 📝 Updating any hardcoded paths in code

---

## 🐛 Troubleshooting

### Issue: Venv creation fails

**Solution:**
- Ensure Python 3.10.15 is installed
- Check Python is in PATH
- Try creating venv manually: `python -m venv venv`

### Issue: Dependencies fail to install

**Solution:**
- Check `requirements.txt` exists
- Verify internet connection
- Try installing manually: `pip install -r requirements.txt`
- Check for version conflicts

### Issue: Paths not updated

**Solution:**
- Manually search for `C:\VoiceStudio` in files
- Use Find & Replace in IDE
- Check config file formats are supported

### Issue: Panels not discovered

**Solution:**
- Run `Discover-Panels.ps1` manually
- Check source directory structure
- Verify panel file patterns match

### Issue: Engine router not working

**Solution:**
- Verify `protocols.py` exists
- Check engine classes inherit `EngineProtocol`
- Test engine registration manually

---

## 📚 Related Documents

- **Panel Migration:** `BULK_PANEL_MIGRATION_GUIDE.md`
- **Panel Strategy:** `PANEL_MIGRATION_STRATEGY.md`
- **Migration Rules:** `Cursor-Migration-Ruleset.md`
- **Migration Log:** `Migration-Log.md`
- **Architecture:** `../design/VoiceStudio-Architecture.md`

---

## ✅ Success Checklist

After running migration:

- [ ] All files copied to E:\VoiceStudio
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] Paths updated in config files
- [ ] Panel catalog generated
- [ ] Engine router created
- [ ] Governor hook created
- [ ] UI components verified
- [ ] Manual panel registration started
- [ ] Engine router tested
- [ ] Governor integration tested
- [ ] UI launches correctly

---

**Run `.\tools\VS_MigrateToE.ps1` to perform complete workspace migration automatically.**

**Note:** `VS_MigrateToE.ps1` is the recommended script (uses Robocopy, more efficient). `Migrate-Workspace.ps1` provides additional features like engine router setup and Governor hooks.

