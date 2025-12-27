# Post-Migration Verification Checklist
## 2-Minute Health Check After Migration

**Quick Fix for Missing Panels:** See [PANEL_DISCOVERY_QUICK_REF.md](PANEL_DISCOVERY_QUICK_REF.md)

**Purpose:** Quick verification that migration was successful and systems are functional.

---

## ✅ Step 1: Activate Venv & Run Health Check

```powershell
cd E:\VoiceStudio

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run health check
python app\cli\verify_env.py

# Run panel verification (if panels seem missing)
python app\cli\verify_panels.py

# Or regenerate panel registry
.\tools\Find-AllPanels.ps1
```

**Expected Output:**
```
============================================================
VoiceStudio Environment Verification
============================================================

[1] Python Version
Python: 3.10.15
  ✓ Python version OK

[2] Critical Paths
  ✓ Workspace root: E:\VoiceStudio
  ✓ Engines directory: E:\VoiceStudio\engines
  ✓ Models directory: E:\VoiceStudio\models
  ✓ Library directory: E:\VoiceStudio\library
  ...

[3] Governor + Learners
  ✓ Governor: E:\VoiceStudio\app\core\runtime\governor.py
  ✓ Quality Scorer: E:\VoiceStudio\app\core\learners\quality_scorer.py
  ...

[4] Engine Configuration
  ✓ Engine config found
    Defaults: {'tts': 'xtts_v2', 'image_gen': 'sdxl_comfy', 'video_gen': 'svd'}
    Installed: 6 engines

[5] Panel Count
  ✓ Found 92 panels in E:\VoiceStudio\ui\Views\Panels
  ✓ Total panels found: 92
  ✓ Panel count matches expected (~90+)

[6] Path References
  ✓ No C:\VoiceStudio references found

============================================================
✓ All checks passed!
```

---

## ✅ Step 2: Launch WinUI 3 App

```powershell
# Build solution (if needed)
dotnet build src\VoiceStudio.sln

# Launch app
start src\VoiceStudio.App\bin\Debug\net8.0-windows10.0.19041.0\VoiceStudio.App.exe
```

**Or:** Open solution in Visual Studio and run.

---

## ✅ Step 3: Verify Engine Manager

1. Open app
2. Navigate to **Settings → Engine Manager**
3. Verify:
   - ✅ Engines are detected (should show 6+ engines)
   - ✅ Default engines set correctly:
     - TTS: `xtts_v2`
     - Image Gen: `sdxl_comfy`
     - Video Gen: `svd`
   - ✅ Installed engines list shows all engines
   - ✅ Engine status indicators work

**Expected:**
- Engine list populated
- Defaults match `engines/config.json`
- Health checks working (if runtime engines)

---

## ✅ Step 4: Verify Panel Manager

1. Navigate to **Settings → Panel Manager** (or View → Panels)
2. Verify:
   - ✅ Panel count matches ~90+
   - ✅ All panels listed (no missing panels)
   - ✅ Panel regions assigned correctly
   - ✅ Default layout panels set:
     - Left: Profiles
     - Center: Timeline
     - Right: EffectsMixer
     - Bottom: Macro

**Expected:**
- Full panel list visible
- Count matches discovery (~90+)
- No panels hidden or missing

---

## ✅ Step 5: Visual Verification

### Premium UI Contract

Verify these are preserved:

- ✅ **Dense, docked panels** - Layout is dense, panels dockable
- ✅ **Waveform/spectrogram/mixer** - Visual components present
- ✅ **Micro-interactions** - Hover effects, animations work
- ✅ **GPU meters** - Performance indicators visible
- ✅ **Design tokens** - Colors, typography consistent
- ✅ **Theme switching** - Themes (Dark/SciFi/Light) work
- ✅ **Density presets** - Compact/Comfort density works
- ✅ **Command-center layout** - Premiere/Resolve/FL-style maintained
- ✅ **Keyboard efficiency** - Shortcuts work
- ✅ **Real-time feedback** - Updates are responsive

---

## 🚨 Troubleshooting

### Issue: Health Check Fails

**Check:**
- Python version (3.10+)
- Virtual environment activated
- Paths exist
- Governor/learners files present

**Fix:**
- Re-run migration script
- Check error messages
- Verify paths

### Issue: Engines Not Detected

**Check:**
- `engines/config.json` exists
- Engine manifests present
- Engine router initialized

**Fix:**
- Verify `engines/` directory structure
- Check manifest files
- Review engine router logs

### Issue: Panel Count Mismatch

**Check:**
- `PanelRegistry.Auto.cs` generated
- Panels in expected directories
- Registry merge working

**Fix:**
- Re-run `Discover-Panels.ps1`
- Verify panel directories
- Check registry merge logic

### Issue: Old Path References

**Check:**
- Path rewrite completed
- Config files updated
- Code files updated

**Fix:**
- Re-run path rewrite in migration script
- Manually search for `C:\VoiceStudio`
- Update remaining references

---

## 📋 Quick Checklist

- [ ] Health check passes
- [ ] App launches successfully
- [ ] Engine Manager shows engines
- [ ] Panel Manager shows ~90+ panels
- [ ] Default layout correct
- [ ] Theme switching works
- [ ] Density presets work
- [ ] No C:\VoiceStudio references
- [ ] Governor + learners intact
- [ ] Premium UI contract maintained

---

## ⏱️ Time Estimate

- **Health check:** 30 seconds
- **App launch:** 30 seconds
- **Engine verification:** 30 seconds
- **Panel verification:** 30 seconds
- **Total:** ~2 minutes

---

**These checks verify migration success and premium UI contract preservation.**

