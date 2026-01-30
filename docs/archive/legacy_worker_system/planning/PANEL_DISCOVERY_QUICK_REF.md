# Panel Discovery Quick Reference
## Find All Missing Panels

**Problem:** Panels are missing from registry or not being discovered.

**Solution:** Use the comprehensive panel discovery tools.

---

## 🚀 Quick Fix (30 seconds)

```powershell
# Run comprehensive panel discovery
.\tools\Find-AllPanels.ps1

# Verify results
python app\cli\verify_panels.py
```

This will:
1. Search all possible panel locations
2. Find all `*View.xaml` and `*Panel.xaml` files
3. Regenerate `PanelRegistry.Auto.cs`
4. Show what's missing or extra

---

## 📋 Step-by-Step

### Step 1: Discover All Panels

```powershell
cd E:\VoiceStudio
.\tools\Find-AllPanels.ps1
```

**Output:**
- Shows all discovered panels
- Generates `app\core\PanelRegistry.Auto.cs`
- Creates `app\core\PanelRegistry.Auto.txt` (text list)

### Step 2: Verify Discovery

```powershell
python app\cli\verify_panels.py
```

**Output:**
- Compares discovered panels with registry
- Shows missing panels
- Shows extra panels in registry
- Provides summary

### Step 3: Review Results

```powershell
# View generated registry
code app\core\PanelRegistry.Auto.cs

# View text list
code app\core\PanelRegistry.Auto.txt
```

---

## 🔍 What Gets Searched

The discovery script searches:

**Directories:**
- `ui\Views\Panels`
- `ui\Views`
- `ui\Panels`
- `src\VoiceStudio.App\Views\Panels`
- `src\VoiceStudio.App\Views`
- `src\VoiceStudio.App\Panels`
- `app\ui\panels`
- `app\ui\views`
- `Views\Panels`
- `Views`
- `Panels`

**Patterns:**
- `*View.xaml`
- `*Panel.xaml`
- `*ViewModel.cs` (to find corresponding XAML)

---

## ✅ Expected Results

After running discovery:

- **Panel count:** ~90+ panels found
- **Registry file:** `app\core\PanelRegistry.Auto.cs` generated
- **Text list:** `app\core\PanelRegistry.Auto.txt` created
- **No missing panels:** All discovered panels in registry

---

## 🚨 Troubleshooting

### Issue: Still Missing Panels

**Check:**
1. Are panels in a non-standard location?
2. Do panels use non-standard naming?
3. Are panels in subdirectories?

**Fix:**
1. Add custom search directory to `Find-AllPanels.ps1`
2. Add custom pattern if needed
3. Check `verify_panels.py` output for locations

### Issue: Too Many Panels Found

**Check:**
1. Are test/mock panels included?
2. Are duplicate panels being found?

**Fix:**
1. Filter out test directories in script
2. Check for duplicates in registry
3. Review `verify_panels.py` for extras

### Issue: Registry Not Updating

**Check:**
1. Is `PanelRegistry.Auto.cs` being generated?
2. Is file writable?
3. Are there syntax errors?

**Fix:**
1. Check script output for errors
2. Verify file permissions
3. Review generated C# code

---

## 📊 Integration with Migration

The migration script (`VS_MigrateToE.ps1`) now:

1. **Searches comprehensively** (11+ directories)
2. **Finds via ViewModels** (if XAML not found directly)
3. **Calls Find-AllPanels.ps1** (if available)
4. **Logs discoveries** (shows what's found)

**During migration:**
- Panels are auto-discovered
- Registry is auto-generated
- Missing panels are logged

**After migration:**
- Run `Find-AllPanels.ps1` to verify
- Run `verify_panels.py` to check
- Review registry file

---

## 🔗 Related Tools

- **Find-AllPanels.ps1** - Comprehensive discovery
- **verify_panels.py** - Verification and comparison
- **Discover-Panels.ps1** - Catalog generation (from C:\VoiceStudio)
- **verify_env.py** - Full environment check (includes panels)

---

## 💡 Tips

1. **Run discovery after migration** - Ensures all panels found
2. **Check verify_panels.py output** - Shows exactly what's missing
3. **Review PanelRegistry.Auto.txt** - Easy-to-read panel list
4. **Update manual registry** - Merge auto-discovered with defaults

---

**Run `.\tools\Find-AllPanels.ps1` to find all missing panels quickly!**

