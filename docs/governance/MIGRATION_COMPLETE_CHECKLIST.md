# Migration Complete Checklist
## Verify Everything After Migration

**Purpose:** Comprehensive checklist to ensure migration is complete and all systems are functional.

---

## ✅ Pre-Migration

- [ ] Source workspace exists: `C:\VoiceStudio`
- [ ] Target workspace ready: `E:\VoiceStudio`
- [ ] Sufficient disk space (~20-80 GB)
- [ ] Python 3.10+ installed
- [ ] .NET 8 SDK installed (for WinUI 3)

---

## ✅ Migration Execution

- [ ] Ran `.\tools\VS_MigrateToE.ps1`
- [ ] Migration completed without errors
- [ ] All files copied successfully
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Paths updated

---

## ✅ Post-Migration Verification

### 1. Environment Check

```powershell
.\.venv\Scripts\Activate.ps1
python app\cli\verify_env.py
```

- [ ] Python version OK (3.10+)
- [ ] All critical paths exist
- [ ] Governor + learners found
- [ ] Engine config loaded
- [ ] No C:\VoiceStudio references

### 2. Panel Discovery

```powershell
.\tools\Find-AllPanels.ps1
python app\cli\verify_panels.py
```

- [ ] ~90+ panels discovered
- [ ] `PanelRegistry.Auto.cs` generated
- [ ] All panels in registry
- [ ] No missing panels

### 3. Engine System

```powershell
# Check engine config
python -c "from app.core.engines.config import get_engine_config; c = get_engine_config(); print(c.get_config())"
```

- [ ] Engine config exists
- [ ] Defaults set correctly
- [ ] Installed engines listed
- [ ] Engine manifests found

### 4. Governor + Learners

- [ ] Governor file exists
- [ ] All 3 learners exist:
  - [ ] Quality scorer
  - [ ] Prosody tuner
  - [ ] Dataset curator
- [ ] Dataset paths updated to `E:\VoiceStudio\library\`
- [ ] Model paths updated

### 5. WinUI 3 App

```powershell
dotnet build src\VoiceStudio.sln
```

- [ ] Solution builds successfully
- [ ] No compilation errors
- [ ] App launches
- [ ] UI loads correctly

### 6. App Functionality

**Engine Manager:**
- [ ] Engines detected
- [ ] Defaults displayed correctly
- [ ] Installed engines listed

**Panel Manager:**
- [ ] ~90+ panels listed
- [ ] Default layout correct
- [ ] Panels can be opened

**UI Features:**
- [ ] Theme switching works
- [ ] Density presets work
- [ ] Design tokens applied
- [ ] Premium UI maintained

---

## 🚨 Common Issues & Fixes

### Issue: Panels Missing

**Fix:**
```powershell
.\tools\Find-AllPanels.ps1
```

### Issue: Old Path References

**Fix:**
```powershell
# Search for C:\VoiceStudio
Select-String -Path "**\*.cs","**\*.py","**\*.json" -Pattern "C:\\VoiceStudio"
# Update manually or re-run migration
```

### Issue: Engine Not Detected

**Fix:**
```powershell
# Check manifest exists
Test-Path "engines\audio\xtts_v2\engine.manifest.json"

# Check config
python -c "from app.core.engines.config import get_engine_config; print(get_engine_config().get_config())"
```

### Issue: Governor/Learners Missing

**Fix:**
- Check if files in different location
- Verify paths updated
- Check import statements

---

## 📊 Success Criteria

Migration is successful when:

- ✅ All panels discovered (~90+)
- ✅ All panels registered
- ✅ Engines detected and configured
- ✅ Governor + learners intact
- ✅ App builds and launches
- ✅ Premium UI maintained
- ✅ No old path references
- ✅ All systems functional

---

## 📝 Next Steps

After verification:

1. **Register panels** in manual `PanelRegistry.cs`
2. **Test engine functionality**
3. **Verify Governor integration**
4. **Test UI features**
5. **Update documentation** if needed

---

**Use this checklist to ensure complete and successful migration!**

