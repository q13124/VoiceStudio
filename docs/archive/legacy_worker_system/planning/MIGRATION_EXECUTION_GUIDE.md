# Migration Execution Guide
## Step-by-Step Migration from C:\VoiceStudio → E:\VoiceStudio

**Purpose:** Detailed guide for executing the migration safely.

---

## ⚠️ Pre-Migration Checklist

Before running migration, verify:

- [ ] Source exists: `C:\VoiceStudio`
- [ ] Destination ready: `E:\VoiceStudio` (will be created if needed)
- [ ] Disk space: ~20-80 GB free on E: drive
- [ ] Python 3.10+ installed and on PATH
- [ ] Robocopy available (Windows built-in)

**Test prerequisites:**
```powershell
.\tools\Test-Migration.ps1
```

---

## 🚀 Migration Execution

### Step 1: Test with Dry-Run (Recommended)

```powershell
.\tools\VS_MigrateToE.ps1 -ListOnly
```

**What it does:**
- Shows what would be copied
- Doesn't actually copy files
- Verifies source is accessible
- Checks for issues

**Expected output:**
- List of files that would be copied
- No actual file operations

### Step 2: Run Full Migration

```powershell
.\tools\VS_MigrateToE.ps1
```

**What it does:**
1. **Preflight checks**
   - Verifies source exists
   - Checks disk space
   - Creates destination directory

2. **File copying** (Robocopy)
   - Copies all files from C:\VoiceStudio → E:\VoiceStudio
   - Excludes: venv, caches, build artifacts, .git
   - Multi-threaded (16 threads) for speed

3. **Virtual environment**
   - Removes old venv (if exists)
   - Creates fresh Python 3.10 venv
   - Upgrades pip
   - Installs dependencies (offline-first if cache available)

4. **Path updates**
   - Scans all text files
   - Updates `C:\VoiceStudio` → `E:\VoiceStudio`
   - Updates `C:\VoiceStudio\datasets\` → `E:\VoiceStudio\library\`
   - Updates `C:\VoiceStudio\models\` → `E:\VoiceStudio\models\`

5. **Panel discovery**
   - Searches 11+ directories for panels
   - Finds `*View.xaml` and `*Panel.xaml`
   - Generates `PanelRegistry.Auto.cs`
   - Runs comprehensive discovery script

6. **Panel catalog**
   - Generates `PANEL_CATALOG.json`
   - Generates `PANEL_CATALOG.md`

**Expected duration:**
- Small workspace: 5-10 minutes
- Large workspace with models: 15-30 minutes

---

## 📊 Monitoring Progress

The script provides progress indicators:

```
[Preflight] Source: C:\VoiceStudio  ->  Dest: E:\VoiceStudio
[Disk] E: Free 150.5 GB
[Copy] Robocopy starting...
[Copy] Robocopy completed (exit code: 1)
[Venv] Creating venv...
[Pip] Installing from requirements.txt ...
[PathRewrite] Path updates complete
[PanelDiscovery] Found 200 unique panels
[PanelRegistry] Generated PanelRegistry.Auto.cs with 200 panels
[Done] Migrated to E:\VoiceStudio
```

**Note:** Robocopy exit codes 0-7 are success (some files may not need copying).

---

## ✅ Post-Migration Verification

### Step 1: Activate Venv & Health Check

```powershell
.\.venv\Scripts\Activate.ps1
python app\cli\verify_env.py
```

**Expected:**
- ✓ Python version OK
- ✓ All critical paths exist
- ✓ Governor + learners found
- ✓ Engine config loaded
- ✓ Panel count ~200
- ✓ No C:\VoiceStudio references

### Step 2: Verify Panels

```powershell
python app\cli\verify_panels.py
```

**Expected:**
- ✓ All discovered panels registered
- ✓ No missing panels
- ✓ Panel count matches discovery

### Step 3: Regenerate Panel Registry (if needed)

```powershell
.\tools\Find-AllPanels.ps1
```

**Use if:**
- Panel count seems low
- Panels missing from registry
- Need to refresh discovery

### Step 4: Build & Test App

```powershell
dotnet build src\VoiceStudio.sln
```

**Then launch app and verify:**
- Engine Manager shows all engines
- Panel Manager shows ~200 panels
- Theme switching works
- Premium UI maintained

---

## 🚨 Troubleshooting

### Issue: Script Fails Immediately

**Check:**
- Source path exists: `Test-Path "C:\VoiceStudio"`
- PowerShell execution policy: `Get-ExecutionPolicy`
- Script syntax: Check for errors in script

**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Robocopy Errors

**Check:**
- Disk space sufficient
- Source accessible
- Permissions correct

**Fix:**
- Free up disk space
- Check source permissions
- Run as administrator if needed

### Issue: Python/Venv Issues

**Check:**
- Python installed: `python --version`
- Python on PATH
- Virtual environment creation

**Fix:**
- Install Python 3.10+
- Add Python to PATH
- Create venv manually if needed

### Issue: Panels Not Discovered

**Check:**
- Panels exist in expected directories
- Search directories correct
- File naming matches patterns

**Fix:**
```powershell
# Run comprehensive discovery
.\tools\Find-AllPanels.ps1

# Check results
python app\cli\verify_panels.py
```

### Issue: Path Updates Incomplete

**Check:**
- Files scanned correctly
- Path patterns match
- Files writable

**Fix:**
```powershell
# Search for remaining C:\VoiceStudio
Select-String -Path "**\*.cs","**\*.py","**\*.json" -Pattern "C:\\VoiceStudio"
```

---

## 📋 Migration Checklist

- [ ] Prerequisites verified (`Test-Migration.ps1`)
- [ ] Dry-run successful (`-ListOnly`)
- [ ] Full migration executed
- [ ] Health check passes
- [ ] Panel verification passes
- [ ] App builds successfully
- [ ] Engines detected
- [ ] Panels visible (~200)
- [ ] Premium UI maintained

---

## ⏱️ Time Estimates

- **Prerequisites check:** 30 seconds
- **Dry-run:** 1-2 minutes
- **Full migration:** 10-30 minutes (depends on size)
- **Verification:** 2-3 minutes
- **Total:** ~15-35 minutes

---

## 📚 Related Documents

- **Migration Guide:** `WORKSPACE_MIGRATION_GUIDE.md`
- **Post-Migration:** `POST_MIGRATION_CHECKS.md`
- **Panel Discovery:** `PANEL_DISCOVERY_QUICK_REF.md`
- **Complete Checklist:** `MIGRATION_COMPLETE_CHECKLIST.md`

---

**Follow this guide for safe and successful migration!**

