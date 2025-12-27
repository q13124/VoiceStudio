# Bulk Panel Migration Guide
## Migrating ~200 Panels from C:\VoiceStudio

**Purpose:** Step-by-step guide for migrating all panels in batches

**Estimated Panels:** ~200 panels

---

## 🚀 Quick Start

### Step 1: Discover All Panels

```powershell
cd E:\VoiceStudio
.\tools\Discover-Panels.ps1
```

This will:
- Scan `C:\VoiceStudio` for all panel files
- Generate `docs/governance/PANEL_CATALOG.json`
- Generate `docs/governance/PANEL_CATALOG.md`
- Categorize panels by tier and type

### Step 2: Review Catalog

Open `docs/governance/PANEL_CATALOG.md` and review:
- Total panel count
- Panel distribution by tier
- Panel types (Python/WinUI3)
- Source and target paths

### Step 3: Start Batch Migration

Follow the migration strategy in `PANEL_MIGRATION_STRATEGY.md`:
1. Migrate Core panels first
2. Then Pro panels
3. Then Advanced panels
4. Then Technical panels
5. Then Meta panels
6. Finally Plugin panels

---

## 📋 Migration Workflow for Each Panel

### For Python/PySide6 Panels

1. **Read Source:**
   - Open panel from `C:\VoiceStudio`
   - Understand structure and functionality

2. **Rebuild in E:\VoiceStudio:**
   - Create `app\ui\panels\{PanelName}.py`
   - Use PySide6 + qfluentwidgets
   - Follow Fluent design system
   - Remove legacy UI coupling

3. **Register Panel:**
   - Add to PanelRegistry (if applicable)
   - Set tier, category, region
   - Add to Command Palette

4. **Test:**
   - Create minimal test
   - Verify panel loads
   - Test basic functionality

5. **Document:**
   - Update PANEL_CATALOG.md
   - Update Migration-Log.md
   - Mark as complete

### For WinUI 3/XAML Panels

1. **Read Source:**
   - Open XAML and code-behind from `C:\VoiceStudio`
   - Understand layout and bindings

2. **Rebuild in E:\VoiceStudio:**
   - Create `src\VoiceStudio.App\Views\Panels\{PanelName}View.xaml`
   - Create `src\VoiceStudio.App\Views\Panels\{PanelName}View.xaml.cs`
   - Create `src\VoiceStudio.App\ViewModels\Panels\{PanelName}ViewModel.cs`
   - Use MVVM pattern
   - Use design tokens (VSQ.*)
   - Use PanelHost

3. **Register Panel:**
   - Add to PanelRegistry
   - Add DataTemplate to PanelTemplates.xaml
   - Set tier, category, region

4. **Test:**
   - Verify panel loads in MainWindow
   - Test data bindings
   - Test theme switching

5. **Document:**
   - Update PANEL_CATALOG.md
   - Update Migration-Log.md
   - Mark as complete

---

## 🔄 Batch Migration Process

### Using Migration Scripts

1. **Discover Panels:**
   ```powershell
   .\tools\Discover-Panels.ps1
   ```

2. **Review and Select Batch:**
   - Open PANEL_CATALOG.md
   - Select panels for batch (e.g., all Core panels)
   - Create list of panel names

3. **Run Batch Migration (Basic):**
   ```powershell
   $panels = @("Panel1", "Panel2", "Panel3")
   .\tools\Migrate-PanelBatch.ps1 -PanelNames $panels
   ```

4. **Manual Review Required:**
   - Script creates basic adapted versions
   - **Manual review and adaptation required** for each panel
   - Follow migration workflow above

5. **Update Catalog:**
   - Mark panels as complete in PANEL_CATALOG.md
   - Update Migration-Log.md with batch entry

---

## 📊 Batch Entry Format

For bulk migrations, use batch entries in Migration-Log.md:

```markdown
- [x] **Panel Batch: Core Panels (15 panels)**  
  Source: `C:\VoiceStudio\ui\panels\core\`  
  Target: `E:\VoiceStudio\app\ui\panels\core\`  
  Status: ✅ Complete  
  Date: 2025-XX-XX  
  Notes: Migrated 15 core panels. All adapted to new architecture.
  
  **Panels Migrated:**
  - ProfilesView ✅
  - TimelineView ✅
  - EffectsMixerView ✅
  - AnalyzerView ✅
  - MacroView ✅
  - DiagnosticsView ✅
  - ... (9 more)
```

---

## 🎯 Recommended Migration Order

### Phase 1: Foundation (Week 1)
- [ ] Run discovery script
- [ ] Review catalog
- [ ] Migrate 6 core panels (if not done)
- [ ] Set up batch infrastructure

### Phase 2: Core Panels (Weeks 2-3)
- [ ] Migrate remaining core panels (10-15 panels)
- [ ] Test core functionality
- [ ] Fix any issues

### Phase 3: Pro Panels (Weeks 4-6)
- [ ] Migrate pro panels (30-50 panels)
- [ ] Test premium features
- [ ] Fix any issues

### Phase 4: Advanced Panels (Weeks 7-9)
- [ ] Migrate advanced panels (40-60 panels)
- [ ] Test specialized tools
- [ ] Fix any issues

### Phase 5: Technical & Meta (Weeks 10-11)
- [ ] Migrate technical panels (20-30 panels)
- [ ] Migrate meta panels (10-20 panels)
- [ ] Test system features

### Phase 6: Plugin Panels (Weeks 12+)
- [ ] Migrate plugin panels (30-50 panels)
- [ ] Test plugin system
- [ ] Final integration

---

## ⚠️ Important Notes

1. **Automation is Limited:**
   - Scripts can discover and create basic structure
   - **Manual adaptation required** for each panel
   - Architecture differences require careful review

2. **Quality Over Speed:**
   - Better to migrate correctly than quickly
   - Test each panel after migration
   - Fix issues before moving on

3. **Incremental Approach:**
   - Migrate in small batches
   - Test after each batch
   - Document progress

4. **No Bulk Copying:**
   - Always read and rebuild
   - Adapt to new architecture
   - Update paths and dependencies

---

## 📚 Reference Documents

- **Migration Strategy:** `PANEL_MIGRATION_STRATEGY.md`
- **Panel Catalog:** `PANEL_CATALOG.md` (generate with discovery script)
- **Migration Rules:** `Cursor-Migration-Ruleset.md`
- **Panel Implementation:** `../design/PANEL_IMPLEMENTATION_GUIDE.md`
- **Architecture:** `../design/VoiceStudio-Architecture.md`

---

## ✅ Success Checklist

All panels migrated when:

- [ ] Discovery script run
- [ ] Catalog generated and reviewed
- [ ] All core panels migrated
- [ ] All pro panels migrated
- [ ] All advanced panels migrated
- [ ] All technical panels migrated
- [ ] All meta panels migrated
- [ ] All plugin panels migrated
- [ ] All panels registered
- [ ] All panels tested
- [ ] Migration log complete
- [ ] Panel catalog updated

---

**Start by running `.\tools\Discover-Panels.ps1` to discover all ~200 panels, then follow this guide for systematic migration.**

